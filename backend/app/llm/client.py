import json
import re
from functools import lru_cache
from typing import TypeVar

from ollama import Client
from pydantic import BaseModel, ValidationError

from app.config import get_settings

T = TypeVar("T", bound=BaseModel)

FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)

JSON_ONLY_INSTRUCTION = (
    "\n\nRespond with ONLY a single valid JSON object — no markdown code fences, no commentary before or "
    "after it, no extra keys. It must conform exactly to this JSON schema:\n{schema}"
)


@lru_cache
def get_chat_client() -> Client:
    settings = get_settings()
    headers = {}
    if settings.ollama_chat_api_key:
        headers["Authorization"] = f"Bearer {settings.ollama_chat_api_key}"
    return Client(host=settings.ollama_chat_host, headers=headers)


@lru_cache
def get_embed_client() -> Client:
    settings = get_settings()
    headers = {}
    if settings.ollama_embed_api_key:
        headers["Authorization"] = f"Bearer {settings.ollama_embed_api_key}"
    return Client(host=settings.ollama_embed_host, headers=headers)


def _extract_json_candidates(text: str) -> list[str]:
    """Ollama Cloud's hosted models don't honor the `format` grammar-constrained decoding
    that local Ollama models do (confirmed: identical requests against local models return
    clean schema JSON, cloud models return prose or JSON wrapped in commentary/fences even
    when explicitly instructed otherwise). So we ask nicely via the system prompt and then
    parse defensively instead of trusting the response is bare JSON."""
    candidates = [text.strip()]
    candidates.extend(m.strip() for m in FENCE_RE.findall(text))
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidates.append(text[start : end + 1])
    return candidates


def _parse_structured(text: str, schema: type[T]) -> T:
    last_error: Exception | None = None
    for candidate in _extract_json_candidates(text):
        try:
            return schema.model_validate(json.loads(candidate))
        except (json.JSONDecodeError, ValidationError) as exc:
            last_error = exc
    raise ValueError(f"Model did not return valid JSON for {schema.__name__}: {text!r}") from last_error


def _chat_structured_call(messages: list[dict], schema: type[T]) -> T:
    settings = get_settings()
    client = get_chat_client()
    response = client.chat(
        model=settings.ollama_chat_model,
        messages=messages,
        format=schema.model_json_schema(),  # honored by local models; harmlessly ignored by cloud ones
        options={"temperature": 0.1},
    )
    content = response.message.content
    try:
        return _parse_structured(content, schema)
    except ValueError:
        # One corrective retry: show the model its bad output and ask again.
        retry_messages = messages + [
            {"role": "assistant", "content": content},
            {
                "role": "user",
                "content": "That was not a single valid JSON object matching the schema. Respond again with "
                "ONLY the corrected JSON object, nothing else.",
            },
        ]
        response = client.chat(
            model=settings.ollama_chat_model,
            messages=retry_messages,
            format=schema.model_json_schema(),
            options={"temperature": 0.1},
        )
        return _parse_structured(response.message.content, schema)


def chat_structured(system_prompt: str, user_prompt: str, schema: type[T]) -> T:
    """Call the chat model and force its reply to conform to a pydantic schema."""
    system_prompt = system_prompt + JSON_ONLY_INSTRUCTION.format(schema=json.dumps(schema.model_json_schema()))
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    return _chat_structured_call(messages, schema)


def chat_structured_conversation(
    system_prompt: str, history: list[dict], user_message: str, schema: type[T]
) -> T:
    """Like chat_structured, but carries prior turns so the model can track a multi-turn
    conversation (e.g. slot-filling a leave request across several messages)."""
    system_prompt = system_prompt + JSON_ONLY_INSTRUCTION.format(schema=json.dumps(schema.model_json_schema()))
    messages = [{"role": "system", "content": system_prompt}, *history, {"role": "user", "content": user_message}]
    return _chat_structured_call(messages, schema)


def chat_text(system_prompt: str, user_prompt: str) -> str:
    settings = get_settings()
    client = get_chat_client()
    response = client.chat(
        model=settings.ollama_chat_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        options={"temperature": 0.3},
    )
    return response.message.content


def embed_texts(texts: list[str]) -> list[list[float]]:
    settings = get_settings()
    client = get_embed_client()
    response = client.embed(model=settings.hf_embed_model, input=texts)
    return response.embeddings
