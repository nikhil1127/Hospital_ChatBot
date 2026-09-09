"""
Comprehensive Unit Tests for Hospital WhatsApp Bot
==================================================
Tests all components: Database, Session Management, AI, and Webhook Flow

Run with: python -m unittest tests.test_comprehensive -v
"""

import unittest
import asyncio
import json
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, AsyncMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def safe_print(message):
    """Print with ASCII only fallback for Windows"""
    try:
        print(message)
    except UnicodeEncodeError:
        safe_msg = message.encode('ascii', 'replace').decode('ascii')
        print(safe_msg)


# ==================== TEST 1: DATABASE MODELS ====================

class TestDatabaseModels(unittest.TestCase):
    """Test SQLAlchemy database models"""

    def setUp(self):
        """Set up test fixtures"""
        from app.db.models import User, Doctor, Appointment
        from app.db.session import Base
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # Create in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        TestingSessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.db = TestingSessionLocal()

    def tearDown(self):
        """Clean up after tests"""
        self.db.close()

    def test_user_creation(self):
        """Test User model creation"""
        from app.db.models import User

        user = User(
            phone_number="whatsapp:+918374657281",
            name="Test Patient",
            email="test@example.com"
        )
        self.db.add(user)
        self.db.commit()

        # Verify user was created
        saved_user = self.db.query(User).filter_by(phone_number="whatsapp:+918374657281").first()
        self.assertIsNotNone(saved_user)
        self.assertEqual(saved_user.name, "Test Patient")
        self.assertEqual(saved_user.email, "test@example.com")
        safe_print("[PASS] User creation test passed")

    def test_doctor_creation(self):
        """Test Doctor model creation"""
        from app.db.models import Doctor

        doctor = Doctor(
            name="Dr. Test Cardiologist",
            specialty="Cardiology",
            experience_years=15,
            consultation_fee=500.0,
            availability_slots="Mon-Fri 09:00-17:00",
            is_available=True
        )
        self.db.add(doctor)
        self.db.commit()

        saved_doctor = self.db.query(Doctor).filter_by(name="Dr. Test Cardiologist").first()
        self.assertIsNotNone(saved_doctor)
        self.assertEqual(saved_doctor.specialty, "Cardiology")
        self.assertEqual(saved_doctor.consultation_fee, 500.0)
        safe_print("[PASS] Doctor creation test passed")

    def test_appointment_creation(self):
        """Test Appointment model creation with relationships"""
        from app.db.models import User, Doctor, Appointment

        # Create user and doctor first
        user = User(phone_number="whatsapp:+918300000001", name="Patient One")
        doctor = Doctor(
            name="Dr. Test Neurologist",
            specialty="Neurology",
            experience_years=10,
            consultation_fee=600.0,
            availability_slots="Mon-Wed 10:00-16:00",
            is_available=True
        )
        self.db.add(user)
        self.db.add(doctor)
        self.db.commit()

        # Create appointment
        appointment = Appointment(
            user_id=user.id,
            doctor_id=doctor.id,
            appointment_date=datetime.now() + timedelta(days=1),
            status="confirmed"
        )
        self.db.add(appointment)
        self.db.commit()

        # Verify relationships
        saved_appointment = self.db.query(Appointment).first()
        self.assertIsNotNone(saved_appointment)
        self.assertEqual(saved_appointment.user_id, user.id)
        self.assertEqual(saved_appointment.doctor_id, doctor.id)
        self.assertEqual(saved_appointment.status, "confirmed")
        safe_print("[PASS] Appointment creation test passed")

    def test_specialty_indexing(self):
        """Test that specialty field is indexed for fast queries"""
        from app.db.models import Doctor

        # Add multiple doctors
        doctors = [
            Doctor(name="Dr. A", specialty="Cardiology", consultation_fee=500, availability_slots="Mon"),
            Doctor(name="Dr. B", specialty="Cardiology", consultation_fee=600, availability_slots="Tue"),
            Doctor(name="Dr. C", specialty="Neurology", consultation_fee=700, availability_slots="Wed"),
        ]
        for d in doctors:
            self.db.add(d)
        self.db.commit()

        # Test filtering by specialty
        cardiology_docs = self.db.query(Doctor).filter_by(specialty="Cardiology").all()
        self.assertEqual(len(cardiology_docs), 2)
        safe_print("[PASS] Specialty indexing test passed")


