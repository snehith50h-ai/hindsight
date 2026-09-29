import json
from typing import TypeVar, Type
from pydantic import BaseModel
from core.app.ports import LLMPort

T = TypeVar("T", bound=BaseModel)

class FakeLLM(LLMPort):
    def __init__(self, json_responses: dict[str, dict] = None, text_responses: dict[str, str] = None):
        self.json_responses = json_responses or {}
        self.text_responses = text_responses or {}
        self.json_calls = []
        self.text_calls = []

    async def complete_json(self, *, system: str, user: str, schema: Type[T], temperature: float = 0.2) -> T:
        self.json_calls.append({"system": system, "user": user, "schema": schema.__name__})
        # match substring in user prompt for rudimentary matching
        for k, v in self.json_responses.items():
            if k in user:
                return schema(**v)
        # return an empty object that satisfies schema if no match
        return schema.model_construct()

    async def complete_text(self, *, system: str, user: str, temperature: float = 0.4) -> str:
        self.text_calls.append({"system": system, "user": user})
        for k, v in self.text_responses.items():
            if k in user:
                return v
        return "fake text response"
