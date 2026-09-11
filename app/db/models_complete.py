"""
COMPLETE Hospital Management Database Models
Includes all modules: IPD, Insurance, Pharmacy, Nursing, Billing, Documents, Emergency, Staff
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Float, Boolean,
    Text, Date, Enum, JSON, DECIMAL, Time, Table
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum

# ==================== ENUMS ====================

class PatientStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DECEASED = "deceased"
    MERGED = "merged"

class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class EncounterType(str, enum.Enum):
    OPD = "opd"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    VIDEO = "video"

class AdmissionStatus(str, enum.Enum):
    ADMITTED = "admitted"
    DISCHARGED = "discharged"
    TRANSFERRED = "transferred"
    EXPIRED = "expired"

class DischargeType(str, enum.Enum):
    NORMAL = "normal"
    DAMA = "dama"  # Discharge Against Medical Advice
    REFERRED = "referred"
    EXPIRED = "expired"

class TriageCategory(str, enum.Enum):
    RED = "red"      # Immediate - Life threatening
    YELLOW = "yellow"  # Urgent - Potentially life threatening
    GREEN = "green"   # Less urgent - Minor
    BLACK = "black"   # Deceased/Expectant

class BedStatus(str, enum.Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"

class WardType(str, enum.Enum):
    GENERAL = "general"
    SEMI_PRIVATE = "semi_private"
    PRIVATE = "private"
    ICU = "icu"
    ICCU = "iccu"
    NICU = "nicu"
    PICU = "picu"

class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    FINALIZED = "finalized"
    PAID = "paid"
    PARTIAL = "partial"
    CANCELLED = "cancelled"

class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    INSURANCE = "insurance"
    ONLINE = "online"
    CHEQUE = "cheque"

class ClaimStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SETTLED = "settled"

class AlertSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# ==================== USER & ROLES ====================

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    permissions = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Authentication
    phone_number = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=True)
    name = Column(String, nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id"))

    # Profile
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    role = relationship("Role")
    patient_profile = relationship("Patient", back_populates="user", uselist=False)
    doctor_profile = relationship("Doctor", back_populates="user", uselist=False)
    employee_profile = relationship("Employee", back_populates="user", uselist=False)

# ==================== DEPARTMENTS ====================

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(20), unique=True)
    floor = Column(String(20))
    head_doctor_id = Column(Integer, ForeignKey("doctors.id"))
    is_active = Column(Boolean, default=True)

# ==================== PATIENT MASTER INDEX ====================

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)

    # Master Patient Index
    patient_id = Column(String(20), unique=True, index=True, nullable=False)
    empi_id = Column(String(50), unique=True, nullable=True)

    # Link to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Demographics
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(20), nullable=False)
    blood_group = Column(String(10))
    marital_status = Column(String(20))
    occupation = Column(String(100))
    nationality = Column(String(50), default="Indian")

    # Contact
    primary_phone = Column(String(20), nullable=False, index=True)
    secondary_phone = Column(String(20))
    email = Column(String(255))
    whatsapp_number = Column(String(20))

    # Address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(20))
    country = Column(String(100), default="India")

    # Emergency Contact
    emergency_name = Column(String(200))
    emergency_relationship = Column(String(50))
    emergency_phone = Column(String(20))

    # Medical Summary
    known_allergies = Column(Text)
    current_medications = Column(Text)
    chronic_conditions = Column(Text)
    surgical_history = Column(Text)
    family_history = Column(Text)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    registered_by = Column(Integer, ForeignKey("users.id"))
    status = Column(String(20), default="ACTIVE")

    # Relationships
    user = relationship("User", back_populates="patient_profile")
    appointments = relationship("Appointment", back_populates="patient")
    encounters = relationship("MedicalEncounter", back_populates="patient")
    admissions = relationship("Admission", back_populates="patient")
    lab_orders = relationship("LabOrder", back_populates="patient")
    insurance_policies = relationship("InsurancePolicy", back_populates="patient")
    documents = relationship("PatientDocument", back_populates="patient")
    invoices = relationship("Invoice", back_populates="patient")

class PatientAlias(Base):
    __tablename__ = "patient_aliases"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    alias_name = Column(String(200))
    alias_type = Column(String(50))
    match_confidence = Column(Float)

# ==================== DOCTORS ====================

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Professional Info
    name = Column(String(100), nullable=False)
    specialty = Column(String(100), index=True, nullable=False)
    qualification = Column(String(255))
    registration_number = Column(String(100), unique=True)
    experience_years = Column(Integer)

    # Department
    department_id = Column(Integer, ForeignKey("departments.id"))

    # Consultation
    consultation_fee = Column(Float, nullable=False)
    follow_up_fee = Column(Float)

    # Schedule (JSON)
    weekly_schedule = Column(JSON)
    slot_duration_minutes = Column(Integer, default=30)

    # Settings
    is_available = Column(Boolean, default=True)
    max_daily_patients = Column(Integer, default=20)

    # Relationships
    user = relationship("User", back_populates="doctor_profile")
    department = relationship("Department")
    appointments = relationship("Appointment", back_populates="doctor")
    ward_rounds = relationship("DailyProgress", back_populates="doctor")

# ==================== APPOINTMENTS ====================

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    appointment_number = Column(String(20), unique=True, nullable=False)

    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)

    appointment_date = Column(Date, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=30)
    token_number = Column(Integer)

    type = Column(String(20), default="OPD")
    chief_complaint = Column(String(500))
    status = Column(String(20), default="SCHEDULED")

    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    encounter = relationship("MedicalEncounter", back_populates="appointment", uselist=False)

# ==================== MEDICAL ENCOUNTERS ====================

class MedicalEncounter(Base):
    __tablename__ = "medical_encounters"

    id = Column(Integer, primary_key=True)
    encounter_number = Column(String(30), unique=True, nullable=False)

    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))

    check_in_time = Column(DateTime(timezone=True))
    encounter_start = Column(DateTime(timezone=True))
    encounter_end = Column(DateTime(timezone=True))

    type = Column(String(20))

    chief_complaint = Column(Text)
    presenting_complaints = Column(Text)
    history_of_present_illness = Column(Text)
    examination_findings = Column(Text)

    vital_bp = Column(String(20))
    vital_pulse = Column(Integer)
    vital_temperature = Column(Float)
    vital_respiratory_rate = Column(Integer)
    vital_spo2 = Column(Integer)
    vital_weight = Column(Float)
    vital_height = Column(Float)
    vital_bmi = Column(Float)

    primary_diagnosis = Column(String(500))
    secondary_diagnosis = Column(String(500))
    icd10_codes = Column(JSON)
    is_provisional_diagnosis = Column(Boolean, default=False)

    clinical_notes = Column(Text)
    advice_given = Column(Text)
    follow_up_plan = Column(Text)

    status = Column(String(20), default="CHECKED_IN")

    signed_by = Column(Integer, ForeignKey("doctors.id"))
    signed_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="encounters")
    appointment = relationship("Appointment", back_populates="encounter")
    prescriptions = relationship("Prescription", back_populates="encounter")
    lab_orders = relationship("LabOrder", back_populates="encounter")
    invoice = relationship("Invoice", back_populates="encounter", uselist=False)

# ==================== PRESCRIPTIONS ====================

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True)
    prescription_number = Column(String(30), unique=True)

    encounter_id = Column(Integer, ForeignKey("medical_encounters.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))

    prescribed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    encounter = relationship("MedicalEncounter", back_populates="prescriptions")
    items = relationship("PrescriptionItem", back_populates="prescription")
    dispense = relationship("PharmacyDispense", back_populates="prescription", uselist=False)

class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    id = Column(Integer, primary_key=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"))

    medicine_id = Column(Integer, ForeignKey("medicines.id"))
    medicine_name = Column(String(200), nullable=False)
    generic_name = Column(String(200))
    dosage = Column(String(100))
    frequency = Column(String(50))
    duration = Column(String(50))
    route = Column(String(50))
    instructions = Column(Text)
    quantity = Column(Integer)

    # Relationships
    prescription = relationship("Prescription", back_populates="items")
    medicine = relationship("Medicine")
    administrations = relationship("MedicationAdministration", back_populates="prescription_item")

# ==================== LABORATORY ====================

class LabOrder(Base):
    __tablename__ = "lab_orders"

    id = Column(Integer, primary_key=True)
    order_number = Column(String(30), unique=True)

    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    encounter_id = Column(Integer, ForeignKey("medical_encounters.id"))

    ordered_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default="ORDERED")

    # Relationships
    patient = relationship("Patient", back_populates="lab_orders")
    encounter = relationship("MedicalEncounter", back_populates="lab_orders")
    tests = relationship("LabTest", back_populates="order")

class LabTest(Base):
    __tablename__ = "lab_tests"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("lab_orders.id"))

    test_name = Column(String(200), nullable=False)
    test_code = Column(String(50))
    category = Column(String(100))

    result_value = Column(String(100))
    unit = Column(String(50))
    reference_range = Column(String(100))
    status = Column(String(20))

    is_critical = Column(Boolean, default=False)
    result_notes = Column(Text)

    collected_at = Column(DateTime(timezone=True))
    resulted_at = Column(DateTime(timezone=True))
    verified_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    order = relationship("LabOrder", back_populates="tests")
    documents = relationship("PatientDocument", back_populates="lab_test")

# ==================== IPD / ADMISSIONS ====================

class Ward(Base):
    __tablename__ = "wards"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    ward_type = Column(String(50))  # GENERAL, SEMI_PRIVATE, PRIVATE, ICU, ICCU
    floor = Column(String(20))
    department_id = Column(Integer, ForeignKey("departments.id"))
    is_active = Column(Boolean, default=True)

    # Relationships
    beds = relationship("Bed", back_populates="ward")
    department = relationship("Department")

class Bed(Base):
    __tablename__ = "beds"

    id = Column(Integer, primary_key=True)
    bed_number = Column(String(20), nullable=False)
    ward_id = Column(Integer, ForeignKey("wards.id"))
    bed_type = Column(String(50))
    status = Column(String(20), default="AVAILABLE")
    current_patient_id = Column(Integer, ForeignKey("patients.id"))
    daily_charge = Column(Float)
    is_active = Column(Boolean, default=True)

    # Relationships
    ward = relationship("Ward", back_populates="beds")
    admissions = relationship("Admission", back_populates="bed")

class Admission(Base):
    __tablename__ = "admissions"

    id = Column(Integer, primary_key=True)
    admission_number = Column(String(30), unique=True, nullable=False)

    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    admission_date = Column(DateTime(timezone=True), default=func.now())
    admission_type = Column(String(50))  # PLANNED, EMERGENCY
    bed_id = Column(Integer, ForeignKey("beds.id"))
    primary_doctor_id = Column(Integer, ForeignKey("doctors.id"))

    chief_complaint = Column(Text)
    provisional_diagnosis = Column(String(500))
    history_present_illness = Column(Text)
    past_history = Column(Text)

    admission_bp = Column(String(20))
    admission_pulse = Column(Integer)
    admission_temperature = Column(Float)
    admission_weight = Column(Float)

    status = Column(String(20), default="ADMITTED")

    discharge_date = Column(DateTime(timezone=True))
    discharge_type = Column(String(50))
    final_diagnosis = Column(String(500))
    discharge_summary = Column(Text)

    # Relationships
    patient = relationship("Patient", back_populates="admissions")
    bed = relationship("Bed", back_populates="admissions")
    daily_progress = relationship("DailyProgress", back_populates="admission")
    nursing_vitals = relationship("NursingVital", back_populates="admission")
    nursing_notes = relationship("NursingNote", back_populates="admission")
    fluid_io = relationship("FluidIntakeOutput", back_populates="admission")
    transfers = relationship("Transfer", back_populates="admission")
    insurance_claims = relationship("InsuranceClaim", back_populates="admission")

class DailyProgress(Base):
    __tablename__ = "daily_progress"

    id = Column(Integer, primary_key=True)
    admission_id = Column(Integer, ForeignKey("admissions.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    progress_date = Column(Date)

    morning_bp = Column(String(20))
    evening_bp = Column(String(20))
    pulse = Column(Integer)
    temperature = Column(Float)
    spo2 = Column(Integer)

    complaints = Column(Text)
    examination_findings = Column(Text)
    plan = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    admission = relationship("Admission", back_populates="daily_progress")
    doctor = relationship("Doctor", back_populates="ward_rounds")

class Transfer(Base):
    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True)
    admission_id = Column(Integer, ForeignKey("admissions.id"))
    from_bed_id = Column(Integer, ForeignKey("beds.id"))
    to_bed_id = Column(Integer, ForeignKey("beds.id"))
    transfer_date = Column(DateTime(timezone=True))
    reason = Column(Text)

    admission = relationship("Admission", back_populates="transfers")

# ==================== NURSING MODULE ====================

class NursingVital(Base):
    __tablename__ = "nursing_vitals"

    id = Column(Integer, primary_key=True)
    admission_id = Column(Integer, ForeignKey("admissions.id"))
    recorded_by = Column(Integer, ForeignKey("users.id"))
    recorded_at = Column(DateTime(timezone=True), default=func.now())

    bp = Column(String(20))
    pulse = Column(Integer)
    temperature = Column(Float)
    respiratory_rate = Column(Integer)
    spo2 = Column(Integer)
    blood_sugar = Column(Float)
    weight = Column(Float)

    pain_score = Column(Integer)
    consciousness_level = Column(String(50))

    admission = relationship("Admission", back_populates="nursing_vitals")

class NursingNote(Base):
    __tablename__ = "nursing_notes"

    id = Column(Integer, primary_key=True)
    admission_id = Column(Integer, ForeignKey("admissions.id"))
    nurse_id = Column(Integer, ForeignKey("users.id"))

    note_type = Column(String(50))
    note_content = Column(Text)

    recorded_at = Column(DateTime(timezone=True), default=func.now())
    shift = Column(String(20))

    admission = relationship("Admission", back_populates="nursing_notes")

class MedicationAdministration(Base):
    __tablename__ = "medication_administrations"

    id = Column(Integer, primary_key=True)
    prescription_item_id = Column(Integer, ForeignKey("prescription_items.id"))
    admission_id = Column(Integer, ForeignKey("admissions.id"))

    scheduled_time = Column(DateTime)
    administered_time = Column(DateTime)
    administered_by = Column(Integer, ForeignKey("users.id"))

    status = Column(String(50))  # GIVEN, NOT_GIVEN, REFUSED, PENDING
    notes = Column(Text)

    prescription_item = relationship("PrescriptionItem", back_populates="administrations")

class FluidIntakeOutput(Base):
    __tablename__ = "fluid_intake_output"

    id = Column(Integer, primary_key=True)
    admission_id = Column(Integer, ForeignKey("admissions.id"))
    recorded_by = Column(Integer, ForeignKey("users.id"))

    oral_intake = Column(Float)
    iv_intake = Column(Float)
    other_intake = Column(Float)

    urine_output = Column(Float)
    stool = Column(String(50))
    vomit = Column(Float)
    drain_output = Column(Float)

    recorded_at = Column(DateTime(timezone=True), default=func.now())

    admission = relationship("Admission", back_populates="fluid_io")

# ==================== EMERGENCY ====================

class EmergencyVisit(Base):
    __tablename__ = "emergency_visits"

    id = Column(Integer, primary_key=True)
    visit_number = Column(String(50), unique=True, nullable=False)

    patient_id = Column(Integer, ForeignKey("patients.id"))

    arrival_time = Column(DateTime(timezone=True), default=func.now())
    arrival_mode = Column(String(50))

    triage_category = Column(String(20))
    triage_time = Column(DateTime(timezone=True))
    triaged_by = Column(Integer, ForeignKey("users.id"))

    chief_complaint = Column(Text)
    history_of_presenting_illness = Column(Text)

    triage_bp = Column(String(20))
    triage_pulse = Column(Integer)
    triage_spo2 = Column(Integer)
    triage_gcs = Column(Integer)

    allergies = Column(Text)
    current_medications = Column(Text)

    primary_doctor_id = Column(Integer, ForeignKey("doctors.id"))
    treatment_started = Column(DateTime(timezone=True))

    disposition = Column(String(50))
    disposition_time = Column(DateTime(timezone=True))

    admission_id = Column(Integer, ForeignKey("admissions.id"))

    status = Column(String(50), default="TRIAGE")

class EmergencyProcedure(Base):
    __tablename__ = "emergency_procedures"

    id = Column(Integer, primary_key=True)
    emergency_visit_id = Column(Integer, ForeignKey("emergency_visits.id"))

    procedure_name = Column(String(200))
    procedure_time = Column(DateTime(timezone=True))
    performed_by = Column(Integer, ForeignKey("doctors.id"))
    notes = Column(Text)

# ==================== INSURANCE / TPA ====================

class InsuranceProvider(Base):
    __tablename__ = "insurance_providers"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    provider_code = Column(String(50), unique=True)
    contact_email = Column(String(255))
    contact_phone = Column(String(20))
    is_active = Column(Boolean, default=True)

    policies = relationship("InsurancePolicy", back_populates="provider")

class InsurancePolicy(Base):
    __tablename__ = "insurance_policies"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    provider_id = Column(Integer, ForeignKey("insurance_providers.id"))

    policy_number = Column(String(100), nullable=False)
    policy_type = Column(String(50))
    sum_insured = Column(Float)

    valid_from = Column(Date)
    valid_until = Column(Date)

    room_rent_limit = Column(Float)
    icu_limit = Column(Float)

    is_active = Column(Boolean, default=True)

    patient = relationship("Patient", back_populates="insurance_policies")
    provider = relationship("InsuranceProvider", back_populates="policies")
    claims = relationship("InsuranceClaim", back_populates="policy")

class InsuranceClaim(Base):
    __tablename__ = "insurance_claims"

    id = Column(Integer, primary_key=True)
    claim_number = Column(String(50), unique=True, nullable=False)
    policy_id = Column(Integer, ForeignKey("insurance_policies.id"))
    admission_id = Column(Integer, ForeignKey("admissions.id"))

    claim_type = Column(String(50))
    claim_amount = Column(Float)
    claimed_date = Column(DateTime(timezone=True))

    status = Column(String(50), default="DRAFT")
    documents = Column(JSON)

    submitted_to = Column(String(200))
    tpa_reference = Column(String(100))

    approved_amount = Column(Float)
    rejection_reason = Column(Text)
    settled_date = Column(DateTime(timezone=True))

    policy = relationship("InsurancePolicy", back_populates="claims")
    admission = relationship("Admission", back_populates="insurance_claims")
    invoices = relationship("Invoice", back_populates="insurance_claim")

class PreAuthorization(Base):
    __tablename__ = "pre_authorizations"

    id = Column(Integer, primary_key=True)
    preauth_number = Column(String(50), unique=True, nullable=False)
    policy_id = Column(Integer, ForeignKey("insurance_policies.id"))

    requested_amount = Column(Float)
    approved_amount = Column(Float)
    status = Column(String(50), default="PENDING")

    proposed_treatment = Column(Text)
    treating_doctor_id = Column(Integer, ForeignKey("doctors.id"))

    requested_date = Column(DateTime(timezone=True))
    approved_date = Column(DateTime(timezone=True))
    validity_until = Column(Date)

# ==================== PHARMACY ====================

class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    generic_name = Column(String(200))
    brand_name = Column(String(200))

    category = Column(String(100))
    form = Column(String(50))
    strength = Column(String(50))

    stock_quantity = Column(Integer, default=0)
    reorder_level = Column(Integer, default=10)
    unit = Column(String(50))

    purchase_price = Column(Float)
    mrp = Column(Float)
    sale_price = Column(Float)
    gst_percentage = Column(Float, default=12)

    expiry_date = Column(Date)
    batch_number = Column(String(100))
    manufacturer = Column(String(200))

    is_active = Column(Boolean, default=True)

    stocks = relationship("PharmacyStock", back_populates="medicine")

class PharmacyStock(Base):
    __tablename__ = "pharmacy_stock"

    id = Column(Integer, primary_key=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id"))
    batch_number = Column(String(100))
    quantity = Column(Integer)
    expiry_date = Column(Date)
    purchase_price = Column(Float)
    received_date = Column(DateTime(timezone=True), default=func.now())

    medicine = relationship("Medicine", back_populates="stocks")

class PharmacyDispense(Base):
    __tablename__ = "pharmacy_dispense"

    id = Column(Integer, primary_key=True)
    dispense_number = Column(String(50), unique=True, nullable=False)

    prescription_id = Column(Integer, ForeignKey("prescriptions.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))
    dispensed_by = Column(Integer, ForeignKey("users.id"))

    dispensed_date = Column(DateTime(timezone=True), default=func.now())

    total_amount = Column(Float)
    discount = Column(Float)
    net_amount = Column(Float)

    status = Column(String(50), default="PENDING")

    prescription = relationship("Prescription", back_populates="dispense")
    items = relationship("PharmacyDispenseItem", back_populates="dispense")

class PharmacyDispenseItem(Base):
    __tablename__ = "pharmacy_dispense_items"

    id = Column(Integer, primary_key=True)
    dispense_id = Column(Integer, ForeignKey("pharmacy_dispense.id"))
    medicine_id = Column(Integer, ForeignKey("medicines.id"))

    requested_qty = Column(Integer)
    dispensed_qty = Column(Integer)
    unit_price = Column(Float)
    total_price = Column(Float)

    batch_number = Column(String(100))

    dispense = relationship("PharmacyDispense", back_populates="items")

class DrugInteraction(Base):
    __tablename__ = "drug_interactions"

    id = Column(Integer, primary_key=True)
    medicine_1_id = Column(Integer, ForeignKey("medicines.id"))
    medicine_2_id = Column(Integer, ForeignKey("medicines.id"))

    interaction_type = Column(String(50))
    description = Column(Text)
    recommendation = Column(Text)

# ==================== BILLING ====================

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    invoice_number = Column(String(50), unique=True, nullable=False)

    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    encounter_id = Column(Integer, ForeignKey("medical_encounters.id"))
    admission_id = Column(Integer, ForeignKey("admissions.id"))
    insurance_claim_id = Column(Integer, ForeignKey("insurance_claims.id"))

    subtotal = Column(Float)
    discount = Column(Float)
    tax_amount = Column(Float)
    total_amount = Column(Float)

    amount_paid = Column(Float, default=0)
    balance_due = Column(Float)

    status = Column(String(50), default="DRAFT")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    finalized_at = Column(DateTime(timezone=True))

    # Relationships
    patient = relationship("Patient", back_populates="invoices")
    encounter = relationship("MedicalEncounter", back_populates="invoice")
    insurance_claim = relationship("InsuranceClaim", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice")
    payments = relationship("Payment", back_populates="invoice")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))

    item_type = Column(String(50))
    item_description = Column(String(500))

    quantity = Column(Float, default=1)
    unit_price = Column(Float)
    total_price = Column(Float)

    reference_id = Column(Integer)
    reference_type = Column(String(50))

    is_insurance_eligible = Column(Boolean, default=True)
    insurance_coverage = Column(Float, default=0)

    invoice = relationship("Invoice", back_populates="items")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))

    payment_amount = Column(Float)
    payment_method = Column(String(50))
    payment_reference = Column(String(200))

    payment_date = Column(DateTime(timezone=True), default=func.now())
    received_by = Column(Integer, ForeignKey("users.id"))

    notes = Column(Text)

    invoice = relationship("Invoice", back_populates="payments")

# ==================== DOCUMENTS ====================

class PatientDocument(Base):
    __tablename__ = "patient_documents"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))

    document_type = Column(String(50))
    document_category = Column(String(50))

    title = Column(String(200))
    description = Column(Text)

    file_path = Column(String(500))
    file_size = Column(Integer)
    file_type = Column(String(50))

    encounter_id = Column(Integer, ForeignKey("medical_encounters.id"))
    admission_id = Column(Integer, ForeignKey("admissions.id"))
    lab_test_id = Column(Integer, ForeignKey("lab_tests.id"))

    uploaded_by = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime(timezone=True), default=func.now())

    is_verified = Column(Boolean, default=False)
    verified_by = Column(Integer, ForeignKey("users.id"))
    verified_at = Column(DateTime(timezone=True))

    is_active = Column(Boolean, default=True)

    patient = relationship("Patient", back_populates="documents")
    lab_test = relationship("LabTest", back_populates="documents")

# ==================== STAFF / EMPLOYEE ====================

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    employee_code = Column(String(50), unique=True)
    designation = Column(String(100))
    department_id = Column(Integer, ForeignKey("departments.id"))

    date_of_joining = Column(Date)
    employment_type = Column(String(50))

    basic_salary = Column(Float)
    allowances = Column(JSON)

    bank_name = Column(String(200))
    bank_account = Column(String(100))
    ifsc_code = Column(String(20))

    documents = Column(JSON)

    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="employee_profile")

class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    start_time = Column(Time)
    end_time = Column(Time)

class EmployeeShift(Base):
    __tablename__ = "employee_shifts"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    shift_id = Column(Integer, ForeignKey("shifts.id"))
    shift_date = Column(Date)

    is_approved = Column(Boolean, default=False)

# ==================== CLINICAL ALERTS ====================

class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True)
    rule_name = Column(String(200))
    rule_type = Column(String(50))

    condition_field = Column(String(100))
    condition_operator = Column(String(20))
    condition_value = Column(String(100))

    severity = Column(String(20))

    alert_message = Column(Text)
    notify_roles = Column(JSON)
    auto_escalate_after_minutes = Column(Integer)

    is_active = Column(Boolean, default=True)

class ClinicalAlert(Base):
    __tablename__ = "clinical_alerts"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    rule_id = Column(Integer, ForeignKey("alert_rules.id"))

    alert_message = Column(Text)
    severity = Column(String(20))

    triggered_at = Column(DateTime(timezone=True), default=func.now())
    acknowledged_by = Column(Integer, ForeignKey("users.id"))
    acknowledged_at = Column(DateTime(timezone=True))

    status = Column(String(20), default="ACTIVE")

# ==================== AUDIT ====================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)

    who = Column(Integer, ForeignKey("users.id"))
    what = Column(String(100), nullable=False)
    when = Column(DateTime(timezone=True), server_default=func.now())
    where_ip = Column(String(50))

    patient_id = Column(Integer, ForeignKey("patients.id"))
    record_type = Column(String(50))
    record_id = Column(Integer)
    action_details = Column(JSON)
    result = Column(String(20))

# ==================== OLD TABLES (for backward compatibility) ====================

class AppointmentHistory(Base):
    """Archive table for completed/cancelled appointments"""
    __tablename__ = "appointment_history"

    id = Column(Integer, primary_key=True, index=True)
    original_appointment_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    appointment_date = Column(DateTime(timezone=True), nullable=False)
    final_status = Column(String, nullable=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(String, nullable=True)