# ==================== TEST 2: DATABASE SERVICE ====================

class TestHospitalDBService(unittest.TestCase):
    """Test HospitalDBService operations"""

    def setUp(self):
        """Set up in-memory database"""
        from app.db.session import Base
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.core.db_service import HospitalDBService
        from app.db.models import Doctor

        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        TestingSessionLocal = sessionmaker(bind=self.engine)
        self.db = TestingSessionLocal()
        self.db_service = HospitalDBService(self.db)

        # Seed with test data
        doctors = [
            Doctor(name="Dr. Sarah Smith", specialty="Cardiology", experience_years=15,
                   consultation_fee=500.0, availability_slots="Mon 09:00-12:00", is_available=True),
            Doctor(name="Dr. James Wilson", specialty="Pediatrics", experience_years=10,
                   consultation_fee=300.0, availability_slots="Tue 10:00-13:00", is_available=True),
            Doctor(name="Dr. Emily Chen", specialty="Cardiology", experience_years=12,
                   consultation_fee=600.0, availability_slots="Wed 14:00-17:00", is_available=True),
        ]
        for d in doctors:
            self.db.add(d)
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_get_or_create_user_new(self):
        """Test creating a new user"""
        user = self.db_service.get_or_create_user("whatsapp:+919876543210")
        self.assertIsNotNone(user)
        self.assertEqual(user.phone_number, "whatsapp:+919876543210")

        # Verify it was saved
        self.assertEqual(self.db.query(type(user)).count(), 1)
        safe_print("[PASS] Get or create user (new) test passed")

    def test_get_or_create_user_existing(self):
        """Test retrieving existing user"""
        # Create user first
        user1 = self.db_service.get_or_create_user("whatsapp:+919876543210", name="John Doe")
        initial_id = user1.id

        # Try to create again - should return existing
        user2 = self.db_service.get_or_create_user("whatsapp:+919876543210")
        self.assertEqual(user2.id, initial_id)
        self.assertEqual(self.db.query(type(user1)).count(), 1)  # Still only 1 user
        safe_print("[PASS] Get or create user (existing) test passed")

    def test_find_doctors_by_specialty(self):
        """Test finding doctors by specialty"""
        # Search for Cardiology
        doctors = self.db_service.find_doctors_by_specialty("Cardiology")
        self.assertEqual(len(doctors), 2)
        self.assertTrue(all(d.specialty == "Cardiology" for d in doctors))

        # Search for Pediatrics
        doctors = self.db_service.find_doctors_by_specialty("Pediatrics")
        self.assertEqual(len(doctors), 1)
        self.assertEqual(doctors[0].name, "Dr. James Wilson")
        safe_print("[PASS] Find doctors by specialty test passed")

    def test_find_doctors_case_insensitive(self):
        """Test case-insensitive specialty search"""
        doctors = self.db_service.find_doctors_by_specialty("cardiology")  # lowercase
        self.assertEqual(len(doctors), 2)
        safe_print("[PASS] Case-insensitive search test passed")

    def test_list_all_specialties(self):
        """Test listing unique specialties"""
        specialties = self.db_service.list_all_specialties()
        specialty_names = [s[0] for s in specialties]
        self.assertIn("Cardiology", specialty_names)
        self.assertIn("Pediatrics", specialty_names)
        self.assertEqual(len(specialty_names), 2)  # Only unique values
        safe_print("[PASS] List all specialties test passed")

    def test_create_appointment(self):
        """Test creating an appointment"""
        from app.db.models import User

        # Create user first
        user = self.db_service.get_or_create_user("whatsapp:+918300000001")
        doctor = self.db_service.find_doctors_by_specialty("Cardiology")[0]

        appointment_date = datetime.now() + timedelta(days=1)
        appointment = self.db_service.create_appointment(
            user_id=user.id,
            doctor_id=doctor.id,
            date_time=appointment_date,
            status="confirmed"
        )

        self.assertIsNotNone(appointment.id)
        self.assertEqual(appointment.user_id, user.id)
        self.assertEqual(appointment.doctor_id, doctor.id)
        self.assertEqual(appointment.status, "confirmed")
        safe_print("[PASS] Create appointment test passed")

    def test_get_user_appointments(self):
        """Test retrieving user appointments"""
        from app.db.models import User

        user = self.db_service.get_or_create_user("whatsapp:+918300000001")
        doctor = self.db_service.find_doctors_by_specialty("Cardiology")[0]

        # Create 2 appointments
        for i in range(2):
            self.db_service.create_appointment(
                user_id=user.id,
                doctor_id=doctor.id,
                date_time=datetime.now() + timedelta(days=i+1),
                status="confirmed"
            )

        appointments = self.db_service.get_user_appointments(user.id)
        self.assertEqual(len(appointments), 2)
        safe_print("[PASS] Get user appointments test passed")

    def test_cancel_appointment(self):
        """Test cancelling an appointment"""
        user = self.db_service.get_or_create_user("whatsapp:+918300000001")
        doctor = self.db_service.find_doctors_by_specialty("Cardiology")[0]

        appointment = self.db_service.create_appointment(
            user_id=user.id,
            doctor_id=doctor.id,
            date_time=datetime.now() + timedelta(days=1),
            status="confirmed"
        )

        # Cancel it
        result = self.db_service.cancel_appointment(appointment.id)
        self.assertTrue(result)

        # Verify status changed
        cancelled = self.db_service.get_appointment_by_id(appointment.id)
        self.assertEqual(cancelled.status, "cancelled")
        safe_print("[PASS] Cancel appointment test passed")

    def test_check_slot_availability(self):
        """Test checking if time slot is available"""
        user = self.db_service.get_or_create_user("whatsapp:+918300000001")
        doctor = self.db_service.find_doctors_by_specialty("Cardiology")[0]

        appointment_time = datetime.now() + timedelta(days=1)

        # Should be available initially
        available = self.db_service.check_slot_availability(doctor.id, appointment_time)
        self.assertTrue(available)

        # Create appointment
        self.db_service.create_appointment(user.id, doctor.id, appointment_time)

        # Should no longer be available
        available = self.db_service.check_slot_availability(doctor.id, appointment_time)
        self.assertFalse(available)
        safe_print("[PASS] Check slot availability test passed")


