"""
COMPLETE Hospital Management System - Main Entry Point
Includes: WhatsApp Bot + Web Dashboards + All Modules
"""

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.db.session import SessionLocal, engine, Base
from app.api.webhook import router as webhook_router
from app.api.complete_routes import router as api_router
from app.core.complete_db_service import CompleteHospitalDBService

from app.ui.ipd_dashboard import IPD_DASHBOARD_HTML
from app.ui.pharmacy_dashboard import PHARMACY_DASHBOARD_HTML
from app.ui.billing_dashboard import BILLING_DASHBOARD_HTML
from app.ui.nursing_dashboard import NURSING_DASHBOARD_HTML
from app.ui.emergency_dashboard import EMERGENCY_DASHBOARD_HTML
from app.ui.patient_portal import PATIENT_PORTAL_HTML

# Create all tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="MedCare Hospital Management System",
    description="Complete Hospital Management with EHR, IPD, Insurance, Pharmacy, Billing",
    version="3.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Event handlers
@app.on_event("startup")
async def startup_event():
    print("=" * 60)
    print("🏥 MEDCARE HOSPITAL MANAGEMENT SYSTEM v3.0")
    print("=" * 60)
    print("\n🌐 WEB DASHBOARDS:")
    print("   • Main Portal:       http://localhost:8000/")
    print("   • Doctor:            http://localhost:8000/doctor")
    print("   • Admin:             http://localhost:8000/admin")
    print("   • IPD:               http://localhost:8000/ipd")
    print("   • Nursing:           http://localhost:8000/nursing")
    print("   • Pharmacy:          http://localhost:8000/pharmacy")
    print("   • Billing:           http://localhost:8000/billing")
    print("   • Emergency:         http://localhost:8000/emergency")
    print("   • Patient Portal:    http://localhost:8000/patient")
    print("\n📱 INTEGRATIONS:")
    print("   • WhatsApp Bot:      POST /whatsapp")
    print("   • API Docs:          GET  /api/docs")
    print("\n🔐 MODULES ENABLED:")
    print("   ✓ Patient Management (EMPI)")
    print("   ✓ OPD / Appointments")
    print("   ✓ EHR / Medical Records")
    print("   ✓ IPD / Bed Management")
    print("   ✓ Insurance / TPA")
    print("   ✓ Pharmacy / Inventory")
    print("   ✓ Billing / Invoicing")
    print("   ✓ Nursing / Vitals")
    print("   ✓ Emergency / Triage")
    print("   ✓ Documents / Alerts")
    print("=" * 60)

# Include routers
app.include_router(webhook_router)
app.include_router(api_router)

# ==================== HTML DASHBOARDS ====================

