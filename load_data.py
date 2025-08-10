import json
import redis
import time
from redisvl.redis.utils import array_to_buffer
from redisvl.utils.vectorize import HFTextVectorizer
from redisvl.extensions.cache.embeddings import EmbeddingsCache
from redis_config import get_redis_client, get_redis_url

# Initialize Hugging Face text vectorizer
hf = HFTextVectorizer(
    model="sentence-transformers/all-MiniLM-L6-v2",
    cache=EmbeddingsCache(
        name="embedcache",
        ttl=None,
        redis_url=get_redis_url(),  # Use shared Redis URL
    )
)

# Generate a unique key for each review
def generate_key(review_data):
    # Generate a timestamp
    timestamp = int(time.time())
    # Use a short product identifier (could be from your product database)
    product_id = hash(review_data['product_name']) % 10000  # or actual product ID
    return f"review:{product_id}:{timestamp}"

def load_data_to_redis(review_data):
    try:
        redis_client = get_redis_client()
        product_key = generate_key(review_data)
        
        # Generate embeddings for the review
        print("Generating embeddings for the review...")
        embeddings = hf.embed(review_data['product_review'])        
        
        # For HASH -- must convert embeddings to bytes
        embeddings_bytes = array_to_buffer(embeddings, dtype='float32')

        # Normalize product name
        normalized_product_name = str(review_data['product_name']).lower().replace(" ", "_")

        redis_client.hset(product_key, mapping={
            'product_name': normalized_product_name,
            'product_url': str(review_data['product_url']),
            'product_image': str(review_data['product_image']),
            'product_review': str(review_data['product_review']),
            'product_recommend': str(review_data['product_recommend']),
            'embeddings': embeddings_bytes
        })
        
        return True, "Review stored successfully"
        
    except Exception as e:
        print(f"Error storing data: {str(e)}")
        return False, f"Error storing review: {str(e)}"