from fastapi import HTTPException

from ..core.config import TOPICS_DIR


def load_topics():
    TOPICS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    return {
        p.stem.replace("_", " ").title():
        p.read_text(encoding="utf-8")
        for p in TOPICS_DIR.glob("*.txt")
    }


def get_topic_source(topic: str):
    data = load_topics()

    if topic in data:
        return topic, data[topic]

    topic_lower = topic.strip().lower()

    for name, text in data.items():
        if name.lower() == topic_lower:
            return name, text

    raise HTTPException(
        status_code=404,
        detail=f"Topic '{topic}' was not found.",
    )
