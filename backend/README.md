# StudyAI Backend Setup

## OpenAI API Configuration

To use the AI-powered study material generation, you need to configure your OpenAI API key:

1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Edit the `.env` file in the backend directory
3. Replace `your_openai_api_key_here` with your actual API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## Running the Application

```bash
cd backend
uvicorn main:app --reload
```

## API Endpoints

- `GET /` - Health check
- `POST /generate` - Generate study materials from PDF upload

## Features

- PDF text extraction (basic)
- MD5-based caching to avoid reprocessing
- OpenAI GPT-3.5-turbo integration for content analysis
- Generates MCQs, theory questions, flashcards, and summaries
- SQLite database for persistence