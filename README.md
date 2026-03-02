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



## Constraints Limitations and Lessons Learned

This application is a proof of concept and is not intended for production use. It is a simple example of how to use AI models to extract information from invoices.

Constraints:
- Use only Free Tier Services for DB, AI, and Storage
- Build within 3 hours of starting the project
- Use only the tokens available in the free tier for the chosen AI model

Lessons Learned:
- The very first attempt, to preserve the computational resources, i metaprompted. I discussed and planned with Gemini in detail about what th eproject needs , which tech stack to use, how the app should behave, the entire workflow.
- What i Observed with the conversation that the initial output of the conversation was much better than what the model concluded at the end, even after multiple reminders that initial output was more detailed. My assumption is two things, first is that because of repeated to and fro with the model it lost the context or it got influenced too much with my prompts. Second is that it forgot the initial conversation, maybe it summarised the long text and then could not find the original text.
- The meta prompt worked, it created the app across the entire stack, but it didnt run. It had auth , db, storage, frontend and backend. Debugging it exhausted the free tier tokens.
- The second attempt, I built theh app from small features, testing them and then moving to additional features. This time the app ran successfully. Iterations were reqruied and the Tool ( antigravity) went into UI validation loops and just took a lot of time and iterations. I stopped it a couple of time, nudged it in corrrect direction. 