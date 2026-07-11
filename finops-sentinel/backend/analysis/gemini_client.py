import os
import json
import time
import logging
from google import genai
from pydantic import BaseModel
from typing import List

logger = logging.getLogger(__name__)

# Ordered from most to least preferred.
# ALL names below were verified with a live generate_content call on 2026-07-10.
# To re-verify: python analysis/list_available_models.py
MODEL_FALLBACK_CHAIN = [
    "gemini-3.5-flash",         # Primary — newest, highest quality, confirmed working
    "gemini-3-flash-preview",   # Fallback 1 — confirmed working
    "gemini-3.1-flash-lite",    # Fallback 2 — lighter, confirmed working
    "gemini-flash-lite-latest", # Fallback 3 — alias to lightest available, confirmed working
]

class Finding(BaseModel):
    resource_id: str
    resource_type: str
    issue: str
    severity: str
    estimated_monthly_savings_usd: float
    fix_recommendation: str

class AnalysisSummary(BaseModel):
    total_resources_scanned: int
    total_issues_found: int
    total_estimated_monthly_savings_usd: float

class AnalysisResponse(BaseModel):
    findings: List[Finding]
    summary: AnalysisSummary

class GeminiAnalysisError(Exception):
    pass

def call_gemini_analysis(prompt_text: str) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise GeminiAnalysisError("GEMINI_API_KEY environment variable is missing.")

    client = genai.Client(api_key=api_key)
    
    config = genai.types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=AnalysisResponse,
        temperature=0.2,
        max_output_tokens=2048,
    )
    
    retry_config = genai.types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=AnalysisResponse,
        temperature=0.1,
        max_output_tokens=2048,
    )
    
    for i, model_name in enumerate(MODEL_FALLBACK_CHAIN):
        try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt_text,
                    config=config
                )
                
                if i == 0:
                    logger.info(f"Analysis completed using {model_name}")
                else:
                    logger.info(f"Analysis completed using {model_name} (fallback from {MODEL_FALLBACK_CHAIN[0]})")
                    
                return json.loads(response.text)
            except json.JSONDecodeError:
                # One-shot correction: send only the bad output back, not the huge original prompt
                retry_prompt = f"Fix this invalid JSON and return only the corrected version. Do NOT include markdown code blocks, ONLY valid JSON:\n{response.text}"
                response = client.models.generate_content(
                    model=model_name,
                    contents=retry_prompt,
                    config=retry_config
                )
                
                logger.info(f"Analysis completed using {model_name} (after JSON fix)")
                    
                try:
                    return json.loads(response.text)
                except json.JSONDecodeError:
                    raise GeminiAnalysisError("Invalid JSON after correction attempt.")
                    
        except Exception as e:
            # SUPPORTNEST LOGIC: If rate limited, 503, 404, or ANY error -> Immediately try the next model!
            # No wasting time with time.sleep()
            error_str = str(e).replace('\n', ' ')[:100] # keep it short for logs
            logger.warning(f"⚠️ Model {model_name} failed ({error_str}...). Trying next...")
            continue
            
    # If we fall through the outer loop, all models failed
    logger.error("All Gemini models in the fallback chain failed.")
    raise GeminiAnalysisError("The AI analysis service is temporarily unavailable. Please try again in a moment.")
