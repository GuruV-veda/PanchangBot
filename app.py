import os
from anyio import Path
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path,  override=True)

print("ENV path:", env_path)
print("Loaded API key:", os.getenv("OPENAI_API_KEY"))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VECTOR_STORE_ID = "vs_69c4481dc2b48191aff0b997e515845b"

st.title("📅 Seattle Panchang Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Ask about Panchang dates...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    response = client.responses.create(
        model="gpt-4.1",
        input=st.session_state.messages,
        tools=[
            {
                "type": "file_search",
                "vector_store_ids": [VECTOR_STORE_ID],
            }
        ],
    )

    reply = response.output_text

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)