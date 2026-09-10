"""
Manual Conversation Test Script
==============================

This script simulates the exact WhatsApp conversation flow
that a patient would experience. Use this to verify the flow works.

Before running:
1. Start the server: uvicorn app.main:app --reload
2. Make sure you have doctors added to the database
3. Run this script to test the flow
"""

import requests
import json

BASE_URL = "http://localhost:8000"
WEBHOOK_URL = f"{BASE_URL}/whatsapp/"

# Test phone number
TEST_PHONE = "whatsapp:+911234567890"


def send_message(body, from_number=TEST_PHONE):
    """Simulate sending a WhatsApp message"""
    try:
        response = requests.post(
            WEBHOOK_URL,
            data={"From": from_number, "Body": body},
            timeout=10
        )
        if response.status_code == 200:
            # Extract message content from TwiML response
            content = response.text
            # Parse the Message content from TwiML
            if "<Message>" in content:
                message = content.split("<Message>")[1].split("</Message>")[0]
                return message.strip()
            return content
        else:
            return f"ERROR: {response.status_code}"
    except Exception as e:
        return f"ERROR: {str(e)}"


def run_conversation_scenario_1():
    """
    SCENARIO 1: Complete Booking Flow
    ================================
    A typical patient booking experience
    """
    print("\n" + "="*70)
    print(" SCENARIO 1: Complete Booking Flow")
    print("="*70)
    print("\nThis simulates a patient booking an ENT appointment\n")

    conversation = [
        ("Hi", "👋 Greeting"),
        ("1", "📋 Select 'Book Appointment'"),
        ("ENT", "👂 Select ENT specialty"),
        ("1", "👨‍⚕️ Select first doctor"),
        ("Tomorrow 2pm", "📅 Provide date/time"),
        ("CONFIRM", "✅ Confirm booking"),
    ]

    for message, description in conversation:
        input(f"\n⏳ Press ENTER to send: '{message}' ({description})")
        response = send_message(message)
        print(f"\n📱 Patient: {message}")
        print(f"🤖 Bot:\n{response}")
        print("-" * 70)


def run_conversation_scenario_2():
    """
    SCENARIO 2: Direct Specialty Input
    ==================================
    Patient types specialty directly without selecting 'Book'
    """
    print("\n" + "="*70)
    print(" SCENARIO 2: Direct Specialty Input")
    print("="*70)
    print("\nPatient types 'Cardiology' directly from main menu\n")

    # Use different phone for clean session
    test_phone = "whatsapp:+911234567891"

    conversation = [
        ("Hello", "👋 Greeting"),
        ("Cardiology", "❤️ Direct specialty input"),
    ]

    for message, description in conversation:
        input(f"\n⏳ Press ENTER to send: '{message}' ({description})")
        response = send_message(message, test_phone)
        print(f"\n📱 Patient: {message}")
        print(f"🤖 Bot:\n{response}")
        print("-" * 70)


def run_conversation_scenario_3():
    """
    SCENARIO 3: Reset During Booking
    ================================
    Patient starts booking then resets
    """
    print("\n" + "="*70)
    print(" SCENARIO 3: Reset During Booking")
    print("="*70)

    test_phone = "whatsapp:+911234567892"

    conversation = [
        ("Hi", "👋 Greeting"),
        ("1", "📋 Start booking"),
        ("ENT", "👂 Select specialty"),
        ("reset", "🔄 Reset the flow"),
    ]

    for message, description in conversation:
        input(f"\n⏳ Press ENTER to send: '{message}' ({description})")
        response = send_message(message, test_phone)
        print(f"\n📱 Patient: {message}")
        print(f"🤖 Bot:\n{response}")
        print("-" * 70)


def run_conversation_scenario_4():
    """
    SCENARIO 4: Cancel at Confirmation
    ==================================
    Patient reaches confirmation but cancels
    """
    print("\n" + "="*70)
    print(" SCENARIO 4: Cancel at Confirmation")
    print("="*70)

    test_phone = "whatsapp:+911234567893"

    conversation = [
        ("Hi", "👋 Greeting"),
        ("book", "📋 Start booking"),
        ("Pediatrics", "👶 Select Pediatrics"),
        ("1", "👨‍⚕️ Select doctor"),
        ("Tomorrow 10am", "📅 Provide date/time"),
        ("no", "❌ Cancel booking"),
    ]

    for message, description in conversation:
        input(f"\n⏳ Press ENTER to send: '{message}' ({description})")
        response = send_message(message, test_phone)
        print(f"\n📱 Patient: {message}")
        print(f"🤖 Bot:\n{response}")
        print("-" * 70)


