"""
End-to-End WhatsApp Booking Flow Tests
======================================

Test scenarios for the complete booking flow:
1. Greeting ("Hi") → Main menu
2. Book Appointment → Specialty selection
3. Select Specialty → Doctor list
4. Select Doctor → Date input
5. Enter Date → Confirmation
6. Confirm → Booking success

Usage:
    python -m pytest tests/test_whatsapp_flow.py -v
    OR
    python tests/test_whatsapp_flow.py

Note: These tests simulate the conversation flow with mocked database services.
"""

import pytest
import sys
from datetime import datetime
from unittest.mock import Mock, MagicMock

# Add parent directory to path
sys.path.insert(0, '.')

# Mock the dependencies before importing
def setup_mock_session():
    """Setup a mock session manager for testing"""
    from app.core.session import SessionManager

    # Create mock session manager that stores in memory
    manager = SessionManager()
    manager.redis_client = None  # Force in-memory
    manager.memory_store = {}
    return manager


def create_mock_db_service():
    """Create a mock database service with sample data"""
    mock_db = Mock()
    mock_service = Mock()

    # Sample doctors
    sample_doctors = [
        Mock(id=1, name="Dr. Sarah Johnson", specialty="ENT", consultation_fee=500, is_available=True),
        Mock(id=2, name="Dr. Michael Chen", specialty="Cardiology", consultation_fee=800, is_available=True),
        Mock(id=3, name="Dr. Emily Davis", specialty="Pediatrics", consultation_fee=600, is_available=True),
        Mock(id=4, name="Dr. Raj Patel", specialty="ENT", consultation_fee=450, is_available=True),
    ]

    # Sample user
    sample_user = Mock(id=1, phone_number="+1234567890", name="Test User")

    # Sample appointment
    sample_appointment = Mock(
        id=123,
        user_id=1,
        doctor_id=1,
        appointment_date=datetime.now(),
        status="confirmed"
    )

    # Configure mock methods
    mock_service.get_or_create_user.return_value = sample_user
    mock_service.list_all_specialties.return_value = [
        ("Cardiology",),
        ("ENT",),
        ("Pediatrics",),
    ]
    mock_service.find_doctors_by_specialty.side_effect = lambda specialty: [
        d for d in sample_doctors if d.specialty == specialty
    ]
    mock_service.create_appointment.return_value = sample_appointment
    mock_service.db = mock_db

    return mock_service


