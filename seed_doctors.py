"""
Seed Sample Doctors
===================
Run this to add sample doctors to the database for testing.
"""

import os
import sys

# Set environment
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL', 'sqlite:///./hospital.db')

# Import after setting env
from app.db.session import SessionLocal, create_tables
from app.db.models import Doctor

def seed_doctors():
    """Add sample doctors if none exist"""

    # Create tables if not exist
    create_tables()

    db = SessionLocal()

    # Check if doctors already exist
    existing = db.query(Doctor).count()
    if existing > 0:
        print(f"[INFO] {existing} doctors already exist.")
        print("To re-seed, delete the database first: rm hospital.db")
        db.close()
        return

    # Sample doctors
    doctors = [
        Doctor(name="Dr. Sarah Johnson", specialty="ENT", experience_years=10, consultation_fee=500, availability_slots="9-12,14-17", is_available=True),
        Doctor(name="Dr. Raj Patel", specialty="ENT", experience_years=8, consultation_fee=450, availability_slots="10-13,16-19", is_available=True),
        Doctor(name="Dr. Michael Chen", specialty="Cardiology", experience_years=15, consultation_fee=800, availability_slots="9-12,15-18", is_available=True),
        Doctor(name="Dr. Emily Davis", specialty="Pediatrics", experience_years=12, consultation_fee=600, availability_slots="9-17", is_available=True),
        Doctor(name="Dr. James Wilson", specialty="Neurology", experience_years=20, consultation_fee=1000, availability_slots="10-14", is_available=True),
        Doctor(name="Dr. Lisa Kumar", specialty="Dermatology", experience_years=9, consultation_fee=550, availability_slots="11-15", is_available=True),
    ]

    for doc in doctors:
        db.add(doc)

    db.commit()
    print(f"[OK] Added {len(doctors)} doctors:")
    for doc in doctors:
        print(f"     - {doc.name} ({doc.specialty}) - Rs.{doc.consultation_fee}")

    db.close()
    print("\n[OK] Done! You can now test the WhatsApp booking flow.")

if __name__ == "__main__":
    seed_doctors()
