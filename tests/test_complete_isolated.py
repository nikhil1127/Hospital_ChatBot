"""
Isolated Tests for Hospital Management System Components
Tests without importing conflicting models
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date, timedelta

# Create isolated test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_complete.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Import and create complete models
import sys
sys.path.insert(0, 'C:/Users/dt233659/.claude/hospital_bot')

# Import fresh models and create tables
from app.db.models_complete import Base
Base.metadata.create_all(bind=engine)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TestDatabaseOperations:
    """Test database operations directly"""

    def setup_method(self):
        """Setup for each test"""
        self.db = TestingSessionLocal()

    def teardown_method(self):
        """Cleanup after each test"""
        self.db.rollback()
        self.db.close()

    def test_database_connection(self):
        """Test database connection"""
        result = self.db.execute("SELECT 1").scalar()
        assert result == 1

    def test_tables_exist(self):
        """Test that all required tables exist"""
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        required_tables = [
            'patients', 'doctors', 'appointments', 'medical_encounters',
            'wards', 'beds', 'admissions', 'insurance_policies',
            'medicines', 'invoices', 'clinical_alerts'
        ]

        for table in required_tables:
            assert table in tables, f"Table {table} not found"

        print(f"✅ All {len(required_tables)} required tables exist")


class TestPatientEMPI:
    """Test Patient Master Index functionality"""

    def setup_method(self):
        self.db = TestingSessionLocal()
        from app.db.models_complete import Patient
        self.Patient = Patient

    def teardown_method(self):
        self.db.rollback()
        self.db.close()

    def test_create_patient(self):
        """Test patient creation with ID generation"""
        patient = self.Patient(
            patient_id="PAT-2026-000001",
            first_name="Test",
            last_name="Patient",
            date_of_birth=date(1990, 1, 1),
            gender="male",
            blood_group="O+",
            primary_phone="+919999999999"
        )

        self.db.add(patient)
        self.db.commit()

        assert patient.id is not None
        assert patient.patient_id == "PAT-2026-000001"
        print(f"✅ Patient created: {patient.patient_id}")

    def test_patient_demographics(self):
        """Test patient demographic fields"""
        patient = self.Patient(
            patient_id="PAT-2026-000002",
            first_name="Rahul",
            last_name="Sharma",
            middle_name="Kumar",
            date_of_birth=date(1985, 5, 15),
            gender="male",
            blood_group="B+",
            marital_status="married",
            occupation="Engineer",
            primary_phone="+919876543210",
            email="rahul@test.com",
            address_line1="123 Main St",
            city="New Delhi",
            state="Delhi",
            pincode="110001",
            emergency_name="Sunita Sharma",
            emergency_relationship="Wife",
            emergency_phone="+919876543211",
            known_allergies="Penicillin, Sulfa",
            chronic_conditions="Hypertension, Diabetes"
        )

        self.db.add(patient)
        self.db.commit()

        # Verify all fields
        assert patient.first_name == "Rahul"
        assert patient.known_allergies == "Penicillin, Sulfa"
        assert patient.chronic_conditions == "Hypertension, Diabetes"
        print(f"✅ Patient demographics stored correctly")

    def test_patient_query(self):
        """Test querying patient by phone"""
        patient = self.Patient(
            patient_id="PAT-2026-000003",
            first_name="Query",
            last_name="Test",
            date_of_birth=date(1992, 3, 10),
            gender="female",
            primary_phone="+918888888888"
        )

        self.db.add(patient)
        self.db.commit()

        # Query by phone
        result = self.db.query(self.Patient).filter(
            self.Patient.primary_phone == "+918888888888"
        ).first()

        assert result is not None
        assert result.first_name == "Query"
        print(f"✅ Patient query by phone works")


class TestDoctorAndSchedule:
    """Test Doctor management"""

    def setup_method(self):
        self.db = TestingSessionLocal()
        from app.db.models_complete import Doctor, Department
        self.Doctor = Doctor
        self.Department = Department

    def teardown_method(self):
        self.db.rollback()
        self.db.close()

    def test_create_department(self):
        """Test department creation"""
        dept = self.Department(
            name="Cardiology",
            code="CARD",
            floor="2nd Floor"
        )

        self.db.add(dept)
        self.db.commit()

        assert dept.id is not None
        assert dept.name == "Cardiology"
        print(f"✅ Department created: {dept.name}")

    def test_create_doctor(self):
        """Test doctor creation"""
        dept = self.Department(name="Neurology", code="NEURO")
        self.db.add(dept)
        self.db.flush()

        doctor = self.Doctor(
            name="Dr. Sarah Smith",
            specialty="Neurology",
            department_id=dept.id,
            qualification="MD, DM (Neurology)",
            registration_number="MCI-12345",
            experience_years=15,
            consultation_fee=800,
            follow_up_fee=400,
            weekly_schedule={
                "monday": ["09:00", "09:30", "10:00"],
                "tuesday": ["09:00", "09:30", "10:00"]
            },
            slot_duration_minutes=30,
            is_available=True
        )

        self.db.add(doctor)
        self.db.commit()

        assert doctor.id is not None
        assert doctor.name == "Dr. Sarah Smith"
        assert doctor.weekly_schedule is not None
        print(f"✅ Doctor created: {doctor.name}")


class TestAppointments:
    """Test Appointment system"""

    def setup_method(self):
        self.db = TestingSessionLocal()
        from app.db.models_complete import Patient, Doctor, Appointment, Department
        self.Patient = Patient
        self.Doctor = Doctor
        self.Appointment = Appointment
        self.Department = Department

    def teardown_method(self):
        self.db.rollback()
        self.db.close()

    def test_create_appointment(self):
        """Test appointment creation"""
        # Create patient
        patient = self.Patient(
            patient_id="PAT-2026-000010",
            first_name="Appointment",
            last_name="Test",
            date_of_birth=date(1990, 1, 1),
            gender="male",
            primary_phone="+917777777777"
        )
        self.db.add(patient)

        # Create doctor
        doctor = self.Doctor(
            name="Dr. Test",
            specialty="General",
            consultation_fee=500
        )
        self.db.add(doctor)
        self.db.flush()

        # Create appointment
        start_time = datetime.now() + timedelta(days=1)
        appointment = self.Appointment(
            appointment_number="APT-2026-000001",
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_date=start_time.date(),
            start_time=start_time,
            end_time=start_time + timedelta(minutes=30),
            token_number=1,
            type="OPD",
            chief_complaint="Headache",
            status="CONFIRMED"
        )

        self.db.add(appointment)
        self.db.commit()

        assert appointment.id is not None
        assert appointment.token_number == 1
        assert appointment.chief_complaint == "Headache"
        print(f"✅ Appointment created: {appointment.appointment_number}")


class TestIPD:
    """Test IPD/Bed management"""

    def setup_method(self):
        self.db = TestingSessionLocal()
        from app.db.models_complete import Ward, Bed, Admission, Patient, Doctor
        self.Ward = Ward
        self.Bed = Bed
        self.Admission = Admission
        self.Patient = Patient
        self.Doctor = Doctor

    def teardown_method(self):
        self.db.rollback()
        self.db.close()

    def test_create_ward(self):
        """Test ward creation"""
        ward = self.Ward(
            name="General Ward A",
            ward_type="GENERAL",
            floor="1st Floor"
        )

        self.db.add(ward)
        self.db.commit()

        assert ward.id is not None
        print(f"✅ Ward created: {ward.name}")

    def test_create_bed(self):
        """Test bed creation"""
        ward = self.Ward(name="ICU", ward_type="ICU")
        self.db.add(ward)
        self.db.flush()

        bed = self.Bed(
            bed_number="ICU-001",
            ward_id=ward.id,
            bed_type="ICU_BED",
            status="AVAILABLE",
            daily_charge=5000
        )

        self.db.add(bed)
        self.db.commit()

        assert bed.id is not None
        assert bed.status == "AVAILABLE"
        assert bed.daily_charge == 5000
        print(f"✅ Bed created: {bed.bed_number} in {ward.name}")

    def test_admit_patient(self):
        """Test patient admission"""
        # Setup
        ward = self.Ward(name="General Ward", ward_type="GENERAL")
        self.db.add(ward)
        self.db.flush()

        bed = self.Bed(bed_number="GW-001", ward_id=ward.id, status="AVAILABLE", daily_charge=1000)
        self.db.add(bed)
        self.db.flush()

        patient = self.Patient(
            patient_id="PAT-2026-000100",
            first_name="Admission",
            last_name="Test",
            date_of_birth=date(1980, 1, 1),
            gender="male",
            primary_phone="+916666666666"
        )
        self.db.add(patient)

        doctor = self.Doctor(name="Dr. Admission Test", specialty="General")
        self.db.add(doctor)
        self.db.flush()

        # Admit
        admission = self.Admission(
            admission_number="IP-2026-000001",
            patient_id=patient.id,
            admission_type="EMERGENCY",
            bed_id=bed.id,
            primary_doctor_id=doctor.id,
            chief_complaint="Chest pain",
            provisional_diagnosis="Possible MI",
            admission_bp="140/90",
            admission_pulse=88,
            status="ADMITTED"
        )

        # Mark bed occupied
        bed.status = "OCCUPIED"

        self.db.add(admission)
        self.db.commit()

        assert admission.id is not None
        assert admission.status == "ADMITTED"
        assert bed.status == "OCCUPIED"
        print(f"✅ Patient admitted: {admission.admission_number}")


class TestPharmacy:
    """Test Pharmacy module"""

    def setup_method(self):
        self.db = TestingSessionLocal()
        from app.db.models_complete import Medicine
        self.Medicine = Medicine

    def teardown_method(self):
        self.db.rollback()
        self.db.close()

    def test_create_medicine(self):
        """Test medicine creation"""
        medicine = self.Medicine(
            name="Paracetamol",
            generic_name="Acetaminophen",
            form="Tablet",
            strength="500mg",
            category="Analgesic",
            stock_quantity=100,
            reorder_level=20,
            mrp=15.0,
            sale_price=12.0,
            manufacturer="Generic Pharma",
            is_active=True
        )

        self.db.add(medicine)
        self.db.commit()

        assert medicine.id is not None
        assert medicine.stock_quantity == 100
        print(f"✅ Medicine created: {medicine.name}")

    def test_stock_management(self):
        """Test stock tracking"""
        medicine = self.Medicine(
            name="Amoxicillin",
            generic_name="Amoxicillin",
            category="Antibiotic",
            stock_quantity=10,
            reorder_level=20
        )

        self.db.add(medicine)
        self.db.commit()

        # Check if low stock
        low_stock = medicine.stock_quantity <= medicine.reorder_level
        assert low_stock is True
        print(f"✅ Low stock detected: {medicine.stock_quantity} <= {medicine.reorder_level}")


class TestInsurance:
    """Test Insurance module"""

    def setup_method(self):
        self.db = TestingSessionLocal()
        from app.db.models_complete import InsuranceProvider, InsurancePolicy, Patient
        self.InsuranceProvider = InsuranceProvider
        self.InsurancePolicy = InsurancePolicy
        self.Patient = Patient

    def teardown_method(self):
        self.db.rollback()
        self.db.close()

    def test_create_insurance_provider(self):
        """Test insurance provider creation"""
        provider = self.InsuranceProvider(
            name="Star Health Insurance",
            provider_code="STAR",
            contact_phone="1800-123-4567",
            is_active=True
        )

        self.db.add(provider)
        self.db.commit()

        assert provider.id is not None
        print(f"✅ Insurance provider created: {provider.name}")

    def test_create_policy(self):
        """Test policy creation for patient"""
        # Create provider
        provider = self.InsuranceProvider(name="ICICI Lombard", provider_code="ICICI")
        self.db.add(provider)

        # Create patient
        patient = self.Patient(
            patient_id="PAT-2026-000200",
            first_name="Insurance",
            last_name="Test",
            date_of_birth=date(1985, 1, 1),
            gender="male",
            primary_phone="+915555555555"
        )
        self.db.add(patient)
        self.db.flush()

        # Create policy
        policy = self.InsurancePolicy(
            patient_id=patient.id,
            provider_id=provider.id,
            policy_number="ICICI12345678",
            policy_type="HEALTH",
            sum_insured=500000,
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=365),
            room_rent_limit=3000,
            icu_limit=5000,
            is_active=True
        )

        self.db.add(policy)
        self.db.commit()

        assert policy.id is not None
        assert policy.sum_insured == 500000
        print(f"✅ Insurance policy created: {policy.policy_number}")


class TestBilling:
    """Test Billing module"""

    def setup_method(self):
        self.db = TestingSessionLocal()
        from app.db.models_complete import Invoice, InvoiceItem, Patient
        self.Invoice = Invoice
        self.InvoiceItem = InvoiceItem
        self.Patient = Patient

    def teardown_method(self):
        self.db.rollback()
        self.db.close()

    def test_create_invoice(self):
        """Test invoice creation"""
        patient = self.Patient(
            patient_id="PAT-2026-000300",
            first_name="Billing",
            last_name="Test",
            date_of_birth=date(1990, 1, 1),
            gender="male",
            primary_phone="+914444444444"
        )
        self.db.add(patient)
        self.db.flush()

        invoice = self.Invoice(
            invoice_number="INV-2026-000001",
            patient_id=patient.id,
            subtotal=1500,
            discount=0,
            tax_amount=150,
            total_amount=1650,
            amount_paid=0,
            balance_due=1650,
            status="DRAFT"
        )

        self.db.add(invoice)
        self.db.commit()

        assert invoice.id is not None
        assert invoice.total_amount == 1650
        print(f"✅ Invoice created: {invoice.invoice_number}")

    def test_add_invoice_items(self):
        """Test adding items to invoice"""
        patient = self.Patient(
            patient_id="PAT-2026-000301",
            first_name="Invoice",
            last_name="Items",
            date_of_birth=date(1990, 1, 1),
            gender="male",
            primary_phone="+914444444443"
        )
        self.db.add(patient)
        self.db.flush()

        invoice = self.Invoice(
            invoice_number="INV-2026-000002",
            patient_id=patient.id,
            subtotal=0,
            total_amount=0,
            balance_due=0,
            status="DRAFT"
        )
        self.db.add(invoice)
        self.db.flush()

        # Add items
        item1 = self.InvoiceItem(
            invoice_id=invoice.id,
            item_type="CONSULTATION",
            item_description="Doctor consultation",
            quantity=1,
            unit_price=500,
            total_price=500,
            is_insurance_eligible=True
        )

        item2 = self.InvoiceItem(
            invoice_id=invoice.id,
            item_type="PHARMACY",
            item_description="Paracetamol 500mg x 10",
            quantity=10,
            unit_price=12,
            total_price=120,
            is_insurance_eligible=True
        )

        self.db.add_all([item1, item2])

        # Update invoice totals
        invoice.subtotal = 620
        invoice.total_amount = 620
        invoice.balance_due = 620

        self.db.commit()

        assert len(invoice.items) == 2
        assert invoice.total_amount == 620
        print(f"✅ Invoice items added: {len(invoice.items)} items")


class TestAlerts:
    """Test Clinical Alerts"""

    def setup_method(self):
        self.db = TestingSessionLocal()
        from app.db.models_complete import AlertRule, ClinicalAlert, Patient
        self.AlertRule = AlertRule
        self.ClinicalAlert = ClinicalAlert
        self.Patient = Patient

    def teardown_method(self):
        self.db.rollback()
        self.db.close()

    def test_create_alert_rule(self):
        """Test alert rule creation"""
        rule = self.AlertRule(
            rule_name="Critical Hypertension",
            rule_type="VITAL",
            condition_field="vital_bp",
            condition_operator=">",
            condition_value="180/110",
            severity="CRITICAL",
            alert_message="🚨 CRITICAL: Hypertensive crisis - BP {value}",
            notify_roles=["doctor", "nurse"],
            is_active=True
        )

        self.db.add(rule)
        self.db.commit()

        assert rule.id is not None
        assert rule.severity == "CRITICAL"
        print(f"✅ Alert rule created: {rule.rule_name}")

    def test_create_clinical_alert(self):
        """Test clinical alert creation"""
        patient = self.Patient(
            patient_id="PAT-2026-000400",
            first_name="Alert",
            last_name="Test",
            date_of_birth=date(1990, 1, 1),
            gender="male",
            primary_phone="+913333333333"
        )
        self.db.add(patient)
        self.db.flush()

        alert = self.ClinicalAlert(
            patient_id=patient.id,
            alert_message="🚨 Critical: BP 190/110",
            severity="CRITICAL",
            status="ACTIVE"
        )

        self.db.add(alert)
        self.db.commit()

        assert alert.id is not None
        assert alert.status == "ACTIVE"
        print(f"✅ Clinical alert created: {alert.alert_message}")


class TestEndToEnd:
    """End-to-end integration tests"""

    def setup_method(self):
        self.db = TestingSessionLocal()

    def teardown_method(self):
        self.db.rollback()
        self.db.close()

    def test_complete_patient_journey(self):
        """Test complete patient journey from registration to discharge"""
        from app.db.models_complete import (
            Patient, Doctor, Department, Ward, Bed, Admission,
            Appointment, MedicalEncounter, Invoice, InsuranceProvider, InsurancePolicy
        )

        # 1. Register Patient
        patient = Patient(
            patient_id="PAT-E2E-001",
            first_name="E2E",
            last_name="Journey",
            date_of_birth=date(1985, 6, 15),
            gender="male",
            blood_group="O+",
            primary_phone="+91-E2E-TEST"
        )
        self.db.add(patient)
        self.db.flush()
        print("   Step 1: Patient registered")

        # 2. Create Doctor
        dept = Department(name="E2E Department", code="E2E")
        self.db.add(dept)
        self.db.flush()

        doctor = Doctor(
            name="Dr. E2E Test",
            specialty="General",
            department_id=dept.id,
            consultation_fee=500
        )
        self.db.add(doctor)
        self.db.flush()
        print("   Step 2: Doctor created")

        # 3. Create Appointment
        appt_time = datetime.now() + timedelta(hours=1)
        appointment = Appointment(
            appointment_number="APT-E2E-001",
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_date=appt_time.date(),
            start_time=appt_time,
            end_time=appt_time + timedelta(minutes=30),
            token_number=1,
            type="OPD",
            chief_complaint="Chest pain",
            status="CONFIRMED"
        )
        self.db.add(appointment)
        self.db.flush()
        print("   Step 3: Appointment created")

        # 4. Create Encounter (Consultation)
        encounter = MedicalEncounter(
            encounter_number="ENC-E2E-001",
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_id=appointment.id,
            type="OPD",
            chief_complaint="Chest pain",
            primary_diagnosis="Hypertension",
            vital_bp="140/90",
            vital_pulse=88,
            status="COMPLETED"
        )
        self.db.add(encounter)
        self.db.flush()
        print("   Step 4: Consultation completed")

        # 5. Create OPD Invoice
        invoice = Invoice(
            invoice_number="INV-E2E-001",
            patient_id=patient.id,
            encounter_id=encounter.id,
            subtotal=500,
            total_amount=500,
            balance_due=500,
            status="DRAFT"
        )
        self.db.add(invoice)
        self.db.flush()
        print("   Step 5: Invoice created")

        # 6. Add Insurance
        provider = InsuranceProvider(name="E2E Insurance", provider_code="E2E")
        self.db.add(provider)
        self.db.flush()

        policy = InsurancePolicy(
            patient_id=patient.id,
            provider_id=provider.id,
            policy_number="E2E-POL-001",
            policy_type="HEALTH",
            sum_insured=100000,
            is_active=True
        )
        self.db.add(policy)
        self.db.flush()
        print("   Step 6: Insurance added")

        # 7. Admit to IPD
        ward = Ward(name="E2E Ward", ward_type="GENERAL")
        self.db.add(ward)
        self.db.flush()

        bed = Bed(bed_number="E2E-001", ward_id=ward.id, status="AVAILABLE", daily_charge=1000)
        self.db.add(bed)
        self.db.flush()

        admission = Admission(
            admission_number="IP-E2E-001",
            patient_id=patient.id,
            admission_type="PLANNED",
            bed_id=bed.id,
            primary_doctor_id=doctor.id,
            status="ADMITTED"
        )
        bed.status = "OCCUPIED"
        self.db.add(admission)
        self.db.flush()
        print("   Step 7: Patient admitted to IPD")

        # 8. Discharge
        admission.status = "DISCHARGED"
        admission.discharge_type = "NORMAL"
        bed.status = "AVAILABLE"
        print("   Step 8: Patient discharged")

        self.db.commit()

        # Verify
        assert patient.id is not None
        assert appointment.id is not None
        assert encounter.id is not None
        assert invoice.id is not None
        assert policy.id is not None
        assert admission.id is not None

        print("✅ Complete E2E journey successful!")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
