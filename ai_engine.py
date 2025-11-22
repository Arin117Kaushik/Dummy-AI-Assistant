import google.generativeai as genai
import os

# Configure the Gemini API
# In production, use environment variables: os.environ.get('GEMINI_API_KEY')
API_KEY = "AIzaSyAIYlJnYVXygXUgFEbFo5V-Op6H_VxS6Ho"

class GeminiHandler:
    def __init__(self):
        try:
            genai.configure(api_key=API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            print("✅ Gemini AI Handler Initialized")
        except Exception as e:
            print(f"❌ Error initializing Gemini: {e}")

    def generate_response(self, history, user_input):
        try:
            # Convert local DB format to Gemini format
            formatted_history = []
            for msg in history:
                # Map 'assistant' role to 'model' for Gemini API
                role = "user" if msg['role'] == "user" else "model"
                formatted_history.append({
                    "role": role,
                    "parts": [msg['content']]
                })

            # Start chat with history
            chat = self.model.start_chat(history=formatted_history)
            response = chat.send_message(user_input)
            return response.text
            
        except Exception as e:
            return f"I'm having trouble connecting right now. Error: {str(e)}"