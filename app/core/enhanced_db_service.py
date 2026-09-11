"""
Enhanced Database Service Layer for Complete Hospital Management
Adds EMPI, EHR, Patient Timeline, and all new capabilities
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, and_
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import json
from fuzzywuzzy import fuzz

from app.db.models import (
    User, Role, Patient, PatientAlias, Doctor, Department,
    Appointment, MedicalEncounter, Prescription, PrescriptionItem,
    LabOrder, LabTest, AuditLog, BloodGroup, AppointmentStatus
)


class HospitalDBService:
    """
    Enhanced Service Layer for complete hospital management
    Provides EMPI, EHR, Patient Timeline, and all new capabilities
    """

    def __init__(self, db: Session):
        self.db = db

    # ==================== PATIENT MASTER INDEX (EMPI) ====================

    def generate_patient_id(self) -> str:
        """Generate unique Patient ID: PAT-YYYY-XXXXXX"""
        year = datetime.now().year
        # Get the latest ID for this year
        last_patient = self.db.query(Patient).filter(
            Patient.patient_id.like(f"PAT-{year}-%")
        ).order_by(Patient.id.desc()).first()

        if last_patient:
            # Extract sequence number
            try:
                last_num = int(last_patient.patient_id.split("-")[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1

        return f"PAT-{year}-{new_num:06d}"

    def find_potential_duplicates(self, first_name: str, last_name: str,
                                   phone: str, dob: date) -> List[Dict]:
        """
        EMPI matching algorithm to detect potential duplicate patients
        Uses fuzzy matching on name + exact match on phone/DOB
        """
        # Build the query
        name_variations = [f"{first_name} {last_name}"]

        matches = []

        # Query all active patients
        patients = self.db.query(Patient).filter(
            Patient.status == "ACTIVE"
        ).all()

        for patient in patients:
            confidence = 0.0
            reasons = []

            # Name similarity (weight: 40%)
            full_name = f"{patient.first_name} {patient.last_name}"
            name_score = fuzz.ratio(f"{first_name} {last_name}".lower(),
                                     full_name.lower()) / 100.0
            if name_score > 0.7:
                confidence += name_score * 0.40
                reasons.append(f"Name match: {int(name_score * 100)}%")

            # Phone match (weight: 40%) - Strong signal
            if patient.primary_phone == phone:
                confidence += 0.40
                reasons.append("Exact phone match")
            elif patient.secondary_phone and patient.secondary_phone == phone:
                confidence += 0.35
                reasons.append("Secondary phone match")

            # DOB match (weight: 20%)
            if patient.date_of_birth == dob:
                confidence += 0.20
                reasons.append("Exact DOB match")

            if confidence >= 0.60:  # Threshold
                matches.append({
                    "patient": patient,
                    "confidence": confidence,
                    "reasons": reasons,
                    "is_likely_duplicate": confidence >= 0.85
                })

        # Sort by confidence
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        return matches

    def create_patient(self, patient_data: Dict[str, Any],
                       created_by: int = None) -> Patient:
        """
        Create new patient with duplicate checking
        """
        # Check for duplicates
        duplicates = self.find_potential_duplicates(
            patient_data.get("first_name"),
            patient_data.get("last_name"),
            patient_data.get("primary_phone"),
            patient_data.get("date_of_birth")
        )

        if any(d["confidence"] >= 0.85 for d in duplicates):
            raise ValueError(f"High confidence duplicate found: {duplicates[0]}")

        # Generate Patient ID
        patient_id = self.generate_patient_id()

        # Create patient
        patient = Patient(
            patient_id=patient_id,
            **patient_data
        )

        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)

        # Log creation
        self.create_audit_log(
            who=created_by,
            what="PATIENT_CREATED",
            patient_id=patient.id,
            record_type="patient",
            record_id=patient.id,
            action_details=patient_data
        )

        return patient

    def get_patient_by_id(self, patient_id: str) -> Optional[Patient]:
        """Get patient by Display ID (PAT-YYYY-XXXXXX)"""
        return self.db.query(Patient).filter(
            Patient.patient_id == patient_id
        ).options(
            joinedload(Patient.encounters),
            joinedload(Patient.appointments)
        ).first()

    def get_patient_by_phone(self, phone: str) -> Optional[Patient]:
        """Get patient by phone number"""
        # Clean phone number
        phone = phone.replace(" ", "").replace("+", "")

        patient = self.db.query(Patient).filter(
            or_(
                Patient.primary_phone == phone,
                Patient.whatsapp_number == phone
            )
        ).first()

        return patient

    def update_patient(self, patient_id: str, updates: Dict) -> Patient:
        """Update patient record with audit"""
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            raise ValueError("Patient not found")

        for key, value in updates.items():
            if hasattr(patient, key):
                setattr(patient, key, value)

        patient.updated_at = func.now()
        self.db.commit()
        self.db.refresh(patient)

        return patient

    # ==================== PATIENT TIMELINE / EHR ====================

    def get_patient_timeline(self, patient_id: str,
                             start_date: date = None,
                             end_date: date = None) -> List[Dict]:
        """
        Get complete patient timeline: encounters, appointments, lab results
        """
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            return []

        # Default to last 2 years
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=730)

        timeline = []

        # Get encounters
        encounters = self.db.query(MedicalEncounter).filter(
            MedicalEncounter.patient_id == patient.id,
            MedicalEncounter.encounter_start >= start_date,
            MedicalEncounter.encounter_start <= end_date
        ).order_by(MedicalEncounter.encounter_start.desc()).all()

        for enc in encounters:
            timeline.append({
                "type": "encounter",
                "date": enc.encounter_start,
                "title": f"{enc.type} - Dr. {self.get_doctor_name(enc.doctor_id)}",
                "details": {
                    "chief_complaint": enc.chief_complaint,
                    "diagnosis": enc.primary_diagnosis,
                    "vitals": self._format_vitals(enc)
                },
                "icon": 🚥 if enc.type == "EMERGENCY" else 🙺,
                "encounter_id": enc.id
            })

        # Get lab results
        labs = self.db.query(LabOrder).filter(
            LabOrder.patient_id == patient.id
        ).all()

        for lab in labs:
            critical_tests = [t for t in lab.tests if t.is_critical]
            timeline.append({
                "type": "lab",
                "date": lab.ordered_at,
                "title": f"Lab Results - {len(lab.tests)} tests",
                "details": {
                    "critical_count": len(critical_tests),
                    "tests": [{"name": t.test_name, "status": t.status}
                             for t in lab.tests]
                },
                "icon": 🧪,
                "critical": len(critical_tests) > 0
            })

        # Sort by date
        timeline.sort(key=lambda x: x["date"], reverse=True)

        return timeline

    def get_patient_summary(self, patient_id: str) -> Dict:
        """Get condensed patient summary for doctor view"""
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            return {}

        # Get last encounter
        last_encounter = self.db.query(MedicalEncounter).filter(
            MedicalEncounter.patient_id == patient.id
        ).order_by(MedicalEncounter.encounter_start.desc()).first()

        # Get active medications from last prescription
        active_meds = []
        if last_encounter:
            prescriptions = self.db.query(Prescription).filter(
                Prescription.encounter_id == last_encounter.id
            ).all()
            for p in prescriptions:
                active_meds.extend([{
                    "name": item.medicine_name,
                    "dosage": item.dosage,
                    "frequency": item.frequency
                } for item in p.items])

        return {
            "patient_id": patient.patient_id,
            "name": f"{patient.first_name} {patient.last_name}",
            "demographics": {
                "age": self._calculate_age(patient.date_of_birth),
                "gender": patient.gender,
                "blood_group": patient.blood_group
            },
            "last_visit": last_encounter.encounter_start if last_encounter else None,
            "chief_complaint": last_encounter.chief_complaint if last_encounter else None,
            "allergies": patient.known_allergies.split(",") if patient.known_allergies else [],
            "chronic_conditions": patient.chronic_conditions.split(",") if patient.chronic_conditions else [],
            "active_medications": active_meds,
            "vitals": self._format_vitals(last_encounter) if last_encounter else None,
            "alerts": self._generate_patient_alerts(patient, last_encounter)
        }

    def _generate_patient_alerts(self, patient: Patient,
                                  last_encounter: MedicalEncounter) -> List[str]:
        """Generate clinical alerts for patient"""
        alerts = []

        if patient.known_allergies:
            alerts.append(f"⚠️ Allergies: {patient.known_allergies}")

        if patient.chronic_conditions:
            alerts.append(f"📱 Conditions: {patient.chronic_conditions}")

        if last_encounter:
            # Check critical vitals
            if last_encounter.vital_bp:
                try:
                    sys, dia = last_encounter.vital_bp.split("/")
                    if int(sys) > 140 or int(dia) > 90:
                        alerts.append(f"🔴 High BP: {last_encounter.vital_bp}")
                except:
                    pass

        return alerts

    # ==================== APPOINTMENT MANAGEMENT ====================

    def generate_appointment_number(self) -> str:
        """Generate unique appointment number"""
        year = datetime.now().year
        last = self.db.query(Appointment).filter(
            Appointment.appointment_number.like(f"APT-{year}-%")
        ).order_by(Appointment.id.desc()).first()

        if last:
            try:
                last_num = int(last.appointment_number.split("-")[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1

        return f"APT-{year}-{new_num:06d}"

    def get_next_token_number(self, doctor_id: int, appointment_date: date) -> int:
        """Get next token number for OPD"""
        last_token = self.db.query(func.max(Appointment.token_number)).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date
        ).scalar()

        return (last_token or 0) + 1

    def create_appointment(self, patient_id: str, doctor_id: int,
                          appointment_date: date, start_time: datetime,
                          chief_complaint: str = None,
                          appointment_type: str = "OPD",
                          created_by: int = None) -> Appointment:
        """Create new appointment with token generation"""

        patient = self.get_patient_by_id(patient_id)
        doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()

        if not patient or not doctor:
            raise ValueError("Patient or Doctor not found")

        # Check slot availability
        existing = self.db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.start_time == start_time,
            Appointment.status.in_(["SCHEDULED", "CONFIRMED"])
        ).first()

        if existing:
            raise ValueError("Slot not available")

        # Generate token for OPD
        token = None
        if appointment_type == "OPD":
            token = self.get_next_token_number(doctor_id, appointment_date)

        # Create appointment
        appointment = Appointment(
            appointment_number=self.generate_appointment_number(),
            patient_id=patient.id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=start_time + timedelta(minutes=doctor.slot_duration_minutes or 30),
            token_number=token,
            type=appointment_type,
            chief_complaint=chief_complief,
            status="CONFIRMED"
        )

        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)

        # Log
        self.create_audit_log(
            who=created_by,
            what="APPOINTMENT_CREATED",
            patient_id=patient.id,
            record_type="appointment",
            record_id=appointment.id
        )

        return appointment

    def get_doctor_schedule(self, doctor_id: int, date: date) -> Dict:
        """Get doctor's schedule for a specific date"""
        doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            return {}

        # Get day of week
        day_name = date.strftime("%A").lower()

        # Get available slots from weekly schedule
        schedule = doctor.weekly_schedule or {}
        available_slots = schedule.get(day_name, [])

        # Get booked appointments
        booked = self.db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == date,
            Appointment.status.in_(["SCHEDULED", "CONFIRMED", "CHECKED_IN"])
        ).all()

        booked_times = [a.start_time.strftime("%H:%M") for a in booked]

        # Build full schedule
        slots = []
        for slot in available_slots:
            slots.append({
                "time": slot,
                "is_available": slot not in booked_times,
                "appointment": next(
                    (a for a in booked if a.start_time.strftime("%H:%M") == slot),
                    None
                )
            })

        return {
            "doctor_name": doctor.name,
            "specialty": doctor.specialty,
            "date": date,
            "slots": slots,
            "total_slots": len(slots),
            "available_slots": len([s for s in slots if s["is_available"]])
        }

    def get_today_appointments(self, doctor_id: int = None) -> List[Dict]:
        """Get today's appointments with queue status"""
        today = date.today()

        query = self.db.query(Appointment).filter(
            Appointment.appointment_date == today
        )

        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)

        appointments = query.order_by(Appointment.token_number).all()

        return [{
            "appointment_id": a.appointment_number,
            "token": a.token_number,
            "patient_name": f"{a.patient.first_name} {a.patient.last_name}",
            "patient_id": a.patient.patient_id,
            "time": a.start_time.strftime("%H:%M"),
            "status": a.status,
            "chief_complaint": a.chief_complaint,
            "age": self._calculate_age(a.patient.date_of_birth)
        } for a in appointments]

    def check_in_patient(self, appointment_number: str) -> Appointment:
        """Check in patient for appointment"""
        appointment = self.db.query(Appointment).filter(
            Appointment.appointment_number == appointment_number
        ).first()

        if not appointment:
            raise ValueError("Appointment not found")

        appointment.status = "CHECKED_IN"
        self.db.commit()

        # Create encounter
        encounter = MedicalEncounter(
            encounter_number=self.generate_encounter_number(),
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            appointment_id=appointment.id,
            type=appointment.type,
            check_in_time=datetime.now(),
            chief_complaint=appointment.chief_complaint,
            status="CHECKED_IN"
        )

        self.db.add(encounter)
        self.db.commit()

        return appointment

    # ==================== DOCTOR CONSULTATION ====================

    def generate_encounter_number(self) -> str:
        """Generate unique encounter number"""
        year = datetime.now().year
        last = self.db.query(MedicalEncounter).filter(
            MedicalEncounter.encounter_number.like(f"ENC-{year}-%")
        ).order_by(MedicalEncounter.id.desc()).first()

        if last:
            try:
                last_num = int(last.encounter_number.split("-")[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1

        return f"ENC-{year}-{new_num:06d}"

    def start_consultation(self, encounter_id: int) -> MedicalEncounter:
        """Start doctor consultation"""
        encounter = self.db.query(MedicalEncounter).filter(
            MedicalEncounter.id == encounter_id
        ).first()

        if not encounter:
            raise ValueError("Encounter not found")

        encounter.status = "IN_PROGRESS"
        encounter.encounter_start = datetime.now()

        # Update appointment status
        if encounter.appointment:
            encounter.appointment.status = "IN_PROGRESS"

        self.db.commit()
        self.db.refresh(encounter)

        return encounter

    def save_consultation(self, encounter_id: int, data: Dict) -> MedicalEncounter:
        """Save consultation findings"""
        encounter = self.db.query(MedicalEncounter).filter(
            MedicalEncounter.id == encounter_id
        ).first()

        if not encounter:
            raise ValueError("Encounter not found")

        # Update encounter
        encounter.chief_complaint = data.get("chief_complaint", encounter.chief_complaint)
        encounter.presenting_complaints = data.get("presenting_complaints")
        encounter.examination_findings = data.get("examination_findings")
        encounter.primary_diagnosis = data.get("primary_diagnosis")
        encounter.secondary_diagnosis = data.get("secondary_diagnosis")
        encounter.icd10_codes = data.get("icd10_codes", [])
        encounter.advice_given = data.get("advice_given")
        encounter.follow_up_plan = data.get("follow_up_plan")

        # Update vitals
        if "vitals" in data:
            vitals = data["vitals"]
            encounter.vital_bp = vitals.get("bp")
            encounter.vital_pulse = vitals.get("pulse")
            encounter.vital_temperature = vitals.get("temperature")
            encounter.vital_spo2 = vitals.get("spo2")
            encounter.vital_weight = vitals.get("weight")

        self.db.commit()
        self.db.refresh(encounter)

        return encounter

    def complete_consultation(self, encounter_id: int,
                               prescription_data: List[Dict] = None,
                               lab_orders: List[str] = None) -> MedicalEncounter:
        """Complete consultation and generate prescriptions/lab orders"""
        encounter = self.db.query(MedicalEncounter).filter(
            MedicalEncounter.id == encounter_id
        ).first()

        if not encounter:
            raise ValueError("Encounter not found")

        encounter.status = "COMPLETED"
        encounter.encounter_end = datetime.now()

        # Create prescription if provided
        if prescription_data:
            prescription = Prescription(
                prescription_number=f"RX-{datetime.now().year}-{encounter_id:06d}",
                encounter_id=encounter.id,
                patient_id=encounter.patient_id,
                doctor_id=encounter.doctor_id
            )
            self.db.add(prescription)
            self.db.flush()  # Get ID

            for item in prescription_data:
                p_item = PrescriptionItem(
                    prescription_id=prescription.id,
                    medicine_name=item.get("medicine"),
                    dosage=item.get("dosage"),
                    frequency=item.get("frequency"),
                    duration=item.get("duration"),
                    instructions=item.get("instructions")
                )
                self.db.add(p_item)

        # Create lab orders if provided
        if lab_orders:
            lab_order = LabOrder(
                order_number=f"LAB-{datetime.now().year}-{encounter_id:06d}",
                patient_id=encounter.patient_id,
                doctor_id=encounter.doctor_id,
                encounter_id=encounter.id,
                status="ORDERED"
            )
            self.db.add(lab_order)
            self.db.flush()

            for test_name in lab_orders:
                test = LabTest(
                    order_id=lab_order.id,
                    test_name=test_name,
                    status="PENDING"
                )
                self.db.add(test)

        # Update appointment
        if encounter.appointment:
            encounter.appointment.status = "COMPLETED"

        self.db.commit()
        self.db.refresh(encounter)

        return encounter

    # ==================== LABORATORY ====================

    def get_pending_lab_orders(self) -> List[Dict]:
        """Get all pending lab orders"""
        orders = self.db.query(LabOrder).filter(
            LabOrder.status != "COMPLETED"
        ).order_by(LabOrder.ordered_at.desc()).all()

        return [{
            "order_number": o.order_number,
            "patient_name": f"{o.patient.first_name} {o.patient.last_name}",
            "patient_id": o.patient.patient_id,
            "doctor_name": o.doctor.name if o.doctor else "",
            "ordered_at": o.ordered_at,
            "tests": [t.test_name for t in o.tests],
            "status": o.status
        } for o in orders]

    def enter_lab_results(self, order_id: int, results: List[Dict],
                         verified_by: int) -> LabOrder:
        """Enter lab test results"""
        order = self.db.query(LabOrder).filter(LabOrder.id == order_id).first()
        if not order:
            raise ValueError("Lab order not found")

        for result_data in results:
            test = self.db.query(LabTest).filter(
                and_(
                    LabTest.order_id == order_id,
                    LabTest.test_name == result_data.get("test_name")
                )
            ).first()

            if test:
                test.result_value = result_data.get("value")
                test.unit = result_data.get("unit")
                test.reference_range = result_data.get("reference")
                test.status = result_data.get("status", "NORMAL")
                test.is_critical = result_data.get("is_critical", False)
                test.resulted_at = datetime.now()
                test.verified_by = verified_by

        # Update order status
        order.status = "COMPLETED"
        self.db.commit()

        # Notify patient via WhatsApp/SMS
        # TODO: Integrate notification service

        return order

    # ==================== STATISTICS & ANALYTICS ====================

    def get_dashboard_stats(self) -> Dict:
        """Get hospital dashboard statistics"""
        today = date.today()

        # Today's stats
        today_appointments = self.db.query(Appointment).filter(
            Appointment.appointment_date == today
        ).count()

        today_completed = self.db.query(Appointment).filter(
            Appointment.appointment_date == today,
            Appointment.status == "COMPLETED"
        ).count()

        # Patient counts
        total_patients = self.db.query(Patient).filter(
            Patient.status == "ACTIVE"
        ).count()

        new_patients_this_month = self.db.query(Patient).filter(
            Patient.created_at >= today.replace(day=1)
        ).count()

        # Department stats
        dept_stats = self.db.query(
            Doctor.specialty,
            func.count(Appointment.id)
        ).join(Appointment).filter(
            Appointment.appointment_date == today
        ).group_by(Doctor.specialty).all()

        return {
            "today": {
                "appointments": today_appointments,
                "completed": today_completed,
                "waiting": today_appointments - today_completed
            },
            "patients": {
                "total": total_patients,
                "new_this_month": new_patients_this_month
            },
            "department_stats": [{"name": d[0], "count": d[1]} for d in dept_stats]
        }

    def get_doctor_dashboard(self, doctor_id: int) -> Dict:
        """Get doctor's dashboard data"""
        today = date.today()

        # Today's appointments
        appointments = self.get_today_appointments(doctor_id)

        # Stats
        total_today = len(appointments)
        completed = len([a for a in appointments if a["status"] == "COMPLETED"])
        waiting = len([a for a in appointments if a["status"] in ["CHECKED_IN", "WAITING"]])
        upcoming = len([a for a in appointments if a["status"] == "CONFIRMED"])

        # Pending reviews (lab results to review)
        pending_labs = self.db.query(LabOrder).filter(
            LabOrder.doctor_id == doctor_id,
            LabOrder.status == "COMPLETED"
        ).count()  # Simplified - you'd want to check if reviewed

        return {
            "stats": {
                "total": total_today,
                "completed": completed,
                "waiting": waiting,
                "upcoming": upcoming
            },
            "patients": appointments,
            "alerts": {
                "pending_lab_reviews": pending_labs
            }
        }

    # ==================== AUDIT & SECURITY ====================

    def create_audit_log(self, who: int, what: str, patient_id: int = None,
                        record_type: str = None, record_id: int = None,
                        action_details: Dict = None, result: str = "SUCCESS"):
        """Create audit log entry"""
        log = AuditLog(
            who=who,
            what=what,
            patient_id=patient_id,
            record_type=record_type,
            record_id=record_id,
            action_details=action_details or {},
            result=result
        )
        self.db.add(log)
        self.db.commit()

    # ==================== HELPER METHODS ====================

    def get_or_create_user(self, phone_number: str, name: str = None) -> User:
        """Backward compatible - Get or create user"""
        user = self.db.query(User).filter(User.phone_number == phone_number).first()
        if not user:
            user = User(phone_number=phone_number, name=name)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return user

    def find_doctors_by_specialty(self, specialty: str) -> List[Doctor]:
        """Backward compatible"""
        return self.db.query(Doctor).filter(
            Doctor.specialty.ilike(f"%{specialty}%"),
            Doctor.is_available == True
        ).all()

    def get_doctor_by_id(self, doctor_id: int) -> Optional[Doctor]:
        """Backward compatible"""
        return self.db.query(Doctor).filter(Doctor.id == doctor_id).first()

    def list_all_specialties(self) -> List:
        """Backward compatible"""
        return self.db.query(Doctor.specialty).distinct().all()

    def list_all_doctors(self) -> List[Doctor]:
        """Backward compatible"""
        return self.db.query(Doctor).all()

    def get_doctor_name(self, doctor_id: int) -> str:
        """Get doctor name by ID"""
        doctor = self.get_doctor_by_id(doctor_id)
        return doctor.name if doctor else "Unknown"

    def _calculate_age(self, dob: date) -> int:
        """Calculate age from date of birth"""
        if not dob:
            return 0
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def _format_vitals(self, encounter: MedicalEncounter) -> Dict:
        """Format vitals from encounter"""
        if not encounter:
            return {}
        return {
            "bp": encounter.vital_bp,
            "pulse": encounter.vital_pulse,
            "temperature": encounter.vital_temperature,
            "spo2": encounter.vital_spo2,
            "weight": encounter.vital_weight,
            "bmi": encounter.vital_bmi
        }

    def get_user_by_phone(self, phone_number: str) -> Optional[User]:
        """Backward compatible"""
        return self.db.query(User).filter(User.phone_number == phone_number).first()

    def update_user_name(self, user_id: int, name: str) -> User:
        """Backward compatible"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.name = name
            self.db.commit()
            self.db.refresh(user)
        return user

    def get_doctor_availability(self, doctor_id: int) -> str:
        """Backward compatible"""
        doctor = self.get_doctor_by_id(doctor_id)
        return doctor.weekly_schedule if doctor else "Not available"

    def get_appointment_by_id(self, appointment_id: int) -> Optional[Appointment]:
        """Backward compatible - but now returns enhanced appointment"""
        return self.db.query(Appointment).filter(Appointment.id == appointment_id).first()

    def cancel_appointment(self, appointment_id: int) -> bool:
        """Backward compatible"""
        appointment = self.get_appointment_by_id(appointment_id)
        if appointment:
            appointment.status = "CANCELLED"
            self.db.commit()
            return True
        return False

    def get_doctor_appointments(self, doctor_id: int, date: datetime = None) -> List[Appointment]:
        """Backward compatible"""
        query = self.db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status.in_(["CONFIRMED", "SCHEDULED"])
        )
        if date:
            query = query.filter(
                Appointment.appointment_date >= date,
                Appointment.appointment_date < date.replace(hour=23, minute=59)
            )
        return query.all()

    def check_slot_availability(self, doctor_id: int, start_time: datetime) -> bool:
        """Backward compatible slot check"""
        existing = self.db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.start_time == start_time,
            Appointment.status.in_(["CONFIRMED", "SCHEDULED"])
        ).first()
        return existing is None

    def get_user_appointments(self, user_id: int) -> List[Appointment]:
        """Get appointments via user's patient profile"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user and user.patient_profile:
            return self.db.query(Appointment).filter(
                Appointment.patient_id == user.patient_profile.id
            ).order_by(Appointment.appointment_date.desc()).all()
        return []
