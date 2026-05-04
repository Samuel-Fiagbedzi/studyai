## Running the Application

```bash
cd backend
python -m uvicorn main:app --reload
```

The server will start at `http://127.0.0.1:8000`

## API Endpoints

- `GET /` - Health check
- `POST /generate` - Generate study materials from PDF/PPT/TXT upload

## Features

- PDF, PPT, PPTX, TXT text extraction
- MD5-based caching to avoid reprocessing same content
- Groq API integration (gpt-oss-120b, llama3-8b-8192)
- OpenAI GPT-3.5-turbo integration (optional fallback)
- Generates MCQs, theory questions, flashcards, and summaries
- SQLite database for persistence
- File size limit: 50MB
- AI processing limit: 4000 characters per request

## Testing

Run the automated test script:

```bash
cd backend
python test_api.py
```

This will:
1. Check backend health
2. Upload a PDF from the backend directory
3. Test caching functionality

## Free Tier Limits

### Groq API (Recommended)
- **Model:** openai/gpt-oss-120b, llama3-8b-8192
- **Requests per minute:** Varies by model
- **Free tier:** Available (registration required)
- **Cost:** Free tier available at https://console.groq.com/

### OpenAI (Alternative)
- **Free credits:** $5 (one-time)
- **Requires:** Credit card for verification
- **Note:** Limited free tier, not recommended for development