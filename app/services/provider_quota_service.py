import asyncio
import os
from typing import Any

import httpx


class ProviderQuotaService:
    """Best-effort provider status and quota discovery.

    Most public LLM providers do not expose a standard remaining-quota API.
    When a provider does not provide a stable endpoint, this service falls back
    to 'unknown' instead of guessing a misleading value.
    """

    @staticmethod
    def _provider_config() -> dict[str, dict[str, Any]]:
        return {
            "gemini": {
                "label": "Gemini",
                "status": "unknown",
                "quota": "unknown",
                "enabled": bool(os.getenv("GEMINI_API_KEY")),
            },
            "openai": {
                "label": "OpenAI",
                "status": "unknown",
                "quota": "unknown",
                "enabled": bool(os.getenv("OPENAI_API_KEY")),
            },
            "groq": {
                "label": "Groq",
                "status": "unknown",
                "quota": "unknown",
                "enabled": bool(os.getenv("GROQ_API_KEY")),
            },
            "meta": {
                "label": "Meta AI",
                "status": "unsupported",
                "quota": "unknown",
                "enabled": False,
            },
        }

    @staticmethod
    async def _safe_get(url: str, headers: dict[str, str] | None = None, timeout: float = 5.0) -> tuple[bool, Any]:
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, headers=headers or {})
                if response.status_code >= 400:
                    return False, {"status_code": response.status_code, "text": response.text[:300]}
                try:
                    return True, response.json()
                except Exception:
                    return True, {"text": response.text[:300]}
        except Exception as exc:
            return False, {"error": str(exc)}

    @staticmethod
    async def _get_openai_status() -> dict[str, Any]:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {"status": "not_configured", "quota": "unknown"}

        url = "https://api.openai.com/v1/dashboard/billing/usage"
        headers = {"Authorization": f"Bearer {api_key}"}
        ok, payload = await ProviderQuotaService._safe_get(url, headers=headers)
        if not ok:
            return {"status": "configured", "quota": "unknown"}

        try:
            total_usage = payload.get("total_usage")
            if total_usage is not None:
                return {"status": "configured", "quota": f"~{float(total_usage)/1000000:.2f}M tokens"}
        except Exception:
            pass

        return {"status": "configured", "quota": "unknown"}

    @staticmethod
    async def _get_groq_status() -> dict[str, Any]:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return {"status": "not_configured", "quota": "unknown"}

        url = "https://api.groq.com/openai/v1/models"
        headers = {"Authorization": f"Bearer {api_key}"}
        ok, payload = await ProviderQuotaService._safe_get(url, headers=headers)
        if ok:
            return {"status": "configured", "quota": "unknown"}
        return {"status": "configured", "quota": "unknown"}

    @staticmethod
    async def _get_gemini_status() -> dict[str, Any]:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {"status": "not_configured", "quota": "unknown"}

        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        ok, payload = await ProviderQuotaService._safe_get(url)
        if ok:
            return {"status": "configured", "quota": "unknown"}
        return {"status": "configured", "quota": "unknown"}

    @staticmethod
    async def get_status() -> list[dict[str, Any]]:
        cfg = ProviderQuotaService._provider_config()

        tasks = {
            "openai": ProviderQuotaService._get_openai_status,
            "groq": ProviderQuotaService._get_groq_status,
            "gemini": ProviderQuotaService._get_gemini_status,
        }

        results = await asyncio.gather(
            *(tasks[name]() for name in tasks.keys()),
            return_exceptions=True,
        )

        for index, name in enumerate(tasks.keys()):
            info = results[index]
            if isinstance(info, Exception):
                info = {"status": "configured", "quota": "unknown"}

            entry = cfg.get(name, {"label": name.title(), "enabled": False})
            entry["key"] = name
            entry["status"] = info.get("status", entry.get("status", "unknown"))
            entry["quota"] = info.get("quota", entry.get("quota", "unknown"))
            entry["enabled"] = bool(entry.get("enabled", False)) or entry["status"] != "not_configured"
            cfg[name] = entry

        cfg["meta"] = {
            "key": "meta",
            "label": "Meta AI",
            "status": "unsupported",
            "quota": "unknown",
            "enabled": False,
        }

        return [cfg[name] for name in ["gemini", "openai", "groq", "meta"]]
