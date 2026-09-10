"""
Check Database Contents
======================
Run this on your Mac to verify database has correct data.
"""

import sqlite3
import os

# Check for database file
db_files = [f for f in os.listdir('.') if f.endswith('.db')]

if not db_files:
    print("[ERROR] No database files found!")
    print("The server will create one when it starts.")
    exit(1)

for db_file in db_files:
    print(f"\n{'='*60}")
    print(f"Database: {db_file}")
    print('='*60)

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # List tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    if not tables:
        print("[WARNING] No tables found! Database is empty.")
        conn.close()
        continue

    print(f"\nTables: {', '.join(t[0] for t in tables)}")

    # Check doctors
    if any('doctors' in t[0] for t in tables):
        cursor.execute('SELECT id, name, specialty, consultation_fee, is_available FROM doctors;')
        doctors = cursor.fetchall()
        print(f"\n[OK] Doctors: {len(doctors)} found")
        for d in doctors:
            print(f"     ID:{d[0]} | {d[1]} | {d[2]} | Rs.{d[3]} | Available:{d[4]}")

        if len(doctors) == 0:
            print("     [WARNING] No doctors! Add doctors via Admin Dashboard.")
    else:
        print("\n[ERROR] 'doctors' table not found!")

    # Check users
    if any('users' in t[0] for t in tables):
        cursor.execute('SELECT id, phone_number, name FROM users;')
        users = cursor.fetchall()
        print(f"\n[OK] Users: {len(users)} found")
        for u in users:
            print(f"     ID:{u[0]} | {u[1]} | {u[2] or 'No name'}")
    else:
        print("\n[ERROR] 'users' table not found!")

    # Check appointments
    if any('appointments' in t[0] for t in tables):
        cursor.execute('SELECT id, user_id, doctor_id, status, is_deleted FROM appointments;')
        appts = cursor.fetchall()
        active = [a for a in appts if not a[4]]  # not deleted
        print(f"\n[OK] Appointments: {len(active)} active, {len(appts) - len(active)} deleted")
        for a in appts[:5]:  # Show first 5
            print(f"     ID:{a[0]} | User:{a[1]} | Doctor:{a[2]} | Status:{a[3]} | Deleted:{a[4]}")
    else:
        print("\n[ERROR] 'appointments' table not found!")

    conn.close()

print("\n" + "="*60)
print("RECOMMENDATIONS:")
print("="*60)
print("""
1. If NO DOCTORS found:
   - Open: http://localhost:8000/admin
   - Add doctors via the dashboard

2. If NO TABLES found:
   - Stop server (Ctrl+C)
   - Delete: rm hospital.db
   - Restart: uvicorn app.main:app --reload
   - Tables will be auto-created

3. For testing WhatsApp flow:
   - Minimum 2 doctors in same specialty needed
   - Test: Hi -> Book -> ENT -> 1 -> Tomorrow -> Confirm
""")
