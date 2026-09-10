"""
Test script to trace through the WhatsApp booking flow
"""
import sys
sys.path.insert(0, '.')

def test_booking_flow():
    """Simulate the booking flow step by step"""

    # Simulate session storage
    session = {"state": "START", "context": {}, "history": []}
    phone = "+1234567890"

    test_messages = [
        ("Hi", "START"),
        ("Book Appointment", "SELECT_SPECIALTY"),
        ("ENT", "SELECT_DOCTOR"),
        ("1", "SELECT_DATE"),
        ("Tomorrow 2pm", "CONFIRM"),
        ("CONFIRM", "START"),
    ]

    print("=" * 60)
    print("TESTING BOOKING FLOW")
    print("=" * 60)

    for msg, expected_next_state in test_messages:
        print(f"\n📱 User sends: '{msg}'")
        print(f"   Current state: {session.get('state', 'START')}")

        # Simulate state machine logic (simplified)
        current_state = session.get("state", "START")
        message_lower = msg.lower().strip()

        if current_state == "START":
            if any(word in message_lower for word in ["1", "book", "appointment", "doctor", "schedule"]):
                print("   ✓ Matched booking intent")
                session["state"] = "SELECT_SPECIALTY"
                print("   → Shows specialty list")
            elif message_lower in ["hi", "hello"]:
                print("   ✓ Matched greeting")
                print("   → Shows main menu")
            else:
                print(f"   ⚠ No match for: {message_lower}")

        elif current_state == "SELECT_SPECIALTY":
            # Simulate matching specialty
            specialty_names = ["Cardiology", "ENT", "Pediatrics", "General"]
            selected = None
            for spec in specialty_names:
                if spec.lower() == message_lower or message_lower == str(specialty_names.index(spec) + 1):
                    selected = spec
                    break

            if selected:
                print(f"   ✓ Matched specialty: {selected}")
                session["state"] = "SELECT_DOCTOR"
                session["context"]["specialty"] = selected
                print("   → Shows doctor list")
            else:
                print(f"   ⚠ Could not match specialty: {message_lower}")

        elif current_state == "SELECT_DOCTOR":
            # Simulate selecting doctor by number
            if message.isdigit():
                print(f"   ✓ Selected doctor #{message}")
                session["state"] = "SELECT_DATE"
                session["context"]["doctor_name"] = f"Dr. Test {message}"
                print("   → Asks for date/time")
            else:
                print(f"   ⚠ Invalid doctor selection: {message}")

        elif current_state == "SELECT_DATE":
            print(f"   ✓ Got date/time: {msg}")
            session["state"] = "CONFIRM"
            session["context"]["appointment_time"] = msg
            print("   → Shows confirmation")

        elif current_state == "CONFIRM":
            if "confirm" in message_lower:
                print("   ✓ Confirmed booking")
                session["state"] = "START"
                session["context"] = {}
                print("   → Booking created!")
            else:
                print("   → Booking cancelled")
                session["state"] = "START"

        print(f"   Next state: {session.get('state', 'START')}")

        # Verify state transition
        if session.get("state") == expected_next_state:
            print(f"   ✅ State transition correct")
        else:
            print(f"   ❌ State mismatch! Expected: {expected_next_state}, Got: {session.get('state')}")

    print("\n" + "=" * 60)
    print("FLOW TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_booking_flow()
