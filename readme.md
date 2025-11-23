<h1>Gemini Chat Clone</h1>

<p>A full-featured AI chat application built with Python (Flask) and Google Gemini API, designed to mirror modern LLM chat interfaces.</p>

<hr>

<h2>Features</h2>

<ul>
  <li><strong>Google Gemini 2.5 Flash integration</strong> for fast and intelligent responses</li>
  <li><strong>Speech-to-Text (Dictation):</strong> Use the microphone button to dictate messages directly into the chat.</li>
  <li><strong>User Authentication:</strong>
    <ul>
      <li>Email/Password Login & Registration</li>
      <li><strong>OAuth Support:</strong> Sign in with Google or GitHub</li>
      <li><strong>Guest Mode:</strong> Try the app without creating an account (data saved locally)</li>
    </ul>
  </li>
  <li><strong>Persistent Memory:</strong> Chat history is saved using SQLite.</li>
  <li><strong>Modern UI:</strong> Dark mode interface with markdown rendering and code syntax highlighting.</li>
  <li><strong>Chat Management:</strong> Pin, rename, and delete conversations.</li>
  <li><strong>Responsive Design:</strong> Works on desktop and mobile with a collapsible sidebar.</li>
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
  
  <li><strong>Configuration:</strong>
    <p>Create a <code>.env</code> file in the root directory and add your API keys:</p>
    <pre><code>GEMINI_API_KEY=your_gemini_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
SECRET_KEY=your_flask_secret_key</code></pre>
  </li>
  
  <li><strong>Run the app:</strong>
    <pre><code>python app.py</code></pre>
    <p>Then visit <code>http://localhost:5000</code></p>
  </li>
</ol>

<hr>

<h2>Project Structure</h2>

<pre><code>app.py               - Flask backend, API routes, and Auth logic
database.py          - SQLite handling and user session logic
ai_engine.py         - Wrapper for Google Gemini API
templates/index.html - Main frontend UI (HTML/JS/CSS)
static/              - Assets
requirements.txt     - Python dependencies
.env                 - Environment variables (not committed)</code></pre>

<hr>

<h2>Deployment</h2>

<ul>
  <li>Can be deployed using Docker, Render, Fly.io, AWS, etc.</li>
  <li>Recommended to run behind gunicorn + Nginx for production.</li>
  <li>Ensure <code>OAUTHLIB_INSECURE_TRANSPORT</code> is NOT set to 1 in production.</li>
</ul>

<hr>

<h2>Notes</h2>

<p>This project demonstrates full-stack development:</p>
<ul>
  <li>Flask backend with RESTful APIs</li>
  <li>SQLite relational database with Authlib integration</li>
  <li>Secure authentication handling (hashing, sessions, OAuth)</li>
  <li>Frontend built with HTML5, Vanilla CSS, and JavaScript (Web Speech API)</li>
</ul>

<hr>

<p><strong>License:</strong> MIT</p>

<p><strong>Contributing:</strong> Pull requests are welcome!</p>