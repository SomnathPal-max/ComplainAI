import httpx
import json
import logging
import socket
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
from backend.config import settings

logger = logging.getLogger("ComplainAI.Ollama")

def is_port_open(url: str, timeout: float = 0.05) -> bool:
    """Fast non-blocking IPv4 check before any network call."""
    import sys
    if "pytest" in sys.modules:
        return False
    try:
        parsed = urlparse(url)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 11434
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        err = s.connect_ex((host, port))
        s.close()
        return err == 0
    except Exception:
        return False

class OllamaClient:
    def __init__(self, base_url: str = settings.OLLAMA_BASE_URL, model: str = settings.OLLAMA_MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = settings.OLLAMA_TIMEOUT
        self.is_connected = False
        self.available_models: List[str] = []

    async def check_health(self) -> Dict[str, Any]:
        """Check if local Ollama daemon is reachable and list models."""
        if not is_port_open(self.base_url, timeout=0.05):
            self.is_connected = False
            return {
                "status": "offline_or_sandboxed",
                "base_url": self.base_url,
                "active_model": self.model,
                "available_models": [],
                "message": f"Ollama daemon not reachable at {self.base_url}. Using autonomous local AI engine."
            }

        try:
            async with httpx.AsyncClient(timeout=0.8) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    self.is_connected = True
                    self.available_models = models
                    return {
                        "status": "connected",
                        "base_url": self.base_url,
                        "active_model": self.model,
                        "available_models": models,
                        "message": f"Ollama is online with {len(models)} model(s) available."
                    }
        except Exception as e:
            self.is_connected = False
            return {
                "status": "offline_or_sandboxed",
                "base_url": self.base_url,
                "active_model": self.model,
                "available_models": [],
                "message": f"Ollama service at {self.base_url} is not responding ({type(e).__name__}). Using autonomous local AI engine."
            }
        return {
            "status": "offline",
            "base_url": self.base_url,
            "active_model": self.model,
            "message": "Ollama service unavailable"
        }

    async def generate(self, prompt: str, system: Optional[str] = None, images: Optional[List[str]] = None, format_json: bool = False) -> Dict[str, Any]:
        """Execute text or multimodal vision generation via Ollama."""
        if not self.is_connected and not is_port_open(self.base_url, timeout=0.05):
            return {
                "success": False,
                "source": "fallback_pipeline",
                "model": self.model
            }

        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        if system:
            payload["system"] = system
        if images and len(images) > 0:
            clean_images = []
            for img in images:
                if "," in img:
                    img = img.split(",", 1)[1]
                clean_images.append(img)
            payload["images"] = clean_images
        if format_json:
            payload["format"] = "json"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(f"{self.base_url}/api/generate", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    response_text = data.get("response", "")
                    return {
                        "success": True,
                        "response": response_text,
                        "source": "ollama",
                        "model": self.model
                    }
        except Exception as err:
            logger.info(f"Ollama call failed: {err}")
        
        return {
            "success": False,
            "source": "fallback_pipeline",
            "model": self.model
        }

    async def chat(self, messages: List[Dict[str, str]], format_json: bool = False) -> Dict[str, Any]:
        """Execute chat completion via Ollama."""
        if not self.is_connected and not is_port_open(self.base_url, timeout=0.05):
            return {
                "success": False,
                "source": "fallback_pipeline",
                "model": self.model
            }

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        if format_json:
            payload["format"] = "json"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(f"{self.base_url}/api/chat", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    content = data.get("message", {}).get("content", "")
                    return {
                        "success": True,
                        "content": content,
                        "source": "ollama",
                        "model": self.model
                    }
        except Exception as err:
            logger.info(f"Ollama chat call failed: {err}")

        return {
            "success": False,
            "source": "fallback_pipeline",
            "model": self.model
        }

ollama_client = OllamaClient()
