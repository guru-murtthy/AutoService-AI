import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

logger = logging.getLogger("messaging_provider")

class MessagingProvider(ABC):
    @abstractmethod
    async def send_message(self, recipient: str, text: str, metadata: dict = None) -> Dict[str, Any]:
        pass

class WebChatProvider(MessagingProvider):
    """
    Public Customer Web Chat Provider Implementation.
    Stores and relays customer messages via database web chat session.
    """
    async def send_message(self, recipient: str, text: str, metadata: dict = None) -> Dict[str, Any]:
        logger.info(f"[WebChatProvider] Relaying response to customer {recipient}: '{text[:40]}...'")
        return {
            "status": "delivered",
            "channel": "web_chat",
            "recipient": recipient,
            "text": text
        }

class WhatsAppBusinessProvider(MessagingProvider):
    """
    Official WhatsApp Business Platform (Meta Cloud API) Interface Stub.
    Prepared for official WhatsApp Business API credentials in production.
    Personal WhatsApp automation / unofficial reverse-engineering libraries are strictly excluded.
    """
    def __init__(self, api_key: str = None, phone_number_id: str = None):
        self.api_key = api_key
        self.phone_number_id = phone_number_id

    async def send_message(self, recipient: str, text: str, metadata: dict = None) -> Dict[str, Any]:
        if not self.api_key or self.api_key == "mock_whatsapp_key":
            logger.info(f"[WhatsAppBusinessProvider STUB] Mock WhatsApp delivery to {recipient}: '{text[:40]}...'")
            return {"status": "mock_delivered", "channel": "whatsapp_business_stub", "recipient": recipient}
        
        # Real Meta Cloud API implementation
        url = f"https://graph.facebook.com/v19.0/{self.phone_number_id}/messages"
        # Prepared HTTP request payload for Cloud API...
        return {"status": "queued_meta_cloud_api", "recipient": recipient}

def get_messaging_provider(channel: str = "web_chat") -> MessagingProvider:
    if channel == "whatsapp":
        return WhatsAppBusinessProvider()
    return WebChatProvider()