# Doctor Dashboard HTML
DOCTOR_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Doctor Dashboard - MedCare Hospital</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            color: white;
            padding: 20px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { font-size: 1.5rem; }
        .nav-tabs {
            display: flex;
            background: white;
            border-bottom: 1px solid #e2e8f0;
            padding: 0 30px;
        }
        .nav-tab {
            padding: 15px 25px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            font-weight: 500;
            color: #64748b;
        }
        .nav-tab.active {
            color: #2563eb;
            border-bottom-color: #2563eb;
        }
        .main-container {
            padding: 24px 30px;
            max-width: 1600px;
            margin: 0 auto;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }
        .stat-card {
            background: white;
            padding: 24px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            text-align: center;
        }
        .stat-card h3 {
            font-size: 0.85rem;
            color: #6b7280;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        .stat-card .number {
            font-size: 2.5rem;
            font-weight: 700;
            color: #2563eb;
        }
        .content-grid {
            display: grid;
            grid-template-columns: 1fr 2fr 1fr;
            gap: 24px;
        }
        .panel {
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            overflow: hidden;
        }
        .panel-header {
            background: #f8fafc;
            padding: 20px;
            border-bottom: 1px solid #e2e8f0;
            font-weight: 600;
        }
        .panel-content { padding: 20px; }
        .queue-item, .ipd-item {
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.2s;
            border: 2px solid transparent;
        }
        .queue-item:hover, .ipd-item:hover { background: #f1f5f9; }
        .queue-item.active { background: #eff6ff; border-color: #2563eb; }
        .token {
            display: inline-block;
            background: #2563eb;
            color: white;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .token.waiting { background: #f59e0b; }
        .name { font-weight: 600; color: #1e293b; }
        .info { font-size: 0.85rem; color: #64748b; margin-top: 5px; }
        .complaint { font-size: 0.8rem; color: #475569; margin-top: 8px; padding-top: 8px; border-top: 1px dashed #e2e8f0; }
        .btn {
            padding: 12px 24px;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            border: none;
            transition: all 0.2s;
        }
        .btn-primary {
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            color: white;
        }
        .btn-primary:hover { transform: translateY(-2px); }
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 500; color: #374151; }
        .form-group input, .form-group textarea { width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 8px; }
        .hidden { display: none; }
        .alert-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.7rem;
            font-weight: 600;
            margin-left: 10px;
        }
        .alert-critical { background: #fee2e2; color: #991b1b; }
        .alert-high { background: #fef3c7; color: #92400e; }
    </style>
</head>
<body>
    <!-- Global Navigation -->
    <nav style="background: #1e293b; padding: 8px 30px; display: flex; justify-content: space-between; align-items: center;">
        <a href="/" style="color: white; text-decoration: none; font-weight: 600; font-size: 1.1rem;">🏥 MedCare HMS</a>
        <div style="display: flex; gap: 5px;">
            <a href="/admin" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">📊 Admin</a>
            <a href="/doctor" style="color: white; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; background: #2563eb;">👨‍⚕️ Doctor</a>
            <a href="/ipd" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🛏️ IPD</a>
            <a href="/nursing" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">👩‍⚕️ Nursing</a>
            <a href="/pharmacy" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">💊 Pharmacy</a>
            <a href="/billing" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">💰 Billing</a>
            <a href="/emergency" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🚨 ER</a>
            <a href="/patient" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🧑‍⚕️ Patient</a>
            <a href="/" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🚪 Exit</a>
        </div>
    </nav>
    <header class="header">
        <h1>👨‍⚕️ Doctor Dashboard</h1>
        <div>
            <div id="doctor-name" style="font-weight: 600;">Loading...</div>
            <div id="doctor-specialty" style="font-size: 0.9rem; opacity: 0.9;">Loading...</div>
        </div>
    </header>

    <div class="nav-tabs">
        <div class="nav-tab active" onclick="switchTab('opd')">📋 OPD Queue</div>
        <div class="nav-tab" onclick="switchTab('ipd')">🏥 IPD Patients</div>
        <div class="nav-tab" onclick="switchTab('alerts')">🚨 Alerts <span id="alert-count" class="alert-badge alert-critical hidden">0</span></div>
    </div>

    <div class="main-container">
        <!-- OPD Tab -->
        <div id="opd-tab">
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Today's Patients</h3>
                    <div class="number" id="stat-total">0</div>
                </div>
                <div class="stat-card">
                    <h3>Completed</h3>
                    <div class="number" id="stat-completed">0</div>
                </div>
                <div class="stat-card">
                    <h3>Waiting</h3>
                    <div class="number" id="stat-waiting">0</div>
                </div>
                <div class="stat-card">
                    <h3>Upcoming</h3>
                    <div class="number" id="stat-upcoming">0</div>
                </div>
            </div>

            <div class="content-grid">
                <div class="panel">
                    <div class="panel-header">📋 Patient Queue</div>
                    <div class="panel-content" id="patient-queue">
                        <p style="color: #64748b; text-align: center;">Loading patients...</p>
                    </div>
                </div>

                <div class="panel" id="consultation-panel">
                    <div class="panel-header">🩺 Consultation</div>
                    <div class="panel-content">
                        <div id="no-patient" style="text-align: center; padding: 60px; color: #64748b;">
                            <div style="font-size: 4rem; margin-bottom: 20px;">🩺</div>
                            <h3>Select a patient to start consultation</h3>
                        </div>
                        <div id="consultation-form" class="hidden">
                            <div style="background: #dbeafe; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                                <h3 id="current-patient" style="color: #1e40af; margin-bottom: 5px;"></h3>
                                <p id="patient-details" style="color: #3b82f6; font-size: 0.9rem;"></p>
                            </div>
                            <div class="form-group">
                                <label>Chief Complaint</label>
                                <textarea id="chief-complaint" rows="3"></textarea>
                            </div>
                            <div class="form-group">
                                <label>Vitals (BP, Pulse, Temp, SpO2)</label>
                                <input type="text" id="vitals" placeholder="120/80, 72, 98.6, 98">
                            </div>
                            <div class="form-group">
                                <label>Diagnosis</label>
                                <input type="text" id="diagnosis">
                            </div>
                            <div class="form-group">
                                <label>Prescription (Medicine | Dose | Freq | Duration)</label>
                                <textarea id="prescription" rows="3" placeholder="Paracetamol | 500mg | 1-1-1 | 5 days"></textarea>
                            </div>
                            <div class="form-group">
                                <label>
                                    <input type="checkbox" id="admit-ipd"> Admit to IPD
                                </label>
                            </div>
                            <button class="btn btn-primary" onclick="completeConsultation()">
                                ✅ Complete Consultation
                            </button>
                        </div>
                    </div>
                </div>

                <div class="panel">
                    <div class="panel-header">📅 Patient Timeline</div>
                    <div class="panel-content" id="patient-timeline">
                        <p style="color: #64748b; text-align: center;">Select a patient to view timeline</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- IPD Tab (Hidden by default) -->
        <div id="ipd-tab" class="hidden">
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total Admissions</h3>
                    <div class="number" id="ipd-total">0</div>
                </div>
                <div class="stat-card">
                    <h3>ICU Patients</h3>
                    <div class="number" id="ipd-icu">0</div>
                </div>
            </div>
            <div class="panel">
                <div class="panel-header">🏥 In-Patients</div>
                <div class="panel-content" id="ipd-list">
                    <p style="color: #64748b; text-align: center;">Loading IPD patients...</p>
                </div>
            </div>
        </div>

        <!-- Alerts Tab -->
        <div id="alerts-tab" class="hidden">
            <div class="panel">
                <div class="panel-header">🚨 Clinical Alerts</div>
                <div class="panel-content" id="alerts-list">
                    <p style="color: #64748b; text-align: center;">Loading alerts...</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentDoctorId = 1;
        let currentEncounter = null;
        let currentPatientId = null;

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadDoctorInfo();
            loadDashboard();
            setInterval(loadDashboard, 30000);
        });

        function switchTab(tab) {
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('[id$="-tab"]').forEach(t => t.classList.add('hidden'));

            event.target.classList.add('active');
            document.getElementById(tab + '-tab').classList.remove('hidden');

            if (tab === 'ipd') loadIPDPatients();
            if (tab === 'alerts') loadAlerts();
        }

        async function loadDoctorInfo() {
            try {
                const response = await fetch(`/api/v1/doctor/${currentDoctorId}/dashboard`);
                const data = await response.json();

                if (data.doctor) {
                    document.getElementById('doctor-name').textContent = `Dr. ${data.doctor.name}`;
                    document.getElementById('doctor-specialty').textContent = data.doctor.specialty;
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }

        async function loadDashboard() {
            try {
                const response = await fetch(`/api/v1/doctor/${currentDoctorId}/dashboard`);
                const data = await response.json();

                document.getElementById('stat-total').textContent = data.stats.total;
                document.getElementById('stat-completed').textContent = data.stats.completed;
                document.getElementById('stat-waiting').textContent = data.stats.waiting;
                document.getElementById('stat-upcoming').textContent = data.stats.upcoming;

                loadPatientQueue(data.patients);
            } catch (error) {
                console.error('Error:', error);
            }
        }

        function loadPatientQueue(patients) {
            const html = patients.map(p => `
                <div class="queue-item" onclick="selectPatient(${p.appointment_id})" data-id="${p.appointment_id}">
                    <span class="token ${p.status === 'WAITING' ? 'waiting' : ''}">Token ${p.token || '-'}</span>
                    <div class="name">${p.patient_name} (${p.age}y)</div>
                    <div class="info">${p.time} • ${p.status}</div>
                    <div class="complaint">📝 ${p.chief_complaint || 'No complaint'}</div>
                </div>
            `).join('');

            document.getElementById('patient-queue').innerHTML = html || '<p style="color: #64748b; text-align: center;">No patients in queue</p>';
        }

        async function selectPatient(appointmentId) {
            document.querySelectorAll('.queue-item').forEach(el => el.classList.remove('active'));
            document.querySelector(`[data-id="${appointmentId}"]`).classList.add('active');

            try {
                const response = await fetch(`/api/v1/consultation/${appointmentId}`);
                const data = await response.json();

                currentPatientId = data.appointment.patient_id;

                document.getElementById('no-patient').classList.add('hidden');
                document.getElementById('consultation-form').classList.remove('hidden');

                document.getElementById('current-patient').textContent = data.appointment.patient_name;
                document.getElementById('patient-details').textContent = `ID: ${data.appointment.patient_id} | Token: ${data.appointment.token}`;
                document.getElementById('chief-complaint').value = data.appointment.chief_complaint || '';

                startConsultation(appointmentId);
                loadTimeline(data.timeline);
            } catch (error) {
                console.error('Error:', error);
            }
        }

        async function startConsultation(appointmentId) {
            try {
                const response = await fetch(`/api/v1/consultation/${appointmentId}/start`, { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    currentEncounter = data.encounter_id;
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }

        function loadTimeline(timeline) {
            const html = timeline.slice(0, 5).map(t => `
                <div style="padding: 10px; border-left: 3px solid #3b82f6; margin-bottom: 10px;">
                    <div style="font-weight: 600; color: #1e293b;">${t.title}</div>
                    <div style="font-size: 0.8rem; color: #64748b;">${new Date(t.date).toLocaleDateString()}</div>
                    <div style="font-size: 0.85rem; color: #475569; margin-top: 5px;">${t.details.diagnosis || t.details.tests?.length + ' tests' || ''}</div>
                </div>
            `).join('');

            document.getElementById('patient-timeline').innerHTML = html || '<p style="color: #64748b;">No history</p>';
        }

        async function completeConsultation() {
            if (!currentEncounter) return;

            const prescriptionText = document.getElementById('prescription').value;
            const prescriptions = prescriptionText.split('\\n').filter(p => p.trim()).map(p => {
                const parts = p.split('|').map(x => x.trim());
                return {
                    medicine: parts[0] || '',
                    dosage: parts[1] || '',
                    frequency: parts[2] || '',
                    duration: parts[3] || ''
                };
            });

            const data = {
                chief_complaint: document.getElementById('chief-complaint').value,
                primary_diagnosis: document.getElementById('diagnosis').value,
                vitals: { bp: document.getElementById('vitals').value },
                prescriptions: prescriptions,
                lab_orders: [],
                admit_to_ipd: document.getElementById('admit-ipd').checked ? {
                    chief_complaint: document.getElementById('chief-complaint').value,
                    provisional_diagnosis: document.getElementById('diagnosis').value
                } : null
            };

            try {
                const response = await fetch(`/api/v1/consultation/${currentEncounter}/complete`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                if (result.success) {
                    alert('Consultation completed!');
                    document.getElementById('consultation-form').classList.add('hidden');
                    document.getElementById('no-patient').classList.remove('hidden');
                    loadDashboard();
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }

        async function loadIPDPatients() {
            try {
                const response = await fetch(`/api/v1/doctor/${currentDoctorId}/dashboard`);
                const data = await response.json();

                document.getElementById('ipd-total').textContent = data.stats.ipd_patients || 0;

                const html = (data.ipd_list || []).map(p => `
                    <div class="ipd-item">
                        <div class="name">${p.patient_name}</div>
                        <div class="info">${p.bed} • Day ${p.admitted_since}</div>
                    </div>
                `).join('');

                document.getElementById('ipd-list').innerHTML = html || '<p style="color: #64748b; text-align: center;">No IPD patients</p>';
            } catch (error) {
                console.error('Error:', error);
            }
        }

        async function loadAlerts() {
            try {
                const response = await fetch('/api/v1/alerts/active');
                const data = await response.json();

                const html = (data.alerts || []).map(a => `
                    <div style="padding: 15px; background: ${a.severity === 'CRITICAL' ? '#fee2e2' : '#fef3c7'}; border-radius: 10px; margin-bottom: 10px;">
                        <div style="font-weight: 600; color: ${a.severity === 'CRITICAL' ? '#991b1b' : '#92400e'}">${a.message}</div>
                        <div style="font-size: 0.85rem; color: #64748b;">${a.patient_name} • ${a.triggered_at}</div>
                    </div>
                `).join('');

                document.getElementById('alerts-list').innerHTML = html || '<p style="color: #64748b; text-align: center;">No active alerts</p>';

                const alertCount = (data.alerts || []).length;
                const badge = document.getElementById('alert-count');
                badge.textContent = alertCount;
                badge.classList.toggle('hidden', alertCount === 0);
            } catch (error) {
                console.error('Error:', error);
            }
        }
    </script>
</body>
</html>
"""

# Admin Dashboard HTML
ADMIN_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - MedCare Hospital</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
        }
        .sidebar {
            width: 260px;
            background: white;
            height: 100vh;
            position: fixed;
            left: 0;
            top: 0;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            z-index: 100;
        }
        .sidebar-header {
            padding: 30px;
            text-align: center;
            border-bottom: 1px solid #e5e7eb;
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            color: white;
        }
        .logo { font-size: 3rem; margin-bottom: 10px; }
        .nav-menu { padding: 20px 0; }
        .nav-item {
            display: block;
            padding: 12px 24px;
            color: #6b7280;
            text-decoration: none;
            font-weight: 500;
            border-left: 3px solid transparent;
            transition: all 0.2s;
        }
        .nav-item:hover { background: #f3f4f6; color: #2563eb; }
        .nav-item.active { background: #eff6ff; color: #2563eb; border-left-color: #2563eb; }
        .main-content { margin-left: 260px; margin-top: 48px; padding: 30px; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }
        .stat-card {
            background: white;
            padding: 24px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            text-align: center;
        }
        .stat-card h3 { font-size: 0.85rem; color: #6b7280; margin-bottom: 10px; }
        .stat-card .number { font-size: 2.5rem; font-weight: 700; color: #2563eb; }
        .card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            overflow: hidden;
            margin-bottom: 24px;
        }
        .card-header {
            background: #f8fafc;
            padding: 20px;
            border-bottom: 1px solid #e2e8f0;
            font-weight: 600;
        }
        .card-content { padding: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th { background: #f9fafb; padding: 14px 20px; text-align: left; font-weight: 600; font-size: 0.75rem; text-transform: uppercase; color: #6b7280; }
        td { padding: 16px 20px; border-bottom: 1px solid #e5e7eb; font-size: 0.9rem; }
        tr:hover { background: #f9fafb; }
        .badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .badge-success { background: #d1fae5; color: #065f46; }
        .badge-warning { background: #fef3c7; color: #92400e; }
        .badge-danger { background: #fee2e2; color: #991b1b; }
    </style>
</head>
<body>
    <!-- Global Navigation -->
    <nav style="background: #1e293b; padding: 8px 30px; display: flex; justify-content: space-between; align-items: center; position: fixed; top: 0; left: 0; right: 0; z-index: 200;">
        <a href="/" style="color: white; text-decoration: none; font-weight: 600; font-size: 1.1rem;">🏥 MedCare HMS</a>
        <div style="display: flex; gap: 5px;">
            <a href="/admin" style="color: white; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; background: #2563eb;">📊 Admin</a>
            <a href="/doctor" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">👨‍⚕️ Doctor</a>
            <a href="/ipd" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🛏️ IPD</a>
            <a href="/nursing" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">👩‍⚕️ Nursing</a>
            <a href="/pharmacy" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">💊 Pharmacy</a>
            <a href="/billing" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">💰 Billing</a>
            <a href="/emergency" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🚨 ER</a>
            <a href="/patient" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🧑‍⚕️ Patient</a>
            <a href="/" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🚪 Exit</a>
        </div>
    </nav>
    <div class="sidebar" style="margin-top: 48px;">
        <div class="sidebar-header">
            <div class="logo">🏥</div>
            <h2>MedCare Hospital</h2>
            <p>Admin Panel</p>
        </div>
        <nav class="nav-menu">
            <a href="#" class="nav-item active" onclick="loadSection('dashboard')">📊 Dashboard</a>
            <a href="/ipd" class="nav-item">🏥 IPD</a>
            <a href="/billing" class="nav-item">💰 Billing</a>
            <a href="/pharmacy" class="nav-item">💊 Pharmacy</a>
            <a href="#" class="nav-item" onclick="loadSection('lab')">🧪 Laboratory</a>
            <a href="#" class="nav-item" onclick="loadSection('insurance')">🛡️ Insurance</a>
            <a href="/emergency" class="nav-item">🚨 Emergency</a>
        </nav>
    </div>

    <div class="main-content">
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Today's OPD</h3>
                <div class="number" id="stat-opd">-</div>
            </div>
            <div class="stat-card">
                <h3>IPD Occupancy</h3>
                <div class="number" id="stat-ipd">-</div>
            </div>
            <div class="stat-card">
                <h3>Pending Bills</h3>
                <div class="number" id="stat-bills">-</div>
            </div>
            <div class="stat-card">
                <h3>Active Alerts</h3>
                <div class="number" id="stat-alerts">-</div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">📅 Today's Overview</div>
            <div class="card-content" id="main-content">
                <p style="color: #64748b; text-align: center; padding: 40px;">Loading...</p>
            </div>
        </div>
    </div>

    <script>
        async function loadDashboard() {
            try {
                const response = await fetch('/api/v1/admin/dashboard');
                const data = await response.json();

                document.getElementById('stat-opd').textContent = data.today.opd_visits;
                document.getElementById('stat-ipd').textContent = data.current.ipd_occupancy;
                document.getElementById('stat-bills').textContent = data.financial.pending_payments;
                document.getElementById('stat-alerts').textContent = data.current.active_alerts;

                // Load ward occupancy
                const wardResponse = await fetch('/api/v1/ipd/wards/occupancy');
                const wardData = await wardResponse.json();

                let html = '<table><thead><tr><th>Ward</th><th>Type</th><th>Total Beds</th><th>Occupied</th><th>Available</th><th>Occupancy %</th></tr></thead><tbody>';
                wardData.ward_stats.forEach(w => {
                    const badgeClass = w.occupancy_rate > 90 ? 'badge-danger' : (w.occupancy_rate > 70 ? 'badge-warning' : 'badge-success');
                    html += `<tr><td><strong>${w.ward_name}</strong></td><td>${w.ward_type}</td><td>${w.total_beds}</td><td>${w.occupied}</td><td>${w.available}</td><td><span class="badge ${badgeClass}">${w.occupancy_rate}%</span></td></tr>`;
                });
                html += '</tbody></table>';

                document.getElementById('main-content').innerHTML = html;
            } catch (error) {
                console.error('Error:', error);
            }
        }

        function loadSection(section) {
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            event.target.classList.add('active');

            // In a real app, this would load different content
            alert('Section: ' + section + ' - Full implementation would load here');
        }

        // Initialize
        loadDashboard();
        setInterval(loadDashboard, 60000);
    </script>
</body>
</html>
"""

@app.get("/doctor")
async def doctor_dashboard_page():
    """Serve doctor dashboard"""
    return HTMLResponse(content=DOCTOR_DASHBOARD_HTML)

@app.get("/admin")
async def admin_dashboard_page():
    """Serve admin dashboard"""
    return HTMLResponse(content=ADMIN_DASHBOARD_HTML)

@app.get("/ipd")
async def ipd_dashboard_page():
    """Serve IPD/Bed Management dashboard"""
    return HTMLResponse(content=IPD_DASHBOARD_HTML)

@app.get("/pharmacy")
async def pharmacy_dashboard_page():
    """Serve Pharmacy dashboard"""
    return HTMLResponse(content=PHARMACY_DASHBOARD_HTML)

@app.get("/billing")
async def billing_dashboard_page():
    """Serve Billing & Insurance dashboard"""
    return HTMLResponse(content=BILLING_DASHBOARD_HTML)

@app.get("/nursing")
async def nursing_dashboard_page():
    """Serve Nursing Station dashboard"""
    return HTMLResponse(content=NURSING_DASHBOARD_HTML)

@app.get("/emergency")
async def emergency_dashboard_page():
    """Serve Emergency Department dashboard"""
    return HTMLResponse(content=EMERGENCY_DASHBOARD_HTML)

@app.get("/patient")
async def patient_portal_page():
    """Serve Patient Portal"""
    return HTMLResponse(content=PATIENT_PORTAL_HTML)

# Unified Login Page
LOGIN_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - MedCare Hospital</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .login-container {
            background: white;
            border-radius: 24px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
            width: 100%;
            max-width: 1000px;
            display: grid;
            grid-template-columns: 1fr 1fr;
        }
        .login-left {
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            color: white;
            padding: 60px 40px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .logo { font-size: 4rem; margin-bottom: 20px; }
        .login-left h1 { font-size: 2.5rem; margin-bottom: 20px; }
        .login-left p { font-size: 1.1rem; opacity: 0.9; line-height: 1.6; }
        .features {
            margin-top: 30px;
        }
        .feature-item {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 15px;
            font-size: 0.95rem;
        }
        .feature-icon {
            width: 32px;
            height: 32px;
            background: rgba(255,255,255,0.2);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-right {
            padding: 60px 40px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .module-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        .module-btn {
            padding: 20px;
            border: 2px solid #e5e7eb;
            border-radius: 16px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            background: white;
            text-decoration: none;
            color: #1f2937;
        }
        .module-btn:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border-color: #2563eb;
        }
        .module-icon {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        .module-label {
            font-weight: 600;
            font-size: 0.95rem;
        }
        .module-desc {
            font-size: 0.75rem;
            color: #6b7280;
            margin-top: 5px;
        }
        .login-footer {
            margin-top: 30px;
            text-align: center;
            color: #6b7280;
            font-size: 0.85rem;
        }
        @media (max-width: 768px) {
            .login-container { grid-template-columns: 1fr; }
            .login-left { display: none; }
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-left">
            <div class="logo">🏥</div>
            <h1>MedCare Hospital</h1>
            <p>Complete Hospital Management System with integrated modules for seamless patient care.</p>
            <div class="features">
                <div class="feature-item">
                    <div class="feature-icon">👨‍⚕️</div>
                    <span>Doctor Consultations & EHR</span>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">🛏️</div>
                    <span>IPD & Bed Management</span>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">💊</div>
                    <span>Pharmacy & Inventory</span>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">💰</div>
                    <span>Billing & Insurance</span>
                </div>
            </div>
        </div>
        <div class="login-right">
            <h2 style="margin-bottom: 10px; color: #1f2937;">Select Portal</h2>
            <p style="color: #6b7280; margin-bottom: 30px;">Choose your dashboard to continue</p>
            <div class="module-grid">
                <a href="/doctor" class="module-btn">
                    <div class="module-icon">👨‍⚕️</div>
                    <div class="module-label">Doctor</div>
                    <div class="module-desc">OPD Queue & Consultations</div>
                </a>
                <a href="/ipd" class="module-btn">
                    <div class="module-icon">🛏️</div>
                    <div class="module-label">IPD</div>
                    <div class="module-desc">Bed Management & Admissions</div>
                </a>
                <a href="/nursing" class="module-btn">
                    <div class="module-icon">👩‍⚕️</div>
                    <div class="module-label">Nursing</div>
                    <div class="module-desc">Vitals & Medications</div>
                </a>
                <a href="/pharmacy" class="module-btn">
                    <div class="module-icon">💊</div>
                    <div class="module-label">Pharmacy</div>
                    <div class="module-desc">Inventory & Dispensing</div>
                </a>
                <a href="/billing" class="module-btn">
                    <div class="module-icon">💰</div>
                    <div class="module-label">Billing</div>
                    <div class="module-desc">Invoices & Insurance</div>
                </a>
                <a href="/emergency" class="module-btn">
                    <div class="module-icon">🚨</div>
                    <div class="module-label">Emergency</div>
                    <div class="module-desc">Triage & ER Queue</div>
                </a>
                <a href="/admin" class="module-btn">
                    <div class="module-icon">📊</div>
                    <div class="module-label">Admin</div>
                    <div class="module-desc">Hospital Overview</div>
                </a>
                <a href="/patient" class="module-btn">
                    <div class="module-icon">🧑‍⚕️</div>
                    <div class="module-label">Patient</div>
                    <div class="module-desc">Portal & Records</div>
                </a>
            </div>
            <div class="login-footer">
                <p>🏥 MedCare Hospital Management System v3.0</p>
                <p style="margin-top: 5px;">WhatsApp Bot: <code>/whatsapp</code> | API Docs: <code>/api/docs</code></p>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.get("/")
async def root():
    """Root endpoint - unified login/portal selector"""
    return HTMLResponse(content=LOGIN_PAGE_HTML)

@app.get("/login")
async def login_page():
    """Dedicated login page"""
    return HTMLResponse(content=LOGIN_PAGE_HTML)

# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
