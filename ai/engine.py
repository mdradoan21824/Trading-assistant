import google.generativeai as genai
from groq import Groq

from config.settings import GEMINI_API_KEY, GROQ_API_KEY
from ai.prompts import SYSTEM_PROMPT
from core.response import success, error
from utils.logger import logger

genai.configure(api_key=GEMINI_API_KEY)

_groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


def _ask_gemini(user_prompt):
    model = genai.GenerativeModel(
        model_name="gemini-flash-latest",
        system_instruction=SYSTEM_PROMPT,
    )

    response = model.generate_content(user_prompt)

    return response.text.strip()


def _ask_groq(user_prompt):
    completion = _groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    return completion.choices[0].message.content.strip()


def ask_ai(user_prompt):
    if not GEMINI_API_KEY and not GROQ_API_KEY:
        logger.error("No AI API key configured.")
        return error("AI analysis is not configured.")

    if GEMINI_API_KEY:
        try:
            text = _ask_gemini(user_prompt)
            return success("AI response", {"text": text})

        except Exception as e:
            logger.error(f"Gemini API error: {e}")

            if not GROQ_API_KEY:
                if "429" in str(e):
                    return error("AI analysis is temporarily rate-limited. Please try again shortly.")
                return error("AI analysis is temporarily unavailable. Please try again in a few minutes.")

            logger.error("Falling back to Groq.")

    if GROQ_API_KEY:
        try:
            text = _ask_groq(user_prompt)
            return success("AI response", {"text": text})

        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return error("AI analysis is temporarily unavailable. Please try again in a few minutes.")

    return error("AI analysis is temporarily unavailable. Please try again in a few minutes.")
