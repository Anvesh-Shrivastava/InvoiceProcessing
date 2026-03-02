from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import os
from google import genai
from PIL import Image
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import shutil
from typing import List, Optional
import uuid
from supabase import create_client, Client
from groq import Groq

# Load environment variables from the root .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = FastAPI(title="Invoice Extraction API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Normalize Supabase URL if it's a dashboard link or S3 endpoint
if SUPABASE_URL:
    if "supabase.com/dashboard" in SUPABASE_URL:
        import re
        project_match = re.search(r'project/([^/]+)', SUPABASE_URL)
        if project_match:
            project_id = project_match.group(1)
            SUPABASE_URL = f"https://{project_id}.supabase.co"
            print(f"Normalized Supabase Dashboard URL to: {SUPABASE_URL}")
    elif ".supabase.co/storage/v1/s3" in SUPABASE_URL:
        SUPABASE_URL = SUPABASE_URL.split("/storage/v1/s3")[0]
        print(f"Normalized Supabase S3 URL to: {SUPABASE_URL}")
    elif SUPABASE_URL.endswith("/"):
        SUPABASE_URL = SUPABASE_URL.rstrip("/")

# Clients
try:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
    supabase: Optional[Client] = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
    groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
    print(f"Clients initialized - Gemini: {gemini_client is not None}, Supabase: {supabase is not None}, Groq: {groq_client is not None}")
except Exception as e:
    print(f"Initialization error: {e}")
    supabase = None
    gemini_client = None
    groq_client = None

def get_db_connection():
    if not DATABASE_URL:
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception:
        return None

def create_tables_if_not_exists():
    conn = get_db_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        # Jobs table for tracking workflow state
        cur.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id UUID PRIMARY KEY,
                filename TEXT,
                storage_url TEXT,
                status TEXT DEFAULT 'PENDING',
                extraction_data JSONB,
                validation_results JSONB,
                thc_content NUMERIC,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Inventory table for final verified data
        cur.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id SERIAL PRIMARY KEY,
                job_id UUID REFERENCES jobs(id),
                invoice_number TEXT,
                amount NUMERIC,
                thc_percent NUMERIC,
                product_name TEXT,
                vendor TEXT,
                verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Schema reconciliation (for existing tables with old schemas)
        # Check if invoice_number exists
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'inventory' AND column_name = 'invoice_number'")
        if not cur.fetchone():
            print("Adding missing column 'invoice_number' to 'inventory' table")
            cur.execute("ALTER TABLE inventory ADD COLUMN invoice_number TEXT")
            
        # Check if amount exists (rename total_cost if found)
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'inventory' AND column_name = 'amount'")
        if not cur.fetchone():
            print("Checking for 'total_cost' to rename to 'amount'...")
            cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'inventory' AND column_name = 'total_cost'")
            if cur.fetchone():
                cur.execute("ALTER TABLE inventory RENAME COLUMN total_cost TO amount")
            else:
                cur.execute("ALTER TABLE inventory ADD COLUMN amount NUMERIC")

        # Make legacy columns nullable
        for col in ['user_id', 'batch_id']:
            cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = 'inventory' AND column_name = '{col}'")
            if cur.fetchone():
                print(f"Making legacy column '{col}' nullable")
                cur.execute(f"ALTER TABLE inventory ALTER COLUMN {col} DROP NOT NULL")

        # Fix foreign key constraint (if it points to inventory_jobs instead of jobs)
        cur.execute("""
            SELECT conname, pg_get_constraintdef(oid) 
            FROM pg_constraint 
            WHERE conrelid = 'inventory'::regclass AND conname = 'inventory_job_id_fkey'
        """)
        constraint = cur.fetchone()
        if constraint and 'REFERENCES inventory_jobs' in constraint[1]:
            print("Correcting foreign key constraint to point to 'jobs' table")
            cur.execute("ALTER TABLE inventory DROP CONSTRAINT inventory_job_id_fkey")
            cur.execute("ALTER TABLE inventory ADD CONSTRAINT inventory_job_id_fkey FOREIGN KEY (job_id) REFERENCES jobs(id)")

        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error creating tables: {e}")

