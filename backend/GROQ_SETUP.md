# Groq API Setup Guide

## Overview
The StudyAI backend uses the Groq API with open-source models (gpt-oss-120b, llama3-8b-8192) for fast AI inference.

## Step 1: Get Your Free API Key

1. Go to **[Groq Console](https://console.groq.com/)**
2. Sign in or create an account
3. Navigate to **API Keys**
4. Create a new API key and copy it

## Step 2: Configure the Backend

Update the `.env` file in the `backend/` directory:

```bash
# Replace with your actual Groq API key
GROQ_API_KEY=gsk_yourActualKeyHere...
```

## Step 3: Start the Backend Server

```bash
cd backend
python -m uvicorn main:app --reload
```

The server will start at `http://127.0.0.1:8000`

## Step 4: Test the API

Run the test script:

```bash
cd backend
python test_api.py
```

## Free Tier Limits (Groq API)

- **Model:** openai/gpt-oss-120b, llama3-8b-8192
- **Requests per minute:** Varies by model
- **Cost:** Free tier available (registration required)
- **Models available:** gpt-oss-120b, llama3-8b-8192, mixtral-8x7b-32768

## API Endpoints

### Health Check
```bash
curl http://127.0.0.1:8000/
```

### Generate Study Materials
Upload a PDF, PPT, or text file to generate study materials:

```bash
curl -X POST "http://127.0.0.1:8000/generate" \
  -F "file=@path/to/your/file.pdf"
```

**Response includes:**
- MCQs (4 multiple choice questions)
- Theory questions (3 explanation questions)
- Flashcards (5 term-definition pairs)
- Summary (2-3 sentence summary)

## Features

✅ **Automatic caching** - Results cached based on file content hash  
✅ **Fallback models** - Can try llama3-8b-8192 if primary model unavailable  
✅ **File format support** - PDF, PPT, PPTX, TXT  
✅ **Size limits** - Max 50MB file size, 4000 char truncation for AI processing  

## Troubleshooting

### API Key Invalid
If you see errors with the API key:
- Verify your API key is correct
- Check that it's active in Groq Console
- Ensure it's not expired

### Rate Limit Exceeded
If you hit rate limits:
- Wait before retrying
- Check Groq Console for your tier limits
- The fallback model (llama3-8b-8192) will be tried automatically

### No API Response
- Check backend is running on port 8000
- Verify GROQ_API_KEY is set in .env
- Check backend logs for errors

## Next Steps

1. Run the test script with a PDF file
2. Customize the AI prompt in `main.py` line 114
3. Add more file format support (images, Word docs)
4. Implement user authentication
5. Set up persistent database storage

## Cost Optimization

With Groq free tier:
- Fast inference on open-source models
- Generous rate limits for development
- No credit card required for free tier

For production:
- Monitor usage at Groq Console
- Choose appropriate models for your use case
- Implement request queuing for high-volume usage

## Resources

- [Groq Console](https://console.groq.com/)
- [Groq API Documentation](https://console.groq.com/docs)
- [StudyAI Backend Code](backend/main.py)