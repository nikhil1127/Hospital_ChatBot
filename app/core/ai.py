import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import json

load_dotenv()

class HospitalAIService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print("WARNING: GROQ_API_KEY not found. Running in MOCK mode.")
            self.llm = None
        else:
            self.llm = ChatGroq(
                temperature=0.1,
                model_name="llama-3.3-70b-specdec",
                groq_api_key=self.api_key
            )

        self.system_prompt = (
            "You are the official AI Assistant for a Multispeciality Hospital. "
            "Your goal is to help patients book appointments and find specialists. "
            "IMPORTANT GUIDELINES:\n"
            "1. Be professional and concise.\n"
            "2. NEVER provide a medical diagnosis.\n"
            "3. For emergencies, tell them to call 112/911 immediately.\n"
            "4. You can identify intents: 'FIND_DOCTOR', 'BOOK_APPOINTMENT', 'GENERAL_CHAT'.\n"
            "5. When booking, you must collect: Specialty, Doctor Name, and Date/Time.\n"
            "6. Format your output as a JSON if you are triggering a tool, otherwise plain text for WhatsApp."
        )

    async def get_response(self, user_message: str, session_data: dict, db_service=None):
        """
        Main entry point for AI logic. Integrates session and DB services.
        """
        if not self.llm:
            return f"[MOCK MODE] I received: {user_message}. Please add GROQ_API_KEY."

        # Build message history for context
        messages = [SystemMessage(content=self.system_prompt)]
        for msg in session_data.get("history", []):
            messages.append(msg)
        messages.append(HumanMessage(content=user_message))

        try:
            # We use a prompt to help the AI decide if it needs DB data
            # For a simple MVP, we'll let the AI respond naturally,
            # and we'll handle DB lookups in the webhook layer based on AI intent.
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            print(f"AI Error: {e}")
            return "I'm having trouble thinking. Please try again or type 'Agent'."

ai_service = HospitalAIService()
