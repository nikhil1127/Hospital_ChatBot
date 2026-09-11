"""
Enhanced Seed Script for Hospital Management System
Creates sample data for testing the new features
"""

from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from app.db.session import SessionLocal
from app.db.models import (
    Role, Department, Doctor, Patient, User,
    Appointment, MedicalEncounter, Prescription, PrescriptionItem,
    LabOrder, LabTest
)
from app.core.enhanced_db_service import HospitalDBService


def seed_enhanced_data():
    """Seed enhanced hospital data"""
    db = SessionLocal()
    db_service = HospitalDBService(db)

    print("🏥 Seeding Enhanced Hospital Data")
    print("=" * 50)

    try:
        # 1. Create Roles
        print("\n1️⃣ Creating roles...")
        roles = [
            ("admin", ["all"]),
            ("doctor", ["view_patients", "edit_encounters", "view_lab_results", "create_prescriptions"]),
            ("nurse", ["view_patients", "check_in_patients", "record_vitals"]),
            ("receptionist", ["view_patients", "create_appointments", "register_patients"]),
            ("lab_technician", ["process_lab_orders", "enter_results"]),
            ("patient", ["view_own_records", "book_appointments"])
        ]

        for role_name, perms in roles:
            existing = db.query(Role).filter(Role.name == role_name).first()
            if not existing:
                role = Role(name=role_name, permissions=perms)
                db.add(role)
                print(f"   Created role: {role_name}")

        db.commit()

        # 2. Create Departments
        print("\n2️⃣ Creating departments...")
        departments = [
            ("Cardiology", "CARD", "2nd Floor"),
            ("Pediatrics", "PEDS", "1st Floor"),
            ("Neurology", "NEURO", "3rd Floor"),
            ("Orthopedics", "ORTHO", "2nd Floor"),
            ("Dermatology", "DERMA", "1st Floor"),
            ("General Medicine", "GEN", "Ground Floor"),
            ("Emergency", "ER", "Ground Floor"),
            ("Laboratory", "LAB", "Basement"),
            ("Radiology", "RAD", "Basement"),
            ("Pharmacy", "PHARM", "Ground Floor")
        ]

        dept_map = {}
        for dept_name, code, floor in departments:
            existing = db.query(Department).filter(Department.code == code).first()
            if not existing:
                dept = Department(name=dept_name, code=code, floor=floor, is_active=True)
                db.add(dept)
                db.flush()
                dept_map[code] = dept
                print(f"   Created department: {dept_name}")
            else:
                dept_map[code] = existing

        db.commit()

        # 3. Create Enhanced Doctors
        print("\n3️⃣ Creating enhanced doctors...")
        doctors_data = [
            {
                "name": "Dr. Sarah Smith",
                "specialty": "Cardiology",
                "department_code": "CARD",
                "qualification": "MD (Cardiology), FACC",
                "experience_years": 15,
                "consultation_fee": 800,
                "follow_up_fee": 400,
                "weekly_schedule": {
                    "monday": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00"],
                    "tuesday": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00"],
                    "wednesday": [],
                    "thursday": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00"],
                    "friday": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00"],
                    "saturday": ["10:00", "10:30", "11:00"],
                    "sunday": []
                },
                "slot_duration_minutes": 30
            },
            {
                "name": "Dr. James Wilson",
                "specialty": "Pediatrics",
                "department_code": "PEDS",
                "qualification": "MD (Pediatrics), DCH",
                "experience_years": 12,
                "consultation_fee": 600,
                "follow_up_fee": 300,
                "weekly_schedule": {
                    "monday": ["10:00", "10:30", "11:00", "11:30", "12:00", "12:30"],
                    "tuesday": ["10:00", "10:30", "11:00", "11:30", "12:00", "12:30"],
                    "wednesday": ["10:00", "10:30", "11:00", "11:30", "12:00", "12:30"],
                    "thursday": ["10:00", "10:30", "11:00", "11:30", "12:00", "12:30"],
                    "friday": ["10:00", "10:30", "11:00", "11:30", "12:00", "12:30"],
                    "saturday": ["10:00", "10:30", "11:00"],
                    "sunday": []
                },
                "slot_duration_minutes": 30
            },
            {
                "name": "Dr. Emily Chen",
                "specialty": "Neurology",
                "department_code": "NEURO",
                "qualification": "MD (Neurology), DM",
                "experience_years": 10,
                "consultation_fee": 1000,
                "follow_up_fee": 500,
                "weekly_schedule": {
                    "monday": ["14:00", "14:30", "15:00", "15:30", "16:00"],
                    "tuesday": ["14:00", "14:30", "15:00", "15:30", "16:00"],
                    "wednesday": ["14:00", "14:30", "15:00", "15:30", "16:00"],
                    "thursday": [],
                    "friday": ["14:00", "14:30", "15:00", "15:30", "16:00"],
                    "saturday": [],
                    "sunday": []
                },
                "slot_duration_minutes": 30
            },
            {
                "name": "Dr. Michael Brown",
                "specialty": "Orthopedics",
                "department_code": "ORTHO",
                "qualification": "MS (Ortho), FRCS",
                "experience_years": 18,
                "consultation_fee": 700,
                "follow_up_fee": 350,
                "weekly_schedule": {
                    "monday": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30"],
                    "tuesday": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30"],
                    "wednesday": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30"],
                    "thursday": [],
                    "friday": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30"],
                    "saturday": ["09:00", "09:30", "10:00"],
                    "sunday": []
                },
                "slot_duration_minutes": 30
            },
            {
                "name": "Dr. Priya Sharma",
                "specialty": "Dermatology",
                "department_code": "DERMA",
                "qualification": "MD (Dermatology)",
                "experience_years": 8,
                "consultation_fee": 600,
                "follow_up_fee": 300,
                "weekly_schedule": {
                    "monday": ["11:00", "11:30", "12:00", "12:30", "13:00"],
                    "tuesday": ["11:00", "11:30", "12:00", "12:30", "13:00"],
                    "wednesday": ["11:00", "11:30", "12:00", "12:30", "13:00"],
                    "thursday": ["11:00", "11:30", "12:00", "12:30", "13:00"],
                    "friday": ["11:00", "11:30", "12:00", "12:30", "13:00"],
                    "saturday": ["11:00", "11:30", "12:00"],
                    "sunday": []
                },
                "slot_duration_minutes": 30
            },
            {
                "name": "Dr. Robert Taylor",
                "specialty": "General Medicine",
                "department_code": "GEN",
                "qualification": "MD (Internal Medicine)",
                "experience_years": 20,
                "consultation_fee": 500,
                "follow_up_fee": 250,
                "weekly_schedule": {
                    "monday": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30"],
                    "tuesday": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30"],
                    "wednesday": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30"],
                    "thursday": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30"],
                    "friday": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30"],
                    "saturday": ["09:00", "09:30", "10:00", "10:30", "11:00"],
                    "sunday": []
                },
                "slot_duration_minutes": 30
            }
        ]

        for doc_data in doctors_data:
            existing = db.query(Doctor).filter(Doctor.name == doc_data["name"]).first()
            if not existing:
                doctor = Doctor(
                    name=doc_data["name"],
                    specialty=doc_data["specialty"],
                    department_id=dept_map[doc_data["department_code"]].id,
                    qualification=doc_data["qualification"],
                    experience_years=doc_data["experience_years"],
                    consultation_fee=doc_data["consultation_fee"],
                    follow_up_fee=doc_data["follow_up_fee"],
                    weekly_schedule=doc_data["weekly_schedule"],
                    slot_duration_minutes=doc_data["slot_duration_minutes"],
                    is_available=True
                )
                db.add(doctor)
                print(f"   Created doctor: {doc_data['name']}")

        db.commit()

        # 4. Create Sample Patients
        print("\n4️⃣ Creating sample patients...")
        patients_data = [
            {
                "first_name": "Rahul",
                "last_name": "Sharma",
                "date_of_birth": date(1995, 1, 12),
                "gender": "male",
                "blood_group": "O+",
                "phone": "+919876543210",
                "emergency_name": "Sunita Sharma",
                "emergency_relationship": "Mother",
                "emergency_phone": "+919876543211",
                "allergies": "Penicillin, Sulfa drugs",
                "conditions": "Hypertension (since 2022)"
            },
            {
                "first_name": "Priya",
                "last_name": "Patel",
                "date_of_birth": date(1988, 5, 23),
                "gender": "female",
                "blood_group": "B+",
                "phone": "+919876543220",
                "emergency_name": "Rajesh Patel",
                "emergency_relationship": "Husband",
                "emergency_phone": "+919876543221",
                "allergies": "None",
                "conditions": "Type 2 Diabetes"
            },
            {
                "first_name": "Amit",
                "last_name": "Kumar",
                "date_of_birth": date(1980, 11, 8),
                "gender": "male",
                "blood_group": "A+",
                "phone": "+919876543230",
                "emergency_name": "Neha Kumar",
                "emergency_relationship": "Wife",
                "emergency_phone": "+919876543231",
                "allergies": "Dust, Pollen",
                "conditions": "Asthma, Allergic Rhinitis"
            },
            {
                "first_name": "Sneha",
                "last_name": "Reddy",
                "date_of_birth": date(1992, 8, 15),
                "gender": "female",
                "blood_group": "AB+",
                "phone": "+919876543240",
                "emergency_name": "Vijay Reddy",
                "emergency_relationship": "Father",
                "emergency_phone": "+919876543241",
                "allergies": "Shellfish",
                "conditions": "None"
            },
            {
                "first_name": "Vikram",
                "last_name": "Rao",
                "date_of_birth": date(1975, 3, 30),
                "gender": "male",
                "blood_group": "O-",
                "phone": "+919876543250",
                "emergency_name": "Lakshmi Rao",
                "emergency_relationship": "Wife",
                "emergency_phone": "+919876543251",
                "allergies": "Aspirin",
                "conditions": "Chronic Kidney Disease Stage 2"
            }
        ]

        for patient_data in patients_data:
            # Check if phone already exists
            existing = db.query(Patient).filter(
                Patient.primary_phone == patient_data["phone"]
            ).first()

            if not existing:
                patient = db_service.create_patient(
                    patient_data={
                        "first_name": patient_data["first_name"],
                        "last_name": patient_data["last_name"],
                        "date_of_birth": patient_data["date_of_birth"],
                        "gender": patient_data["gender"],
                        "blood_group": patient_data["blood_group"],
                        "primary_phone": patient_data["phone"],
                        "emergency_name": patient_data["emergency_name"],
                        "emergency_relationship": patient_data["emergency_relationship"],
                        "emergency_phone": patient_data["emergency_phone"],
                        "known_allergies": patient_data["allergies"],
                        "chronic_conditions": patient_data["conditions"]
                    },
                    created_by=None
                )
                print(f"   Created patient: {patient_data['first_name']} {patient_data['last_name']} ({patient.patient_id})")

        # 5. Create Sample Appointments
        print("\n5️⃣ Creating sample appointments for today...")
        today = date.today()
        doctors = db.query(Doctor).all()
        patients = db.query(Patient).all()

        # Create appointments for today
        for i, (patient, doctor) in enumerate(zip(patients[:4], doctors[:4])):
            start_time = datetime.combine(today, datetime.strptime("09:00", "%H:%M").time()) + timedelta(minutes=30*i)

            appointment = db_service.create_appointment(
                patient_id=patient.patient_id,
                doctor_id=doctor.id,
                appointment_date=today,
                start_time=start_time,
                chief_complaint=["Chest pain", "Fever", "Knee pain", "Skin rash"][i],
                appointment_type="OPD",
                created_by=None
            )
            print(f"   Created appointment: {appointment.appointment_number} - {patient.first_name} with Dr. {doctor.name}")

        # 6. Create Sample Past Encounters
        print("\n6️⃣ Creating sample past encounters...")
        yesterday = today - timedelta(days=1)
        last_week = today - timedelta(days=7)

        # Past encounter for Rahul Sharma
        rahul = db.query(Patient).filter(Patient.first_name == "Rahul").first()
        dr_smith = db.query(Doctor).filter(Doctor.name == "Dr. Sarah Smith").first()

        if rahul and dr_smith:
            encounter = MedicalEncounter(
                encounter_number=f"ENC-{today.year}-000001",
                patient_id=rahul.id,
                doctor_id=dr_smith.id,
                encounter_start=datetime.combine(last_week, datetime.strptime("10:00", "%H:%M").time()),
                encounter_end=datetime.combine(last_week, datetime.strptime("10:30", "%H:%M").time()),
                type="OPD",
                chief_complaint="Chest pain on exertion",
                vital_bp="140/90",
                vital_pulse=88,
                vital_temperature=98.6,
                primary_diagnosis="Hypertension, Grade 2",
                clinical_notes="Patient reports chest tightness on climbing stairs. BP elevated. ECG normal. Started on antihypertensive.",
                status="COMPLETED"
            )
            db.add(encounter)
            db.flush()

            # Add prescription
            prescription = Prescription(
                prescription_number=f"RX-{today.year}-{encounter.id:06d}",
                encounter_id=encounter.id,
                patient_id=rahul.id,
                doctor_id=dr_smith.id
            )
            db.add(prescription)
            db.flush()

            # Add medicines
            meds = [
                ("Amlodipine", "5mg", "1-0-0", "30 days"),
                ("Metoprolol", "50mg", "0-0-1", "30 days"),
                ("Atorvastatin", "10mg", "0-0-1", "30 days")
            ]
            for med, dose, freq, dur in meds:
                p_item = PrescriptionItem(
                    prescription_id=prescription.id,
                    medicine_name=med,
                    dosage=dose,
                    frequency=freq,
                    duration=dur
                )
                db.add(p_item)

            # Add lab order
            lab_order = LabOrder(
                order_number=f"LAB-{today.year}-{encounter.id:06d}",
                patient_id=rahul.id,
                doctor_id=dr_smith.id,
                encounter_id=encounter.id,
                status="COMPLETED"
            )
            db.add(lab_order)
            db.flush()

            # Add lab tests with results
            tests = [
                ("Hemoglobin", "13.8", "g/dL", "13.0-17.0", "NORMAL"),
                ("Total Cholesterol", "220", "mg/dL", "<200", "HIGH"),
                ("LDL Cholesterol", "150", "mg/dL", "<100", "HIGH"),
                ("Blood Sugar (Fasting)", "110", "mg/dL", "70-100", "HIGH")
            ]
            for test_name, value, unit, ref, status in tests:
                test = LabTest(
                    order_id=lab_order.id,
                    test_name=test_name,
                    result_value=value,
                    unit=unit,
                    reference_range=ref,
                    status=status,
                    is_critical=False
                )
                db.add(test)

            print(f"   Created past encounter for {rahul.first_name} with lab results")

        db.commit()

        # 7. Create Pending Lab Orders
        print("\n7️⃣ Creating pending lab orders...")
        priya = db.query(Patient).filter(Patient.first_name == "Priya").first()
        dr_wilson = db.query(Doctor).filter(Doctor.name == "Dr. James Wilson").first()

        if priya and dr_wilson:
            lab_order = LabOrder(
                order_number=f"LAB-{today.year}-999001",
                patient_id=priya.id,
                doctor_id=dr_wilson.id,
                status="ORDERED"
            )
            db.add(lab_order)
            db.flush()

            pending_tests = ["HbA1c", "Blood Sugar (Post Prandial)", "Urine Microalbumin"]
            for test_name in pending_tests:
                test = LabTest(
                    order_id=lab_order.id,
                    test_name=test_name,
                    status="PENDING"
                )
                db.add(test)

            print(f"   Created pending lab order for {priya.first_name}")

        db.commit()

        print("\n" + "=" * 50)
        print("✅ Enhanced data seeded successfully!")
        print("\n📊 Summary:")
        print(f"   • Departments: {db.query(Department).count()}")
        print(f"   • Doctors: {db.query(Doctor).count()}")
        print(f"   • Patients: {db.query(Patient).count()}")
        print(f"   • Today's Appointments: {db.query(Appointment).filter(Appointment.appointment_date == today).count()}")
        print(f"   • Past Encounters: {db.query(MedicalEncounter).count()}")
        print(f"   • Lab Orders: {db.query(LabOrder).count()}")
        print("\n🚀 Next steps:")
        print("   1. Start server: python -m app.main_enhanced")
        print("   2. Open Doctor Dashboard: http://localhost:8000/doctor")
        print("   3. WhatsApp bot continues to work!")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed_enhanced_data()
