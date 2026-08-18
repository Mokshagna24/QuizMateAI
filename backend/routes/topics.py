from ..core.app import app
from ..services.topics import load_topics


@app.get("/api/topics")
def topics():

    return [
        {
            "name": name,
            "description": (
                "Practice important concepts with AI."
            ),
        }
        for name in load_topics()
    ]


@app.get("/api/topics/{topic_name}")
def topic_content(
    topic_name: str,
):

    data = load_topics()

    if topic_name not in data:

        raise HTTPException(
            status_code=404,
            detail="Topic not found",
        )

    return {
        "name": topic_name,
        "text": data[topic_name],
    }
