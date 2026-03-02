# Invoice Processing Application

An intelligent web application that uses an agentic workflow to extract information from uploaded invoices using Google's Gemini API and other AI models. The project consists of a modern web frontend built with Next.js and a fast, AI-powered backend built with FastAPI.

## Features

- **Upload & OCR**: Upload invoices and automatically extract details (like total amount) using Google Gemini vision capabilities.
- **Agentic Workflow**: Intelligent backend processing to validate and sequence information extraction.
- **Next.js Frontend**: Responsive, modern UI using Next.js App Router, React 19, and TailwindCSS.
- **Better Auth Integration**: Authentication powered by Better Auth.
- **FastAPI Backend**: Robust, high-performance API supporting asynchronous file uploads and integration with AI models.
- **Database & Storage**: Utilizes Neon Serverless Postgres for relational data and Supabase for object storage.

## Tech Stack

### Frontend (`/frontend`)
- **Framework**: [Next.js](https://nextjs.org/) (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth
- **Database Client**: Neon Serverless
- **Icons**: Lucide React

### Backend (`/backend`)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Language**: Python 3.x
- **AI Models**: Google GenAI (Gemini API), Groq
- **Storage**: Supabase
- **Image Processing**: Pillow

## Getting Started

### Prerequisites
- Node.js (v18+)
- Python 3.9+
- Postgres Database (e.g., Neon)
- Google Gemini API Key
- Supabase Account
- Groq API Key (Optional)

### Environment Variables

Copy the `.env.example` in the root and in the frontend to `.env` and fill in the required values:

```bash
cp .env.example .env
```
Key variables needed:
- `DATABASE_URL` (Neon Postgres)
- `GEMINI_API_KEY`
- `BETTER_AUTH_SECRET` & `BETTER_AUTH_URL`
- `NEXT_PUBLIC_BACKEND_URL` (defaults to http://localhost:8000)

### Running the Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn extract_invoice:app --reload
   ```
   The backend will start at `http://localhost:8000`.

### Running the Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install the dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:3000`.

## Project Structure

- `/frontend`: Next.js application containing the UI, routing, and client-side logic.
- `/backend`: FastAPI application containing the agentic workflow, AI integration, and file processing endpoints.
