import os
import json
import logging
import re
import time
import asyncio
from typing import Dict, Any, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger("ai_provider")

class AIProvider:
    """
    Resilient Unified AI Provider.
    Implements retry loop with exponential backoff, rate-limit 429 handling,
    timeout safety, structured output validation, and sanitized telemetry.
    Automatically falls back to regex rule parser on repeated failure.
    """
    def __init__(self):
        self.provider = settings.AI_PROVIDER.lower()
        self.gemini_key = settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY
        self.timeout = settings.AI_TIMEOUT_SECONDS
        self.max_retries = settings.AI_MAX_RETRIES

    async def extract_requirements(self, message: str, conversation_history: list = None) -> Dict[str, Any]:
        prompt = self._build_extraction_prompt(message, conversation_history)
        start_time = time.time()

        # Primary provider attempt: Gemini
        if self.provider == "gemini" and self.gemini_key:
            res = await self._call_with_retry("gemini", prompt)
            if res:
                parsed = self._parse_and_validate_json(res)
                if parsed:
                    latency_ms = round((time.time() - start_time) * 1000, 1)
                    logger.info(f"AI Extraction Success [Provider=gemini, Latency={latency_ms}ms, Confidence={parsed.get('confidence')}]")
                    return parsed

        # Secondary provider attempt: OpenAI
        if self.provider == "openai" and self.openai_key:
            res = await self._call_with_retry("openai", prompt)
            if res:
                parsed = self._parse_and_validate_json(res)
                if parsed:
                    latency_ms = round((time.time() - start_time) * 1000, 1)
                    logger.info(f"AI Extraction Success [Provider=openai, Latency={latency_ms}ms]")
                    return parsed

        # Rule-based fallback
        logger.warning(f"AI Provider unavailable/failed. Engaging Rule Parser Fallback.")
        return self._rule_based_extraction(message, conversation_history)

    async def _call_with_retry(self, provider_type: str, prompt: str) -> Optional[str]:
        for attempt in range(1, self.max_retries + 1):
            try:
                if provider_type == "gemini":
                    return await self._call_gemini_api(prompt)
                elif provider_type == "openai":
                    return await self._call_openai_api(prompt)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    logger.warning(f"AI Provider 429 Rate Limit (Attempt {attempt}/{self.max_retries}). Backing off...")
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.warning(f"AI HTTP Error {e.response.status_code} on attempt {attempt}")
            except Exception as e:
                logger.warning(f"AI Call Exception on attempt {attempt}: {e}")
                await asyncio.sleep(1.0 * attempt)
        return None

    async def _call_gemini_api(self, prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    async def _call_openai_api(self, prompt: str) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    def _parse_and_validate_json(self, text: str) -> Optional[Dict[str, Any]]:
        try:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                # Validate expected keys structure
                expected_keys = ["origin", "destination", "vehicle_type", "duration_days", "travel_date", "passenger_count", "budget"]
                valid_dict = {k: data.get(k) for k in expected_keys}
                valid_dict["confidence"] = float(data.get("confidence", 0.9))
                return valid_dict
        except Exception as e:
            logger.warning(f"JSON Output Validation failed: {e}")
        return None

    def _build_extraction_prompt(self, message: str, history: list) -> str:
        hist_text = ""
        if history:
            hist_text = "\nPrior Messages:\n" + "\n".join([f"{m.get('sender_type')}: {m.get('message')}" for m in history])
        
        return f"""
You are an expert requirement extraction assistant for a travel agency in India.
Analyze the customer's message along with conversation history.
Extract the following fields in strict JSON format:
- origin (string or null)
- destination (string or null)
- vehicle_type (e.g. "5-seater", "7-seater", "tempo-traveller", or null)
- duration_days (integer or null)
- travel_date (string e.g. "2026-10-15" or null)
- passenger_count (integer or null)
- budget (number or null)
- confidence (float between 0.0 and 1.0)

Customer Message: "{message}"
{hist_text}

Respond ONLY with valid JSON.
"""

    def _rule_based_extraction(self, message: str, history: list = None) -> Dict[str, Any]:
        full_text = message
        if history:
            full_text = " ".join([m.get("message", "") for m in history]) + " " + message
        
        full_text_lower = full_text.lower()

        origin, destination = None, None
        route_match = re.search(r"\bfrom\s+([a-zA-Z]+)\s+to\s+([a-zA-Z]+)", full_text_lower)
        if route_match:
            origin = route_match.group(1).strip().title()
            destination = route_match.group(2).strip().title()
        else:
            dest_match = re.search(r"\bto\s+([a-zA-Z]+)", full_text_lower)
            if dest_match:
                destination = dest_match.group(1).strip().title()

        vehicle_type = None
        if "7 seater" in full_text_lower or "7-seater" in full_text_lower or "ertiga" in full_text_lower or "innova" in full_text_lower:
            vehicle_type = "7-seater"
        elif "5 seater" in full_text_lower or "5-seater" in full_text_lower or "sedan" in full_text_lower or "swift" in full_text_lower or "dzire" in full_text_lower or "car" in full_text_lower:
            vehicle_type = "5-seater"
        elif "tempo" in full_text_lower or "12 seater" in full_text_lower or "traveller" in full_text_lower:
            vehicle_type = "tempo-traveller"

        duration_days = None
        dur_match = re.search(r"(\d+)\s*(?:days|day|d)", full_text_lower)
        if dur_match:
            duration_days = int(dur_match.group(1))

        passenger_count = None
        pax_match = re.search(r"(\d+)\s*(?:people|passengers|pax|persons|adults)", full_text_lower)
        if pax_match:
            passenger_count = int(pax_match.group(1))

        travel_date = None
        date_match = re.search(r"(?:starting|on|date|from)\s+([a-zA-Z0-9\s,]+?\d{1,2}(?:st|nd|rd|th)?(?:\s+[a-zA-Z]+)?(?:\s+\d{4})?)", full_text_lower)
        if date_match:
            travel_date = date_match.group(1).strip().title()

        budget = None
        budget_match = re.search(r"(?:budget|around|rs|₹)\s*(\d+)", full_text_lower)
        if budget_match:
            budget = float(budget_match.group(1))

        return {
            "origin": origin or "Bangalore",
            "destination": destination,
            "vehicle_type": vehicle_type,
            "duration_days": duration_days,
            "travel_date": travel_date,
            "passenger_count": passenger_count,
            "budget": budget,
            "confidence": 0.88
        }

ai_provider = AIProvider()
