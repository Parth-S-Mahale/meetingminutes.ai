import json
import re
from functools import lru_cache
from typing import Any, Dict

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from app.config import get_settings
from app.prompts.meeting_summary_prompt import SYSTEM_MESSAGE, build_user_prompt

settings = get_settings()


def _str_to_bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _build_quantization_config():
    if not _str_to_bool(settings.SUMMARIZER_LOAD_IN_4BIT):
        return None

    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_quant_type="nf4",
    )


def _hf_auth_kwargs() -> dict:
    """
    Return auth kwargs for gated/private Hugging Face repos.
    """
    if settings.HF_TOKEN:
        # Newer transformers/huggingface_hub use `token=...`
        return {"token": settings.HF_TOKEN}
    return {}


@lru_cache(maxsize=1)
def get_tokenizer():
    tokenizer = AutoTokenizer.from_pretrained(
        settings.SUMMARIZER_MODEL_ID,
        **_hf_auth_kwargs()
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


@lru_cache(maxsize=1)
def get_summarizer_model():
    quant_config = _build_quantization_config()

    common_kwargs = {
        "device_map": settings.SUMMARIZER_DEVICE_MAP,
        **_hf_auth_kwargs(),
    }

    if quant_config is not None:
        common_kwargs["quantization_config"] = quant_config

    model = AutoModelForCausalLM.from_pretrained(
        settings.SUMMARIZER_MODEL_ID,
        **common_kwargs
    )
    return model


def _extract_json_block(text: str) -> Dict[str, Any]:
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"Could not find JSON object in model output: {text[:500]}")

    json_text = match.group(0)
    return json.loads(json_text)


def summarize_meeting(transcript: str, title: str | None = None) -> Dict[str, Any]:
    tokenizer = get_tokenizer()
    model = get_summarizer_model()

    user_prompt = build_user_prompt(transcript=transcript, title=title)

    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": user_prompt},
    ]

    inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt",
    )

    inputs = inputs.to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_new_tokens=settings.MAX_NEW_TOKENS,
            temperature=settings.TEMPERATURE,
            top_p=settings.TOP_P,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )

    generated_tokens = outputs[0][inputs.shape[-1]:]
    generated_text = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

    parsed = _extract_json_block(generated_text)

    summary = parsed.get("summary", "")
    key_decisions = parsed.get("key_decisions", [])
    action_items = parsed.get("action_items", [])

    if not isinstance(key_decisions, list):
        key_decisions = []

    if not isinstance(action_items, list):
        action_items = []

    normalized_action_items = []
    for item in action_items:
        if isinstance(item, dict):
            normalized_action_items.append({
                "task": item.get("task", "").strip() or "Unspecified task",
                "owner": item.get("owner", "Unassigned"),
                "deadline": item.get("deadline", "Not specified"),
            })

    return {
        "summary": summary,
        "key_decisions": key_decisions,
        "action_items": normalized_action_items,
    }