import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()
os.environ["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY")


model = init_chat_model(
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    model_provider="openrouter",
)

response = model.invoke("Hi how r u doing?")

print(response.content)