"""DeepSeek 客户端：通过 OpenAI 兼容 SDK 调用模型并请求 JSON 输出。"""
from openai import OpenAI

from backend.app.core.config import get_settings


class DeepSeekClient:
    def __init__(self, config: dict | None = None, openai_client=None):
        settings = get_settings()
        resolved = {
            "api_key": settings.DEEPSEEK_API_KEY,
            "base_url": settings.DEEPSEEK_BASE_URL,
            "model": settings.DEEPSEEK_MODEL,
            "timeout": settings.DEEPSEEK_TIMEOUT_SECONDS,
        }
        if config:
            resolved.update(config)
        self.api_key = resolved["api_key"]
        self.model = resolved["model"]
        self.client = openai_client
        if self.client is None and self.api_key:
            self.client = OpenAI(
                api_key=resolved["api_key"],
                base_url=resolved["base_url"],
                timeout=resolved["timeout"],
            )

    def is_configured(self) -> bool:
        return bool(self.api_key and self.model)

    def generate_json(self, messages: list[dict]) -> str:
        if not self.client:
            raise RuntimeError("DeepSeek API key is not configured")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=1400,
            stream=False,
        )
        return response.choices[0].message.content or ""
