from functools import wraps
from redisvl.index import SearchIndex
from redisvl.query import VectorQuery
from redisvl.query.filter import Text
from redis_config import get_redis_url
from index_schema import get_index_schema
from redisvl.utils.vectorize import HFTextVectorizer
from redisvl.extensions.cache.embeddings import EmbeddingsCache
from redisvl.extensions.llmcache import SemanticCache
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import os

hf = HFTextVectorizer(
    model="sentence-transformers/all-MiniLM-L6-v2",
    cache=EmbeddingsCache(
        name="embedcache",
        ttl=None,
        redis_url=get_redis_url(),  # Use shared Redis URL
    )
)

llmcache = SemanticCache(
    name="llmcache",
    vectorizer=hf,
    redis_url=get_redis_url(),
    ttl=1800,
    distance_threshold=0.2,
    overwrite=True,
)

# Get API key from environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

search_index = SearchIndex.from_dict(get_index_schema(), redis_url=get_redis_url())

# Create an LLM caching decorator
def cache(func):
    @wraps(func)
    def wrapper(index, product_name):
        query = f"Please provide a detailed review of {product_name} which can help me in making a better and informed purchasing decision."
        query_vector = llmcache._vectorizer.embed(query)

        # Check the cache with the vector
        if result := llmcache.check(vector=query_vector):
            print("Cache hit!")
            return result[0]['response']

        response = func(index, product_name)
        llmcache.store(query, response, query_vector)
        return response
    return wrapper

@cache
def generate_review(index: SearchIndex, product_name: str):
    """Generate helpful tech and lifestyle product reviews using a two-step approach:
    1. Get factual product information from the model's knowledge
    2. Analyze user reviews from context to provide insights
    """

    # Normalize product name
    product_name = str(product_name).lower().replace(" ", "_")

    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
            google_api_key=GOOGLE_API_KEY,
            model="gemini-1.5-flash",
            temperature=0)
    
    # STEP 1: Get factual product information (first conversation)
    factual_info = get_factual_information(llm, product_name)
    print(f"Factual information generated: {factual_info[:200]}...")
    
    # STEP 2: Retrieve user reviews and analyze them (second conversation)
    query = f"Please provide insights on {product_name} based on user reviews."
    query_vector = hf.embed(query)
    
    # Fetch context from Redis using vector search with product name filter
    context = retrieve_context(index, query_vector, product_name)
    print(f"Retrieved context: {context[:500]}...")  # Print first 500 chars for debugging
    
    # Get user review insights from the second conversation
    user_insights = analyze_user_reviews(llm, product_name, context)
    print(f"User insights generated: {user_insights[:200]}...")
    
    # Combine the results
    combined_review = f"""## Product Overview
{factual_info}

## User Experience & Review Analysis
{user_insights}
"""
    return combined_review


def retrieve_context(search_index: SearchIndex, query_vector, product_name: str) -> str:
    """Fetch the relevant context from Redis using vector search"""
    
    # Create a filter to only search within reviews for the specific product
    product_filter = Text("product_name") == product_name
    
    results = search_index.query(
        VectorQuery(
            vector=query_vector,
            vector_field_name="embeddings",
            return_fields=["product_review", "product_name"],
            num_results=50,
            filter_expression=product_filter
        )
    )

    content = "\n".join([result["product_review"] for result in results])
    return content


def get_factual_information(llm, product_name: str) -> str:
    """First conversation: Get factual product information from the model's knowledge"""
    
    system_prompt = """You are an expert product researcher with extensive knowledge across various tech and lifestyle product categories. 
    Your task is to provide factual, informative details about a specific product based on your knowledge.
    Focus on specifications, features, typical pricing, target audience, and how it compares to alternatives.
    Only provide factual information that would be generally known about this product category."""
    
    user_prompt = f"""Please provide detailed factual information about {product_name}.
    
    Structure your response with these sections:
    
    ## Product Specifications & Features
    - Detailed specifications and key features
    - Pricing range (if known)
    - Target audience and intended use
    
    ## Comparative Analysis
    - How it compares to competitors or alternatives
    - Unique selling points
    - Typical drawbacks or limitations
    
    Provide comprehensive, factual information to help understand this product objectively. 
    Do not include user reviews or subjective opinions in this section."""
    
    # Create messages for the first conversation
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    # Get factual information
    response = llm.invoke(messages)
    return response.content


def analyze_user_reviews(llm, product_name: str, context: str) -> str:
    """Second conversation: Analyze user reviews from the context"""
    
    system_prompt = """You are an expert review analyst who specializes in extracting meaningful insights from user reviews.
    Your task is to analyze the provided user reviews and identify patterns, trends, and common feedback points.
    Focus on being objective and extracting what actual users are saying about their experiences."""
    
    if context.strip():
        user_prompt = f"""Based on the following user reviews for {product_name}, provide an analysis of user experiences.
        
        USER REVIEWS:
        {context}
        
        Please analyze these reviews and structure your response with:
        
        ## User Experience Summary
        - Overall sentiment and satisfaction level
        - Most frequently mentioned points
        
        ## What Users Love
        - Positive aspects mentioned across reviews
        - Standout features according to users
        
        ## Common Concerns
        - Issues or limitations mentioned by users
        - Recurring complaints or drawbacks
        
        ## Recommendations Based on User Feedback
        - Who would benefit most from this product according to actual users
        - Situations where this product performs best
        
        Only base your analysis on the actual user reviews provided. Be specific about what real users are saying."""
    else:
        user_prompt = f"""There are currently no user reviews available for {product_name} in our database.
        
        Please provide:
        
        ## User Review Limitations
        - A brief note explaining that your analysis is limited due to lack of specific user reviews
        - General expectations about what users might experience with this type of product
        - What potential buyers should look out for when considering this product
        
        Be honest about the lack of specific user feedback while still providing helpful guidance."""
    
    # Create messages for the second conversation
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    # Get user review analysis
    response = llm.invoke(messages)
    return response.content