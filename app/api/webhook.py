from fastapi import APIRouter, Form, Response, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.ai import ai_service
from app.core.session import session_manager
from app.core.db_service import HospitalDBService
from app.db.session import get_db
from app.db.models import Doctor
import json

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

@router.post("/")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Main WhatsApp webhook endpoint.
    Handles conversation state, AI responses, and appointment booking.
    """
    print(f"📱 Incoming message from {From}: {Body}")

    # Initialize services
    db_service = HospitalDBService(db)

    # Get or create user session
    session = session_manager.get_session(From)
    user = db_service.get_or_create_user(From)

    # Get AI response with full context
    ai_response = await ai_service.get_response(
        user_message=Body,
        session_data=session,
        db_service=db_service
    )

    # Handle conversation states for booking flow
    response_text = await handle_conversation_flow(
        Body, ai_response, session, db_service, user.id
    )

    # Update session history
    session["history"].append({"role": "user", "content": Body})
    session["history"].append({"role": "assistant", "content": response_text[:500]})  # Limit length
    session_manager.update_session(From, session)

    # Check if response is already TwiML (from menu functions)
    if response_text.strip().startswith("<?xml"):
        return Response(content=response_text, media_type="application/xml")

    # Otherwise, wrap in TwiML
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Message>{response_text}</Message>
    </Response>
    """

    return Response(content=twiml_response, media_type="application/xml")


def get_main_menu_twiml():
    """Returns TwiML for interactive main menu with buttons"""
    return """<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Message>
🏥 *Welcome to MedCare Hospital!*

How can we help you today?

*Reply with a number:*
1️⃣ Book an Appointment
2️⃣ View Doctors & Specialties
3️⃣ Hospital Information
4️⃣ Emergency Contact
5️⃣ Talk to Reception

_Type "menu" anytime to see options_
        </Message>
    </Response>"""


def get_specialties_list_twiml(specialties: list) -> str:
    """Returns formatted list of specialties"""
    specialty_emojis = {
        "Cardiology": "❤️",
        "Pediatrics": "👶",
        "Neurology": "🧠",
        "Orthopedics": "🦴",
        "Dermatology": "🩹",
        "ENT": "👂",
        "General": "🏥"
    }

    text = "🏥 *Available Specialties*\n\n"
    for i, (spec,) in enumerate(specialties, 1):
        emoji = specialty_emojis.get(spec, "🏥")
        text += f"{i}. {emoji} {spec}\n"

    text += "\n_Reply with the specialty name or number_"

    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Message>{text}</Message>
    </Response>"""


async def handle_conversation_flow(message: str, ai_response: str, session: dict, db_service, user_id: int):
    """
    Manages the conversation state machine for booking appointments.
    States: START → SELECT_SPECIALTY → SELECT_DOCTOR → SELECT_DATE → CONFIRM → BOOKED
    """
    message_lower = message.lower().strip()
    current_state = session.get("state", "START")
    context = session.get("context", {})

    # Handle "reset" or "start over" commands
    if any(word in message_lower for word in ["reset", "start over"]):
        session["state"] = "START"
        session["context"] = {}
        return get_main_menu_twiml()

    # Handle menu command
    if message_lower in ["menu", "help", "options", "start"]:
        return get_main_menu_twiml()

    # Handle greetings - show main menu
    if message_lower in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "namaste"]:
        return get_main_menu_twiml()

    # Handle human handoff
    if any(word in message_lower for word in ["agent", "human", "staff", "reception", "talk to someone"]):
        return """<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Message>👨‍⚕️ *Connecting you to our reception*

📞 Call us: +91 630 202 1700
⏰ Working hours: 9 AM - 6 PM

