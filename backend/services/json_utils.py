import json

def clean_json(raw: str):
    if not raw:
        return ""

    raw = raw.strip()

    if raw.startswith("```json"):
        raw = raw[len("```json"):]

    elif raw.startswith("```"):
        raw = raw[len("```"):]

    if raw.endswith("```"):
        raw = raw[:-3]

    return raw.strip()


def parse_ai_json(raw: str):
    cleaned = clean_json(raw)

    if not cleaned:
        raise ValueError(
            "AI returned an empty response."
        )

    try:
        return json.loads(cleaned)

    except json.JSONDecodeError as e:
        print(
            "JSON PARSE ERROR:",
            repr(e),
        )

        print(
            "RAW AI RESPONSE:",
            cleaned[:5000],
        )

        raise ValueError(
            "AI returned invalid JSON."
        )