@app.on_event("startup")
async def startup_event():
    create_tables_if_not_exists()
    # Ensure bucket exists at startup to avoid SSL/concurrency issues later
    if supabase:
        try:
            buckets = supabase.storage.list_buckets()
            if not any(b.name == 'invoices' for b in buckets):
                print("Creating 'invoices' bucket...")
                supabase.storage.create_bucket('invoices', options={'public': True})
            else:
                # Ensure it's public even if it exists
                print("Bucket 'invoices' already exists. Ensuring it's public...")
                supabase.storage.update_bucket('invoices', options={'public': True})
        except Exception as e:
            print(f"Startup Warning: Could not check/create bucket: {e}")

# --- Workflow Stages ---

async def run_stage_1_extraction(job_id: str, file_path: str):
    """Stage 1: Gemini Extraction"""
    try:
        update_job_status(job_id, "EXTRACTING")
        img = Image.open(file_path)
        
        prompt = (
            "Extract details from this invoice. Return strictly JSON with keys: "
            "'invoice_number', 'amount', 'thc_percent', 'product_name', 'vendor'. "
            "For 'thc_percent', extract the THC percentage value if present (cannabis product)."
        )
        
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, img],
            config={'response_mime_type': 'application/json'}
        )
        
        data = json.loads(response.text)
        
        # Update job with extracted data
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE jobs SET extraction_data = %s, thc_content = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (json.dumps(data), data.get('thc_percent'), job_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        
        await run_stage_2_validation(job_id, data)
        
    except Exception as e:
        update_job_status(job_id, f"FAILED: Extraction - {str(e)}")

async def run_stage_2_validation(job_id: str, extraction_data: dict):
    """Stage 2: Groq Validation"""
    try:
        update_job_status(job_id, "VALIDATING")
        
        thc = extraction_data.get('thc_percent', 0)
        try:
            thc_val = float(thc) if thc else 0
        except:
            thc_val = 0
            
        # Groq handshake
        prompt = f"Validate this extracted cannabis invoice data: {json.dumps(extraction_data)}. Rule: THC must be < 35%. Current THC: {thc_val}%. Return JSON with 'valid' (bool) and 'message' (string)."
        
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        validation_res = json.loads(chat_completion.choices[0].message.content)
        
        # Override validity if THC > 35
        if thc_val > 35:
            validation_res['valid'] = False
            validation_res['message'] = f"THC Content {thc_val}% exceeds regulatory limit of 35%."

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE jobs SET validation_results = %s, status = 'VERIFYING', updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (json.dumps(validation_res), job_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        
    except Exception as e:
        update_job_status(job_id, f"FAILED: Validation - {str(e)}")

def update_job_status(job_id: str, status: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE jobs SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s", (status, job_id))
    conn.commit()
    cur.close()
    conn.close()

# --- Endpoints ---

@app.post("/upload")
async def upload_invoices(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    # Ensure clients are ready
    if not gemini_client or not supabase or not groq_client:
        print(f"Error: Clients not initialized - Gemini: {gemini_client is not None}, Supabase: {supabase is not None}, Groq: {groq_client is not None}")
        raise HTTPException(status_code=500, detail="Clients not initialized (Check .env)")

    job_ids = []
    for file in files:
        job_id = str(uuid.uuid4())
        job_ids.append(job_id)
        print(f"Processing job {job_id} for file {file.filename}")
        
        # 1. Save locally temporarily
        temp_path = os.path.join(os.getcwd(), f"temp_{job_id}_{file.filename}")
        try:
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            print(f"Saved temp file to {temp_path}")
        except Exception as e:
            print(f"Failed to save temp file: {e}")
            raise HTTPException(status_code=500, detail=f"Temp save error: {str(e)}")
            
        # 2. Upload to Supabase Storage
        try:
            with open(temp_path, "rb") as f:
                path_on_supa = f"{job_id}_{file.filename}"
                print(f"Uploading to bucket 'invoices' at path: {path_on_supa}")
                
                content_type = getattr(file, "content_type", "image/png")
                res = supabase.storage.from_("invoices").upload(
                    path=path_on_supa,
                    file=f,
                    file_options={"content-type": content_type}
                )
                print(f"Supabase upload success: {res}")
                storage_url = supabase.storage.from_("invoices").get_public_url(path_on_supa)
                print(f"Public URL: {storage_url}")
        except Exception as e:
            print(f"Supabase storage error: {e}")
            if os.path.exists(temp_path): os.remove(temp_path)
            # Re-raise with more detail
            raise HTTPException(status_code=500, detail=f"Storage error (Supabase): {str(e)}")

        # 3. Create Job Entry
        try:
            conn = get_db_connection()
            if not conn:
                raise Exception("Database connection failed")
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO jobs (id, filename, storage_url) VALUES (%s, %s, %s)",
                (job_id, file.filename, storage_url)
            )
            conn.commit()
            cur.close()
            conn.close()
            print(f"Job {job_id} inserted into DB")
        except Exception as e:
            print(f"Database error: {e}")
            if os.path.exists(temp_path): os.remove(temp_path)
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        # 4. Start Background Process
        background_tasks.add_task(process_job, job_id, temp_path)
        print(f"Background process started for job {job_id}")

    return {"message": "Upload successful", "job_ids": job_ids}

async def process_job(job_id: str, temp_path: str):
    await run_stage_1_extraction(job_id, temp_path)
    if os.path.exists(temp_path):
        os.remove(temp_path)

@app.get("/jobs")
async def get_jobs():
    conn = get_db_connection()
    if not conn: return []
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM jobs ORDER BY created_at DESC")
    jobs = cur.fetchall()
    cur.close()
    conn.close()
    
    # Generate signed URLs for each job to ensure preview works
    if supabase:
        for job in jobs:
            try:
                # Extract path from storage_url or reconstruct it
                # Our path was {job_id}_{filename}
                path = job['storage_url'].split('/')[-1]
                signed_res = supabase.storage.from_("invoices").create_signed_url(path, expires_in=3600)
                if isinstance(signed_res, dict) and 'signedURL' in signed_res:
                    job['storage_url'] = signed_res['signedURL']
                elif isinstance(signed_res, str):
                    job['storage_url'] = signed_res
            except Exception as e:
                print(f"Error generating signed URL for job {job['id']}: {e}")
                
    return jobs

@app.post("/jobs/{job_id}/verify")
async def verify_job(job_id: str, data: dict):
    """Stage 3: Human Verification Handshake"""
    print(f"Verifying job {job_id} with data: {data}")
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cur = conn.cursor()
    try:
        # Sanitize amount (remove commas, currency symbols)
        amount_raw = str(data.get('amount') or '0')
        amount_clean = "".join(c for c in amount_raw if c.isdigit() or c == '.')
        
        # Sanitize thc_percent
        thc_raw = str(data.get('thc_percent') or '0')
        thc_clean = "".join(c for c in thc_raw if c.isdigit() or c == '.')
        
        # Move to inventory
        cur.execute(
            """INSERT INTO inventory (job_id, invoice_number, amount, thc_percent, product_name, vendor) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (job_id, data.get('invoice_number'), 
             float(amount_clean) if amount_clean else 0.0, 
             float(thc_clean) if thc_clean else 0.0, 
             data.get('product_name'), data.get('vendor'))
        )
        # Update job status
        cur.execute("UPDATE jobs SET status = 'COMPLETED', updated_at = CURRENT_TIMESTAMP WHERE id = %s", (job_id,))
        conn.commit()
        print(f"Job {job_id} successfully verified and moved to inventory")
        return {"status": "Job completed and added to inventory"}
    except Exception as e:
        print(f"Verification error for job {job_id}: {e}")
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/health")
def health_check():
    return {"status": "ok", "gemini": gemini_client is not None, "supabase": supabase is not None, "groq": groq_client is not None}
