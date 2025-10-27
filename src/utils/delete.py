from pinecone.grpc import PineconeGRPC as Pinecone
from dotenv import load_dotenv
import os

load_dotenv()
pinecone_api_key = os.getenv("PINECONE_API_KEY")

pc = Pinecone(api_key=pinecone_api_key)

# Get the index description (contains the host)
index_name = "ml-project-index"
namespace_name = "ml-project-space"

index_info = pc.describe_index(index_name)
print(index_info)

# Use the "host" field from index_info
index = pc.Index(host=index_info.host)

# Delete namespace
index.delete(delete_all=True, namespace=namespace_name)
print("Deleted.")