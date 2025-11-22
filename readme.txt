# Gemini Chat Clone

A full-featured AI chat application built with Python (Flask) and Google Gemini API, designed to mirror modern LLM chat interfaces.

## Features

- Google Gemini 1.5 Flash integration
- Persistent memory using SQLite
- User authentication (login/signup)
- Modern UI with markdown + code highlighting
- Pin, rename, delete conversations
- Typing animations and auto-expanding input box

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/gemini-chat.git
   cd gemini-chat
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set your API key:**
   
   Open `ai_engine.py` and replace the API_KEY placeholder with your Google Gemini API key.

4. **Run the app:**
   ```bash
   python app.py
   ```
   
   Then visit `http://localhost:5000`

## Project Structure

```
app.py               - Flask backend and API routes
database.py          - SQLite handling and user session logic
ai_engine.py         - Wrapper for Google Gemini API
templates/index.html - Main frontend UI
static/              - CSS/JS assets
requirements.txt
```

## Configuration

Set your API key inside `ai_engine.py`:

```python
API_KEY = "YOUR_GOOGLE_GEMINI_API_KEY"
```

For production, use environment variables.

## Deployment

- Can be deployed using Docker, Render, Fly.io, AWS, etc.
- Recommended to run behind gunicorn + Nginx

## Notes

This project demonstrates full-stack development:
- Flask backend and REST APIs
- SQLite relational database
- Authentication system
- Frontend built with HTML, CSS (Grid/Flexbox), and Vanilla JS

---

**License:** MIT (or specify your license)

**Contributing:** Pull requests are welcome!