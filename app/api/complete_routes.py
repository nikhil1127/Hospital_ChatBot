"""
COMPLETE Hospital Management System API Routes
Includes: IPD, Insurance, Pharmacy, Nursing, Billing, Documents, Emergency, Admin
"""

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
import os

from app.db.session import get_db
from app.core.complete_db_service import CompleteHospitalDBService
from app.db.models_complete import (
    Doctor, Patient, Appointment, MedicalEncounter,
    Ward, Bed, Admission, EmergencyVisit, Invoice,
    Medicine, InsuranceProvider, ClinicalAlert
)


router = APIRouter(prefix="/api/v1")

# ==================== ADMIN DASHBOARD ====================

@router.get("/admin/dashboard")
async def admin_dashboard(db: Session = Depends(get_db)):
    """Get admin dashboard statistics"""
    db_service = CompleteHospitalDBService(db)
    stats = db_service.get_dashboard_stats()
    return stats

@router.get("/admin/today")
async def admin_today_overview(db: Session = Depends(get_db)):
    """Get today's hospital overview"""
    db_service = CompleteHospitalDBService(db)
    today = date.today()

    return {
        "stats": db_service.get_dashboard_stats(),
        "ward_occupancy": db_service.get_ward_occupancy()
    }

# ==================== DOCTOR DASHBOARD ====================

