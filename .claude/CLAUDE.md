# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based article generator project using `uv` for dependency management. The project is a FastAPI-based web service that generates articles for various exam types (TOEIC, IELTS, GRE, SAT) using multiple LLM providers (OpenAI, Gemini).

## Development Commands

- **Run the application**: `uv run main.py`
- **Install dependencies**: `uv install` (uses uv.lock for consistent installs)
- **Add new dependencies**: `uv add <package-name>`
- **Run tests**: `uv run pytest -v`
- **Python version**: Requires Python >= 3.13.5

## Project Structure

```
app/
├── api/routes/          # API route handlers
├── core/               # Core configuration and exceptions
├── models/             # Pydantic models for requests/responses
├── services/           # Business logic services
└── utils/              # Utility functions

configs/                # Configuration files
templates/              # Prompt templates
tests/                  # Test files
main.py                 # FastAPI application entry point
```

## Key Components

- **LLM Service** (`app/services/llm_service.py`) - Unified interface for multiple LLM providers
- **Template Service** (`app/services/template_service.py`) - Dynamic prompt template generation
- **Article Generator** (`app/services/article_generator.py`) - Core article generation logic
- **Configuration** (`app/core/config.py`) - Centralized settings management

## Dependencies

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `openai` - OpenAI API client
- `pydantic` - Data validation
- `python-dotenv` - Environment variable management
- `pytest` - Testing framework
- `httpx` - HTTP client for testing

## Environment Variables

Configure these in your `.env` file:

```
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
DEFAULT_LLM_PROVIDER=openai
```

## API Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health status
- `POST /api/v1/generate` - Generate articles

## Development Notes

- This project uses `uv` as the package manager instead of pip
- The application supports multiple LLM providers with unified interface
- All API configurations are centralized in `app/core/config.py`
- Testing framework is configured with pytest and pytest-asyncio
- Use `uv run` for all Python commands to ensure consistent environment