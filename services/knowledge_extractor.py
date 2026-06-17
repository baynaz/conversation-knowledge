import json
from ollama import chat


def extract_knowledge(thread_text: str):
    """
    Send a Teams thread to Mistral and extract a knowledge object.
    """

    prompt = f"""
        You are an expert technical knowledge extraction system.

        Analyze the following Teams conversation and extract:

        - problem
        - context
        - symptoms
        - solutions_tried
        - confirmed_solution
        - technology

        Return ONLY valid JSON.

        Conversation:

        {thread_text}
    """

    response = chat(
        model="mistral",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response["message"]["content"]

    try:
        return json.loads(content)

    except Exception:
        return {
            "error": "Invalid JSON returned by model",
            "raw_response": content
        }