@router.get("/doctor/{doctor_id}/dashboard")
async def doctor_dashboard(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    """Get complete doctor dashboard"""
    db_service = CompleteHospitalDBService(db)

    doctor = db_service.db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    dashboard = db_service.get_doctor_dashboard(doctor_id)

    return {
        "doctor": {
            "id": doctor.id,
            "name": doctor.name,
            "specialty": doctor.specialty
        },
        **dashboard
    }

@router.get("/doctor/{doctor_id}/schedule")
async def doctor_schedule(
    doctor_id: int,
    schedule_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get doctor schedule for date"""
    db_service = CompleteHospitalDBService(db)

    if schedule_date:
        date_obj = datetime.strptime(schedule_date, "%Y-%m-%d").date()
    else:
        date_obj = date.today()

    schedule = db_service.get_doctor_schedule(doctor_id, date_obj)
    return schedule

# ==================== CONSULTATION ====================

@router.get("/consultation/{appointment_id}")
async def get_consultation(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Get consultation view"""
    db_service = CompleteHospitalDBService(db)

    appointment = db_service.db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    patient_summary = db_service.get_patient_summary(appointment.patient.patient_id)
    timeline = db_service.get_patient_timeline(appointment.patient.patient_id, limit=10)

    return {
        "appointment": {
            "id": appointment.appointment_number,
            "token": appointment.token_number,
            "patient_name": f"{appointment.patient.first_name} {appointment.patient.last_name}",
            "patient_id": appointment.patient.patient_id,
            "chief_complaint": appointment.chief_complaint,
            "status": appointment.status,
            "time": appointment.start_time.strftime("%H:%M")
        },
        "patient_summary": patient_summary,
        "timeline": timeline
    }

@router.post("/consultation/{appointment_id}/start")
async def start_consultation(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Start consultation"""
    db_service = CompleteHospitalDBService(db)

    appointment = db_service.db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment = db_service.check_in_patient(appointment.appointment_number)

    encounter = db_service.db.query(MedicalEncounter).filter(
        MedicalEncounter.appointment_id == appointment_id
    ).first()

    if encounter:
        encounter = db_service.start_consultation(encounter.id)
        return {
            "success": True,
            "encounter_id": encounter.id,
            "encounter_number": encounter.encounter_number,
            "status": encounter.status
        }

    return {"success": False, "error": "Could not create encounter"}

@router.post("/consultation/{encounter_id}/save")
async def save_consultation(
    encounter_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Save consultation progress"""
    db_service = CompleteHospitalDBService(db)

    encounter = db_service.save_consultation(encounter_id, data)

    return {
        "success": True,
        "encounter_id": encounter.id,
        "status": encounter.status
    }

@router.post("/consultation/{encounter_id}/complete")
async def complete_consultation(
    encounter_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Complete consultation"""
    db_service = CompleteHospitalDBService(db)

    encounter = db_service.complete_consultation(
        encounter_id=encounter_id,
        prescription_data=data.get("prescriptions", []),
        lab_orders=data.get("lab_orders", []),
        ipd_admission=data.get("admit_to_ipd")
    )

    return {
        "success": True,
        "encounter_number": encounter.encounter_number,
        "status": encounter.status,
        "invoice_created": True
    }

# ==================== IPD / ADMISSIONS ====================

@router.get("/ipd/beds/available")
async def get_available_beds(
    ward_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get available beds"""
    db_service = CompleteHospitalDBService(db)
    beds = db_service.get_available_beds(ward_type)
    return {"beds": beds}

@router.get("/ipd/wards/occupancy")
async def get_ward_occupancy(db: Session = Depends(get_db)):
    """Get ward occupancy statistics"""
    db_service = CompleteHospitalDBService(db)
    return db_service.get_ward_occupancy()

@router.post("/ipd/admit")
async def admit_patient(
    data: dict,
    db: Session = Depends(get_db)
):
    """Admit patient"""
    db_service = CompleteHospitalDBService(db)

    try:
        admission = db_service.admit_patient(
            patient_id=data.get("patient_id"),
            doctor_id=data.get("doctor_id"),
            admission_data=data
        )

        return {
            "success": True,
            "admission_number": admission.admission_number,
            "admission_id": admission.id,
            "bed": f"{admission.bed.ward.name} - Bed {admission.bed.bed_number}" if admission.bed else None
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}

@router.get("/ipd/admission/{admission_id}")
async def get_admission(
    admission_id: int,
    db: Session = Depends(get_db)
):
    """Get admission details"""
    admission = db_service.db.query(Admission).filter(Admission.id == admission_id).first()

    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")

    return {
        "admission_number": admission.admission_number,
        "patient": {
            "name": f"{admission.patient.first_name} {admission.patient.last_name}",
            "patient_id": admission.patient.patient_id
        },
        "admission_date": admission.admission_date.strftime("%Y-%m-%d %H:%M"),
        "bed": f"{admission.bed.ward.name} - Bed {admission.bed.bed_number}" if admission.bed else None,
        "doctor": admission.doctor.name if admission.doctor else None,
        "diagnosis": admission.provisional_diagnosis,
        "status": admission.status
    }

@router.post("/ipd/admission/{admission_id}/progress")
async def record_daily_progress(
    admission_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Record daily progress"""
    db_service = CompleteHospitalDBService(db)

    progress = db_service.record_daily_progress(
        admission_id=admission_id,
        doctor_id=data.get("doctor_id"),
        progress_data=data
    )

    return {
        "success": True,
        "progress_id": progress.id
    }

@router.post("/ipd/admission/{admission_id}/discharge")
async def discharge_patient(
    admission_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Discharge patient"""
    db_service = CompleteHospitalDBService(db)

    try:
        admission = db_service.discharge_patient(admission_id, data)

        return {
            "success": True,
            "admission_number": admission.admission_number,
            "discharge_type": admission.discharge_type,
            "discharge_summary": admission.discharge_summary
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}

@router.post("/ipd/admission/{admission_id}/transfer")
async def transfer_patient(
    admission_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Transfer patient to another bed"""
    db_service = CompleteHospitalDBService(db)

    # Implementation for transfer
    admission = db_service.db.query(Admission).filter(Admission.id == admission_id).first()
    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")

    new_bed_id = data.get("new_bed_id")
    new_bed = db_service.db.query(Bed).filter(Bed.id == new_bed_id).first()

    if not new_bed or new_bed.status != "AVAILABLE":
        return {"success": False, "error": "Bed not available"}

    # Transfer logic
    from_bed = admission.bed
    if from_bed:
        from_bed.status = "AVAILABLE"

    admission.bed_id = new_bed_id
    new_bed.status = "OCCUPIED"

    db_service.db.commit()

    return {
        "success": True,
        "new_bed": f"{new_bed.ward.name} - Bed {new_bed.bed_number}"
    }

# ==================== NURSING ====================

@router.post("/nursing/admission/{admission_id}/vitals")
async def record_nursing_vitals(
    admission_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Record nursing vitals"""
    db_service = CompleteHospitalDBService(db)

    vital = db_service.record_nursing_vital(
        admission_id=admission_id,
        vitals_data=data,
        recorded_by=data.get("nurse_id")
    )

    return {
        "success": True,
        "vital_id": vital.id
    }

@router.post("/nursing/admission/{admission_id}/note")
async def record_nursing_note(
    admission_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Record nursing note"""
    db_service = CompleteHospitalDBService(db)

    note = db_service.record_nursing_note(
        admission_id=admission_id,
        note_data=data,
        nurse_id=data.get("nurse_id")
    )

    return {
        "success": True,
        "note_id": note.id
    }

@router.post("/nursing/admission/{admission_id}/fluid-io")
async def record_fluid_io(
    admission_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Record fluid intake/output"""
    db_service = CompleteHospitalDBService(db)

    record = db_service.record_fluid_io(
        admission_id=admission_id,
        io_data=data,
        recorded_by=data.get("nurse_id")
    )

    return {
        "success": True,
        "record_id": record.id
    }

# ==================== EMERGENCY ====================

@router.post("/emergency/register")
async def register_emergency(
    data: dict,
    db: Session = Depends(get_db)
):
    """Register emergency visit"""
    db_service = CompleteHospitalDBService(db)

    visit = db_service.create_emergency_visit(
        patient_id=data.get("patient_id"),
        visit_data=data
    )

    return {
        "success": True,
        "visit_number": visit.visit_number,
        "visit_id": visit.id
    }

@router.post("/emergency/{visit_id}/triage")
async def triage_patient(
    visit_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Perform triage"""
    db_service = CompleteHospitalDBService(db)

    visit = db_service.triage_patient(
        visit_id=visit_id,
        triage_data=data,
        triaged_by=data.get("nurse_id")
    )

    return {
        "success": True,
        "visit_number": visit.visit_number,
        "triage_category": visit.triage_category
    }

@router.get("/emergency/queue")
async def get_emergency_queue(db: Session = Depends(get_db)):
    """Get emergency queue"""
    visits = db_service.db.query(EmergencyVisit).filter(
        EmergencyVisit.status.in_(["TRIAGE", "TREATMENT"])
    ).order_by(
        # Order by triage priority
        EmergencyVisit.triage_category,
        EmergencyVisit.arrival_time
    ).all()

    return {
        "visits": [{
            "visit_number": v.visit_number,
            "patient_name": f"{v.patient.first_name} {v.patient.last_name}" if v.patient else "Unknown",
            "patient_id": v.patient.patient_id if v.patient else None,
            "category": v.triage_category,
            "chief_complaint": v.chief_complaint,
            "status": v.status,
            "waiting_time": (datetime.now() - v.arrival_time).seconds // 60
        } for v in visits]
    }

# ==================== INSURANCE ====================

@router.post("/insurance/providers")
async def create_insurance_provider(
    data: dict,
    db: Session = Depends(get_db)
):
    """Create insurance provider"""
    provider = InsuranceProvider(
        name=data.get("name"),
        provider_code=data.get("code"),
        contact_email=data.get("email"),
        contact_phone=data.get("phone"),
        is_active=True
    )

    db.add(provider)
    db.commit()

    return {"success": True, "provider_id": provider.id}

@router.get("/insurance/providers")
async def get_insurance_providers(db: Session = Depends(get_db)):
    """Get all insurance providers"""
    providers = db.query(InsuranceProvider).filter(InsuranceProvider.is_active == True).all()

    return {
        "providers": [{
            "id": p.id,
            "name": p.name,
            "code": p.provider_code,
            "phone": p.contact_phone
        } for p in providers]
    }

@router.post("/patient/{patient_id}/insurance")
async def add_insurance_policy(
    patient_id: str,
    data: dict,
    db: Session = Depends(get_db)
):
    """Add insurance policy to patient"""
    db_service = CompleteHospitalDBService(db)

    policy = db_service.create_insurance_policy(patient_id, data)

    return {
        "success": True,
        "policy_id": policy.id,
        "policy_number": policy.policy_number
    }

@router.post("/insurance/claim")
async def create_claim(
    data: dict,
    db: Session = Depends(get_db)
):
    """Create insurance claim"""
    db_service = CompleteHospitalDBService(db)

    try:
        claim = db_service.create_insurance_claim(
            admission_id=data.get("admission_id"),
            claim_data=data
        )

        return {
            "success": True,
            "claim_number": claim.claim_number,
            "claim_id": claim.id
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}

@router.get("/insurance/claim/{claim_id}/coverage")
async def calculate_coverage(
    claim_id: int,
    db: Session = Depends(get_db)
):
    """Calculate insurance coverage"""
    db_service = CompleteHospitalDBService(db)

    try:
        coverage = db_service.calculate_insurance_coverage(claim_id)
        return coverage
    except ValueError as e:
        return {"error": str(e)}

@router.get("/insurance/pending-claims")
async def get_pending_claims(db: Session = Depends(get_db)):
    """Get pending insurance claims"""
    claims = db.query(InsuranceClaim).filter(
        InsuranceClaim.status.in_(["SUBMITTED", "UNDER_REVIEW"])
    ).all()

    return {
        "claims": [{
            "claim_number": c.claim_number,
            "patient_name": f"{c.admission.patient.first_name} {c.admission.patient.last_name}",
            "amount": c.claim_amount,
            "status": c.status
        } for c in claims]
    }

# ==================== BILLING ====================

@router.get("/patient/{patient_id}/bills")
async def get_patient_bills(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """Get patient bills"""
    db_service = CompleteHospitalDBService(db)
    bills = db_service.get_patient_bills(patient_id)
    return {"bills": bills}

@router.get("/invoice/{invoice_id}")
async def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    """Get invoice details"""
    invoice = db_service.db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return {
        "invoice_number": invoice.invoice_number,
        "patient_name": f"{invoice.patient.first_name} {invoice.patient.last_name}",
        "date": invoice.created_at.strftime("%Y-%m-%d"),
        "items": [{
            "type": item.item_type,
            "description": item.item_description,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "total": item.total_price
        } for item in invoice.items],
        "subtotal": invoice.subtotal,
        "discount": invoice.discount,
        "tax": invoice.tax_amount,
        "total": invoice.total_amount,
        "paid": invoice.amount_paid,
        "balance": invoice.balance_due,
        "status": invoice.status
    }

@router.post("/invoice/{invoice_id}/add-item")
async def add_invoice_item(
    invoice_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Add item to invoice"""
    db_service = CompleteHospitalDBService(db)

    item = db_service.add_invoice_item(invoice_id, data)

    return {
        "success": True,
        "item_id": item.id
    }

@router.post("/invoice/{invoice_id}/payment")
async def record_payment(
    invoice_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Record payment"""
    db_service = CompleteHospitalDBService(db)

    payment = db_service.record_payment(invoice_id, data)

    return {
        "success": True,
        "payment_id": payment.id,
        "amount_paid": payment.payment_amount
    }

# ==================== PHARMACY ====================

@router.post("/pharmacy/medicine")
async def add_medicine(
    data: dict,
    db: Session = Depends(get_db)
):
    """Add medicine"""
    db_service = CompleteHospitalDBService(db)

    medicine = db_service.add_medicine(data)

    return {
        "success": True,
        "medicine_id": medicine.id,
        "name": medicine.name
    }

@router.get("/pharmacy/medicines")
async def get_medicines(
    search: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get medicines"""
    query = db.query(Medicine).filter(Medicine.is_active == True)

    if search:
        query = query.filter(
            Medicine.name.ilike(f"%{search}%") |
            Medicine.generic_name.ilike(f"%{search}%")
        )

    if category:
        query = query.filter(Medicine.category == category)

    medicines = query.all()

    return {
        "medicines": [{
            "id": m.id,
            "name": m.name,
            "generic": m.generic_name,
            "stock": m.stock_quantity,
            "mrp": m.mrp,
            "sale_price": m.sale_price
        } for m in medicines]
    }

@router.post("/pharmacy/medicine/{medicine_id}/stock")
async def add_stock(
    medicine_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Add stock"""
    db_service = CompleteHospitalDBService(db)

    stock = db_service.add_stock(medicine_id, data)

    return {
        "success": True,
        "stock_id": stock.id
    }

@router.get("/pharmacy/low-stock")
async def get_low_stock(db: Session = Depends(get_db)):
    """Get low stock medicines"""
    db_service = CompleteHospitalDBService(db)
    low_stock = db_service.get_low_stock_medicines()
    return {"low_stock": low_stock}

@router.post("/pharmacy/prescription/{prescription_id}/dispense")
async def dispense_prescription(
    prescription_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Dispense prescription"""
    db_service = CompleteHospitalDBService(db)

    try:
        dispense = db_service.dispense_prescription(
            prescription_id=prescription_id,
            dispensed_by=data.get("pharmacist_id")
        )

        return {
            "success": True,
            "dispense_number": dispense.dispense_number,
            "total_amount": dispense.total_amount
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}

@router.post("/pharmacy/check-interactions")
async def check_drug_interactions(
    data: dict,
    db: Session = Depends(get_db)
):
    """Check drug interactions"""
    db_service = CompleteHospitalDBService(db)

    interactions = db_service.check_drug_interactions(
        data.get("patient_id"),
        data.get("medicine")
    )

    return {
        "interactions": interactions,
        "safe": len(interactions) == 0
    }

# ==================== PATIENT API ====================

@router.post("/patient/register")
async def register_patient(
    data: dict,
    db: Session = Depends(get_db)
):
    """Register new patient"""
    db_service = CompleteHospitalDBService(db)

    try:
        patient = db_service.create_patient(data)
        return {
            "success": True,
            "patient_id": patient.patient_id,
            "name": f"{patient.first_name} {patient.last_name}"
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}

@router.get("/patient/{patient_id}")
async def get_patient(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """Get patient details"""
    db_service = CompleteHospitalDBService(db)
    patient = db_service.get_patient_by_id(patient_id)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return {
        "patient_id": patient.patient_id,
        "name": f"{patient.first_name} {patient.last_name}",
        "age": db_service._calculate_age(patient.date_of_birth),
        "gender": patient.gender,
        "blood_group": patient.blood_group,
        "phone": patient.primary_phone,
        "emergency_contact": {
            "name": patient.emergency_name,
            "phone": patient.emergency_phone,
            "relationship": patient.emergency_relationship
        },
        "allergies": patient.known_allergies.split(",") if patient.known_allergies else [],
        "conditions": patient.chronic_conditions.split(",") if patient.chronic_conditions else []
    }

@router.get("/patient/{patient_id}/summary")
async def get_patient_summary(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """Get patient summary"""
    db_service = CompleteHospitalDBService(db)
    summary = db_service.get_patient_summary(patient_id)
    return summary

@router.get("/patient/{patient_id}/timeline")
async def get_patient_timeline(
    patient_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get patient timeline"""
    db_service = CompleteHospitalDBService(db)
    timeline = db_service.get_patient_timeline(patient_id, limit)
    return {"timeline": timeline}

@router.get("/search/patients")
async def search_patients(
    q: str,
    db: Session = Depends(get_db)
):
    """Search patients"""
    db_service = CompleteHospitalDBService(db)

    # Try patient ID
    patient = db_service.get_patient_by_id(q)
    if patient:
        return [{
            "patient_id": patient.patient_id,
            "name": f"{patient.first_name} {patient.last_name}",
            "phone": patient.primary_phone,
            "age": db_service._calculate_age(patient.date_of_birth)
        }]

    # Try phone
    patient = db_service.get_patient_by_phone(q)
    if patient:
        return [{
            "patient_id": patient.patient_id,
            "name": f"{patient.first_name} {patient.last_name}",
            "phone": patient.primary_phone,
            "age": db_service._calculate_age(patient.date_of_birth)
        }]

    # Search by name
    patients = db.query(Patient).filter(
        Patient.first_name.ilike(f"%{q}%") |
        Patient.last_name.ilike(f"%{q}%")
    ).limit(10).all()

    return [{
        "patient_id": p.patient_id,
        "name": f"{p.first_name} {p.last_name}",
        "phone": p.primary_phone,
        "age": db_service._calculate_age(p.date_of_birth)
    } for p in patients]

# ==================== DOCUMENTS ====================

@router.post("/patient/{patient_id}/document")
async def upload_document(
    patient_id: str,
    data: dict,
    db: Session = Depends(get_db)
):
    """Upload document"""
    db_service = CompleteHospitalDBService(db)

    document = db_service.upload_document(
        patient_id=patient_id,
        document_data=data,
        uploaded_by=data.get("uploaded_by")
    )

    return {
        "success": True,
        "document_id": document.id
    }

@router.get("/patient/{patient_id}/documents")
async def get_patient_documents(
    patient_id: str,
    doc_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get patient documents"""
    db_service = CompleteHospitalDBService(db)
    documents = db_service.get_patient_documents(patient_id, doc_type)
    return {"documents": documents}

# ==================== ALERTS ====================

@router.get("/alerts/active")
async def get_active_alerts(
    patient_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get active clinical alerts"""
    db_service = CompleteHospitalDBService(db)
    alerts = db_service.get_active_alerts(patient_id)
    return {"alerts": alerts}

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Acknowledge alert"""
    alert = db_service.db.query(ClinicalAlert).filter(ClinicalAlert.id == alert_id).first()
    if alert:
        alert.status = "ACKNOWLEDGED"
        alert.acknowledged_by = data.get("user_id")
        alert.acknowledged_at = datetime.now()
        db.commit()

    return {"success": True}

# ==================== DAILY BED CHARGES (CRON JOB) ====================

@router.post("/admin/generate-daily-charges")
async def generate_daily_bed_charges(
    data: dict,
    db: Session = Depends(get_db)
):
    """Generate daily bed charges (should be run by cron job)"""
    db_service = CompleteHospitalDBService(db)

    admissions = db.query(Admission).filter(Admission.status == "ADMITTED").all()

    count = 0
    for admission in admissions:
        db_service.generate_daily_bed_charges(admission.id)
        count += 1

    return {
        "success": True,
        "admissions_processed": count
    }

# ==================== LAB ====================

@router.get("/lab/pending-orders")
async def get_pending_lab_orders(db: Session = Depends(get_db)):
    """Get pending lab orders"""
    orders = db.query(LabOrder).filter(
        LabOrder.status.in_(["ORDERED", "SAMPLE_COLLECTED", "PROCESSING"])
    ).order_by(LabOrder.ordered_at).all()

    return {
        "orders": [{
            "order_number": o.order_number,
            "patient_name": f"{o.patient.first_name} {o.patient.last_name}",
            "patient_id": o.patient.patient_id,
            "doctor_name": o.doctor.name if o.doctor else "",
            "ordered_at": o.ordered_at.strftime("%Y-%m-%d %H:%M"),
            "tests": [t.test_name for t in o.tests],
            "status": o.status
        } for o in orders]
    }

@router.post("/lab/order/{order_id}/results")
async def submit_lab_results(
    order_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Submit lab results"""
    db_service = CompleteHospitalDBService(db)

    # Implementation for lab results
    order = db.query(LabOrder).filter(LabOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    for result in data.get("results", []):
        test = db.query(LabTest).filter(
            LabTest.order_id == order_id,
            LabTest.test_name == result.get("test_name")
        ).first()

        if test:
            test.result_value = result.get("value")
            test.unit = result.get("unit")
            test.reference_range = result.get("reference")
            test.status = result.get("status", "NORMAL")
            test.is_critical = result.get("is_critical", False)
            test.resulted_at = datetime.now()

    order.status = "COMPLETED"
    db.commit()

    return {"success": True}

# Initialize db_service reference
from app.db.session import SessionLocal
db_session = SessionLocal()
db_service = CompleteHospitalDBService(db_session)