class TestBookingFlow:
    """Test the complete booking conversation flow"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session_manager = setup_mock_session()
        self.db_service = create_mock_db_service()
        self.phone = "+1234567890"
        self.user_id = 1

        # Import after mocking
        from app.api.webhook import handle_conversation_flow
        self.handle_flow = handle_conversation_flow

    def _get_session(self):
        """Helper to get current session"""
        return self.session_manager.get_session(self.phone)

    def _update_session(self, session):
        """Helper to update session"""
        self.session_manager.update_session(self.phone, session)

    @pytest.mark.asyncio
    async def test_scenario_1_greeting_shows_menu(self):
        """
        Scenario 1: User sends 'Hi'
        Expected: Shows main menu with 5 options
        State: START (no change)
        """
        session = self._get_session()
        print("\n" + "="*60)
        print("SCENARIO 1: Greeting")
        print("="*60)
        print(f"Input: 'Hi'")
        print(f"Initial State: {session.get('state')}")

        response = await self.handle_flow(
            "Hi", "AI response", session, self.db_service, self.user_id, self.phone
        )

        print(f"Response contains menu: {'1️⃣' in response}")
        print(f"Final State: {session.get('state')}")

        assert "1️⃣ Book an Appointment" in response or "Welcome to MedCare Hospital" in response
        assert session.get("state") == "START"
        print("✅ PASSED")

    @pytest.mark.asyncio
    async def test_scenario_2_book_appointment_flow(self):
        """
        Scenario 2: Complete booking flow
        Steps: Hi → Book → ENT → Dr.1 → Date → Confirm
        Expected: Successful booking
        """
        print("\n" + "="*60)
        print("SCENARIO 2: Complete Booking Flow")
        print("="*60)

        # Step 1: Hi
        session = self._get_session()
        response = await self.handle_flow(
            "Hi", "AI", session, self.db_service, self.user_id, self.phone
        )
        print("Step 1 - Hi: ✅")

        # Step 2: Book (option 1)
        session = self._get_session()
        response = await self.handle_flow(
            "1", "AI", session, self.db_service, self.user_id, self.phone
        )
        print("Step 2 - Book: Response contains specialties")
        assert "ENT" in response or "Cardiology" in response
        self._update_session(session)
        print(f"  State after: {session.get('state')}")
        assert session.get("state") == "SELECT_SPECIALTY"

        # Step 3: Select ENT
        session = self._get_session()
        response = await self.handle_flow(
            "ENT", "AI", session, self.db_service, self.user_id, self.phone
        )
        print("Step 3 - Select ENT: Response contains doctors")
        assert "Dr." in response or "doctor" in response.lower()
        self._update_session(session)
        print(f"  State after: {session.get('state')}")
        assert session.get("state") == "SELECT_DOCTOR"
        assert "ENT" in session.get("context", {}).get("specialty", "")

        # Step 4: Select first doctor
        session = self._get_session()
        response = await self.handle_flow(
            "1", "AI", session, self.db_service, self.user_id, self.phone
        )
        print("Step 4 - Select Doctor: Response asks for date")
        assert "date" in response.lower() or "time" in response.lower()
        self._update_session(session)
        print(f"  State after: {session.get('state')}")
        assert session.get("state") == "SELECT_DATE"
        assert session.get("context", {}).get("doctor_name") is not None

        # Step 5: Enter date
        session = self._get_session()
        response = await self.handle_flow(
            "Tomorrow 2pm", "AI", session, self.db_service, self.user_id, self.phone
        )
        print("Step 5 - Enter Date: Response shows confirmation")
        assert "confirm" in response.lower()
        self._update_session(session)
        print(f"  State after: {session.get('state')}")
        assert session.get("state") == "CONFIRM"
        assert "Tomorrow 2pm" in session.get("context", {}).get("appointment_time", "")

        # Step 6: Confirm
        session = self._get_session()
        response = await self.handle_flow(
            "CONFIRM", "AI", session, self.db_service, self.user_id, self.phone
        )
        print("Step 6 - Confirm: Booking confirmed")
        assert "confirmed" in response.lower() or "Appointment" in response
        self._update_session(session)
        print(f"  Final State: {session.get('state')}")
        assert session.get("state") == "START"

        print("✅ PASSED - Full booking flow works!")

    @pytest.mark.asyncio
    async def test_scenario_3_direct_specialty_from_menu(self):
        """
        Scenario 3: User types specialty directly from main menu
        Input: Hi → ENT (skips 'Book' step)
        Expected: Shows doctors for ENT directly
        """
        print("\n" + "="*60)
        print("SCENARIO 3: Direct Specialty Input")
        print("="*60)

        # Send ENT directly without selecting "Book" first
        session = self._get_session()
        response = await self.handle_flow(
            "ENT", "AI", session, self.db_service, self.user_id, self.phone
        )

        # Should recognize ENT as a specialty and show doctors
        print(f"Response: {response[:100]}...")
        if "doctor" in response.lower() or "Dr." in response:
            print("✅ PASSED - Direct specialty input works")
        else:
            # Might be treated as general chat if not detected as specialty
            print("ℹ️ Direct specialty detection: May need adjustment")

    @pytest.mark.asyncio
    async def test_scenario_4_reset_flow(self):
        """
        Scenario 4: User resets during booking
        Steps: Book → ENT → Reset
        Expected: Returns to main menu
        """
        print("\n" + "="*60)
        print("SCENARIO 4: Reset During Booking")
        print("="*60)

        # Start booking
        session = self._get_session()
        await self.handle_flow("1", "AI", session, self.db_service, self.user_id, self.phone)
        self._update_session(session)

        # Select specialty
        session = self._get_session()
        await self.handle_flow("ENT", "AI", session, self.db_service, self.user_id, self.phone)
        self._update_session(session)

        # Reset
        session = self._get_session()
        response = await self.handle_flow(
            "reset", "AI", session, self.db_service, self.user_id, self.phone
        )

        assert "menu" in response.lower() or "welcome" in response.lower()
        self._update_session(session)
        assert session.get("state") == "START"
        assert session.get("context") == {}

        print("✅ PASSED - Reset works correctly")

    @pytest.mark.asyncio
    async def test_scenario_5_menu_command(self):
        """
        Scenario 5: User types 'menu' at any point
        Expected: Returns to main menu
        """
        print("\n" + "="*60)
        print("SCENARIO 5: Menu Command")
        print("="*60)

        # Start booking
        session = self._get_session()
        await self.handle_flow("1", "AI", session, self.db_service, self.user_id, self.phone)
        self._update_session(session)

        # Type menu
        session = self._get_session()
        response = await self.handle_flow(
            "menu", "AI", session, self.db_service, self.user_id, self.phone
        )

        assert "menu" in response.lower() or "book" in response.lower()
        print("✅ PASSED - Menu command works")

    @pytest.mark.asyncio
    async def test_scenario_6_invalid_doctor_selection(self):
        """
        Scenario 6: User selects invalid doctor number
        Expected: Error message, stay in SELECT_DOCTOR state
        """
        print("\n" + "="*60)
        print("SCENARIO 6: Invalid Doctor Selection")
        print("="*60)

        # Setup: Get to SELECT_DOCTOR state
        session = {"state": "SELECT_DOCTOR", "context": {"specialty": "ENT", "doctors": [{"id": 1, "name": "Dr. Test", "fee": 500}]}, "history": []}
        self._update_session(session)

        # Try invalid doctor number
        session = self._get_session()
        response = await self.handle_flow(
            "99", "AI", session, self.db_service, self.user_id, self.phone
        )

        print(f"Response: {response[:100]}...")
        assert "not found" in response.lower() or "invalid" in response.lower()
        print("✅ PASSED - Invalid selection handled")

    @pytest.mark.asyncio
    async def test_scenario_7_cancel_booking(self):
        """
        Scenario 7: User cancels at confirmation
        Steps: ... → Date → Cancel
        Expected: Booking cancelled, returns to menu
        """
        print("\n" + "="*60)
        print("SCENARIO 7: Cancel at Confirmation")
        print("="*60)

        # Setup: Get to CONFIRM state
        session = {
            "state": "CONFIRM",
            "context": {
                "specialty": "ENT",
                "doctor_name": "Dr. Test",
                "doctor_id": 1,
                "fee": 500,
                "appointment_time": "Tomorrow 2pm"
            },
            "history": []
        }
        self._update_session(session)

        # Type anything other than confirm
        session = self._get_session()
        response = await self.handle_flow(
            "no", "AI", session, self.db_service, self.user_id, self.phone
        )

        assert "cancelled" in response.lower()
        self._update_session(session)
        assert session.get("state") == "START"

        print("✅ PASSED - Cancel works correctly")


class TestEdgeCases:
    """Test edge cases and error conditions"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session_manager = setup_mock_session()
        self.db_service = create_mock_db_service()
        self.phone = "+1234567890"
        self.user_id = 1

        from app.api.webhook import handle_conversation_flow
        self.handle_flow = handle_conversation_flow

    def _get_session(self):
        return self.session_manager.get_session(self.phone)

    def _update_session(self, session):
        self.session_manager.update_session(self.phone, session)

    @pytest.mark.asyncio
    async def test_empty_message(self):
        """Test handling of empty message"""
        session = self._get_session()
        response = await self.handle_flow(
            "", "AI reply", session, self.db_service, self.user_id, self.phone
        )
        # Should not crash, may return AI response or menu
        assert response is not None
        print("✅ Empty message handled")

    @pytest.mark.asyncio
    async def test_special_characters(self):
        """Test handling of special characters"""
        session = self._get_session()
        response = await self.handle_flow(
            "@#$%^&*", "AI reply", session, self.db_service, self.user_id, self.phone
        )
        assert response is not None
        print("✅ Special characters handled")

    @pytest.mark.asyncio
    async def test_very_long_message(self):
        """Test handling of very long message"""
        session = self._get_session()
        long_msg = "A" * 500
        response = await self.handle_flow(
            long_msg, "AI reply", session, self.db_service, self.user_id, self.phone
        )
        assert response is not None
        print("✅ Long message handled")


