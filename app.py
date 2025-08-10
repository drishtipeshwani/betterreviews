from flask import Flask, render_template, flash, redirect, url_for, request
import json
import secrets
import asyncio
import load_data  # Assuming load_data.py is in the same directory
import review_generator
from redis_config import index_exists, get_search_index, INDEX_NAME
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# In app.py - Check once at startup
def verify_index_exists():
    """Verify that the required index exists - don't create it"""
    if index_exists():
        print(f"✓ Redis index '{INDEX_NAME}' is available")
        return True
    else:
        print(f"✗ Redis index '{INDEX_NAME}' not found")
        print("Please run 'python create_index.py' to create the index")
        return False

# At app startup
if not verify_index_exists():
    # You could either exit gracefully or continue with a warning
    print("Warning: Running without search index - some features may not work")

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generates a 32-character random hex string

# Add custom filter for line breaks
@app.template_filter('nl2br')
def nl2br_filter(text):
    """Convert newlines to HTML <br> tags"""
    if text is None:
        return ''
    # Replace \n with <br> tags
    return text.replace('\n', '<br>')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/page1')
def page1():
    return render_template('page1.html')

@app.route('/page2', methods=['POST'])
def page2():
    searched_product = request.form.get('searched_product')
    if not searched_product:
        flash('Please enter a product name to search.', 'error')
        return redirect(url_for('home'))
    
    # Use synchronous function - no need for asyncio.run()
    generated_review = review_generator.generate_review(review_generator.search_index, searched_product)
    return render_template('page2.html', 
                         product_name=searched_product, 
                         generated_review=generated_review)

@app.route('/submit_review', methods=['POST'])
def submit_review():
    # Get form data
    product_name = request.form.get('product_name')
    product_url = request.form.get('product_url')
    product_image = request.form.get('product_image')
    product_review = request.form.get('product_review')
    product_recommend = request.form.get('product_recommend')
    
    # Create a dictionary to store the review
    review_data = {
        "product_name": product_name,
        "product_url": product_url,
        "product_image": product_image,
        "product_review": product_review,
        "product_recommend": product_recommend
    }

    # Store the review in Redis
    load_data.load_data_to_redis(review_data)

    flash('Review submitted successfully!')  # This will show the popup message
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
