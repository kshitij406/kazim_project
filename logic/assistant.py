import requests
from config import CFG


class AssistantError(RuntimeError):
    pass


def explain_queue(question: str, context_block: str) -> str:
    if not CFG.openrouter_key:
        raise AssistantError(
            "OPENROUTER_API_KEY is not set. Add it to .env and restart Streamlit."
        )

    url = f"{CFG.openrouter_base_url}/chat/completions"

    headers = {
        "Authorization": f"Bearer {CFG.openrouter_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",  # OpenRouter requirement
        "X-Title": "Ops Command Center",      # App name
    }

    payload = {
        "model": CFG.openrouter_model,  # deepseek/deepseek-chat
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an operations analyst. "
                    "Give concise, actionable guidance in bullet points."
                ),
            },
            {
                "role": "user",
                "content": f"Question:\n{question}\n\nContext:\n{context_block}",
            },
        ],
        "temperature": 0.4,
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)

        if r.status_code == 402:
            raise AssistantError(
                "OpenRouter returned HTTP 402 (Payment Required). "
                "Add credits to your OpenRouter account."
            )

        r.raise_for_status()
        data = r.json()

        msg = data["choices"][0]["message"]["content"]
        if not msg or not msg.strip():
            raise AssistantError("AI returned an empty response.")
        return msg

    except requests.exceptions.Timeout as e:
        raise AssistantError("AI request timed out.") from e
    except requests.exceptions.HTTPError as e:
        raise AssistantError(
            f"OpenRouter error HTTP {r.status_code}: {r.text}"
        ) from e
    except Exception as e:
        raise AssistantError(f"AI request failed: {e}") from e