# ==================== TEST 3: SESSION MANAGEMENT ====================

class TestSessionManager(unittest.TestCase):
    """Test Redis session management (mocked)"""

    def setUp(self):
        """Set up mocked Redis"""
        from app.core.session import SessionManager

        # Mock Redis for testing
        self.mock_redis = MagicMock()
        self.mock_redis.get.return_value = None
        self.mock_redis.setex = MagicMock()
        self.mock_redis.delete = MagicMock()

        # Patch the session manager to use mock
        self.session_manager = SessionManager()
        self.session_manager.redis_client = self.mock_redis
        self.session_manager.memory_store = {}

    def test_get_session_new_user(self):
        """Test getting session for new user"""
        self.mock_redis.get.return_value = None  # No existing session

        session = self.session_manager.get_session("whatsapp:+918300000001")

        # Should return default structure
        self.assertEqual(session["state"], "START")
        self.assertEqual(session["context"], {})
        self.assertEqual(session["history"], [])
        self.mock_redis.get.assert_called_once_with("session:whatsapp:+918300000001")
        safe_print("[PASS] Get session (new user) test passed")

    def test_get_session_existing(self):
        """Test getting existing session"""
        existing_session = {
            "state": "SELECT_SPECIALTY",
            "context": {"specialty": "Cardiology"},
            "history": [{"role": "user", "content": "Hello"}]
        }
        self.mock_redis.get.return_value = json.dumps(existing_session)

        session = self.session_manager.get_session("whatsapp:+918300000001")

        self.assertEqual(session["state"], "SELECT_SPECIALTY")
        self.assertEqual(session["context"]["specialty"], "Cardiology")
        safe_print("[PASS] Get session (existing) test passed")

    def test_update_session(self):
        """Test updating session"""
        session_data = {
            "state": "SELECT_DOCTOR",
            "context": {"specialty": "Neurology"},
            "history": [{"role": "user", "content": "I need a neurologist"}]
        }

        self.session_manager.update_session("whatsapp:+918300000001", session_data)

        # Verify Redis setex was called with 30-minute expiry (1800 seconds)
        self.mock_redis.setex.assert_called_once()
        call_args = self.mock_redis.setex.call_args[0]
        self.assertEqual(call_args[0], "session:whatsapp:+918300000001")
        self.assertEqual(call_args[1], 1800)  # 30 minutes
        self.assertEqual(json.loads(call_args[2]), session_data)
        safe_print("[PASS] Update session test passed")

    def test_clear_session(self):
        """Test clearing session"""
        self.session_manager.clear_session("whatsapp:+918300000001")
        self.mock_redis.delete.assert_called_once_with("session:whatsapp:+918300000001")
        safe_print("[PASS] Clear session test passed")

    def test_memory_fallback(self):
        """Test in-memory storage when Redis is unavailable"""
        self.session_manager.redis_client = None  # Simulate Redis down

        # Create session
        session_data = {"state": "TEST", "context": {}, "history": []}
        self.session_manager.update_session("user123", session_data)

        # Retrieve session
        retrieved = self.session_manager.get_session("user123")
        self.assertEqual(retrieved["state"], "TEST")
        safe_print("[PASS] Memory fallback test passed")