Our staff will assist you shortly!</Message>
    </Response>"""

    # Handle menu selections
    if current_state == "START":
        # Menu option 1: Book Appointment
        if any(word in message_lower for word in ["1", "book", "appointment", "doctor", "schedule"]):
            specialties = db_service.list_all_specialties()
            return get_specialties_list_twiml(specialties)

        # Menu option 2: View Doctors
        elif any(word in message_lower for word in ["2", "view doctor", "specialties", "departments"]):
            doctors = db_service.db.query(Doctor).filter(Doctor.is_available == True).all()
            text = "👨‍⚕️ *Our Doctors*\n\n"
            for doc in doctors[:5]:  # Show first 5
                text += f"• *{doc.name}*\n  {doc.specialty}\n  Fee: ₹{doc.consultation_fee}\n\n"
            text += "_Reply with doctor name to book_"

            return f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Message>{text}</Message>
    </Response>"""

        # Menu option 3: Hospital Info
        elif any(word in message_lower for word in ["3", "information", "info", "hospital", "about", "address", "location"]):
            return """<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Message>🏥 *MedCare Hospital*

📍 Address: 123 Health Street, City
⏰ Visiting Hours: 9 AM - 9 PM
📞 Reception: +91 630 202 1700
🌐 www.medcarehospital.com

*Available Services:*
• 24/7 Emergency
• Outpatient Services
• Pharmacy
• Laboratory
• Radiology

_Type "menu" to see options_</Message>
    </Response>"""

        # Menu option 4: Emergency
        elif any(word in message_lower for word in ["4", "emergency", "ambulance", "urgent"]):
            return """<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Message>🚨 *EMERGENCY CONTACTS*

📞 Hospital Emergency: 108
📞 Ambulance: 102
📞 Police: 100
📞 Fire: 101

⚠️ For life-threatening emergencies, call 108 immediately!

Our 24/7 Emergency Department is always open._</Message>
    </Response>"""

        # Menu option 5: Reception
        elif any(word in message_lower for word in ["5", "reception", "call", "phone", "contact"]):
            return """<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Message>📞 *Contact Reception*

☎️ Phone: +91 630 202 1700
📧 Email: reception@medcare.com

⏰ Working Hours:
Monday - Saturday: 9 AM - 6 PM
Sunday: 10 AM - 2 PM

_Type "menu" to see all options_</Message>
    </Response>"""

        # If they type a specialty directly, go to SELECT_DOCTOR state
        else:
            # Check if message matches a specialty
            specialties = db_service.list_all_specialties()
            specialty_names = [s[0].lower() for s in specialties]

            if message_lower in specialty_names:
                session["state"] = "SELECT_SPECIALTY"
                # Continue to specialty handling below
            else:
                # General chat response
                return ai_response

    elif current_state == "SELECT_SPECIALTY":
        # User selected a specialty - try to match by name or check if number
        specialties = db_service.list_all_specialties()
        specialty_names = [s[0] for s in specialties]

        selected_specialty = None

        # Try to match by name (case insensitive)
        for spec in specialty_names:
            if spec.lower() == message_lower or spec.lower() in message_lower:
                selected_specialty = spec
                break

        # If not found, try to parse as number
        if not selected_specialty and message.isdigit():
            idx = int(message) - 1
            if 0 <= idx < len(specialty_names):
                selected_specialty = specialty_names[idx]

        if selected_specialty:
            doctors = db_service.find_doctors_by_specialty(selected_specialty)
            if doctors:
                context["specialty"] = selected_specialty
                context["doctors"] = [{"id": d.id, "name": d.name, "fee": d.consultation_fee} for d in doctors]
                session["context"] = context
                session["state"] = "SELECT_DOCTOR"

                doctor_list = "\n".join([f"{i+1}. {d.name} (Fee: ₹{d.consultation_fee})" for i, d in enumerate(doctors)])
                return f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Message>👨‍⚕️ *Available {selected_specialty} doctors:*

{doctor_list}

_Please reply with the doctor's number (1, 2, etc.)_</Message>
    </Response>"""
            else:
                return f"❌ No doctors available for {selected_specialty}. Please try another specialty."
        else:
            return f"❌ No doctors found for '{message}'. Please check the spelling or type 'menu' to start over."

    elif current_state == "SELECT_DOCTOR":
        # User selected a doctor
        selected_doctor = None
        for doc in context.get("doctors", []):
            if message_lower in doc["name"].lower() or message == str(context["doctors"].index(doc) + 1):
                selected_doctor = doc
                break

        if selected_doctor:
            context["doctor_id"] = selected_doctor["id"]
            context["doctor_name"] = selected_doctor["name"]
            context["fee"] = selected_doctor["fee"]
            session["context"] = context
            session["state"] = "SELECT_DATE"
            return f"📅 You selected **{selected_doctor['name']}**.\n\nPlease provide your preferred date and time (e.g., 'Tomorrow at 2 PM' or '2026-09-15 14:00')."
        else:
            return "❌ Doctor not found. Please reply with the exact name or number from the list."

    elif current_state == "SELECT_DATE":
        # User provided date/time - show confirmation
        context["appointment_time"] = message
        session["context"] = context
        session["state"] = "CONFIRM"

        return f"📝 **Please confirm your appointment:**\n\n👨‍⚕️ Doctor: {context['doctor_name']}\n🏥 Specialty: {context['specialty']}\n📅 Date/Time: {message}\n💰 Fee: ₹{context['fee']}\n\nReply **CONFIRM** to book or **CHANGE** to modify."

    elif current_state == "CONFIRM":
        if "confirm" in message_lower:
            # Create the appointment
            try:
                from datetime import datetime, timedelta

                # Parse date (simplified - in production use proper date parsing)
                if "tomorrow" in context["appointment_time"].lower():
                    appt_date = datetime.now() + timedelta(days=1)
                else:
                    # Try to parse the date string
                    try:
                        appt_date = datetime.strptime(context["appointment_time"], "%Y-%m-%d %H:%M")
                    except:
                        appt_date = datetime.now() + timedelta(days=1)

                appointment = db_service.create_appointment(
                    user_id=user_id,
                    doctor_id=context["doctor_id"],
                    date_time=appt_date
                )

                session["state"] = "START"
                session["context"] = {}

                return f"✅ **Appointment Confirmed!**\n\n📋 Appointment ID: #{appointment.id}\n👨‍⚕️ Dr. {context['doctor_name']}\n📅 {context['appointment_time']}\n💰 Fee: ₹{context['fee']}\n\nPlease arrive 15 minutes early. Type 'book' for another appointment."
            except Exception as e:
                print(f"Booking error: {e}")
                return "❌ Sorry, there was an error booking your appointment. Please try again or type 'agent' for help."
        else:
            session["state"] = "START"
            session["context"] = {}
            return "🔄 Booking cancelled. How else can I help you?"

    # Default: return AI response
    return ai_response
