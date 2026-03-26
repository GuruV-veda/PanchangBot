import os
from dotenv import load_dotenv
from openai import OpenAI

# -----------------------------
# Setup
# -----------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
VECTOR_STORE_ID = "vs_69c4481dc2b48191aff0b997e515845b"
# question = "What is the Nakshatra and Rahukala on August 15 2026 in Seattle?"
question = "how many occurances of Trayodashi during the evening hours in 2026"

print("Querying vector store...")
print("Question:", question)

response = client.responses.create(
    model="gpt-4.1",
    input=question,
    tools=[
        {
            "type": "file_search",
            "vector_store_ids": [VECTOR_STORE_ID],
        }
    ],
)
print("\n--- Model Answer ---\n")
print(response.output_text)
