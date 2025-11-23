<h1>Gemini Chat Clone</h1>

<p>A full-featured AI chat application built with Python (Flask) and Google Gemini API, designed to mirror modern LLM chat interfaces.</p>

<hr>

<h2>Features</h2>

<ul>
  <li>Google Gemini 1.5 Flash integration</li>
  <li>Persistent memory using SQLite</li>
  <li>User authentication (login/signup)</li>
  <li>Modern UI with markdown + code highlighting</li>
  <li>Pin, rename, delete conversations</li>
  <li>Typing animations and auto-expanding input box</li>
</ul>

<hr>

<h2>Installation</h2>

<ol>
  <li><strong>Clone the repository:</strong>
    <pre><code>git clone https://github.com/yourusername/gemini-chat.git
cd gemini-chat</code></pre>
  </li>
  
  <li><strong>Install dependencies:</strong>
    <pre><code>pip install -r requirements.txt</code></pre>
  </li>
  
  <li><strong>Set your API key:</strong>
    <p>Open <code>ai_engine.py</code> and replace the API_KEY placeholder with your Google Gemini API key.</p>
  </li>
  
  <li><strong>Run the app:</strong>
    <pre><code>python app.py</code></pre>
    <p>Then visit <code>http://localhost:5000</code></p>
  </li>
</ol>

<hr>

<h2>Project Structure</h2>

<pre><code>app.py               - Flask backend and API routes
database.py          - SQLite handling and user session logic
ai_engine.py         - Wrapper for Google Gemini API
templates/index.html - Main frontend UI
static/              - CSS/JS assets
requirements.txt</code></pre>

<hr>

<h2>Configuration</h2>

<p>Set your API key inside <code>ai_engine.py</code>:</p>

<pre><code>API_KEY = "YOUR_GOOGLE_GEMINI_API_KEY"</code></pre>

<p>For production, use environment variables.</p>

<hr>

<h2>Deployment</h2>

<ul>
  <li>Can be deployed using Docker, Render, Fly.io, AWS, etc.</li>
  <li>Recommended to run behind gunicorn + Nginx</li>
</ul>

<hr>

<h2>Notes</h2>

<p>This project demonstrates full-stack development:</p>
<ul>
  <li>Flask backend and REST APIs</li>
  <li>SQLite relational database</li>
  <li>Authentication system</li>
  <li>Frontend built with HTML, CSS (Grid/Flexbox), and Vanilla JS</li>
</ul>

<hr>

<p><strong>License:</strong> MIT (or specify your license)</p>

<p><strong>Contributing:</strong> Pull requests are welcome!</p>