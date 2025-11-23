import google.generativeai as genai
import os

# Configure the Gemini API
# In production, use environment variables: os.environ.get('GEMINI_API_KEY')
API_KEY = os.getenv('GEMINI_API_KEY')

class GeminiHandler:
    """
    Handles interactions with the Google Gemini API.
    Manages model initialization and chat generation.
    """
    def __init__(self):
        try:
            if not API_KEY:
                print("❌ Error: GEMINI_API_KEY not found in environment variables.")
                return
                
            genai.configure(api_key=API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            print("✅ Gemini AI Handler Initialized")
        except Exception as e:
            print(f"❌ Error initializing Gemini: {e}")

    def generate_response(self, history, user_input):
        """
        Generates a response from the AI model based on the conversation history.
        
        Args:
            history (list): List of message dicts from the database.
            user_input (str): The current message from the user.
            
        Returns:
            str: The AI's response text.
        """
        try:
            if not hasattr(self, 'model'):
                 return "AI service is not initialized. Please check server logs."

            # Convert local DB format to Gemini format
            # Gemini expects 'user' and 'model' roles.
            formatted_history = []
            for msg in history:
                # Map 'assistant' role to 'model' for Gemini API
                role = "user" if msg['role'] == "user" else "model"
                formatted_history.append({
                    "role": role,
                    "parts": [msg['content']]
                })

            # Start a chat session with the formatted history
            chat = self.model.start_chat(history=formatted_history)
            
            # Send the new user message and get the response
            response = chat.send_message(user_input)
            return response.text
            
        except Exception as e:
            return f"I'm having trouble connecting right now. Error: {str(e)}"