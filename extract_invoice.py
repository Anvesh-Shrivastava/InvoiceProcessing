import os
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key or api_key == "your_api_key_here":
    print("Error: Please set a valid GEMINI_API_KEY in the .env file.")
    exit(1)

genai.configure(api_key=api_key)

def extract_total_due(image_path):
    """
    Uploads an image to Gemini and extracts the 'Total Due' amount.
    """
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return None

    try:
        # Load the image
        img = Image.open(image_path)
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-flash-latest')
        
        # Prepare the prompt
        prompt = "Extract the 'Total Due' or 'Total Amount' from this invoice. Return only the numerical value with currency if present."
        
        # Generate content
        response = model.generate_content([prompt, img])
        
        return response.text.strip()
    except Exception as e:
        print(f"An error occurred during extraction: {e}")
        return None

if __name__ == "__main__":
    invoice_image = "/Users/anvesh/AgenticExperiments/InvoiceProcessing/Gemini_Generated_Image_sggidfsggidfsggi.png"
    print(f"Processing invoice: {invoice_image}")
    
    total_due = extract_total_due(invoice_image)
    if total_due:
        print(f"Extracted Total Due: {total_due}")
    else:
        print("Failed to extract Total Due.")
