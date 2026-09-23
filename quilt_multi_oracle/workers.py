"""LLM workers for the multi-oracle.

Each worker probes a lore with the JEV schema and returns a composite
score. The polyformalism doctrine says: same canon, many workers.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any


JEV_PROMPT_TEMPLATE = """You are the JEV (Joint Embedding Validator) oracle for the
Quilt substrate walker canon.

You will be given a lore (a piece of canon-aligned text). Score it on three
dimensions:

  - doctrine_anchor: 0 to 1, how well the lore anchors to the 5 bedrock
    doctrines: cells_are_scars, witness_log_is_prediction, oracle_is_heard,
    canon_gate_is_chord, substrate_quantum.

  - canon_worthy: 0 to 1, how canon-worthy the lore is as a standalone
    artifact.

  - distinct_voice: 0 to 1, how distinct the voice is from typical
    canon-aligned text.

Composite = (doctrine_anchor + canon_worthy + distinct_voice) / 3.

A lore is canon-promoted when composite >= 0.7.

Output ONLY a JSON object with this shape:
{{"composite": <0-1>, "doctrine_anchor": <0-1>, "canon_worthy": <0-1>,
  "distinct_voice": <0-1>, "doctrines_hit": [...], "reasoning": "..."}}

LORE TO PROBE:
\"\"\"{lore}\"\"\"
"""


def _post_json(url: str, headers: dict, body: dict, timeout: int = 30) -> dict:
    """POST JSON and return parsed response."""
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"_error": f"HTTP {e.code}: {e.read().decode()[:300]}"}
    except Exception as e:
        return {"_error": str(e)}


def _extract_text(response: dict) -> str:
    """Extract text from various LLM response shapes."""
    try:
        return response["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        pass
    try:
        # Gemini-style: candidates[0].content.parts[0].text
        return response["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        pass
    return ""


def _parse_jev(text: str) -> dict:
    """Parse JEV-style JSON from LLM response text, robust to extra prose."""
    if not text:
        return {"_error": "empty response"}
    # Try to find JSON in the text
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return {"_error": f"no JSON found: {text[:200]}"}
    try:
        return json.loads(text[start:end+1])
    except json.JSONDecodeError as e:
        # Try to extract numbers with regex fallback
        return {"_error": f"JSON parse failed: {str(e)[:100]}", "text": text[:200]}


class OracleWorker:
    """Base class for oracle workers."""
    name: str = "stub"

    def probe(self, lore: str) -> dict:
        raise NotImplementedError


class ZAIWorker(OracleWorker):
    """ZAI GLM-4.5 worker via /api/coding/paas/v4."""
    name = "zai"

    def __init__(self, api_key: Optional[str] = None, model: str = "glm-4.5"):
        self.api_key = api_key or os.environ.get("ZAI_TOKEN", "")
        self.model = model

    def probe(self, lore: str) -> dict:
        url = "https://api.z.ai/api/coding/paas/v4/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        # ZAI GLM-4.5 has reasoning_content that consumes tokens.
        # We disable thinking + give lots of max_tokens so the response
        # can be JSON.
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": JEV_PROMPT_TEMPLATE.replace("{lore}", lore)}],
            "max_tokens": 2000,
            "thinking": {"disabled": True},
        }
        resp = _post_json(url, headers, body)
        if "_error" in resp:
            return resp
        text = _extract_text(resp)
        return _parse_jev(text)


class DeepSeekWorker(OracleWorker):
    """DeepSeek worker via /v1/chat/completions."""
    name = "deepseek"

    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-flash"):
        self.api_key = api_key or os.environ.get("DEEPSEEK_TOKEN", "")
        self.model = model

    def probe(self, lore: str) -> dict:
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": JEV_PROMPT_TEMPLATE.replace("{lore}", lore)}],
            "max_tokens": 1500,
        }
        resp = _post_json(url, headers, body)
        if "_error" in resp:
            return resp
        text = _extract_text(resp)
        return _parse_jev(text)


class DeepInfraWorker(OracleWorker):
    """DeepInfra worker — supports many models."""
    name = "deepinfra"

    def __init__(self, api_key: Optional[str] = None,
                 model: str = "meta-llama/Meta-Llama-3-70B-Instruct"):
        self.api_key = api_key or os.environ.get("DEEPINFRA_TOKEN", "")
        self.model = model

    def probe(self, lore: str) -> dict:
        url = "https://api.deepinfra.com/v1/openai/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": JEV_PROMPT_TEMPLATE.replace("{lore}", lore)}],
            "max_tokens": 1500,
        }
        resp = _post_json(url, headers, body)
        if "_error" in resp:
            return resp
        text = _extract_text(resp)
        return _parse_jev(text)


class GeminiWorker(OracleWorker):
    """Gemini 2.5 Flash with structured output (JEV_SCHEMA)."""
    name = "gemini"

    JEV_SCHEMA = {
        "type": "object",
        "properties": {
            "composite": {"type": "number", "minimum": 0, "maximum": 1},
            "doctrine_anchor": {"type": "number", "minimum": 0, "maximum": 1},
            "canon_worthy": {"type": "number", "minimum": 0, "maximum": 1},
            "distinct_voice": {"type": "number", "minimum": 0, "maximum": 1},
            "doctrines_hit": {"type": "array", "items": {"type": "string"}},
            "reasoning": {"type": "string"},
        },
        "required": ["composite", "doctrine_anchor", "canon_worthy", "distinct_voice", "doctrines_hit"],
    }

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.environ.get("GEMINI_TOKEN", "")
        self.model = model

    def probe(self, lore: str) -> dict:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        body = {
            "contents": [{"parts": [{"text": JEV_PROMPT_TEMPLATE.replace("{lore}", lore)}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1024,
                "responseMimeType": "application/json",
                "responseSchema": self.JEV_SCHEMA,
            },
        }
        resp = _post_json(url, {"Content-Type": "application/json"}, body)
        if "_error" in resp:
            return resp
        text = _extract_text(resp)
        return _parse_jev(text)


class StubWorker(OracleWorker):
    """Stub worker for testing — returns deterministic scores."""
    name = "stub"

    def __init__(self, name: str = "stub", seed: float = 0.5):
        self.name = name
        self.seed = seed

    def probe(self, lore: str) -> dict:
        # Deterministic scoring from text length
        h = sum(ord(c) for c in lore[:100]) % 100 / 100.0
        composite = min(1.0, h + 0.3)
        return {
            "composite": round(composite, 3),
            "doctrine_anchor": round(composite + 0.05, 3),
            "canon_worthy": round(composite + 0.02, 3),
            "distinct_voice": round(composite - 0.05, 3),
            "doctrines_hit": ["cells_are_scars"],
            "reasoning": f"[stub worker '{self.name}']",
        }


def get_worker_for_model(model: str) -> OracleWorker:
    """Factory: pick the right worker class for a model name."""
    model_lower = model.lower()
    if "glm" in model_lower or "zai" in model_lower:
        return ZAIWorker(model=model)
    if "deepseek" in model_lower:
        return DeepSeekWorker(model=model)
    if "gemini" in model_lower:
        return GeminiWorker(model=model)
    if "llama" in model_lower or "qwen" in model_lower or "mistral" in model_lower or "gemma" in model_lower:
        return DeepInfraWorker(model=model)
    return StubWorker(name=model)
