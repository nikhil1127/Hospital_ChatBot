from fastapi import APIRouter, Form, Response, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.ai import ai_service
from app.core.session import session_manager
from app.core.db_service import HospitalDBService
from app.db.session import get_db
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
    session["history"].append({"role": "assistant", "content": response_text})
    session_manager.update_session(From, session)

    # Twilio expects TwiML (XML) as a response
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Message>{response_text}</Message>
    </Response>
    """

    return Response(content=twiml_response, media_type="application/xml")


async def handle_conversation_flow(message: str, ai_response: str, session: dict, db_service, user_id: int):
    """
    Manages the conversation state machine for booking appointments.
    States: START → SELECT_SPECIALTY → SELECT_DOCTOR → SELECT_DATE → CONFIRM → BOOKED
    """
    message_lower = message.lower().strip()
    current_state = session.get("state", "START")
    context = session.get("context", {})

    # Handle "reset" or "start over" commands
    if any(word in message_lower for word in ["reset", "start over", "cancel"]):
        session["state"] = "START"
        session["context"] = {}
        return "🔄 Conversation reset. How can I help you today?"

    # Handle human handoff
    if any(word in message_lower for word in ["agent", "human", "staff", "help"]):
        return "👨‍⚕️ Connecting you to a human staff member. Please wait..."

    # STATE MACHINE: Booking Flow
    if current_state == "START":
        # Check if user wants to book
        if any(word in message_lower for word in ["book", "appointment", "doctor", "schedule"]):
            specialties = db_service.list_all_specialties()
            specialty_list = "\n".join([f"• {s[0]}" for s in specialties])
            session["state"] = "SELECT_SPECIALTY"
            return f"🏥 Which specialty do you need?\n\n{specialty_list}\n\nPlease type the specialty name."
        else:
            # General chat response from AI
            return ai_response

    elif current_state == "SELECT_SPECIALTY":
        # User selected a specialty
        doctors = db_service.find_doctors_by_specialty(message)
        if doctors:
            context["specialty"] = message
            context["doctors"] = [{"id": d.id, "name": d.name, "fee": d.consultation_fee} for d in doctors]
            session["context"] = context
            session["state"] = "SELECT_DOCTOR"

            doctor_list = "\n".join([f"{i+1}. {d.name} (Fee: ₹{d.consultation_fee})" for i, d in enumerate(doctors)])
            return f"👨‍⚕️ Available {message} doctors:\n\n{doctor_list}\n\nPlease reply with the doctor's name or number."
        else:
            return f"❌ No doctors found for '{message}'. Please check the spelling or type 'list' to see all specialties."

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
