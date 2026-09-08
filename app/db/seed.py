from app.db.session import SessionLocal
from app.db.models import Doctor

def seed_doctors():
    """
    Seeds the database with a set of fake doctors for testing.
    """
    db = SessionLocal()
    try:
        # Check if doctors already exist to avoid duplicates
        existing_docs = db.query(Doctor).all()
        if existing_docs:
            print("Doctors already exist in the database. Skipping seeding.")
            return

        print("Seeding doctors into the database...")

        sample_doctors = [
            Doctor(name="Dr. Sarah Smith", specialty="Cardiology", experience_years=15, consultation_fee=500.0, availability_slots="Mon 09:00-12:00, Wed 14:00-17:00", is_available=True),
            Doctor(name="Dr. James Wilson", specialty="Pediatrics", experience_years=10, consultation_fee=300.0, availability_slots="Tue 10:00-13:00, Thu 10:00-13:00", is_available=True),
            Doctor(name="Dr. Emily Chen", specialty="Neurology", experience_years=12, consultation_fee=600.0, availability_slots="Mon 15:00-18:00, Fri 09:00-12:00", is_available=True),
            Doctor(name="Dr. Michael Brown", specialty="Orthopedics", experience_years=20, consultation_fee=400.0, availability_slots="Wed 09:00-12:00, Thu 14:00-17:00", is_available=True),
            Doctor(name="Dr. Priya Sharma", specialty="Dermatology", experience_years=8, consultation_fee=300.0, availability_slots="Tue 14:00-17:00, Fri 14:00-17:00", is_available=True),
            Doctor(name="Dr. Robert Taylor", specialty="General Medicine", experience_years=25, consultation_fee=200.0, availability_slots="Mon 09:00-17:00, Tue 09:00-17:00", is_available=True),
        ]

        db.add_all(sample_doctors)
        db.commit()
        print(f"Successfully seeded {len(sample_doctors)} doctors!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_doctors()
