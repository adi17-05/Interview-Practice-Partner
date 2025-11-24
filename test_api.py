#!/usr/bin/env python
"""Test script to verify Gemini API integration"""

import sys
sys.path.insert(0, '.')

from interview_partner.core import llm

print("Testing LLM call...")
try:
    result = llm.chat_completion(
        user_prompt="Say hello in one sentence",
        temperature=0.5,
        max_output_tokens=50
    )
    print(f"✓ Success: {result}")
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
