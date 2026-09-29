import asyncio
import json
import re
from typing import TypeVar, Type, Any
from pydantic import BaseModel, ValidationError
from openai import AsyncOpenAI, APIError, RateLimitError
from core.app.ports import LLMPort

T = TypeVar("T", bound=BaseModel)

class LLMFailure(Exception):
    pass

def _strip_fences(s: str) -> str:
    return re.sub(r"^```(?:json)?|```$", "", s.strip(), flags=re.M).strip()

class GroqLLM(LLMPort):
    def __init__(self, api_key: str, primary: str, fallback: str):
        self._c = AsyncOpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
        self._models = [primary, fallback]

    async def complete_json(self, *, system: str, user: str, schema: Type[T], temperature: float = 0.2, max_attempts: int = 3) -> T:
        sys_msg = system + "\nReturn ONLY valid JSON matching this schema:\n" + json.dumps(schema.model_json_schema())
        last: Exception | None = None
        for model in self._models:
            messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": user}]
            for attempt in range(max_attempts):
                try:
                    r = await self._c.chat.completions.create(
                        model=model, messages=messages, temperature=temperature,
                        response_format={"type": "json_object"}
                    )
                    content = r.choices[0].message.content or ""
                    return schema.model_validate_json(_strip_fences(content))
                except (ValidationError, json.JSONDecodeError) as e:
                    last = e
                    messages.append({"role": "user", "content": f"Invalid output: {e}. Return corrected JSON only."})
                except (RateLimitError, APIError) as e:
                    last = e
                    await asyncio.sleep(2 ** attempt)
        raise LLMFailure("all models failed") from last

    async def complete_text(self, *, system: str, user: str, temperature: float = 0.4) -> str:
        last: Exception | None = None
        for model in self._models:
            messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
            try:
                r = await self._c.chat.completions.create(
                    model=model, messages=messages, temperature=temperature
                )
                return r.choices[0].message.content or ""
            except (RateLimitError, APIError) as e:
                last = e
                await asyncio.sleep(1)
        raise LLMFailure("all models failed") from last
