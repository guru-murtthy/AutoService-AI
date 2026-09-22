import logging
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger("automaton_adapter")

class AutomatonAdapter:
    """
    Bridge adapter connecting AutoService AI to Conway Automaton external runtime.
    Features graceful fallback to internal agent loop if Automaton is offline.
    """
    def __init__(self):
        self.url = settings.AUTOMATON_URL.rstrip('/')
        self.api_key = settings.AUTOMATON_API_KEY

    async def check_health(self) -> Dict[str, Any]:
        """
        Check if Conway Automaton external runtime is online.
        """
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{self.url}/health", headers=self._headers())
                if resp.status_code == 200:
                    return {"status": "online", "automaton_url": self.url, "data": resp.json()}
        except Exception as e:
            logger.info(f"Automaton offline ({e}). Using internal fallback worker.")
        
        return {"status": "offline", "fallback_active": True}

    async def dispatch_task(self, task_type: str, payload: dict) -> Dict[str, Any]:
        health = await self.check_health()
        if health["status"] == "online":
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.post(
                        f"{self.url}/api/v1/agent/tasks",
                        json={"task_type": task_type, "payload": payload},
                        headers=self._headers()
                    )
                    resp.raise_for_status()
                    return {"dispatched_to": "automaton", "response": resp.json()}
            except Exception as e:
                logger.warning(f"Failed to dispatch to Automaton: {e}. Executing fallback.")

        # Fallback: Handled locally by internal agent framework
        return {"dispatched_to": "local_fallback_worker", "status": "QUEUED_LOCAL"}

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

automaton_adapter = AutomatonAdapter()
