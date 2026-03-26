import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VECTOR_STORE_ID = "vs_69c4c313a79c8191b4d8619377036ed8"
# "vs_69c4481dc2b48191aff0b997e515845b"

conversation = []

print("Panchang Chatbot (type 'exit' to quit)\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    conversation.append({"role": "user", "content": user_input})

    response = client.responses.create(
        model="gpt-4.1",
        input=conversation,
        tools=[
            {
                "type": "file_search",
                "vector_store_ids": [VECTOR_STORE_ID],
            }
        ],
    )

    assistant_reply = response.output_text
    print("\nBot:", assistant_reply, "\n")

    conversation.append({"role": "assistant", "content": assistant_reply})