def run_conversation_scenario_5():
    """
    SCENARIO 5: Menu Navigation
    ===========================
    Patient navigates using menu options
    """
    print("\n" + "="*70)
    print(" SCENARIO 5: Menu Navigation")
    print("="*70)

    test_phone = "whatsapp:+911234567894"

    conversation = [
        ("Hi", "👋 Greeting"),
        ("3", "ℹ️ Hospital Information"),
        ("menu", "📋 Back to menu"),
        ("2", "👨‍⚕️ View Doctors"),
        ("menu", "📋 Back to menu"),
        ("4", "🚨 Emergency Info"),
    ]

    for message, description in conversation:
        input(f"\n⏳ Press ENTER to send: '{message}' ({description})")
        response = send_message(message, test_phone)
        print(f"\n📱 Patient: {message}")
        print(f"🤖 Bot:\n{response[:200]}...")  # Truncate long responses
        print("-" * 70)


def check_server():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False


def add_sample_doctors():
    """Add sample doctors if needed"""
    print("\n📋 Checking/Adding sample doctors...")

    doctors = [
        {
            "name": "Dr. Sarah Johnson",
            "specialty": "ENT",
            "experience_years": "10",
            "consultation_fee": "500.00",
            "availability_slots": "9-12,14-17"
        },
        {
            "name": "Dr. Raj Patel",
            "specialty": "ENT",
            "experience_years": "8",
            "consultation_fee": "450.00",
            "availability_slots": "10-13,16-19"
        },
        {
            "name": "Dr. Michael Chen",
            "specialty": "Cardiology",
            "experience_years": "15",
            "consultation_fee": "800.00",
            "availability_slots": "9-12,15-18"
        },
        {
            "name": "Dr. Emily Davis",
            "specialty": "Pediatrics",
            "experience_years": "12",
            "consultation_fee": "600.00",
            "availability_slots": "9-17"
        },
    ]

    for doc in doctors:
        try:
            response = requests.post(
                f"{BASE_URL}/admin/add-doctor",
                data=doc,
                timeout=5
            )
            if response.status_code in [200, 307]:
                print(f"  ✅ {doc['name']} ({doc['specialty']})")
        except Exception as e:
            print(f"  ⚠️  Could not add {doc['name']}: {e}")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║           🏥 HOSPITAL CHATBOT - MANUAL TEST SCRIPT                   ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  This script will guide you through testing the WhatsApp             ║
║  conversation flow step by step.                                     ║
║                                                                      ║
║  Make sure:                                                          ║
║  1. Server is running: uvicorn app.main:app --reload                ║
║  2. You have doctors added to the database                          ║
║  3. ngrok is running (for real WhatsApp testing)                    ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
""")

    # Check server
    if not check_server():
        print("\n❌ ERROR: Server is not running!")
        print("   Start it with: uvicorn app.main:app --reload")
        exit(1)

    print("\n✅ Server is running")

    # Add sample doctors
    add_sample_doctors()

    # Menu
    while True:
        print("""

📋 TEST SCENARIOS:
==================
1. Complete Booking Flow (ENT appointment)
2. Direct Specialty Input (Cardiology from menu)
3. Reset During Booking
4. Cancel at Confirmation
5. Menu Navigation
6. Run ALL scenarios
0. Exit
""")

        choice = input("Select scenario (0-6): ").strip()

        if choice == "1":
            run_conversation_scenario_1()
        elif choice == "2":
            run_conversation_scenario_2()
        elif choice == "3":
            run_conversation_scenario_3()
        elif choice == "4":
            run_conversation_scenario_4()
        elif choice == "5":
            run_conversation_scenario_5()
        elif choice == "6":
            run_conversation_scenario_1()
            run_conversation_scenario_2()
            run_conversation_scenario_3()
            run_conversation_scenario_4()
            run_conversation_scenario_5()
            print("\n✅ All scenarios completed!")
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice")
