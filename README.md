# BetterReviews

A Flask-based web application that combines human reviews with AI-generated analysis to provide comprehensive product reviews.

## Features

- Submit product reviews through a user-friendly interface
- Search for products to get comprehensive reviews
- AI-powered review analysis using Google Gemini
- Vector search for finding relevant reviews using Redis

## Tech Stack

- **Web Framework**: Flask 3.1.1
- **Database**: Redis with RedisVL for vector search
- **AI Models**: Google Gemini via LangChain
- **Embedding Generation**: SentenceTransformer (all-MiniLM-L6-v2)
- **Frontend**: HTML/CSS with Jinja2 templates

## Setup

1. **Clone the repository:**
   ```
   git clone https://github.com/drishtipeshwani/betterreviews.git
   cd betterreviews
   ```

2. **Create a virtual environment and install dependencies:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up your environment variables:**
   - Create a `.env` file in the project root
   - Add your Google API key for Gemini:
     ```
     GOOGLE_API_KEY=your_api_key_here
     ```

4. **Set up Redis:**
   - Make sure Redis is installed and running
   - Run `python create_index.py` to create the required search index

5. **Run the application:**
   ```
   python app.py
   ```

## Usage

1. Open your browser and navigate to `http://127.0.0.1:5000/`
2. Use the search function to look for product reviews
3. Submit new product reviews via the "Share a Review" button

## Project Structure

- `app.py`: Main Flask application
- `review_generator.py`: AI review generation using Gemini
- `redis_config.py`: Redis connection management
- `load_data.py`: Data loading and vector embedding
- `create_index.py`: Creates the Redis vector search index
- `index_schema.py`: Defines the search index schema
- `templates/`: HTML templates for the web interface
