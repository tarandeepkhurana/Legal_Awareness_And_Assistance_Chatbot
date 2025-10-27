from langchain_huggingface import HuggingFaceEndpointEmbeddings
from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()

hugging_face_api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")    
pinecone_api_key = os.getenv("PINECONE_API_KEY")

# Load embedding model
embed_model = HuggingFaceEndpointEmbeddings(
    repo_id="BAAI/bge-large-en-v1.5",
    huggingfacehub_api_token=hugging_face_api_key
)

# Connect to Pinecone
pc = Pinecone(api_key=pinecone_api_key)
index_name = "ml-project-index"
namespace_name = "ml-project-space"
index = pc.Index(index_name)

def fetch_relevant_chunks(user_query: str, namespace=namespace_name) -> list:
    """
    Retrieves the relevant context from the document uploaded and the topic selected
    """
    query_vector = embed_model.embed_query(user_query)

    results = index.query(
        namespace=namespace,
        vector=query_vector,
        top_k=5,  
        include_metadata=True
    )

    chunks = [match["metadata"]["text"] for match in results["matches"]]
    
    cleaned_docs = [doc.strip() for doc in chunks if doc.strip()]
   
    context_text = "\n\n".join(cleaned_docs)
    
    return context_text


if __name__ == "__main__":
    result = fetch_relevant_chunks("I am a woman, I am being tortured by my husband what should i do?")
    print(result)
    