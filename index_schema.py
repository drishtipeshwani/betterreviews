"""
Shared index schema definition for RedisVL
This ensures consistency between index creation and usage
"""

from redis_config import INDEX_NAME

# RedisVL index schema definition
INDEX_SCHEMA = {
    "index": {
        "name": INDEX_NAME,
        "prefix": "review:"
    },
    "fields": [
        {
            "name": "product_name",
            "type": "text",
            "attrs": {
                "weight": 1.0,
                "no_stem": False,
            }
        },
        {
            "name": "product_url",
            "type": "text",
            "attrs": {
                "weight": 0.5,
                "no_stem": True,
            }
        },
        {
            "name": "product_image",
            "type": "text",
            "attrs": {
                "weight": 0.5,
                "no_stem": True,
            }
        },
        {
            "name": "product_review",
            "type": "text",
            "attrs": {
                "weight": 2.0,
                "no_stem": False,
            }
        },
        {
            "name": "product_recommend",
            "type": "tag",
            "attrs": {
                "weight": 1.0,
                "no_stem": True,
            }
        },
        {
            "name": "embeddings",
            "type": "vector",
            "attrs": {
                "dims": 384,
                "distance_metric": "cosine",
                "algorithm": "hnsw",
                "datatype": "float32"
            }
        }
    ]
}

def get_index_schema():
    """Get the RedisVL index schema"""
    return INDEX_SCHEMA
