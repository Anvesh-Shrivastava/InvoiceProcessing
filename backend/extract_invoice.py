from fastapi import FastAPI, UploadFile, File, HTTPException
import os
from google import genai
from PIL import Image
from dotenv import load_dotenv
import psycopg2
import json
import shutil
from typing import Optional

# Load environment variables from the root .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = FastAPI(title="Invoice Extraction API")

# Configure Gemini API Client
api_key = os.getenv("GEMINI_API_KEY")
client = None
if api_key and api_key != "your_api_key_here":
    client = genai.Client(api_key=api_key)

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    if not DATABASE_URL:
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception:
        return None

def create_table_if_not_exists():
    conn = get_db_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id SERIAL PRIMARY KEY,
                invoice_number TEXT,
                amount TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass

@app.on_event("startup")
async def startup_event():
    create_table_if_not_exists()

def insert_invoice(invoice_number, amount):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO invoices (invoice_number, amount) VALUES (%s, %s)",
            (invoice_number, amount)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception:
        return False

@app.post("/extract")
async def extract_invoice(file: UploadFile = File(...)):
    if not client:
        raise HTTPException(status_code=500, detail="Gemini Client not initialized")

    # Save uploaded file temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Load the image
        img = Image.open(temp_path)
        
        # Prepare the prompt
        prompt = "Extract the 'Invoice Number' and 'Total Amount' (or 'Total Due') from this invoice. Return the result strictly in JSON format with keys 'invoice_number' and 'amount'."
        
        # Generate content
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[prompt, img],
            config={'response_mime_type': 'application/json'}
        )
        
        data = json.loads(response.text)
        
        # Save to database
        invoice_num = data.get("invoice_number")
        total_amount = data.get("amount")
        insert_invoice(invoice_num, total_amount)
        
        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/health")
def health_check():
    return {"status": "ok"}
