import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from typing import Optional

load_dotenv()

# Import RAG service if available
try:
    from app.core.rag_service import rag_service
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("⚠️ RAG service not available. Knowledge base features disabled.")


class HospitalAIService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print("⚠️ WARNING: GROQ_API_KEY not found. Running in MOCK mode.")
            self.llm = None
        else:
            try:
                self.llm = ChatGroq(
                    temperature=0.1,
                    model_name="llama-3.3-70b-specdec",
                    groq_api_key=self.api_key,
                    max_tokens=1024
                )
                print("✅ AI Service initialized with Groq")
            except Exception as e:
                print(f"⚠️ Error initializing Groq: {e}")
                self.llm = None

        self.rag_enabled = RAG_AVAILABLE and rag_service.has_documents()
        if self.rag_enabled:
            print("📚 Knowledge Base (RAG) is ACTIVE")

        self.system_prompt = """You are the official AI Assistant for a Multispeciality Hospital.

ROLE:
- Help patients book appointments
- Find appropriate specialists based on symptoms
- Answer general hospital FAQs
- Provide empathetic, professional support

CRITICAL RULES:
1. NEVER provide medical diagnosis or prescribe treatment
2. ALWAYS recommend consulting a doctor for medical concerns
3. For emergencies (chest pain, severe bleeding, difficulty breathing), tell them to call 112/911 IMMEDIATELY
4. Be concise - WhatsApp users prefer short, clear messages
5. Use bullet points and bold text for readability
6. If unsure, ask them to wait for a human staff member

SYMPTOM TO SPECIALTY GUIDE:
- Chest pain, heart issues → Cardiology
- Children's health → Pediatrics
- Brain, headaches, seizures → Neurology
- Bones, joints, fractures → Orthopedics
- Skin issues → Dermatology
- General checkup, fever, cold → General Medicine

FORMAT: Always be warm, professional, and use emojis where appropriate."""

    async def get_response(self, user_message: str, session_data: dict, db_service=None) -> str:
        """
        Generate AI response with context from session and database.
        """
        if not self.llm:
            return await self._mock_response(user_message, db_service)

        # Build context-aware messages
        messages = [SystemMessage(content=self.system_prompt)]

        # Add conversation history (last 5 messages for context)
        history = session_data.get("history", [])
        for msg in history[-5:]:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

        # Add current message
        messages.append(HumanMessage(content=user_message))

        # Check for emergency keywords
        emergency_keywords = ["chest pain", "heart attack", "bleeding", "can't breathe", "unconscious", "emergency"]
        if any(keyword in user_message.lower() for keyword in emergency_keywords):
            return ("🚨 **EMERGENCY DETECTED** 🚨\n\n"
                    "Please call emergency services (112/911) immediately or go to the nearest ER.\n\n"
                    "Do not wait for an appointment!")

        # Check if RAG can help with this query
        rag_context = ""
        if self.rag_enabled and self._should_use_rag(user_message):
            rag_context = rag_service.get_relevant_context(user_message)
            if rag_context:
                print(f"📚 RAG context found for query: {user_message[:50]}...")

        try:
            # Build enhanced prompt with RAG context if available
            if rag_context:
                enhanced_prompt = f"""Answer the patient's question using ONLY the information provided below.
If the answer isn't in the context, say you don't have that information.

HOSPITAL INFORMATION:
{rag_context}

PATIENT QUESTION: {user_message}"""
                messages.append(HumanMessage(content=enhanced_prompt))

            # Get AI response
            response = self.llm.invoke(messages)
            ai_text = response.content

            # If user asks about doctors and we have db_service, enhance response
            if db_service and any(word in user_message.lower() for word in ["doctor", "specialist", "cardiologist", "physician"]):
                ai_text = await self._enhance_with_doctor_info(ai_text, user_message, db_service)

            return ai_text

        except Exception as e:
            print(f"❌ AI Error: {e}")
            return "I'm having trouble processing your request. Please try again in a moment or type 'agent' to speak with a human."

    def _should_use_rag(self, message: str) -> bool:
        """Determine if this query should search the knowledge base."""
        rag_keywords = [
            "hour", "timing", "open", "close", "visit", "location", "address",
            "reach", "direction", "parking", "policy", "insurance", "cashless",
            "payment", "billing", "facility", "room", "icu", "operation",
            "laboratory", "pharmacy", "procedure", "surgery", "test", "package",
            "cost", "price", "contact", "phone", "email", "profile", "about dr",
            "about doctor", "qualification"
        ]
        return any(kw in message.lower() for kw in rag_keywords)

    async def _mock_response(self, user_message: str, db_service) -> str:
        """Fallback mock response when AI is unavailable."""
        message_lower = user_message.lower()

        # Simple keyword-based responses
        if any(word in message_lower for word in ["book", "appointment"]):
            return "I'd be happy to help you book an appointment! What specialty do you need?"

        if any(word in message_lower for word in ["doctor", "specialist"]):
            if db_service:
                specialties = db_service.list_all_specialties()
                if specialties:
                    specialty_list = ", ".join([s[0] for s in specialties[:5]])
                    return f"We have doctors in: {specialty_list}. Which specialty do you need?"
            return "We have specialists in Cardiology, Pediatrics, Neurology, Orthopedics, Dermatology, and General Medicine. Which do you need?"

        if any(word in message_lower for word in ["emergency", "urgent", "chest pain"]):
            return "🚨 For emergencies, please call 112/911 immediately or go to the nearest ER!"

        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            return "👋 Hello! Welcome to our Multispeciality Hospital. I'm your AI assistant. How can I help you today? (Book appointment / Find doctor / General enquiry)"

        return "I understand. Could you please provide more details? You can ask me to:\n• Book an appointment\n• Find a specialist\n• Answer general questions"

    async def _enhance_with_doctor_info(self, ai_text: str, user_message: str, db_service) -> str:
        """Enhance AI response with real doctor data from database."""
        # Extract potential specialty from user message
        specialties = {
            "cardiology": "Cardiology",
            "heart": "Cardiology",
            "pediatric": "Pediatrics",
            "child": "Pediatrics",
            "neurology": "Neurology",
            "brain": "Neurology",
            "orthopedic": "Orthopedics",
            "bone": "Orthopedics",
            "joint": "Orthopedics",
            "dermatology": "Dermatology",
            "skin": "Dermatology",
            "general": "General Medicine"
        }

        message_lower = user_message.lower()
        detected_specialty = None

        for keyword, specialty in specialties.items():
            if keyword in message_lower:
                detected_specialty = specialty
                break

        if detected_specialty:
            doctors = db_service.find_doctors_by_specialty(detected_specialty)
            if doctors:
                doctor_info = f"\n\n🩺 **Available {detected_specialty} Doctors:**\n"
                for doc in doctors[:3]:
                    doctor_info += f"• {doc.name} ({doc.experience_years} yrs exp) - ₹{doc.consultation_fee}\n"
                return ai_text + doctor_info

        return ai_text

# Singleton instance
ai_service = HospitalAIService()
