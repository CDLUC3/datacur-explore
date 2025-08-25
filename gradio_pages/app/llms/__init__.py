# llms/__init__.py

from . import open_api_code, google_api_code, bedrock_llama

UI_OPTIONS = ["GPT-4o", "GPT-4.1", "gemini-2.0-flash", "gemini-2.5-flash", "llama3.1-70b"]

MODEL_NAMES_TO_GEN_FUNC = {
        "GPT-4o": open_api_code.generate,
        "GPT-4.1": open_api_code.generate,
        "gemini-2.0-flash": google_api_code.generate,
        "gemini-2.5-flash": google_api_code.generate,
        "llama3.1-70b": bedrock_llama.generate,
    }

MODEL_NAMES_TO_IDS = {
        "GPT-4o": "gpt-4o",
        "GPT-4.1": "gpt-4.1-2025-04-14",
        "gemini-2.0-flash": "gemini-2.0-flash",
        "gemini-2.5-flash": "gemini-2.5-flash",
        "llama3.1-70b": "meta.llama3-1-70b-instruct-v1:0",
    }