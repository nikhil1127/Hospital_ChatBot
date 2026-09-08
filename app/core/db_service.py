from sqlalchemy.orm import Session
from app.db.models import User, Doctor, Appointment
from datetime import datetime
from typing import List, Optional

class HospitalDBService:
    """
    Service layer for all database operations.
    Provides clean interface between the bot and PostgreSQL.
    """

    def __init__(self, db: Session):
        self.db = db

    # ============== USER OPERATIONS ==============

    def get_or_create_user(self, phone_number: str, name: str = None) -> User:
        """
        Get existing user by phone number or create a new one.
        Phone number is used as unique identifier (WhatsApp ID).
        """
        user = self.db.query(User).filter(User.phone_number == phone_number).first()
        if not user:
            user = User(phone_number=phone_number, name=name)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            print(f"✅ New user created: {phone_number}")
        return user

    def get_user_by_phone(self, phone_number: str) -> Optional[User]:
        """Get user by phone number."""
        return self.db.query(User).filter(User.phone_number == phone_number).first()

    def update_user_name(self, user_id: int, name: str) -> User:
        """Update user's name."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.name = name
            self.db.commit()
            self.db.refresh(user)
        return user

    # ============== DOCTOR OPERATIONS ==============

    def find_doctors_by_specialty(self, specialty: str) -> List[Doctor]:
        """
        Find available doctors by specialty (case-insensitive).
        """
        return self.db.query(Doctor).filter(
            Doctor.specialty.ilike(f"%{specialty}%"),
            Doctor.is_available == True
        ).all()

    def get_doctor_by_id(self, doctor_id: int) -> Optional[Doctor]:
        """Get doctor details by ID."""
        return self.db.query(Doctor).filter(Doctor.id == doctor_id).first()

    def get_doctor_details(self, doctor_id: int) -> Optional[Doctor]:
        """Alias for get_doctor_by_id."""
        return self.get_doctor_by_id(doctor_id)

    def list_all_specialties(self) -> List:
        """
        Return list of all unique specialties available in the hospital.
        """
        return self.db.query(Doctor.specialty).distinct().all()

    def list_all_doctors(self) -> List[Doctor]:
        """Return all doctors in the system."""
        return self.db.query(Doctor).all()

    def get_doctor_availability(self, doctor_id: int) -> str:
        """
        Get doctor's availability slots.
        """
        doctor = self.get_doctor_by_id(doctor_id)
        return doctor.availability_slots if doctor else "Not available"

    # ============== APPOINTMENT OPERATIONS ==============

    def create_appointment(self, user_id: int, doctor_id: int, date_time: datetime, status: str = "confirmed") -> Appointment:
        """
        Create a new appointment.
        """
        appointment = Appointment(
            user_id=user_id,
            doctor_id=doctor_id,
            appointment_date=date_time,
            status=status
        )
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        print(f"✅ Appointment created: #{appointment.id} for user {user_id}")
        return appointment

    def get_user_appointments(self, user_id: int) -> List[Appointment]:
        """
        Get all appointments for a user.
        """
        return self.db.query(Appointment).filter(
            Appointment.user_id == user_id
        ).order_by(Appointment.appointment_date.desc()).all()

    def get_appointment_by_id(self, appointment_id: int) -> Optional[Appointment]:
        """Get appointment details by ID."""
        return self.db.query(Appointment).filter(Appointment.id == appointment_id).first()

    def cancel_appointment(self, appointment_id: int) -> bool:
        """
        Cancel an appointment by ID.
        """
        appointment = self.get_appointment_by_id(appointment_id)
        if appointment:
            appointment.status = "cancelled"
            self.db.commit()
            return True
        return False

    def get_doctor_appointments(self, doctor_id: int, date: datetime = None) -> List[Appointment]:
        """
        Get appointments for a specific doctor.
        Optional: filter by date.
        """
        query = self.db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status.in_(["confirmed", "pending"])
        )
        if date:
            query = query.filter(
                Appointment.appointment_date >= date,
                Appointment.appointment_date < date.replace(hour=23, minute=59)
            )
        return query.all()

    def check_slot_availability(self, doctor_id: int, date_time: datetime) -> bool:
        """
        Check if a time slot is available for a doctor.
        """
        existing = self.db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == date_time,
            Appointment.status.in_(["confirmed", "pending"])
        ).first()
        return existing is None

    # ============== STATISTICS ==============

    def get_today_appointments_count(self) -> int:
        """Get count of today's appointments."""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today.replace(day=today.day + 1)
        return self.db.query(Appointment).filter(
            Appointment.appointment_date >= today,
            Appointment.appointment_date < tomorrow,
            Appointment.status == "confirmed"
        ).count()

    def get_department_stats(self) -> dict:
        """Get appointment counts by department."""
        from sqlalchemy import func
        stats = self.db.query(
            Doctor.specialty,
            func.count(Appointment.id)
        ).join(Appointment).filter(
            Appointment.status == "confirmed"
        ).group_by(Doctor.specialty).all()
        return {specialty: count for specialty, count in stats}