# ==================== TEST 4: AI SERVICE (MOCK MODE) ====================

class TestAIServiceMockMode(unittest.IsolatedAsyncioTestCase):
    """Test AI service in mock mode (no API key needed)"""

    def setUp(self):
        """Set up AI service without API key"""
        from app.core.ai import HospitalAIService

        # Temporarily clear API key
        self.original_key = os.environ.get("GROQ_API_KEY")
        os.environ["GROQ_API_KEY"] = ""

        self.ai_service = HospitalAIService()

    def tearDown(self):
        """Restore API key"""
        if self.original_key:
            os.environ["GROQ_API_KEY"] = self.original_key

    async def test_mock_response_booking(self):
        """Test mock response for booking intent"""
        response = await self.ai_service._mock_response("I want to book an appointment", None)
        self.assertIn("appointment", response.lower())
        safe_print("[PASS] Mock response (booking) test passed")

    async def test_mock_response_doctor_query(self):
        """Test mock response for doctor query"""
        # Mock db_service
        mock_db = MagicMock()
        mock_db.list_all_specialties.return_value = [("Cardiology",), ("Pediatrics",)]

        response = await self.ai_service._mock_response("Which doctors do you have?", mock_db)
        self.assertIn("Cardiology", response)
        self.assertIn("Pediatrics", response)
        safe_print("[PASS] Mock response (doctor query) test passed")

    async def test_mock_response_emergency(self):
        """Test emergency detection in mock mode"""
        response = await self.ai_service._mock_response("I have chest pain", None)
        self.assertIn("112/911", response)
        self.assertIn("emergency", response.lower())
        safe_print("[PASS] Mock response (emergency) test passed")

    async def test_should_use_rag(self):
        """Test RAG detection logic"""
        # Should use RAG for policy questions
        self.assertTrue(self.ai_service._should_use_rag("What are your visiting hours?"))
        self.assertTrue(self.ai_service._should_use_rag("Do you accept insurance?"))
        self.assertTrue(self.ai_service._should_use_rag("What is the parking cost?"))

        # Should not use RAG for booking
        self.assertFalse(self.ai_service._should_use_rag("Book an appointment"))
        self.assertFalse(self.ai_service._should_use_rag("I need a doctor"))
        safe_print("[PASS] RAG detection test passed")

    async def test_get_response_emergency_detection(self):
        """Test emergency detection in main get_response"""
        # Force mock mode
        self.ai_service.api_key = ""
        self.ai_service.llm = None

        response = await self.ai_service.get_response("I have chest pain and can't breathe", {}, None)
        self.assertIn("EMERGENCY", response)
        safe_print("[PASS] Emergency detection in get_response test passed")

    async def test_intent_detection(self):
        """Test intent detection logic"""
        from app.core.ai import detect_intent

        # Test booking intent
        self.assertEqual(detect_intent("book an appointment"), "book_appointment")
        self.assertEqual(detect_intent("schedule a doctor"), "book_appointment")

        # Test doctor inquiry
        self.assertEqual(detect_intent("what doctors do you have"), "doctor_inquiry")
        self.assertEqual(detect_intent("list specialists"), "doctor_inquiry")

        # Test general chat
        self.assertEqual(detect_intent("hello there"), "general_chat")
        self.assertIsNone(detect_intent("random message"))
        safe_print("[PASS] Intent detection test passed")


