from redisvl.index import SearchIndex
from redis_config import get_redis_url, INDEX_NAME
from index_schema import get_index_schema

REDIS_URL = get_redis_url()
schema = get_index_schema()

try:
  index = SearchIndex.from_dict(schema, redis_url=REDIS_URL)
  index.create(overwrite=True, drop=True)
  print(f"Index '{INDEX_NAME}' created successfully with schema: {schema}")
except Exception as e:
  print(f"Error creating index: {str(e)}")