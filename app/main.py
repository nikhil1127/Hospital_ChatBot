from fastapi import FastAPI, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
from app.api.webhook import router as webhook_router
from app.db.session import get_db, create_tables
from app.db.models import Appointment, User, Doctor, AppointmentHistory

app = FastAPI(title="Multispeciality Hospital Bot")

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    print("✅ Database tables created/verified")

# Include the webhook routes (both /whatsapp and /whatsapp/)
app.include_router(webhook_router)

@app.get("/")
async def root():
    return {"message": "Hospital Bot Server is running!"}


def get_base_template(title, content, active_tab="dashboard"):
    """Base template with navigation"""
    nav_items = {
        "dashboard": ("/admin", "📊 Dashboard"),
        "today": ("/admin/today", "📅 Today"),
        "completed": ("/admin/completed", "✓ Completed"),
        "cancelled": ("/admin/cancelled", "✕ Cancelled"),
        "deleted": ("/admin/deleted", "🗑 Deleted"),
        "doctors": ("/admin/doctors", "👨‍⚕️ Doctors"),
    }

    nav_html = ""
    for key, (url, label) in nav_items.items():
        active_class = "active" if key == active_tab else ""
        nav_html += f'<a href="{url}" class="nav-item {active_class}">{label}</a>'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - MedCare Hospital</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
               background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
               min-height: 100vh; color: #333; }}

        /* Sidebar */
        .sidebar {{ width: 260px; background: white; height: 100vh; position: fixed;
                   left: 0; top: 0; box-shadow: 0 0 20px rgba(0,0,0,0.1); z-index: 100; }}
        .sidebar-header {{ padding: 30px; text-align: center; border-bottom: 1px solid #e5e7eb; }}
        .logo {{ width: 60px; height: 60px; background: linear-gradient(135deg, #2563eb, #7c3aed);
                 border-radius: 15px; display: flex; align-items: center; justify-content: center;
                 margin: 0 auto 15px; font-size: 28px; }}
        .sidebar-header h1 {{ font-size: 1.3rem; color: #1f2937; margin-bottom: 5px; }}
        .sidebar-header p {{ font-size: 0.85rem; color: #6b7280; }}

        .nav-menu {{ padding: 20px 0; }}
        .nav-item {{ display: block; padding: 12px 24px; color: #6b7280; text-decoration: none;
                    font-weight: 500; border-left: 3px solid transparent;
                    transition: all 0.2s; }}
        .nav-item:hover {{ background: #f3f4f6; color: #2563eb; }}
        .nav-item.active {{ background: #eff6ff; color: #2563eb; border-left-color: #2563eb; }}

        /* Main Content */
        .main-content {{ margin-left: 260px; padding: 30px; min-height: 100vh; }}

        /* Cards */
        .card {{ background: white; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                 overflow: hidden; margin-bottom: 24px; }}
        .card-header {{ padding: 24px 30px; background: linear-gradient(135deg, #2563eb, #7c3aed);
                       color: white; display: flex; justify-content: space-between; align-items: center; }}
        .card-header h2 {{ font-size: 1.4rem; font-weight: 600; }}

        /* Stats */
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                      gap: 20px; margin-bottom: 24px; }}
        .stat-card {{ background: white; padding: 24px; border-radius: 15px;
                     box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; }}
        .stat-card h3 {{ font-size: 0.85rem; color: #6b7280; text-transform: uppercase; margin-bottom: 10px; }}
        .stat-card .number {{ font-size: 2.5rem; font-weight: 700; color: #2563eb; }}

        /* Table */
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ background: #f9fafb; padding: 14px 20px; text-align: left;
              font-weight: 600; font-size: 0.75rem; text-transform: uppercase; color: #6b7280; }}
        td {{ padding: 16px 20px; border-bottom: 1px solid #e5e7eb; font-size: 0.9rem; }}
        tr:hover {{ background: #f9fafb; }}

        .status {{ display: inline-block; padding: 5px 12px; border-radius: 20px;
                 font-size: 0.75rem; font-weight: 600; }}
        .status-confirmed {{ background: #d1fae5; color: #065f46; }}
        .status-pending {{ background: #fef3c7; color: #92400e; }}
        .status-cancelled {{ background: #fee2e2; color: #991b1b; }}
        .status-completed {{ background: #dbeafe; color: #1e40af; }}
        .status-deleted {{ background: #f3f4f6; color: #6b7280; }}

        .phone {{ font-family: monospace; color: #2563eb; font-size: 0.85rem; }}
        .fee {{ font-weight: 700; color: #10b981; }}

        /* Actions */
        .actions {{ display: flex; gap: 8px; }}
        .btn-action {{ width: 32px; height: 32px; border-radius: 8px; display: flex;
                      align-items: center; justify-content: center; text-decoration: none;
                      font-size: 0.9rem; transition: all 0.2s; cursor: pointer; border: none; }}
        .btn-action:hover {{ transform: scale(1.1); }}
        .btn-complete {{ background: #d1fae5; color: #065f46; }}
        .btn-cancel {{ background: #fef3c7; color: #92400e; }}
        .btn-delete {{ background: #fee2e2; color: #991b1b; }}
        .btn-restore {{ background: #dbeafe; color: #1e40af; }}

        .empty-state {{ text-align: center; padding: 60px 20px; color: #6b7280; }}
        .empty-icon {{ font-size: 4rem; margin-bottom: 20px; }}

        /* Date Filter */
        .date-filter {{ display: flex; gap: 10px; margin-bottom: 20px; }}
        .date-filter input, .date-filter select {{ padding: 10px 15px; border: 1px solid #e5e7eb;
                                                   border-radius: 8px; font-size: 0.9rem; }}
        .date-filter button {{ padding: 10px 20px; background: #2563eb; color: white;
                              border: none; border-radius: 8px; cursor: pointer; font-weight: 500; }}
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-header">
            <div class="logo">🏥</div>
            <h1>MedCare Hospital</h1>
            <p>Admin Dashboard</p>
        </div>
        <nav class="nav-menu">
            {nav_html}
        </nav>
    </div>

    <div class="main-content">
        {content}
    </div>
</body>
</html>'''


def generate_appointment_table(appointments, db, show_actions=True, show_restore=False):
    """Generate HTML table for appointments"""
    if not appointments:
        return '''<div class="empty-state">
            <div class="empty-icon">📭</div>
            <h3>No Appointments Found</h3>
            <p>No appointments in this category.</p>
        </div>'''

    rows = ""
    for apt in appointments:
        patient = db.query(User).filter(User.id == apt.user_id).first()
        doctor = db.query(Doctor).filter(Doctor.id == apt.doctor_id).first()

        patient_name = patient.name if patient else "Unknown"
        phone = patient.phone_number if patient else "N/A"
        doctor_name = doctor.name if doctor else "Unknown"
        specialty = doctor.specialty if doctor else "N/A"
        date_str = apt.appointment_date.strftime("%Y-%m-%d %H:%M") if apt.appointment_date else "N/A"
        fee = doctor.consultation_fee if doctor else 0
        status = apt.status if hasattr(apt, 'status') else 'unknown'

        actions = ""
        if show_actions:
            if status not in ['completed', 'cancelled', 'deleted']:
                actions = f'''<div class="actions">
                    <a href="/admin/appointment/{apt.id}/complete" class="btn-action btn-complete" title="Mark Complete">✓</a>
                    <a href="/admin/appointment/{apt.id}/cancel" class="btn-action btn-cancel" title="Cancel">✕</a>
                    <a href="/admin/appointment/{apt.id}/soft-delete" class="btn-action btn-delete" title="Delete" onclick="return confirm('Delete this appointment?')">🗑</a>
                </div>'''
            else:
                actions = "-"
        elif show_restore:
            actions = f'''<div class="actions">
                <a href="/admin/appointment/{apt.id}/restore" class="btn-action btn-restore" title="Restore">↩</a>
            </div>'''

        rows += f'''
        <tr>
            <td>#{apt.id}</td>
            <td><strong>{patient_name}</strong></td>
            <td class="phone">{phone}</td>
            <td>{doctor_name}</td>
            <td>{specialty}</td>
            <td>{date_str}</td>
            <td class="fee">₹{fee}</td>
            <td><span class="status status-{status}">{status.title()}</span></td>
            {'<td>' + actions + '</td>' if show_actions or show_restore else ''}
        </tr>
        '''

    action_header = '<th>Actions</th>' if show_actions or show_restore else ''

    return f'''
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
                {action_header}
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    '''


# ========== MAIN DASHBOARD ==========
@app.get("/admin")
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """Main dashboard - shows active appointments only"""
    appointments = db.query(Appointment).filter(
        Appointment.is_deleted == False,
        Appointment.status.in_(["confirmed", "pending"])
    ).order_by(Appointment.appointment_date.desc()).all()

    # Stats
    total_active = len(appointments)
    confirmed = len([a for a in appointments if a.status == "confirmed"])
    pending = len([a for a in appointments if a.status == "pending"])

    today = datetime.now().date()
    today_count = len([a for a in appointments if a.appointment_date and a.appointment_date.date() == today])

    # Get counts for other sections
    completed_count = db.query(AppointmentHistory).count()
    cancelled_count = db.query(Appointment).filter_by(status="cancelled", is_deleted=False).count()
    deleted_count = db.query(Appointment).filter_by(is_deleted=True).count()

    content = f'''
    <div class="stats-grid">
        <div class="stat-card">
            <h3>Active Appointments</h3>
            <div class="number">{total_active}</div>
        </div>
        <div class="stat-card">
            <h3>Confirmed</h3>
            <div class="number">{confirmed}</div>
        </div>
        <div class="stat-card">
            <h3>Pending</h3>
            <div class="number">{pending}</div>
        </div>
        <div class="stat-card">
            <h3>Today's Appointments</h3>
            <div class="number">{today_count}</div>
        </div>
    </div>

    <div class="stats-grid" style="margin-top: 20px;">
        <div class="stat-card" style="background: linear-gradient(135deg, #d1fae5, #a7f3d0);">
            <h3 style="color: #065f46;">Completed History</h3>
            <div class="number" style="color: #065f46;">{completed_count}</div>
        </div>
        <div class="stat-card" style="background: linear-gradient(135deg, #fef3c7, #fde68a);">
            <h3 style="color: #92400e;">Cancelled</h3>
            <div class="number" style="color: #92400e;">{cancelled_count}</div>
        </div>
        <div class="stat-card" style="background: linear-gradient(135deg, #fee2e2, #fecaca);">
            <h3 style="color: #991b1b;">Deleted</h3>
            <div class="number" style="color: #991b1b;">{deleted_count}</div>
        </div>
    </div>

    <div class="card">
        <div class="card-header">
            <h2>📋 Active Appointments</h2>
            <span style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 0.85rem;">{total_active} total</span>
        </div>
        {generate_appointment_table(appointments, db)}
    </div>
    '''

    return HTMLResponse(content=get_base_template("Dashboard", content, "dashboard"))


# ========== TODAY'S APPOINTMENTS ==========
@app.get("/admin/today")
async def admin_today(request: Request, db: Session = Depends(get_db)):
    """Show only today's appointments"""
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    appointments = db.query(Appointment).filter(
        Appointment.is_deleted == False,
        Appointment.appointment_date >= today_start,
        Appointment.appointment_date <= today_end
    ).order_by(Appointment.appointment_date).all()

    # Also get tomorrow's
    tomorrow = today + timedelta(days=1)
    tomorrow_start = datetime.combine(tomorrow, datetime.min.time())
    tomorrow_end = datetime.combine(tomorrow, datetime.max.time())
    tomorrow_appointments = db.query(Appointment).filter(
        Appointment.is_deleted == False,
        Appointment.appointment_date >= tomorrow_start,
        Appointment.appointment_date <= tomorrow_end
    ).order_by(Appointment.appointment_date).all()

    content = f'''
    <div class="stats-grid">
        <div class="stat-card" style="background: linear-gradient(135deg, #2563eb, #7c3aed); color: white;">
            <h3 style="color: rgba(255,255,255,0.8);">Today's Total</h3>
            <div class="number" style="color: white;">{len(appointments)}</div>
        </div>
        <div class="stat-card">
            <h3>Confirmed Today</h3>
            <div class="number">{len([a for a in appointments if a.status == 'confirmed'])}</div>
        </div>
        <div class="stat-card">
            <h3>Pending Today</h3>
            <div class="number">{len([a for a in appointments if a.status == 'pending'])}</div>
        </div>
        <div class="stat-card">
            <h3>Tomorrow</h3>
            <div class="number">{len(tomorrow_appointments)}</div>
        </div>
    </div>

    <div class="card">
        <div class="card-header">
            <h2>📅 Today's Appointments ({today.strftime('%A, %B %d, %Y')})</h2>
        </div>
        {generate_appointment_table(appointments, db)}
    </div>
    '''

    return HTMLResponse(content=get_base_template("Today's Appointments", content, "today"))


# ========== COMPLETED APPOINTMENTS (HISTORY) ==========
@app.get("/admin/completed")
async def admin_completed(request: Request, db: Session = Depends(get_db)):
    """Show completed appointments from history"""
    history = db.query(AppointmentHistory).filter(
        AppointmentHistory.final_status == "completed"
    ).order_by(AppointmentHistory.completed_at.desc()).all()

    # Calculate revenue
    total_revenue = 0
    for h in history:
        doctor = db.query(Doctor).filter(Doctor.id == h.doctor_id).first()
        if doctor:
            total_revenue += doctor.consultation_fee

    content = f'''
    <div class="stats-grid">
        <div class="stat-card" style="background: linear-gradient(135deg, #d1fae5, #a7f3d0);">
            <h3 style="color: #065f46;">Total Completed</h3>
            <div class="number" style="color: #065f46;">{len(history)}</div>
        </div>
        <div class="stat-card" style="background: linear-gradient(135deg, #dbeafe, #bfdbfe);">
            <h3 style="color: #1e40af;">Total Revenue</h3>
            <div class="number" style="color: #1e40af;">₹{total_revenue}</div>
        </div>
    </div>

    <div class="card">
        <div class="card-header" style="background: linear-gradient(135deg, #10b981, #059669);">
            <h2>✓ Completed Appointments History</h2>
        </div>
        {generate_appointment_table(history, db, show_actions=False)}
    </div>
    '''

    return HTMLResponse(content=get_base_template("Completed Appointments", content, "completed"))


# ========== CANCELLED APPOINTMENTS ==========
@app.get("/admin/cancelled")
async def admin_cancelled(request: Request, db: Session = Depends(get_db)):
    """Show cancelled appointments"""
    appointments = db.query(Appointment).filter(
        Appointment.status == "cancelled",
        Appointment.is_deleted == False
    ).order_by(Appointment.appointment_date.desc()).all()

    content = f'''
    <div class="stats-grid">
        <div class="stat-card" style="background: linear-gradient(135deg, #fef3c7, #fde68a);">
            <h3 style="color: #92400e;">Total Cancelled</h3>
            <div class="number" style="color: #92400e;">{len(appointments)}</div>
        </div>
    </div>

    <div class="card">
        <div class="card-header" style="background: linear-gradient(135deg, #f59e0b, #d97706);">
            <h2>✕ Cancelled Appointments</h2>
        </div>
        {generate_appointment_table(appointments, db, show_actions=True)}
    </div>
    '''

    return HTMLResponse(content=get_base_template("Cancelled Appointments", content, "cancelled"))


# ========== DELETED APPOINTMENTS (TRASH) ==========
@app.get("/admin/deleted")
async def admin_deleted(request: Request, db: Session = Depends(get_db)):
    """Show soft-deleted appointments"""
    appointments = db.query(Appointment).filter(
        Appointment.is_deleted == True
    ).order_by(Appointment.deleted_at.desc()).all()

    content = f'''
    <div class="stats-grid">
        <div class="stat-card" style="background: linear-gradient(135deg, #fee2e2, #fecaca);">
            <h3 style="color: #991b1b;">Deleted Items</h3>
            <div class="number" style="color: #991b1b;">{len(appointments)}</div>
        </div>
    </div>

    <div class="card">
        <div class="card-header" style="background: linear-gradient(135deg, #ef4444, #dc2626);">
            <h2>🗑 Deleted Appointments (Trash)</h2>
            <span style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 0.85rem;">Can be restored</span>
        </div>
        {generate_appointment_table(appointments, db, show_actions=False, show_restore=True)}
    </div>
    '''

    return HTMLResponse(content=get_base_template("Deleted Appointments", content, "deleted"))


# ========== APPOINTMENT ACTIONS ==========
@app.get("/admin/appointment/{appointment_id}/complete")
async def complete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Mark appointment as completed and move to history"""
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.is_deleted == False
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Create history record
    history = AppointmentHistory(
        original_appointment_id=appointment.id,
        user_id=appointment.user_id,
        doctor_id=appointment.doctor_id,
        appointment_date=appointment.appointment_date,
        final_status="completed",
        notes="Marked as completed"
    )
    db.add(history)

    # Soft delete from active
    appointment.status = "deleted"
    appointment.is_deleted = True
    appointment.deleted_at = datetime.now()

    db.commit()
    return RedirectResponse(url="/admin/completed", status_code=302)


@app.get("/admin/appointment/{appointment_id}/cancel")
async def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Mark appointment as cancelled and move to history"""
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.is_deleted == False
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Create history record
    history = AppointmentHistory(
        original_appointment_id=appointment.id,
        user_id=appointment.user_id,
        doctor_id=appointment.doctor_id,
        appointment_date=appointment.appointment_date,
        final_status="cancelled",
        notes="Cancelled by staff"
    )
    db.add(history)

    # Soft delete from active
    appointment.status = "deleted"
    appointment.is_deleted = True
    appointment.deleted_at = datetime.now()

    db.commit()
    return RedirectResponse(url="/admin/cancelled", status_code=302)


@app.get("/admin/appointment/{appointment_id}/soft-delete")
async def soft_delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Soft delete appointment (move to trash)"""
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.is_deleted == False
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.is_deleted = True
    appointment.deleted_at = datetime.now()
    db.commit()

    return RedirectResponse(url="/admin/deleted", status_code=302)


@app.get("/admin/appointment/{appointment_id}/restore")
async def restore_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Restore soft-deleted appointment"""
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.is_deleted == True
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.is_deleted = False
    appointment.deleted_at = None
    appointment.status = "pending"  # Reset to pending
    db.commit()

    return RedirectResponse(url="/admin", status_code=302)


# ========== DOCTORS PAGE ==========
@app.get("/admin/doctors")
async def admin_doctors(request: Request, db: Session = Depends(get_db)):
    """View all doctors"""
    doctors = db.query(Doctor).all()

    rows = ""
    for doc in doctors:
        status_class = "status-confirmed" if doc.is_available else "status-cancelled"
        status_text = "Available" if doc.is_available else "Unavailable"
        rows += f'''
        <tr>
            <td>#{doc.id}</td>
            <td><strong>{doc.name}</strong></td>
            <td>{doc.specialty}</td>
            <td>{doc.experience_years} years</td>
            <td class="fee">₹{doc.consultation_fee}</td>
            <td>{doc.availability_slots}</td>
            <td><span class="status {status_class}">{status_text}</span></td>
        </tr>
        '''

    content = f'''
    <div class="card">
        <div class="card-header">
            <h2>👨‍⚕️ Doctors Directory</h2>
            <span style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 0.85rem;">{len(doctors)} doctors</span>
        </div>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Specialty</th>
                    <th>Experience</th>
                    <th>Fee</th>
                    <th>Availability</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
    '''

    return HTMLResponse(content=get_base_template("Doctors", content, "doctors"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
