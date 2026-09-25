from ollama import chat

response = chat(
    model="mistral",
    messages=[
        {
            "role": "user",
            "content": "Say hello"
        }
    ]
)

print(response["message"]["content"])