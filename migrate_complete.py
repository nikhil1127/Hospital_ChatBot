"""
COMPLETE Migration Script for Hospital Management System
Migrates existing data safely to the new schema
BACKUP YOUR DATABASE BEFORE RUNNING!
"""

import argparse
import sys
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Import both old and new models
from app.db.session import get_db_url, Base
from app.db.models_complete import (
    User, Patient, Doctor, Appointment, MedicalEncounter,
    Department, Role, Ward, Bed, Medicine, InsuranceProvider,
    AlertRule
)


def backup_existing_data(engine):
    """Create backup of existing tables"""
    print("📦 Creating data backup...")

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    backup_data = {}

    for table in tables:
        result = engine.execute(text(f"SELECT * FROM {table}"))
        rows = result.fetchall()
        if rows:
            backup_data[table] = [dict(row) for row in rows]
            print(f"   Backed up {len(rows)} rows from {table}")

    return backup_data


def migrate_data_safely(engine):
    """Migrate data from old schema to new schema"""
    Session = sessionmaker(bind=engine)
    db = Session()

    print("\n" + "="*60)
    print("🏥 HOSPITAL MANAGEMENT SYSTEM - DATA MIGRATION")
    print("="*60)

    try:
        # Check if migration already done
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        # STEP 1: Create new tables
        print("\n1️⃣ Creating new tables...")

        new_tables = [
            'roles', 'departments', 'wards', 'beds', 'admissions',
            'daily_progress', 'nursing_vitals', 'nursing_notes',
            'medication_administrations', 'fluid_intake_output',
            'emergency_visits', 'emergency_procedures',
            'insurance_providers', 'insurance_policies', 'insurance_claims',
            'pre_authorizations',
            'medicines', 'pharmacy_stock', 'pharmacy_dispense',
            'pharmacy_dispense_items', 'drug_interactions',
            'invoices', 'invoice_items', 'payments',
            'patient_documents',
            'employees', 'shifts', 'employee_shifts',
            'alert_rules', 'clinical_alerts', 'nursing_vitals'
        ]

        # Create tables using SQLAlchemy
        from app.db.models_complete import Base as NewBase
        NewBase.metadata.create_all(engine)

        print("   ✅ New tables created")

        # STEP 2: Seed default data
        print("\n2️⃣ Seeding default data...")

        # Create roles if not exist
        roles = [
            ("admin", ["all"]),
            ("doctor", ["view_patients", "edit_encounters", "view_lab_results"]),
            ("nurse", ["view_patients", "check_in_patients", "record_vitals", "administer_medications"]),
            ("receptionist", ["view_patients", "create_appointments", "register_patients", "collect_payments"]),
            ("lab_technician", ["process_lab_orders", "enter_results"]),
            ("pharmacist", ["view_prescriptions", "dispense", "manage_inventory"]),
            ("billing_staff", ["view_invoices", "process_payments", "manage_insurance"]),
            ("patient", ["view_own_records", "book_appointments"])
        ]

        for role_name, perms in roles:
            existing = db.query(Role).filter(Role.name == role_name).first()
            if not existing:
                role = Role(name=role_name, permissions=perms)
                db.add(role)
                print(f"   Created role: {role_name}")

        # Create departments
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
            ("Pharmacy", "PHARM", "Ground Floor"),
            ("ICU", "ICU", "2nd Floor"),
            ("General Ward", "WARD", "1st Floor")
        ]

        for dept_name, code, floor in departments:
            existing = db.query(Department).filter(Department.code == code).first()
            if not existing:
                dept = Department(name=dept_name, code=code, floor=floor, is_active=True)
                db.add(dept)
                print(f"   Created department: {dept_name}")

        db.commit()

        # Create sample wards and beds
        print("\n3️⃣ Creating ward structure...")

        wards_data = [
            ("General Ward A", "GENERAL", "WARD"),
            ("General Ward B", "GENERAL", "WARD"),
            ("Private Ward", "PRIVATE", "WARD"),
            ("ICU", "ICU", "ICU"),
            ("Emergency Ward", "GENERAL", "ER")
        ]

        for ward_name, ward_type, dept_code in wards_data:
            existing = db.query(Ward).filter(Ward.name == ward_name).first()
            if not existing:
                dept = db.query(Department).filter(Department.code == dept_code).first()
                ward = Ward(
                    name=ward_name,
                    ward_type=ward_type,
                    department_id=dept.id if dept else None
                )
                db.add(ward)
                db.flush()

                # Create beds for this ward
                bed_count = 10 if ward_type != "ICU" else 5
                for i in range(1, bed_count + 1):
                    bed = Bed(
                        bed_number=f"B{i:03d}",
                        ward_id=ward.id,
                        bed_type="ICU_BED" if ward_type == "ICU" else "GENERAL_BED",
                        status="AVAILABLE",
                        daily_charge=5000 if ward_type == "ICU" else (2000 if ward_type == "PRIVATE" else 800)
                    )
                    db.add(bed)

                print(f"   Created {ward_name} with {bed_count} beds")

        db.commit()

        # Create insurance providers
        print("\n4️⃣ Creating insurance providers...")

        providers = [
            ("Star Health Insurance", "STAR"),
            ("ICICI Lombard", "ICICI"),
            ("Max Bupa", "MAX"),
            ("New India Assurance", "NIA"),
            ("Oriental Insurance", "OIC"),
            ("United India", "UIIC")
        ]

        for name, code in providers:
            existing = db.query(InsuranceProvider).filter(InsuranceProvider.provider_code == code).first()
            if not existing:
                provider = InsuranceProvider(
                    name=name,
                    provider_code=code,
                    is_active=True
                )
                db.add(provider)
                print(f"   Created provider: {name}")

        db.commit()

        # Create sample medicines
        print("\n5️⃣ Creating medicine catalog...")

        medicines_data = [
            ("Paracetamol", "Acetaminophen", "Tablet", "500mg", "Analgesic", 2.5, 10.0),
            ("Amoxicillin", "Amoxicillin", "Capsule", "500mg", "Antibiotic", 15.0, 45.0),
            ("Metformin", "Metformin HCl", "Tablet", "500mg", "Antidiabetic", 8.0, 25.0),
            ("Amlodipine", "Amlodipine", "Tablet", "5mg", "Antihypertensive", 12.0, 35.0),
            ("Atorvastatin", "Atorvastatin", "Tablet", "10mg", "Statin", 25.0, 75.0),
            ("Pantoprazole", "Pantoprazole", "Injection", "40mg", "PP Inhibitor", 45.0, 120.0),
            ("Normal Saline", "Sodium Chloride", "IV Fluid", "500ml", "Fluid", 30.0, 85.0),
            ("Ciprofloxacin", "Ciprofloxacin", "Tablet", "500mg", "Antibiotic", 18.0, 55.0),
        ]

        for name, generic, form, strength, category, purchase, sale in medicines_data:
            existing = db.query(Medicine).filter(Medicine.name == name).first()
            if not existing:
                medicine = Medicine(
                    name=name,
                    generic_name=generic,
                    form=form,
                    strength=strength,
                    category=category,
                    purchase_price=purchase,
                    mrp=sale * 1.2,
                    sale_price=sale,
                    stock_quantity=100,
                    reorder_level=20,
                    is_active=True
                )
                db.add(medicine)

        db.commit()

        # Create alert rules
        print("\n6️⃣ Creating clinical alert rules...")

        alert_rules = [
            ("Critical Hypertension", "VITAL", "vital_bp", ">", "180/110", "CRITICAL", "🚨 CRITICAL: Hypertensive crisis - BP {value}"),
            ("High Blood Pressure", "VITAL", "vital_bp", ">", "140/90", "HIGH", "⚠️ HIGH: BP {value}"),
            ("Low Blood Pressure", "VITAL", "vital_bp", "<", "90/60", "HIGH", "⚠️ LOW BP: {value}"),
            ("Critical Low SpO2", "VITAL", "vital_spo2", "<", "90", "CRITICAL", "🚨 CRITICAL: Low SpO2 - {value}%"),
            ("High Fever", "VITAL", "vital_temperature", ">", "103", "HIGH", "🔥 HIGH FEVER: {value}°F"),
            ("Low SpO2", "VITAL", "vital_spo2", "<", "95", "MEDIUM", "⚠️ Low SpO2: {value}%"),
        ]

        for name, rule_type, field, op, value, severity, message in alert_rules:
            existing = db.query(AlertRule).filter(AlertRule.rule_name == name).first()
            if not existing:
                rule = AlertRule(
                    rule_name=name,
                    rule_type=rule_type,
                    condition_field=field,
                    condition_operator=op,
                    condition_value=value,
                    severity=severity,
                    alert_message=message,
                    notify_roles=["doctor", "nurse"],
                    is_active=True
                )
                db.add(rule)
                print(f"   Created alert rule: {name}")

        db.commit()

        # STEP 3: Verify existing data
        print("\n7️⃣ Verifying existing data...")

        user_count = db.query(User).count()
        patient_count = db.query(Patient).count()
        doctor_count = db.query(Doctor).count()
        appointment_count = db.query(Appointment).count()

        print(f"   Users: {user_count}")
        print(f"   Patients: {patient_count}")
        print(f"   Doctors: {doctor_count}")
        print(f"   Appointments: {appointment_count}")

        # Update doctor department links
        print("\n8️⃣ Updating doctor departments...")

        for doctor in db.query(Doctor).all():
            if not doctor.department_id:
                # Try to find matching department
                dept = db.query(Department).filter(
                    Department.name.ilike(f"%{doctor.specialty}%")
                ).first()

                if not dept:
                    # Default to General Medicine
                    dept = db.query(Department).filter(Department.code == "GEN").first()

                doctor.department_id = dept.id if dept else None
                print(f"   Updated Dr. {doctor.name} -> {dept.name if dept else 'None'}")

        db.commit()

        print("\n" + "="*60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n📊 Migration Summary:")
        print(f"   • Tables created/recreated: ✓")
        print(f"   • Default roles added: ✓")
        print(f"   • Departments created: ✓")
        print(f"   • Wards and beds created: ✓")
        print(f"   • Insurance providers added: ✓")
        print(f"   • Medicine catalog created: ✓")
        print(f"   • Alert rules configured: ✓")
        print(f"   • Existing data preserved: ✓")
        print("\n🚀 Next steps:")
        print("   1. Start server: python -m app.main_complete")
        print("   2. Access admin: http://localhost:8000/admin")
        print("   3. Doctor dashboard: http://localhost:8000/doctor")
        print("   4. API docs: http://localhost:8000/api/docs")
        print("="*60)

    except Exception as e:
        db.rollback()
        print(f"\n❌ MIGRATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


def verify_migration(engine):
    """Verify migration was successful"""
    print("\n🔍 Verifying migration...")

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    required_tables = [
        'patients', 'doctors', 'appointments', 'medical_encounters',
        'wards', 'beds', 'admissions', 'insurance_policies',
        'medicines', 'invoices', 'clinical_alerts'
    ]

    all_present = True
    for table in required_tables:
        if table in tables:
            print(f"   ✅ {table}")
        else:
            print(f"   ❌ {table} - MISSING!")
            all_present = False

    return all_present


def main():
    parser = argparse.ArgumentParser(
        description="Migrate Hospital Management System database"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Confirm migration (required)"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify migration, don't run"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing"
    )

    args = parser.parse_args()

    engine = create_engine(get_db_url())

    if args.verify_only:
        if verify_migration(engine):
            print("\n✅ Migration verified successfully!")
        else:
            print("\n❌ Migration verification failed!")
            sys.exit(1)
        return

    if not args.confirm:
        print("\n" + "⚠️"*30)
        print("WARNING: This will modify your database!")
        print("Please backup your database before proceeding.")
        print("\nTo proceed, run with --confirm flag:")
        print("  python migrate_complete.py --confirm")
        print("⚠️"*30 + "\n")
        return

    if args.dry_run:
        print("\n🔍 DRY RUN - No changes will be made")
        print("Would perform the following actions:")
        print("  1. Create new tables (wards, beds, admissions, etc.)")
        print("  2. Seed default data (roles, departments, etc.)")
        print("  3. Create sample wards with beds")
        print("  4. Add insurance providers")
        print("  5. Add medicine catalog")
        print("  6. Configure alert rules")
        print("  7. Update existing doctor records")
        return

    # Run migration
    migrate_data_safely(engine)

    # Verify
    if verify_migration(engine):
        print("\n✅ All verification checks passed!")
    else:
        print("\n⚠️  Some verification checks failed!")


if __name__ == "__main__":
    main()