# ==================== TEST 5: WEBHOOK STATE MACHINE ====================

class TestWebhookStateMachine(unittest.IsolatedAsyncioTestCase):
    """Test the conversation state machine in webhook"""

    async def asyncSetUp(self):
        """Set up test fixtures"""
        from app.api.webhook import handle_conversation_flow
        self.handle_flow = handle_conversation_flow

        # Mock database service
        self.mock_db = MagicMock()
        self.mock_db.list_all_specialties.return_value = [
            ("Cardiology",), ("Pediatrics",), ("Neurology",)
        ]
        self.mock_db.find_doctors_by_specialty.return_value = [
            Mock(id=1, name="Dr. Sarah Smith", consultation_fee=500),
            Mock(id=2, name="Dr. John Doe", consultation_fee=600)
        ]
        self.mock_db.create_appointment.return_value = Mock(id=123)

    async def test_start_state_to_specialty(self):
        """Test transition from START to SELECT_SPECIALTY"""
        session = {"state": "START", "context": {}, "history": []}

        response = await self.handle_flow("I want to book", "", session, self.mock_db, 1)

        self.assertEqual(session["state"], "SELECT_SPECIALTY")
        self.assertIn("specialty", response.lower())
        self.assertIn("Cardiology", response)
        safe_print("[PASS] State transition: START -> SELECT_SPECIALTY test passed")

    async def test_specialty_to_doctor(self):
        """Test transition from SELECT_SPECIALTY to SELECT_DOCTOR"""
        session = {"state": "SELECT_SPECIALTY", "context": {}, "history": []}

        response = await self.handle_flow("Cardiology", "", session, self.mock_db, 1)

        self.assertEqual(session["state"], "SELECT_DOCTOR")
        self.assertEqual(session["context"]["specialty"], "Cardiology")
        self.assertIn("Dr. Sarah Smith", response)
        safe_print("[PASS] State transition: SELECT_SPECIALTY -> SELECT_DOCTOR test passed")

    async def test_doctor_to_date(self):
        """Test transition from SELECT_DOCTOR to SELECT_DATE"""
        session = {
            "state": "SELECT_DOCTOR",
            "context": {
                "specialty": "Cardiology",
                "doctors": [
                    {"id": 1, "name": "Dr. Sarah Smith", "fee": 500},
                    {"id": 2, "name": "Dr. John Doe", "fee": 600}
                ]
            },
            "history": []
        }

        response = await self.handle_flow("Dr. Sarah Smith", "", session, self.mock_db, 1)

        self.assertEqual(session["state"], "SELECT_DATE")
        self.assertEqual(session["context"]["doctor_id"], 1)
        self.assertIn("date", response.lower())
        safe_print("[PASS] State transition: SELECT_DOCTOR -> SELECT_DATE test passed")

    async def test_date_to_confirm(self):
        """Test transition from SELECT_DATE to CONFIRM"""
        session = {
            "state": "SELECT_DATE",
            "context": {
                "specialty": "Cardiology",
                "doctor_id": 1,
                "doctor_name": "Dr. Sarah Smith",
                "fee": 500
            },
            "history": []
        }

        response = await self.handle_flow("Tomorrow at 2 PM", "", session, self.mock_db, 1)

        self.assertEqual(session["state"], "CONFIRM")
        self.assertEqual(session["context"]["appointment_time"], "Tomorrow at 2 PM")
        self.assertIn("confirm", response.lower())
        self.assertIn("500", response)
        safe_print("[PASS] State transition: SELECT_DATE -> CONFIRM test passed")

    async def test_confirm_to_booked(self):
        """Test final booking transition"""
        session = {
            "state": "CONFIRM",
            "context": {
                "specialty": "Cardiology",
                "doctor_id": 1,
                "doctor_name": "Dr. Sarah Smith",
                "fee": 500,
                "appointment_time": "Tomorrow at 2 PM"
            },
            "history": []
        }

        response = await self.handle_flow("CONFIRM", "", session, self.mock_db, 1)

        self.assertEqual(session["state"], "START")  # Reset after booking
        self.assertEqual(session["context"], {})  # Cleared
        self.assertIn("appointment confirmed", response.lower())
        self.assertIn("#123", response)
        safe_print("[PASS] State transition: CONFIRM -> BOOKED test passed")

    async def test_reset_command(self):
        """Test reset/cancel functionality"""
        session = {
            "state": "SELECT_DOCTOR",
            "context": {"specialty": "Cardiology"},
            "history": []
        }

        response = await self.handle_flow("cancel", "", session, self.mock_db, 1)

        self.assertEqual(session["state"], "START")
        self.assertEqual(session["context"], {})
        self.assertIn("reset", response.lower())
        safe_print("[PASS] Reset command test passed")

    async def test_general_chat_in_start(self):
        """Test general conversation in START state"""
        session = {"state": "START", "context": {}, "history": []}
        ai_response = "Hello! How can I help you today?"

        response = await self.handle_flow("Hello", ai_response, session, self.mock_db, 1)

        # Should return AI response, not trigger booking
        self.assertEqual(response, ai_response)
        self.assertEqual(session["state"], "START")  # Unchanged
        safe_print("[PASS] General chat in START state test passed")

    async def test_human_handoff(self):
        """Test human agent handoff trigger"""
        session = {"state": "START", "context": {}, "history": []}

        response = await self.handle_flow("I need a human agent", "", session, self.mock_db, 1)

        self.assertIn("human", response.lower())
        self.assertIn("staff", response.lower())
        safe_print("[PASS] Human handoff test passed")


