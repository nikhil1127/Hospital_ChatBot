from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime
import os
from app.api.webhook import router as webhook_router
from app.db.session import get_db
from app.db.models import Appointment, User, Doctor

app = FastAPI(title="Multispeciality Hospital Bot")

# Include the webhook routes
app.include_router(webhook_router)

@app.get("/")
async def root():
    return {"message": "Hospital Bot Server is running!"}

# Simple HTML template as string
ADMIN_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedCare Hospital - Admin Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); margin-bottom: 30px; text-align: center; }}
        .logo {{ width: 80px; height: 80px; background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%); border-radius: 20px; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; font-size: 36px; }}
        h1 {{ color: #1f2937; font-size: 2em; margin-bottom: 5px; }}
        .subtitle {{ color: #6b7280; font-size: 1.1em; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: white; padding: 25px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); text-align: center; }}
        .stat-card h3 {{ color: #6b7280; font-size: 0.9em; text-transform: uppercase; margin-bottom: 10px; }}
        .stat-card .number {{ font-size: 2.5em; font-weight: bold; color: #2563eb; }}
        .appointments-section {{ background: white; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); overflow: hidden; }}
        .section-header {{ padding: 25px 30px; background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%); color: white; }}
        .section-header h2 {{ font-size: 1.5em; }}
        table {{ width: 100%; border-collapse: collapse; }}
        thead {{ background: #f9fafb; }}
        th {{ padding: 15px; text-align: left; font-weight: 600; color: #374151; font-size: 0.8em; text-transform: uppercase; }}
        td {{ padding: 15px; border-bottom: 1px solid #e5e7eb; }}
        tbody tr:hover {{ background: #f9fafb; }}
        .status {{ display: inline-block; padding: 5px 15px; border-radius: 20px; font-size: 0.85em; font-weight: 600; }}
        .status-confirmed {{ background: #d1fae5; color: #065f46; }}
        .status-pending {{ background: #fef3c7; color: #92400e; }}
        .status-cancelled {{ background: #fee2e2; color: #991b1b; }}
        .phone {{ font-family: monospace; color: #2563eb; }}
        .fee {{ font-weight: 700; color: #10b981; }}
        .empty-state {{ text-align: center; padding: 60px 20px; color: #6b7280; }}
        .empty-icon {{ font-size: 4em; margin-bottom: 20px; }}
        footer {{ text-align: center; padding: 20px; color: rgba(255,255,255,0.8); margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">🏥</div>
            <h1>MedCare Hospital</h1>
            <p class="subtitle">Appointment Management Dashboard</p>
        </header>

        <div class="stats">
            <div class="stat-card">
                <h3>Total Appointments</h3>
                <div class="number">{total_appointments}</div>
            </div>
            <div class="stat-card">
                <h3>Confirmed</h3>
                <div class="number">{confirmed_count}</div>
            </div>
            <div class="stat-card">
                <h3>Pending</h3>
                <div class="number">{pending_count}</div>
            </div>
            <div class="stat-card">
                <h3>Today</h3>
                <div class="number">{today_count}</div>
            </div>
        </div>

        <div class="appointments-section">
            <div class="section-header">
                <h2>📋 Recent Appointments</h2>
            </div>
            {appointments_table}
        </div>

        <footer>
            <p>Hospital ChatBot System © 2026</p>
        </footer>
    </div>
</body>
</html>'''

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """
    Admin dashboard to view all appointments
    """
    try:
        # Get all appointments with patient and doctor info
        appointments = db.query(Appointment).order_by(Appointment.appointment_date.desc()).all()

        # Calculate stats
        total = len(appointments)
        confirmed = len([a for a in appointments if a.status == "confirmed"])
        pending = len([a for a in appointments if a.status == "pending"])

        # Today's appointments
        today = datetime.now().date()
        today_count = len([a for a in appointments if a.appointment_date and a.appointment_date.date() == today])

        # Build appointments table
        if appointments:
            table_rows = ""
            for apt in appointments:
                patient = db.query(User).filter(User.id == apt.user_id).first()
                doctor = db.query(Doctor).filter(Doctor.id == apt.doctor_id).first()

                patient_name = patient.name if patient else "Unknown"
                phone = patient.phone_number if patient else "N/A"
                doctor_name = doctor.name if doctor else "Unknown"
                specialty = doctor.specialty if doctor else "N/A"
                date_str = apt.appointment_date.strftime("%Y-%m-%d %H:%M") if apt.appointment_date else "N/A"
                fee = doctor.consultation_fee if doctor else 0
                status = apt.status

                table_rows += f"""
                <tr>
                    <td>#{apt.id}</td>
                    <td>{patient_name}</td>
                    <td class="phone">{phone}</td>
                    <td>{doctor_name}</td>
                    <td>{specialty}</td>
                    <td>{date_str}</td>
                    <td class="fee">₹{fee}</td>
                    <td><span class="status status-{status}">{status.title()}</span></td>
                </tr>
                """

            appointments_table = f"""
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Patient</th>
                        <th>Phone</th>
                        <th>Doctor</th>
                        <th>Specialty</th>
                        <th>Date & Time</th>
                        <th>Fee</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
            """
        else:
            appointments_table = """
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                <h3>No Appointments Yet</h3>
                <p>Appointments will appear here when patients book through WhatsApp.</p>
            </div>
            """

        # Fill template
        html_content = ADMIN_TEMPLATE.format(
            total_appointments=total,
            confirmed_count=confirmed,
            pending_count=pending,
            today_count=today_count,
            appointments_table=appointments_table
        )

        return HTMLResponse(content=html_content)

    except Exception as e:
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body style="font-family: Arial; padding: 50px;">
            <h1 style="color: #dc2626;">Dashboard Error</h1>
            <p style="color: #666;">{str(e)}</p>
            <p>Please check that the database is initialized.</p>
            <a href="/" style="color: #2563eb;">Go Home</a>
        </body>
        </html>
        """)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
