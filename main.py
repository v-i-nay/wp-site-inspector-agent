from fastapi import FastAPI, Request, HTTPException
import httpx
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()
logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY environment variable is missing")

@app.get("/")
async def root():
    return {"status": "WP Site Inspector is live 🚀"}

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "")
        
        if not message:
            raise HTTPException(
                status_code=400,
                detail="No message provided"
            )

        url = "https://api.openrouter.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-v3",
            "messages": [{"role": "user", "content": message}]
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            answer = result.get("choices", [{}])[0].get("message", {}).get("content", "No reply")
            
            return {"reply": answer}

    except httpx.TimeoutException:
        logger.error("OpenRouter API timeout")
        raise HTTPException(
            status_code=504,
            detail="OpenRouter API timed out"
        )
    except httpx.RequestError as e:
        logger.error(f"Network error: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail=f"Network error contacting OpenRouter: {str(e)}"
        )
    except Exception as e:
        logger.exception("Unexpected error")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