# ==================== TEST 6: INTEGRATION FLOW ====================

class TestFullIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests for complete booking flow"""

    async def test_complete_booking_flow(self):
        """Test entire booking flow from start to finish"""
        from app.api.webhook import handle_conversation_flow

        # Setup mock database
        mock_db = MagicMock()
        mock_db.list_all_specialties.return_value = [("Cardiology",)]
        mock_db.find_doctors_by_specialty.return_value = [
            Mock(id=1, name="Dr. Test", consultation_fee=500)
        ]
        mock_db.create_appointment.return_value = Mock(id=999)

        session = {"state": "START", "context": {}, "history": []}
        user_id = 1

        # Step 1: Initial booking request
        response = await handle_conversation_flow("Book appointment", "", session, mock_db, user_id)
        self.assertEqual(session["state"], "SELECT_SPECIALTY")

        # Step 2: Select specialty
        response = await handle_conversation_flow("Cardiology", "", session, mock_db, user_id)
        self.assertEqual(session["state"], "SELECT_DOCTOR")

        # Step 3: Select doctor
        response = await handle_conversation_flow("Dr. Test", "", session, mock_db, user_id)
        self.assertEqual(session["state"], "SELECT_DATE")

        # Step 4: Provide date
        response = await handle_conversation_flow("Tomorrow 2pm", "", session, mock_db, user_id)
        self.assertEqual(session["state"], "CONFIRM")

        # Step 5: Confirm
        response = await handle_conversation_flow("CONFIRM", "", session, mock_db, user_id)
        self.assertEqual(session["state"], "START")  # Reset
        self.assertIn("#999", response)

        safe_print("[PASS] Complete booking flow integration test passed")


# ==================== RUN TESTS ====================

if __name__ == "__main__":
    # Run all tests with verbose output
    unittest.main(verbosity=2)
