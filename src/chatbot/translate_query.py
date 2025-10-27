from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION") 
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") 
azure_openai_model = os.getenv("AZURE_OPENAI_MODEL")

llm = AzureChatOpenAI(
    deployment_name=azure_openai_model,
    openai_api_version=azure_openai_api_version,
    azure_endpoint=azure_openai_endpoint,
    openai_api_key=azure_openai_api_key,
    temperature=0.0,
)

def translate_user_query_to_english(user_query: str):
    template = f"""
    You are a translation assistant.  
    Translate the following user query into **clear and proper English**, keeping the meaning exactly the same. 
    Return ONLY the translated English text. No explanation, no formatting, no quotes.\n\n
    User query: {user_query}"""

    result = llm.invoke(template)

    return result.content

if __name__ == "__main__":
    print(translate_user_query_to_english("mere husband mujhe torture karte hain, mai kya karu?"))


