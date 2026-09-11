"""
Database Migration Script: Upgrade existing database to enhanced schema
Run this AFTER backing up your database!
"""

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from app.db.session import Base, get_db_url
from app.db.models import (
    User, Role, Patient, PatientAlias, Doctor, Department,
    Appointment, MedicalEncounter, Prescription, PrescriptionItem,
    LabOrder, LabTest, AuditLog, AppointmentHistory
)
import datetime


def migrate_database():
    """Run all migration steps"""
    print("🏥 Hospital Database Migration")
    print("=" * 50)

    engine = create_engine(get_db_url())

    # Check existing tables
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    print(f"\n📊 Existing tables: {existing_tables}")

    # Step 1: Add new tables
    print("\n1️⃣ Creating new tables...")
    create_new_tables(engine)

    # Step 2: Migrate existing data
    print("\n2️⃣ Migrating existing data...")
    migrate_existing_data(engine)

    # Step 3: Add columns to existing tables
    print("\n3️⃣ Enhancing existing tables...")
    enhance_existing_tables(engine)

    # Step 4: Seed default data
    print("\n4️⃣ Seeding default data...")
    seed_default_data(engine)

    print("\n" + "=" * 50)
    print("✅ Migration completed successfully!")
    print("\nNext steps:")
    print("1. Update your webhook to use EnhancedDBService")
    print("2. Run: python -m app.db.seed_enhanced")
    print("3. Access Doctor Dashboard at: http://localhost:8000/dashboard/doctor")


def create_new_tables(engine):
    """Create all new tables"""

    # Create tables that don't exist yet
    new_tables = [
        Role, Patient, PatientAlias, Department,
        MedicalEncounter, Prescription, PrescriptionItem,
        LabOrder, LabTest, AuditLog
    ]

    for table_model in new_tables:
        table_name = table_model.__tablename__
        if table_name not in inspect(engine).get_table_names():
            print(f"   Creating table: {table_name}")
            table_model.__table__.create(engine)
        else:
            print(f"   Table exists: {table_name}")


def migrate_existing_data(engine):
    """Migrate data from old tables to new structure"""
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # Check if we have old appointments table data
        if "appointments" in [t.name for t in Base.metadata.tables.values()]:
            print("   Migrating appointments...")

            # Get all existing appointments
            result = db.execute(text("""
                SELECT id, user_id, doctor_id, appointment_date, status, is_deleted, deleted_at, created_at
                FROM appointments
            """))

            appointments = result.fetchall()
            print(f"   Found {len(appointments)} appointments to migrate")

            # For each appointment, link to patient if exists
            for appt in appointments:
                # Find or create patient from user
                user_result = db.execute(text(
                    "SELECT id, phone_number, name FROM users WHERE id = :uid"
                ), {"uid": appt.user_id})
                user = user_result.fetchone()

                if user:
                    # Check if patient already exists
                    patient_result = db.execute(text(
                        "SELECT id FROM patients WHERE primary_phone = :phone"
                    ), {"phone": user.phone_number})
                    patient = patient_result.fetchone()

                    if not patient:
                        # Create patient record
                        patient_id = f"PAT-{datetime.datetime.now().year}-{appt.user_id:06d}"

                        db.execute(text("""
                            INSERT INTO patients (
                                user_id, patient_id, first_name, last_name,
                                primary_phone, date_of_birth, gender, status, created_at
                            ) VALUES (
                                :uid, :pid, :first, :last, :phone,
                                :dob, :gender, :status, :created
                            )
                        """), {
                            "uid": user.id,
                            "pid": patient_id,
                            "first": user.name.split()[0] if user.name and " " in user.name else (user.name or "Unknown"),
                            "last": user.name.split()[-1] if user.name and " " in user.name else "",
                            "phone": user.phone_number,
                            "dob": datetime.date(1990, 1, 1),  # Default DOB
                            "gender": "unknown",
                            "status": "ACTIVE",
                            "created": appt.created_at
                        })

                        print(f"     Created patient for user {user.id}")

        # Add appointment numbers to existing appointments
        print("   Adding appointment numbers...")
        db.execute(text("""
            UPDATE appointments
            SET appointment_number = 'APT-2026-' || LPAD(id::text, 6, '0')
            WHERE appointment_number IS NULL
        """))

        db.commit()
        print("   Data migration completed")

    except Exception as e:
        db.rollback()
        print(f"   ⚠️ Error migrating data: {e}")
    finally:
        db.close()