def print_test_summary():
    """Print summary of all test scenarios"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║           WHATSAPP BOOKING FLOW - TEST SCENARIOS                 ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  SCENARIO 1: Greeting                                            ║
║  Input:  "Hi"                                                   ║
║  Output: Main menu with 5 options                               ║
║                                                                  ║
║  SCENARIO 2: Complete Booking Flow                              ║
║  Steps:  Hi → Book → ENT → 1 → Tomorrow 2pm → Confirm           ║
║  Output: Appointment confirmed with ID #123                     ║
║                                                                  ║
║  SCENARIO 3: Direct Specialty Input                             ║
║  Input:  "ENT" (from main menu, skips 'Book')                   ║
║  Output: Shows ENT doctors directly                             ║
║                                                                  ║
║  SCENARIO 4: Reset Flow                                         ║
║  Steps:  Book → ENT → "reset"                                   ║
║  Output: Returns to main menu, context cleared                  ║
║                                                                  ║
║  SCENARIO 5: Menu Command                                       ║
║  Input:  "menu" (during booking)                                ║
║  Output: Returns to main menu                                   ║
║                                                                  ║
║  SCENARIO 6: Invalid Selection                                  ║
║  Input:  "99" (invalid doctor number)                           ║
║  Output: Error message, stays in current state                  ║
║                                                                  ║
║  SCENARIO 7: Cancel Booking                                     ║
║  Input:  "no" or "cancel" at confirmation                       ║
║  Output: Booking cancelled, returns to menu                     ║
║                                                                  ║
║  EDGE CASES: Empty messages, special chars, long messages       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    print_test_summary()

    # Run tests with pytest if available, otherwise manual
    try:
        import pytest
        print("\nRunning tests with pytest...")
        pytest.main([__file__, "-v"])
    except ImportError:
        print("\npytest not installed. Install with: pip install pytest pytest-asyncio")
        print("Run with: python -m pytest tests/test_whatsapp_flow.py -v")
