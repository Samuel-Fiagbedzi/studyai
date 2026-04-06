"""
StudyAI Backend - FastAPI Application
=====================================

A FastAPI application for an AI-powered study system that handles file uploads
and AI processing for educational content.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn
import hashlib
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
import os
import json
from openai import OpenAI

# Create FastAPI application instance
app = FastAPI(
    title="StudyAI Backend",
    description="AI-powered study system backend for processing educational content",
    version="1.0.0"
)

# Configure CORS middleware to allow all origins (for development)
# TODO: In production, specify allowed origins for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# In-memory cache for storing processed content results
# Key: MD5 hash of file content, Value: AI processing result
content_cache = {}

async def generate_study_materials_with_ai(text_content: str) -> dict:
    """
    Generate study materials using OpenAI API.

    Args:
        text_content: The extracted text content from the document

    Returns:
        dict: Structured study materials with mcq, theory, flashcards, and summary
    """
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    # Truncate text if too long to reduce token usage (keep first 4000 characters)
    truncated_text = text_content[:4000] if len(text_content) > 4000 else text_content

    prompt = f"""
Analyze the following educational content and generate study materials. Be concise and focused.

Content:
{truncated_text}

Generate exactly 4 multiple choice questions (MCQs) with 4 options each (A, B, C, D) and indicate the correct answer.
Generate exactly 3 theory questions that require explanation.
Generate exactly 5 flashcards in "Term: Definition" format.
Provide a concise summary (2-3 sentences).

Return ONLY a valid JSON object with this exact structure:
{{
  "mcq": ["Question 1? A) Option1 B) Option2 C) Option3 D) Option4 [Correct: A]"],
  "theory": ["Theory question 1?", "Theory question 2?", "Theory question 3?"],
  "flashcards": ["Term1: Definition1", "Term2: Definition2"],
  "summary": "Concise summary text here."
}}
"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an educational assistant that creates study materials. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,  # Limit token usage
            temperature=0.7
        )

        # Parse the JSON response
        result_text = response.choices[0].message.content.strip()

        # Try to parse as JSON
        try:
            result = json.loads(result_text)
            # Validate structure
            required_keys = ["mcq", "theory", "flashcards", "summary"]
            if not all(key in result for key in required_keys):
                raise ValueError("Missing required keys in response")

            return result

        except (json.JSONDecodeError, ValueError) as e:
            # Fallback: create structured response from text
            return {
                "mcq": ["Error parsing MCQ questions"],
                "theory": ["Error parsing theory questions"],
                "flashcards": ["Error parsing flashcards"],
                "summary": f"Content processed but parsing failed: {str(e)}"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

@app.get("/")
async def root():
    """
    Root endpoint to check if the backend is running.

    Returns:
        dict: A simple message indicating the backend status
    """
    return {"message": "StudyAI Backend Running"}

# TODO: Add file upload endpoint for processing study materials
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint for uploading files to be processed by AI.

    This endpoint will handle various file types (PDF, images, documents)
    and prepare them for AI analysis.

    Args:
        file: The uploaded file

    Returns:
        dict: Processing status and file information
    """
    # Placeholder for file upload logic
    # TODO: Implement file validation, storage, and AI processing
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "status": "File uploaded successfully - AI processing to be implemented"
    }

# TODO: Add AI processing endpoints
@app.post("/process")
async def process_content(content: dict):
    """
    Endpoint for processing content with AI.

    This will handle various AI tasks like:
    - Text analysis and summarization
    - Question generation
    - Study plan creation
    - Content categorization

    Args:
        content: The content to process

    Returns:
        dict: AI processing results
    """
    # Placeholder for AI processing logic
    # TODO: Integrate with OpenAI or other AI services
    return {
        "status": "AI processing placeholder",
        "input": content,
        "result": "AI processing logic to be implemented"
    }

@app.post("/generate")
async def generate_study_materials(file: UploadFile = File(...)):
    """
    Generate study materials from uploaded PDF file.

    This endpoint processes PDF files to generate:
    - Multiple choice questions (MCQs)
    - Theory questions
    - Flashcards
    - Content summary

    Uses caching based on file content hash to avoid reprocessing.

    Args:
        file: PDF file to process

    Returns:
        dict: Generated study materials with MCQs, theory questions, flashcards, and summary
    """
    # Read file content
    file_content = await file.read()

    # Convert to text (basic decoding for now)
    # TODO: Implement proper PDF text extraction
    try:
        text_content = file_content.decode('utf-8')
    except UnicodeDecodeError:
        # Fallback for binary content - convert to string representation
        text_content = str(file_content)

    # Generate MD5 hash of the content
    content_hash = hashlib.md5(text_content.encode('utf-8')).hexdigest()

    # Check if result is already cached
    if content_hash in content_cache:
        return content_cache[content_hash]

    # Generate AI response using OpenAI
    ai_response = await generate_study_materials_with_ai(text_content)

    # Store result in cache
    content_cache[content_hash] = ai_response

    return ai_response

if __name__ == "__main__":
    # Run the application with uvicorn server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload for development
    )