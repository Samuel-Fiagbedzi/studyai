"""
StudyAI Backend - FastAPI Application
=====================================

A FastAPI application for an AI-powered study system that handles file uploads
and AI processing for educational content.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import asyncio
import uvicorn
import hashlib
import os
import json
import google.genai as genai
from dotenv import load_dotenv
from collections import OrderedDict
import gc

# Load environment variables from .env file
load_dotenv()

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

# Initialize AI clients
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if GOOGLE_API_KEY:
    google_client = genai.Client(api_key=GOOGLE_API_KEY)

openai_client = None
if OPENAI_API_KEY:
    from openai import OpenAI
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Bounded in-memory cache for storing processed content results
# Key: MD5 hash of file content, Value: AI processing result
# Max size: 100 entries; uses LRU eviction policy
class BoundedCache:
    def __init__(self, max_size: int = 100):
        self.cache = OrderedDict()
        self.max_size = max_size
    
    def get(self, key: str):
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def set(self, key: str, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        
        # Evict oldest entry if cache exceeds max size
        if len(self.cache) > self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            gc.collect()  # Force garbage collection

content_cache = BoundedCache(max_size=100)

# Max file size: 50MB
MAX_FILE_SIZE = 50 * 1024 * 1024

async def generate_study_materials_with_ai(text_content: str, timeout: int = 30) -> dict:
    """
    Generate study materials using AI API with real content processing.

    Args:
        text_content: The extracted text content from the document

    Returns:
        dict: Structured study materials with mcq, theory, flashcards, and summary
    """
    if not GOOGLE_API_KEY and not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="No AI API key configured. Set GOOGLE_API_KEY or OPENAI_API_KEY.")

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
        if GOOGLE_API_KEY:
            def google_request() -> str:
                response = google_client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        temperature=0.7,
                        max_output_tokens=1500,
                    )
                )
                return response.text

            result_text = await asyncio.to_thread(google_request)
        else:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an educational assistant that creates study materials. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,  # Limit token usage
                temperature=0.7,
                timeout=timeout
            )
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
        raise HTTPException(status_code=500, detail=f"AI API error: {str(e)}")

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
    Generate study materials from uploaded slide file.

    This endpoint processes PDF or PowerPoint files to generate:
    - Multiple choice questions (MCQs)
    - Theory questions
    - Flashcards
    - Content summary

    Uses caching based on file content hash to avoid reprocessing.

    Args:
        file: Slide file to process

    Returns:
        dict: Generated study materials with MCQs, theory questions, flashcards, and summary
    """
    allowed_mimetypes = {
        "application/pdf",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "text/plain",
    }
    allowed_extensions = {".pdf", ".ppt", ".pptx", ".txt"}
    filename_lower = file.filename.lower()
    file_extension = os.path.splitext(filename_lower)[1]

    if file.content_type not in allowed_mimetypes and file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF, PPT, or PPTX file."
        )

    # Read file content with size check
    file_content = b""
    try:
        while True:
            chunk = await file.read(8192)  # Read in 8KB chunks
            if not chunk:
                break
            file_content += chunk
            
            # Check file size limit
            if len(file_content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File size exceeds {MAX_FILE_SIZE / (1024 * 1024):.0f}MB limit"
                )
    finally:
        # Ensure file is closed and cleaned up
        await file.close()

    # Extract text from PDF
    try:
        from PyPDF2 import PdfReader
        from io import BytesIO
        
        # Create a PDF reader from the file content
        pdf_file = BytesIO(file_content)
        pdf_reader = PdfReader(pdf_file)
        
        # Extract text from all pages
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text() + "\n"
        
        # If no text was extracted, fall back to basic decoding
        if not text_content.strip():
            text_content = file_content.decode('utf-8', errors='ignore')
            
    except Exception as e:
        # Fallback: basic decoding if PDF extraction fails
        print(f"PDF extraction failed: {e}, using fallback method")
        try:
            text_content = file_content.decode('utf-8', errors='ignore')
        except Exception:
            text_content = str(file_content)[:10000]

    # Clean up large file_content from memory
    del file_content
    gc.collect()

    # Generate MD5 hash of the content
    content_hash = hashlib.md5(text_content.encode('utf-8')).hexdigest()

    # Check if result is already cached
    cached_result = content_cache.get(content_hash)
    if cached_result:
        return cached_result

    # Generate AI response using OpenAI
    ai_response = await generate_study_materials_with_ai(text_content, timeout=30)

    # Store result in cache
    content_cache.set(content_hash, ai_response)

    return ai_response

if __name__ == "__main__":
    # Run the application with uvicorn server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload for development
    )