import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv()

from analysis.gemini_client import call_gemini_analysis

prompt = """
Analyze the following AWS resources for cost savings. Return a valid JSON.
[{"id": "i-12345", "type": "EC2", "status": "stopped"}]
"""

try:
    result = call_gemini_analysis(prompt)
    print("Success:", result)
except Exception as e:
    print("Failed:", e)
