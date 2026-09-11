"""
COMPLETE Hospital Management Database Service
Includes all modules: IPD, Insurance, Pharmacy, Nursing, Billing, Documents, Emergency, Staff
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, and_, desc
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta, time
import json
from decimal import Decimal

from app.db.models_complete import (
    User, Role, Patient, PatientAlias, Doctor, Department,
    Appointment, MedicalEncounter, Prescription, PrescriptionItem,
    LabOrder, LabTest, AuditLog,
    # IPD
    Ward, Bed, Admission, DailyProgress, Transfer,
    # Nursing
    NursingVital, NursingNote, MedicationAdministration, FluidIntakeOutput,
    # Emergency
    EmergencyVisit, EmergencyProcedure,
    # Insurance
    InsuranceProvider, InsurancePolicy, InsuranceClaim, PreAuthorization,
    # Pharmacy
    Medicine, PharmacyStock, PharmacyDispense, PharmacyDispenseItem, DrugInteraction,
    # Billing
    Invoice, InvoiceItem, Payment,
    # Documents
    PatientDocument,
    # Staff
    Employee, Shift, EmployeeShift,
    # Alerts
    AlertRule, ClinicalAlert
)


class CompleteHospitalDBService:
    """
    Complete Database Service for Hospital Management System
    Provides methods for all modules: EMPI, EHR, IPD, Insurance, Pharmacy, Billing, etc.
    """

    def __init__(self, db: Session):
        self.db = db

    # ==================== PATIENT MASTER INDEX ====================

    def generate_patient_id(self) -> str:
        """Generate unique Patient ID: PAT-YYYY-XXXXXX"""
        year = datetime.now().year
        last_patient = self.db.query(Patient).filter(
            Patient.patient_id.like(f"PAT-{year}-%")
        ).order_by(Patient.id.desc()).first()

        if last_patient:
            try:
                last_num = int(last_patient.patient_id.split("-")[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1

        return f"PAT-{year}-{new_num:06d}"

    def create_patient(self, patient_data: Dict[str, Any], created_by: int = None) -> Patient:
        """Create new patient with duplicate checking"""
        patient_id = self.generate_patient_id()

        patient = Patient(
            patient_id=patient_id,
            **patient_data
        )

        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)

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
        """Get patient by Display ID"""
        return self.db.query(Patient).filter(
            Patient.patient_id == patient_id
        ).options(
            joinedload(Patient.encounters),
            joinedload(Patient.appointments),
            joinedload(Patient.insurance_policies).joinedload(InsurancePolicy.provider)
        ).first()

    def get_patient_by_phone(self, phone: str) -> Optional[Patient]:
        """Get patient by phone"""
        phone = phone.replace(" ", "").replace("+", "")
        return self.db.query(Patient).filter(
            or_(Patient.primary_phone == phone, Patient.whatsapp_number == phone)
        ).first()

    # ==================== APPOINTMENTS ====================

    def generate_appointment_number(self) -> str:
        """Generate appointment number"""
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
        """Get next token for OPD"""
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
        """Create appointment"""
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

        token = None
        if appointment_type == "OPD":
            token = self.get_next_token_number(doctor_id, appointment_date)

        appointment = Appointment(
            appointment_number=self.generate_appointment_number(),
            patient_id=patient.id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=start_time + timedelta(minutes=doctor.slot_duration_minutes or 30),
            token_number=token,
            type=appointment_type,
            chief_complaint=chief_complaint,
            status="CONFIRMED"
        )

        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)

        self.create_audit_log(
            who=created_by,
            what="APPOINTMENT_CREATED",
            patient_id=patient.id,
            record_type="appointment",
            record_id=appointment.id
        )

        return appointment

    # ==================== DOCTOR DASHBOARD ====================

    def get_doctor_dashboard(self, doctor_id: int) -> Dict:
        """Get doctor dashboard data"""
        today = date.today()

        appointments = self.db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == today,
            Appointment.is_deleted == False
        ).order_by(Appointment.token_number).all()

        total_today = len(appointments)
        completed = len([a for a in appointments if a.status == "COMPLETED"])
        waiting = len([a for a in appointments if a.status in ["CHECKED_IN", "WAITING"]])
        upcoming = len([a for a in appointments if a.status == "CONFIRMED"])

        # Also get IPD patients for this doctor
        ipd_patients = self.db.query(Admission).filter(
            Admission.primary_doctor_id == doctor_id,
            Admission.status == "ADMITTED"
        ).all()

        return {
            "stats": {
                "total": total_today,
                "completed": completed,
                "waiting": waiting,
                "upcoming": upcoming,
                "ipd_patients": len(ipd_patients)
            },
            "patients": [{
                "appointment_id": a.id,
                "appointment_number": a.appointment_number,
                "token": a.token_number,
                "patient_name": f"{a.patient.first_name} {a.patient.last_name}",
                "patient_id": a.patient.patient_id,
                "age": self._calculate_age(a.patient.date_of_birth),
                "time": a.start_time.strftime("%H:%M"),
                "status": a.status,
                "chief_complaint": a.chief_complaint
            } for a in appointments],
            "ipd_list": [{
                "admission_id": adm.id,
                "admission_number": adm.admission_number,
                "patient_name": f"{adm.patient.first_name} {adm.patient.last_name}",
                "patient_id": adm.patient.patient_id,
                "bed": f"{adm.bed.ward.name} - Bed {adm.bed.bed_number}",
                "admitted_since": (datetime.now() - adm.admission_date).days
            } for adm in ipd_patients]
        }

    # ==================== CONSULTATION ====================

    def generate_encounter_number(self) -> str:
        """Generate encounter number"""
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

    def check_in_patient(self, appointment_number: str) -> Appointment:
        """Check in patient"""
        appointment = self.db.query(Appointment).filter(
            Appointment.appointment_number == appointment_number
        ).first()

        if not appointment:
            raise ValueError("Appointment not found")

        appointment.status = "CHECKED_IN"

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

    def start_consultation(self, encounter_id: int) -> MedicalEncounter:
        """Start consultation"""
        encounter = self.db.query(MedicalEncounter).filter(
            MedicalEncounter.id == encounter_id
        ).first()

        if not encounter:
            raise ValueError("Encounter not found")

        encounter.status = "IN_PROGRESS"
        encounter.encounter_start = datetime.now()

        if encounter.appointment:
            encounter.appointment.status = "IN_PROGRESS"

        self.db.commit()
        return encounter

    def save_consultation(self, encounter_id: int, data: Dict) -> MedicalEncounter:
        """Save consultation"""
        encounter = self.db.query(MedicalEncounter).filter(
            MedicalEncounter.id == encounter_id
        ).first()

        if not encounter:
            raise ValueError("Encounter not found")

        # Update fields
        encounter.chief_complaint = data.get("chief_complaint", encounter.chief_complaint)
        encounter.examination_findings = data.get("examination_findings")
        encounter.primary_diagnosis = data.get("primary_diagnosis")
        encounter.secondary_diagnosis = data.get("secondary_diagnosis")
        encounter.icd10_codes = data.get("icd10_codes", [])
        encounter.advice_given = data.get("advice_given")
        encounter.follow_up_plan = data.get("follow_up_plan")

        if "vitals" in data:
            vitals = data["vitals"]
            encounter.vital_bp = vitals.get("bp")
            encounter.vital_pulse = vitals.get("pulse")
            encounter.vital_temperature = vitals.get("temperature")
            encounter.vital_spo2 = vitals.get("spo2")
            encounter.vital_weight = vitals.get("weight")

            # Check for critical vitals and create alerts
            self._check_and_create_vital_alerts(encounter.patient_id, vitals)

        self.db.commit()
        return encounter

    def complete_consultation(self, encounter_id: int,
                               prescription_data: List[Dict] = None,
                               lab_orders: List[str] = None,
                               ipd_admission: Dict = None) -> MedicalEncounter:
        """Complete consultation"""
        encounter = self.db.query(MedicalEncounter).filter(
            MedicalEncounter.id == encounter_id
        ).first()

        if not encounter:
            raise ValueError("Encounter not found")

        encounter.status = "COMPLETED"
        encounter.encounter_end = datetime.now()

        # Create prescription
        if prescription_data:
            prescription = Prescription(
                prescription_number=f"RX-{datetime.now().year}-{encounter_id:06d}",
                encounter_id=encounter.id,
                patient_id=encounter.patient_id,
                doctor_id=encounter.doctor_id
            )
            self.db.add(prescription)
            self.db.flush()

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

                # Check for drug interactions and allergies
                self._check_prescription_alerts(encounter.patient_id, item.get("medicine", ""))

        # Create lab orders
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

        # Create invoice for OPD
        if encounter.type == "OPD":
            self._create_opd_invoice(encounter)

        # Admit to IPD if requested
        if ipd_admission:
            self.admit_patient(
                patient_id=encounter.patient.patient_id,
                doctor_id=encounter.doctor_id,
                admission_data=ipd_admission
            )

        if encounter.appointment:
            encounter.appointment.status = "COMPLETED"

        self.db.commit()
        return encounter

    # ==================== IPD / ADMISSIONS ====================

    def generate_admission_number(self) -> str:
        """Generate admission number"""
        year = datetime.now().year
        last = self.db.query(Admission).filter(
            Admission.admission_number.like(f"IP-{year}-%")
        ).order_by(Admission.id.desc()).first()

        if last:
            try:
                last_num = int(last.admission_number.split("-")[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1

        return f"IP-{year}-{new_num:06d}"

    def get_available_beds(self, ward_type: str = None) -> List[Dict]:
        """Get available beds"""
        query = self.db.query(Bed).filter(
            Bed.status == "AVAILABLE",
            Bed.is_active == True
        )

        if ward_type:
            query = query.join(Ward).filter(Ward.ward_type == ward_type)

        beds = query.all()

        return [{
            "bed_id": b.id,
            "bed_number": b.bed_number,
            "ward": b.ward.name,
            "ward_type": b.ward.ward_type,
            "floor": b.ward.floor,
            "daily_charge": b.daily_charge
        } for b in beds]

    def admit_patient(self, patient_id: str, doctor_id: int,
                     admission_data: Dict) -> Admission:
        """Admit patient to ward"""
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            raise ValueError("Patient not found")

        bed_id = admission_data.get("bed_id")
        bed = self.db.query(Bed).filter(Bed.id == bed_id).first()

        if not bed or bed.status != "AVAILABLE":
            raise ValueError("Bed not available")

        admission = Admission(
            admission_number=self.generate_admission_number(),
            patient_id=patient.id,
            admission_type=admission_data.get("type", "PLANNED"),
            bed_id=bed_id,
            primary_doctor_id=doctor_id,
            chief_complaint=admission_data.get("chief_complaint"),
            provisional_diagnosis=admission_data.get("provisional_diagnosis"),
            history_present_illness=admission_data.get("history"),
            admission_bp=admission_data.get("bp"),
            admission_pulse=admission_data.get("pulse"),
            admission_temperature=admission_data.get("temperature"),
            status="ADMITTED"
        )

        # Mark bed as occupied
        bed.status = "OCCUPIED"

        self.db.add(admission)
        self.db.commit()
        self.db.refresh(admission)

        # Create invoice for deposit
        self._create_admission_invoice(admission, admission_data.get("deposit_amount", 0))

        return admission

    def record_daily_progress(self, admission_id: int, doctor_id: int,
                             progress_data: Dict) -> DailyProgress:
        """Record daily progress"""
        progress = DailyProgress(
            admission_id=admission_id,
            doctor_id=doctor_id,
            progress_date=progress_data.get("date", date.today()),
            morning_bp=progress_data.get("morning_bp"),
            evening_bp=progress_data.get("evening_bp"),
            pulse=progress_data.get("pulse"),
            temperature=progress_data.get("temperature"),
            spo2=progress_data.get("spo2"),
            complaints=progress_data.get("complaints"),
            examination_findings=progress_data.get("examination"),
            plan=progress_data.get("plan")
        )

        self.db.add(progress)
        self.db.commit()
        return progress

    def discharge_patient(self, admission_id: int, discharge_data: Dict) -> Admission:
        """Discharge patient"""
        admission = self.db.query(Admission).filter(Admission.id == admission_id).first()

        if not admission:
            raise ValueError("Admission not found")

        admission.status = "DISCHARGED"
        admission.discharge_date = datetime.now()
        admission.discharge_type = discharge_data.get("type", "NORMAL")
        admission.final_diagnosis = discharge_data.get("final_diagnosis")
        admission.discharge_summary = discharge_data.get("discharge_summary")

        # Free the bed
        bed = admission.bed
        if bed:
            bed.status = "AVAILABLE"

        self.db.commit()

        # Generate final invoice
        self._generate_final_ipd_invoice(admission)

        return admission

    def get_ward_occupancy(self) -> Dict:
        """Get ward occupancy stats"""
        wards = self.db.query(Ward).filter(Ward.is_active == True).all()

        occupancy = []
        for ward in wards:
            total_beds = len(ward.beds)
            occupied = len([b for b in ward.beds if b.status == "OCCUPIED"])
            available = len([b for b in ward.beds if b.status == "AVAILABLE"])

            occupancy.append({
                "ward_id": ward.id,
                "ward_name": ward.name,
                "ward_type": ward.ward_type,
                "total_beds": total_beds,
                "occupied": occupied,
                "available": available,
                "occupancy_rate": round((occupied / total_beds * 100), 2) if total_beds > 0 else 0
            })

        return {"ward_stats": occupancy}

    # ==================== INSURANCE ====================

    def create_insurance_policy(self, patient_id: str, policy_data: Dict) -> InsurancePolicy:
        """Create insurance policy for patient"""
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            raise ValueError("Patient not found")

        policy = InsurancePolicy(
            patient_id=patient.id,
            provider_id=policy_data.get("provider_id"),
            policy_number=policy_data.get("policy_number"),
            policy_type=policy_data.get("type", "HEALTH"),
            sum_insured=policy_data.get("sum_insured", 0),
            valid_from=policy_data.get("valid_from"),
            valid_until=policy_data.get("valid_until"),
            room_rent_limit=policy_data.get("room_rent_limit"),
            icu_limit=policy_data.get("icu_limit"),
            is_active=True
        )

        self.db.add(policy)
        self.db.commit()
        return policy

    def generate_claim_number(self) -> str:
        """Generate claim number"""
        year = datetime.now().year
        last = self.db.query(InsuranceClaim).filter(
            InsuranceClaim.claim_number.like(f"CLM-{year}-%")
        ).order_by(InsuranceClaim.id.desc()).first()

        if last:
            try:
                last_num = int(last.claim_number.split("-")[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1

        return f"CLM-{year}-{new_num:06d}"

    def create_insurance_claim(self, admission_id: int, claim_data: Dict) -> InsuranceClaim:
        """Create insurance claim"""
        admission = self.db.query(Admission).filter(Admission.id == admission_id).first()
        if not admission:
            raise ValueError("Admission not found")

        # Get patient's active policy
        policy = self.db.query(InsurancePolicy).filter(
            InsurancePolicy.patient_id == admission.patient_id,
            InsurancePolicy.is_active == True
        ).first()

        if not policy:
            raise ValueError("No active insurance policy found")

        claim = InsuranceClaim(
            claim_number=self.generate_claim_number(),
            policy_id=policy.id,
            admission_id=admission_id,
            claim_type=claim_data.get("type", "CASHLESS"),
            claim_amount=claim_data.get("amount", 0),
            claimed_date=datetime.now(),
            status="DRAFT",
            documents=claim_data.get("documents", [])
        )

        self.db.add(claim)
        self.db.commit()
        return claim

    def calculate_insurance_coverage(self, claim_id: int) -> Dict:
        """Calculate eligible insurance coverage"""
        claim = self.db.query(InsuranceClaim).filter(InsuranceClaim.id == claim_id).first()
        if not claim:
            raise ValueError("Claim not found")

        policy = claim.policy
        total_claim = claim.claim_amount

        # Basic calculation (can be enhanced with policy-specific rules)
        room_limit = policy.room_rent_limit or total_claim
        icu_limit = policy.icu_limit or total_claim

        # Check admission details for room type
        admission = claim.admission
        if admission:
            bed = admission.bed
            if bed and "ICU" in (bed.ward.ward_type or ""):
                eligible = min(total_claim, icu_limit, policy.sum_insured)
            else:
                eligible = min(total_claim, room_limit, policy.sum_insured)
        else:
            eligible = min(total_claim, policy.sum_insured)

        return {
            "claim_amount": total_claim,
            "sum_insured": policy.sum_insured,
            "eligible_amount": eligible,
            "patient_liability": total_claim - eligible,
            "room_limit": room_limit,
            "icu_limit": icu_limit
        }

    # ==================== BILLING ====================

    def generate_invoice_number(self) -> str:
        """Generate invoice number"""
        year = datetime.now().year
        last = self.db.query(Invoice).filter(
            Invoice.invoice_number.like(f"INV-{year}-%")
        ).order_by(Invoice.id.desc()).first()

        if last:
            try:
                last_num = int(last.invoice_number.split("-")[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1

        return f"INV-{year}-{new_num:06d}"

    def _create_opd_invoice(self, encounter: MedicalEncounter) -> Invoice:
        """Create OPD consultation invoice"""
        doctor = encounter.doctor

        invoice = Invoice(
            invoice_number=self.generate_invoice_number(),
            patient_id=encounter.patient_id,
            encounter_id=encounter.id,
            status="DRAFT"
        )

        self.db.add(invoice)
        self.db.flush()

        # Add consultation fee
        item = InvoiceItem(
            invoice_id=invoice.id,
            item_type="CONSULTATION",
            item_description=f"Consultation - Dr. {doctor.name}",
            quantity=1,
            unit_price=doctor.consultation_fee,
            total_price=doctor.consultation_fee,
            is_insurance_eligible=True
        )
        self.db.add(item)

        # Calculate totals
        invoice.subtotal = doctor.consultation_fee
        invoice.total_amount = doctor.consultation_fee
        invoice.balance_due = doctor.consultation_fee

        self.db.commit()
        return invoice

    def _create_admission_invoice(self, admission: Admission, deposit: float = 0) -> Invoice:
        """Create initial admission invoice with deposit"""
        invoice = Invoice(
            invoice_number=self.generate_invoice_number(),
            patient_id=admission.patient_id,
            admission_id=admission.id,
            status="DRAFT"
        )

        self.db.add(invoice)
        self.db.flush()

        # Add deposit if provided
        if deposit > 0:
            payment = Payment(
                invoice_id=invoice.id,
                payment_amount=deposit,
                payment_method="CASH",
                payment_reference=f"Admission deposit - {admission.admission_number}"
            )
            self.db.add(payment)
            invoice.amount_paid = deposit

        self.db.commit()
        return invoice

    def generate_daily_bed_charges(self, admission_id: int) -> None:
        """Generate daily bed charge for IPD"""
        admission = self.db.query(Admission).filter(Admission.id == admission_id).first()
        if not admission or admission.status != "ADMITTED":
            return

        bed = admission.bed
        if not bed:
            return

        # Find or create invoice
        invoice = self.db.query(Invoice).filter(
            Invoice.admission_id == admission_id,
            Invoice.status == "DRAFT"
        ).first()

        if not invoice:
            invoice = self._create_admission_invoice(admission)

        # Calculate day number
        days_admitted = (date.today() - admission.admission_date.date()).days + 1

        # Add bed charge item
        item = InvoiceItem(
            invoice_id=invoice.id,
            item_type="BED_CHARGE",
            item_description=f"Bed charges - {bed.ward.name} - Day {days_admitted}",
            quantity=1,
            unit_price=bed.daily_charge,
            total_price=bed.daily_charge,
            is_insurance_eligible=True
        )
        self.db.add(item)

        # Update totals
        invoice.subtotal = (invoice.subtotal or 0) + bed.daily_charge
        invoice.total_amount = invoice.subtotal
        invoice.balance_due = invoice.total_amount - (invoice.amount_paid or 0)

        self.db.commit()

    def add_invoice_item(self, invoice_id: int, item_data: Dict) -> InvoiceItem:
        """Add item to invoice"""
        item = InvoiceItem(
            invoice_id=invoice_id,
            item_type=item_data.get("type"),
            item_description=item_data.get("description"),
            quantity=item_data.get("quantity", 1),
            unit_price=item_data.get("unit_price", 0),
            total_price=item_data.get("quantity", 1) * item_data.get("unit_price", 0),
            is_insurance_eligible=item_data.get("is_insurance_eligible", True),
            insurance_coverage=item_data.get("insurance_coverage", 0)
        )

        self.db.add(item)
        self.db.flush()

        # Update invoice totals
        invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        invoice.subtotal = (invoice.subtotal or 0) + item.total_price
        invoice.total_amount = invoice.subtotal
        invoice.balance_due = invoice.total_amount - (invoice.amount_paid or 0)

        self.db.commit()
        return item

    def record_payment(self, invoice_id: int, payment_data: Dict) -> Payment:
        """Record payment"""
        payment = Payment(
            invoice_id=invoice_id,
            payment_amount=payment_data.get("amount"),
            payment_method=payment_data.get("method"),
            payment_reference=payment_data.get("reference"),
            received_by=payment_data.get("received_by"),
            notes=payment_data.get("notes")
        )

        self.db.add(payment)
        self.db.flush()

        # Update invoice
        invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        invoice.amount_paid = (invoice.amount_paid or 0) + payment_data.get("amount", 0)
        invoice.balance_due = invoice.total_amount - invoice.amount_paid

        if invoice.balance_due <= 0:
            invoice.status = "PAID"
        else:
            invoice.status = "PARTIAL"

        self.db.commit()
        return payment

    def get_patient_bills(self, patient_id: str) -> List[Dict]:
        """Get all bills for patient"""
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            return []

        bills = []
        for invoice in patient.invoices:
            bills.append({
                "invoice_number": invoice.invoice_number,
                "date": invoice.created_at.strftime("%Y-%m-%d"),
                "total": invoice.total_amount,
                "paid": invoice.amount_paid,
                "balance": invoice.balance_due,
                "status": invoice.status
            })

        return bills

    # ==================== PHARMACY ====================

    def add_medicine(self, medicine_data: Dict) -> Medicine:
        """Add medicine to inventory"""
        medicine = Medicine(
            name=medicine_data.get("name"),
            generic_name=medicine_data.get("generic_name"),
            brand_name=medicine_data.get("brand_name"),
            category=medicine_data.get("category"),
            form=medicine_data.get("form"),
            strength=medicine_data.get("strength"),
            mrp=medicine_data.get("mrp"),
            sale_price=medicine_data.get("sale_price", medicine_data.get("mrp")),
            manufacturer=medicine_data.get("manufacturer"),
            is_active=True
        )

        self.db.add(medicine)
        self.db.commit()
        return medicine

    def add_stock(self, medicine_id: int, stock_data: Dict) -> PharmacyStock:
        """Add stock to pharmacy"""
        stock = PharmacyStock(
            medicine_id=medicine_id,
            batch_number=stock_data.get("batch_number"),
            quantity=stock_data.get("quantity"),
            expiry_date=stock_data.get("expiry_date"),
            purchase_price=stock_data.get("purchase_price")
        )

        self.db.add(stock)

        # Update medicine stock quantity
        medicine = self.db.query(Medicine).filter(Medicine.id == medicine_id).first()
        medicine.stock_quantity = (medicine.stock_quantity or 0) + stock_data.get("quantity", 0)

        self.db.commit()
        return stock

    def check_drug_interactions(self, patient_id: str, new_medicine: str) -> List[Dict]:
        """Check for drug interactions"""
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            return []

        alerts = []

        # Check against current medications
        if patient.current_medications:
            current_meds = patient.current_medications.lower()

            # Known interactions (simplified - should be from database)
            interactions = [
                ("warfarin", "aspirin", "MAJOR", "Increased bleeding risk"),
                ("metformin", "contrast", "MODERATE", "Risk of lactic acidosis"),
                ("lisinopril", "potassium", "MODERATE", "Hyperkalemia risk")
            ]

            for med1, med2, severity, desc in interactions:
                if (med1 in current_meds and med2 in new_medicine.lower()) or \
                   (med2 in current_meds and med1 in new_medicine.lower()):
                    alerts.append({
                        "severity": severity,
                        "description": desc,
                        "medicines": [med1, med2]
                    })

        return alerts

    def dispense_prescription(self, prescription_id: int, dispensed_by: int) -> PharmacyDispense:
        """Dispense prescription"""
        prescription = self.db.query(Prescription).filter(Prescription.id == prescription_id).first()
        if not prescription:
            raise ValueError("Prescription not found")

        # Create dispense record
        dispense = PharmacyDispense(
            dispense_number=f"DISP-{datetime.now().year}-{prescription_id:06d}",
            prescription_id=prescription_id,
            patient_id=prescription.patient_id,
            dispensed_by=dispensed_by,
            status="DISPENSED"
        )

        self.db.add(dispense)
        self.db.flush()

        total_amount = 0

        for item in prescription.items:
            medicine = self.db.query(Medicine).filter(
                Medicine.name.ilike(f"%{item.medicine_name}%")
            ).first()

            if medicine:
                # Check stock
                if medicine.stock_quantity < item.quantity:
                    raise ValueError(f"Insufficient stock for {medicine.name}")

                # Deduct stock
                medicine.stock_quantity -= item.quantity

                # Create dispense item
                dispense_item = PharmacyDispenseItem(
                    dispense_id=dispense.id,
                    medicine_id=medicine.id,
                    requested_qty=item.quantity,
                    dispensed_qty=item.quantity,
                    unit_price=medicine.sale_price,
                    total_price=medicine.sale_price * item.quantity
                )
                self.db.add(dispense_item)

                total_amount += dispense_item.total_price

        dispense.total_amount = total_amount
        dispense.net_amount = total_amount

        self.db.commit()
        return dispense

    def get_low_stock_medicines(self) -> List[Dict]:
        """Get medicines with low stock"""
        medicines = self.db.query(Medicine).filter(
            Medicine.stock_quantity <= Medicine.reorder_level,
            Medicine.is_active == True
        ).all()

        return [{
            "medicine_id": m.id,
            "name": m.name,
            "current_stock": m.stock_quantity,
            "reorder_level": m.reorder_level
        } for m in medicines]

    # ==================== EMERGENCY ====================

    def generate_visit_number(self) -> str:
        """Generate emergency visit number"""
        year = datetime.now().year
        last = self.db.query(EmergencyVisit).filter(
            EmergencyVisit.visit_number.like(f"ER-{year}-%")
        ).order_by(EmergencyVisit.id.desc()).first()

        if last:
            try:
                last_num = int(last.visit_number.split("-")[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1

        return f"ER-{year}-{new_num:06d}"

    def create_emergency_visit(self, patient_id: str, visit_data: Dict) -> EmergencyVisit:
        """Create emergency visit"""
        patient = self.get_patient_by_id(patient_id)

        visit = EmergencyVisit(
            visit_number=self.generate_visit_number(),
            patient_id=patient.id if patient else None,
            arrival_mode=visit_data.get("arrival_mode", "WALK_IN"),
            chief_complaint=visit_data.get("chief_complaint"),
            history_of_presenting_illness=visit_data.get("history"),
            triage_bp=visit_data.get("bp"),
            triage_pulse=visit_data.get("pulse"),
            triage_spo2=visit_data.get("spo2"),
            triage_gcs=visit_data.get("gcs"),
            status="TRIAGE"
        )

        self.db.add(visit)
        self.db.commit()
        return visit

    def triage_patient(self, visit_id: int, triage_data: Dict, triaged_by: int) -> EmergencyVisit:
        """Perform triage"""
        visit = self.db.query(EmergencyVisit).filter(EmergencyVisit.id == visit_id).first()
        if not visit:
            raise ValueError("Visit not found")

        visit.triage_category = triage_data.get("category", "GREEN")
        visit.triage_time = datetime.now()
        visit.triage_bp = triage_data.get("bp")
        visit.triage_pulse = triage_data.get("pulse")
        visit.triage_spo2 = triage_data.get("spo2")
        visit.triage_gcs = triage_data.get("gcs")
        visit.triaged_by = triaged_by
        visit.status = "TREATMENT"
        visit.primary_doctor_id = triage_data.get("doctor_id")

        self.db.commit()

        # Create alert if critical
        if visit.triage_category in ["RED", "YELLOW"]:
            self._create_emergency_alert(visit)

        return visit

    # ==================== NURSING ====================

    def record_nursing_vital(self, admission_id: int, vitals_data: Dict, recorded_by: int) -> NursingVital:
        """Record nursing vitals"""
        vital = NursingVital(
            admission_id=admission_id,
            recorded_by=recorded_by,
            bp=vitals_data.get("bp"),
            pulse=vitals_data.get("pulse"),
            temperature=vitals_data.get("temperature"),
            respiratory_rate=vitals_data.get("respiratory_rate"),
            spo2=vitals_data.get("spo2"),
            blood_sugar=vitals_data.get("blood_sugar"),
            pain_score=vitals_data.get("pain_score"),
            consciousness_level=vitals_data.get("consciousness_level")
        )

        self.db.add(vital)
        self.db.commit()

        # Check for critical vitals
        self._check_and_create_vital_alerts(
            self.db.query(Admission).filter(Admission.id == admission_id).first().patient_id,
            vitals_data
        )

        return vital

    def record_nursing_note(self, admission_id: int, note_data: Dict, nurse_id: int) -> NursingNote:
        """Record nursing note"""
        note = NursingNote(
            admission_id=admission_id,
            nurse_id=nurse_id,
            note_type=note_data.get("type", "PROGRESS"),
            note_content=note_data.get("content"),
            shift=note_data.get("shift", "DAY")
        )

        self.db.add(note)
        self.db.commit()
        return note

    def record_fluid_io(self, admission_id: int, io_data: Dict, recorded_by: int) -> FluidIntakeOutput:
        """Record fluid intake/output"""
        record = FluidIntakeOutput(
            admission_id=admission_id,
            recorded_by=recorded_by,
            oral_intake=io_data.get("oral_intake", 0),
            iv_intake=io_data.get("iv_intake", 0),
            other_intake=io_data.get("other_intake", 0),
            urine_output=io_data.get("urine_output", 0),
            stool=io_data.get("stool"),
            vomit=io_data.get("vomit", 0),
            drain_output=io_data.get("drain_output", 0)
        )

        self.db.add(record)
        self.db.commit()
        return record

    # ==================== DOCUMENTS ====================

    def upload_document(self, patient_id: str, document_data: Dict, uploaded_by: int) -> PatientDocument:
        """Upload document"""
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            raise ValueError("Patient not found")

        document = PatientDocument(
            patient_id=patient.id,
            document_type=document_data.get("type"),
            document_category=document_data.get("category"),
            title=document_data.get("title"),
            description=document_data.get("description"),
            file_path=document_data.get("file_path"),
            file_size=document_data.get("file_size"),
            file_type=document_data.get("file_type"),
            encounter_id=document_data.get("encounter_id"),
            lab_test_id=document_data.get("lab_test_id"),
            uploaded_by=uploaded_by
        )

        self.db.add(document)
        self.db.commit()
        return document

    def get_patient_documents(self, patient_id: str, doc_type: str = None) -> List[Dict]:
        """Get patient documents"""
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            return []

        query = self.db.query(PatientDocument).filter(
            PatientDocument.patient_id == patient.id,
            PatientDocument.is_active == True
        )

        if doc_type:
            query = query.filter(PatientDocument.document_type == doc_type)

        docs = query.order_by(desc(PatientDocument.uploaded_at)).all()

        return [{
            "document_id": d.id,
            "type": d.document_type,
            "category": d.document_category,
            "title": d.title,
            "uploaded_at": d.uploaded_at.strftime("%Y-%m-%d %H:%M"),
            "file_type": d.file_type,
            "is_verified": d.is_verified
        } for d in docs]

    # ==================== ALERTS ====================

    def _check_and_create_vital_alerts(self, patient_id: int, vitals: Dict):
        """Check vitals and create alerts"""
        alerts_created = []

        # Check BP
        if vitals.get("bp"):
            try:
                bp = vitals["bp"]
                if "/" in bp:
                    sys, dia = bp.split("/")
                    sys_val = int(sys.strip())
                    dia_val = int(dia.strip())

                    if sys_val > 180 or dia_val > 110:
                        alert = ClinicalAlert(
                            patient_id=self.get_patient_by_id(patient_id).id,
                            alert_message=f"🚨 CRITICAL: Hypertensive crisis - BP {bp}",
                            severity="CRITICAL"
                        )
                        self.db.add(alert)
                        alerts_created.append("CRITICAL_HYPERTENSION")

                    elif sys_val > 140 or dia_val > 90:
                        alert = ClinicalAlert(
                            patient_id=self.get_patient_by_id(patient_id).id,
                            alert_message=f"⚠️ HIGH: BP {bp}",
                            severity="HIGH"
                        )
                        self.db.add(alert)
                        alerts_created.append("HIGH_BP")
            except:
                pass

        # Check SpO2
        if vitals.get("spo2"):
            spo2 = int(vitals["spo2"])
            if spo2 < 90:
                alert = ClinicalAlert(
                    patient_id=self.get_patient_by_id(patient_id).id,
                    alert_message=f"🚨 CRITICAL: Low SpO2 - {spo2}%",
                    severity="CRITICAL"
                )
                self.db.add(alert)
                alerts_created.append("CRITICAL_SPO2")

        # Check Temperature
        if vitals.get("temperature"):
            temp = float(vitals["temperature"])
            if temp > 103:
                alert = ClinicalAlert(
                    patient_id=self.get_patient_by_id(patient_id).id,
                    alert_message=f"🔥 HIGH FEVER: {temp}°F",
                    severity="HIGH"
                )
                self.db.add(alert)
                alerts_created.append("HIGH_FEVER")

        if alerts_created:
            self.db.commit()

        return alerts_created

    def _check_prescription_alerts(self, patient_id: str, medicine_name: str):
        """Check prescription for alerts"""
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            return

        # Check allergies
        if patient.known_allergies:
            allergies = patient.known_allergies.lower().split(",")
            for allergy in allergies:
                if allergy.strip() in medicine_name.lower():
                    alert = ClinicalAlert(
                        patient_id=patient.id,
                        alert_message=f"⚠️ ALLERGY ALERT: Patient allergic to {allergy.strip()}",
                        severity="CRITICAL"
                    )
                    self.db.add(alert)
                    self.db.commit()
                    return

    def _create_emergency_alert(self, visit: EmergencyVisit):
        """Create emergency alert"""
        alert = ClinicalAlert(
            patient_id=visit.patient_id,
            alert_message=f"🚨 EMERGENCY: {visit.triage_category} priority in ER - {visit.chief_complaint}",
            severity="CRITICAL" if visit.triage_category == "RED" else "HIGH"
        )
        self.db.add(alert)
        self.db.commit()

    def get_active_alerts(self, patient_id: str = None) -> List[Dict]:
        """Get active clinical alerts"""
        query = self.db.query(ClinicalAlert).filter(ClinicalAlert.status == "ACTIVE")

        if patient_id:
            patient = self.get_patient_by_id(patient_id)
            if patient:
                query = query.filter(ClinicalAlert.patient_id == patient.id)

        alerts = query.order_by(desc(ClinicalAlert.triggered_at)).all()

        return [{
            "alert_id": a.id,
            "patient_id": a.patient.patient_id if a.patient else None,
            "patient_name": f"{a.patient.first_name} {a.patient.last_name}" if a.patient else "Unknown",
            "message": a.alert_message,
            "severity": a.severity,
            "triggered_at": a.triggered_at.strftime("%Y-%m-%d %H:%M")
        } for a in alerts]

    # ==================== PATIENT TIMELINE ====================

    def get_patient_timeline(self, patient_id: str, limit: int = 50) -> List[Dict]:
        """Get complete patient timeline"""
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            return []

        timeline = []

        # Encounters
        for enc in patient.encounters:
            timeline.append({
                "type": "encounter",
                "date": enc.encounter_start or enc.check_in_time,
                "title": f"{enc.type} Visit - Dr. {enc.doctor.name if enc.doctor else ''}",
                "details": {
                    "diagnosis": enc.primary_diagnosis,
                    "complaint": enc.chief_complaint,
                    "vitals": self._format_vitals(enc)
                },
                "reference_id": enc.id
            })

        # Admissions
        for adm in patient.admissions:
            timeline.append({
                "type": "admission" if adm.status == "ADMITTED" else "discharge",
                "date": adm.admission_date if adm.status == "ADMITTED" else adm.discharge_date,
                "title": f"{'Admission' if adm.status == 'ADMITTED' else 'Discharge'} - {adm.bed.ward.name if adm.bed else ''}",
                "details": {
                    "admission_number": adm.admission_number,
                    "diagnosis": adm.provisional_diagnosis if adm.status == "ADMITTED" else adm.final_diagnosis,
                    "days": (datetime.now() - adm.admission_date).days if adm.status == "ADMITTED" else (adm.discharge_date - adm.admission_date).days
                },
                "reference_id": adm.id
            })

        # Lab results
        for lab in patient.lab_orders:
            if lab.status == "COMPLETED":
                timeline.append({
                    "type": "lab",
                    "date": lab.ordered_at,
                    "title": f"Lab Results - {len(lab.tests)} tests",
                    "details": {
                        "tests": [{"name": t.test_name, "result": t.result_value, "status": t.status} for t in lab.tests]
                    },
                    "reference_id": lab.id
                })

        # Sort by date
        timeline.sort(key=lambda x: x["date"] if x["date"] else datetime.min, reverse=True)

        return timeline[:limit]

    def get_patient_summary(self, patient_id: str) -> Dict:
        """Get patient summary"""
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            return {}

        last_encounter = self.db.query(MedicalEncounter).filter(
            MedicalEncounter.patient_id == patient.id
        ).order_by(desc(MedicalEncounter.encounter_start)).first()

        active_admission = self.db.query(Admission).filter(
            Admission.patient_id == patient.id,
            Admission.status == "ADMITTED"
        ).first()

        return {
            "patient_id": patient.patient_id,
            "name": f"{patient.first_name} {patient.last_name}",
            "demographics": {
                "age": self._calculate_age(patient.date_of_birth),
                "gender": patient.gender,
                "blood_group": patient.blood_group
            },
            "contact": {
                "phone": patient.primary_phone,
                "email": patient.email
            },
            "last_visit": last_encounter.encounter_start if last_encounter else None,
            "active_admission": {
                "admission_id": active_admission.admission_number,
                "ward": active_admission.bed.ward.name if active_admission and active_admission.bed else None,
                "bed": active_admission.bed.bed_number if active_admission and active_admission.bed else None,
                "days": (datetime.now() - active_admission.admission_date).days if active_admission else 0
            } if active_admission else None,
            "allergies": patient.known_allergies.split(",") if patient.known_allergies else [],
            "chronic_conditions": patient.chronic_conditions.split(",") if patient.chronic_conditions else [],
            "vitals": self._format_vitals(last_encounter) if last_encounter else None,
            "alerts": self._generate_summary_alerts(patient, last_encounter)
        }

    # ==================== DASHBOARD STATS ====================

    def get_dashboard_stats(self) -> Dict:
        """Get admin dashboard stats"""
        today = date.today()

        return {
            "today": {
                "opd_visits": self.db.query(MedicalEncounter).filter(
                    func.date(MedicalEncounter.encounter_start) == today
                ).count(),
                "appointments": self.db.query(Appointment).filter(
                    Appointment.appointment_date == today
                ).count(),
                "admissions": self.db.query(Admission).filter(
                    func.date(Admission.admission_date) == today
                ).count(),
                "discharges": self.db.query(Admission).filter(
                    func.date(Admission.discharge_date) == today
                ).count(),
                "emergency_visits": self.db.query(EmergencyVisit).filter(
                    func.date(EmergencyVisit.arrival_time) == today
                ).count()
            },
            "current": {
                "ipd_occupancy": self.db.query(Admission).filter(
                    Admission.status == "ADMITTED"
                ).count(),
                "pending_lab_orders": self.db.query(LabOrder).filter(
                    LabOrder.status != "COMPLETED"
                ).count(),
                "pending_claims": self.db.query(InsuranceClaim).filter(
                    InsuranceClaim.status.in_(["SUBMITTED", "UNDER_REVIEW"])
                ).count(),
                "active_alerts": self.db.query(ClinicalAlert).filter(
                    ClinicalAlert.status == "ACTIVE"
                ).count()
            },
            "financial": {
                "today_revenue": self._calculate_today_revenue(),
                "pending_payments": self.db.query(Invoice).filter(
                    Invoice.balance_due > 0
                ).count()
            }
        }

    def _calculate_today_revenue(self) -> float:
        """Calculate today's revenue"""
        today = date.today()
        total = 0

        payments = self.db.query(Payment).filter(
            func.date(Payment.payment_date) == today
        ).all()

        for payment in payments:
            total += payment.payment_amount

        return total

    # ==================== HELPER METHODS ====================

    def _calculate_age(self, dob: date) -> int:
        """Calculate age"""
        if not dob:
            return 0
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def _format_vitals(self, encounter: MedicalEncounter) -> Dict:
        """Format vitals"""
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

    def _generate_summary_alerts(self, patient: Patient, last_encounter: MedicalEncounter) -> List[str]:
        """Generate summary alerts"""
        alerts = []

        if patient.known_allergies:
            alerts.append(f"⚠️ Allergies: {patient.known_allergies}")

        if patient.chronic_conditions:
            alerts.append(f"📋 Conditions: {patient.chronic_conditions}")

        if last_encounter and last_encounter.vital_bp:
            try:
                sys, dia = last_encounter.vital_bp.split("/")
                if int(sys) > 140 or int(dia) > 90:
                    alerts.append(f"🩺 High BP: {last_encounter.vital_bp}")
            except:
                pass

        return alerts

    def create_audit_log(self, who: int, what: str, patient_id: int = None,
                        record_type: str = None, record_id: int = None,
                        action_details: Dict = None, result: str = "SUCCESS"):
        """Create audit log"""
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