def enhance_existing_tables(engine):
    """Add new columns to existing tables"""

    enhancements = [
        ("users", [
            ("email", "VARCHAR(255)"),
            ("password_hash", "VARCHAR(255)"),
            ("role_id", "INTEGER"),
            ("is_staff", "BOOLEAN DEFAULT FALSE"),
            ("is_active", "BOOLEAN DEFAULT TRUE"),
            ("updated_at", "TIMESTAMP")
        ]),
        ("doctors", [
            ("user_id", "INTEGER"),
            ("qualification", "VARCHAR(255)"),
            ("registration_number", "VARCHAR(100)"),
            ("department_id", "INTEGER"),
            ("follow_up_fee", "FLOAT"),
            ("weekly_schedule", "JSON"),
            ("slot_duration_minutes", "INTEGER DEFAULT 30"),
            ("max_daily_patients", "INTEGER DEFAULT 20")
        ]),
        ("appointments", [
            ("appointment_number", "VARCHAR(20)"),
            ("patient_id", "INTEGER"),
            ("token_number", "INTEGER"),
            ("duration_minutes", "INTEGER DEFAULT 30"),
            ("chief_complaint", "VARCHAR(500)"),
            ("type", "VARCHAR(20) DEFAULT 'OPD'")
        ])
    ]

    with engine.connect() as conn:
        for table_name, columns in enhancements:
            for col_name, col_type in columns:
                try:
                    conn.execute(text(f"""
                        ALTER TABLE {table_name}
                        ADD COLUMN IF NOT EXISTS {col_name} {col_type}
                    """))
                    print(f"   Added column: {table_name}.{col_name}")
                except Exception as e:
                    print(f"   Column exists or error: {table_name}.{col_name} - {e}")

        conn.commit()


def seed_default_data(engine):
    """Seed default roles and admin user"""
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # Create default roles
        roles = [
            ("admin", ["all"]),
            ("doctor", ["view_patients", "edit_encounters", "view_lab_results"]),
            ("nurse", ["view_patients", "check_in_patients", "record_vitals"]),
            ("receptionist", ["view_patients", "create_appointments", "register_patients"]),
            ("lab_technician", ["process_lab_orders", "enter_results"]),
            ("pharmacist", ["view_prescriptions", "dispense"]),
            ("patient", ["view_own_records", "book_appointments"])
        ]

        for role_name, perms in roles:
            existing = db.execute(text(
                "SELECT id FROM roles WHERE name = :name"
            ), {"name": role_name}).fetchone()

            if not existing:
                db.execute(text("""
                    INSERT INTO roles (name, permissions, created_at)
                    VALUES (:name, :perms, NOW())
                """), {"name": role_name, "perms": str(perms)})
                print(f"   Created role: {role_name}")

        # Create default departments
        departments = [
            ("Cardiology", "CARD"),
            ("Pediatrics", "PEDS"),
            ("Neurology", "NEURO"),
            ("Orthopedics", "ORTHO"),
            ("Dermatology", "DERMA"),
            ("General Medicine", "GEN"),
            ("Laboratory", "LAB"),
            ("Radiology", "RAD"),
            ("Emergency", "ER"),
            ("Pharmacy", "PHARM")
        ]

        for dept_name, code in departments:
            existing = db.execute(text(
                "SELECT id FROM departments WHERE code = :code"
            ), {"code": code}).fetchone()

            if not existing:
                db.execute(text("""
                    INSERT INTO departments (name, code, is_active)
                    VALUES (:name, :code, TRUE)
                """), {"name": dept_name, "code": code})
                print(f"   Created department: {dept_name}")

        db.commit()
        print("   Default data seeded")

    except Exception as e:
        db.rollback()
        print(f"   ⚠️ Error seeding data: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate hospital database to enhanced schema"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Confirm migration (required)"
    )

    args = parser.parse_args()

    if not args.confirm:
        print("⚠️ WARNING: This will modify your database!")
        print("Please backup your database before proceeding.")
        print("\nTo proceed, run with --confirm flag:")
        print("  python -m app.db.migrate_to_enhanced --confirm")
    else:
        migrate_database()
