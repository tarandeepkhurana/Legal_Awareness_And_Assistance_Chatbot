from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()

azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION") 
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") 
azure_openai_model = os.getenv("AZURE_OPENAI_MODEL")      
azure_openai_embedding = os.getenv("AZURE_OPENAI_EMBEDDING")    
hugging_face_api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")    
pinecone_api_key = os.getenv("PINECONE_API_KEY")

def upload_docs(file_path: str) -> int:
    """
    Step 1: Load PDF using PyPDFLoader
    Step 2: Chunk text using RecursiveCharacterTextSplitter
    Step 3: Load embedding model
    Step 4: Generate embeddings using text-embedding-ada-002
    Step 5: Connect to Pinecone Vector Store
    Step 6: Prepare data for upsert
    Step 7: Upsert to Pinecone
    """
    # Step 1: Load PDF
    # loader = DirectoryLoader(
    #     parent_folder_path,
    #     glob="**/*.pdf",           
    #     loader_cls=PyPDFLoader,    
    #     show_progress=True         
    # )
    loader = PyPDFLoader("extracted_21_50.pdf")
    pages = loader.load()

    # Step 2: Chunk text
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = splitter.split_documents(pages)

    # Step 3: Load embedding model
    embed_model = HuggingFaceEndpointEmbeddings(
        repo_id="BAAI/bge-large-en-v1.5",
        huggingfacehub_api_token=hugging_face_api_key
    )

    # Step 4: Generate embeddings
    text = [doc.page_content for doc in docs]
    all_embeddings = embed_model.embed_documents(text)

    # Step 5: Connect to Pinecone
    pc = Pinecone(api_key=pinecone_api_key)
    index_name = "ml-project-index"
    namespace_name = "ml-project-space"
    index = pc.Index(index_name)

    # Step 6: Prepare data for upsert
    # Each vector: (id, embedding, metadata)
    vectors = []
    for i, vector in enumerate(all_embeddings):
        vectors.append((
            f"vec-{i}",
            vector,
            {"text": docs[i].page_content}
        ))

    # Step 7: Upsert to Pinecone 
    index.upsert(vectors=vectors, namespace=namespace_name)

    return len(vectors)

if __name__ == "__main__":
    parent_folder_path = "src\docs"
    num_of_vectors = upload_docs(parent_folder_path)
    print(f"Inserted {num_of_vectors} vectors successfully.")

