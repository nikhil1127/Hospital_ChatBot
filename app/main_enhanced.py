"""
Enhanced Hospital Management System
Combines WhatsApp Bot + Web Dashboards
"""

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.db.session import create_tables
from app.api.webhook import router as webhook_router
from app.api.dashboard import router as dashboard_router
from app.db.session import get_db

# Create FastAPI app
app = FastAPI(
    title="MedCare Hospital Management System",
    description="Complete Hospital Management with WhatsApp Bot + Web Dashboards",
    version="2.0.0"
)

# Event handlers
@app.on_event("startup")
async def startup_event():
    create_tables()
    print("✅ Hospital Management System Started")
    print("📱 WhatsApp Bot: /whatsapp")
    print("🩺 Doctor Dashboard: /doctor")
    print("🏥 Admin Dashboard: /")

# Include routers
app.include_router(webhook_router)
app.include_router(dashboard_router)


# ============================================================
# DOCTOR DASHBOARD HTML PAGE
# ============================================================

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

        /* Header */
        .header {
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            color: white;
            padding: 20px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .header h1 { font-size: 1.5rem; }
        .header .doctor-info {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .header .avatar {
            width: 45px; height: 45px;
            background: white;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.5rem;
        }

        /* Main Layout */
        .main-container {
            display: grid;
            grid-template-columns: 280px 1fr 350px;
            gap: 24px;
            padding: 24px;
            max-width: 1600px;
            margin: 0 auto;
        }

        /* Patient Queue */
        .queue-card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            overflow: hidden;
        }
        .queue-header {
            background: #f8fafc;
            padding: 20px;
            border-bottom: 1px solid #e2e8f0;
        }
        .queue-header h2 {
            font-size: 1.1rem;
            color: #1e293b;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .queue-list { padding: 10px; }

        .queue-item {
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.2s;
            border: 2px solid transparent;
        }
        .queue-item:hover { background: #f1f5f9; }
        .queue-item.active {
            background: #eff6ff;
            border-color: #2563eb;
        }
        .queue-item .token {
            display: inline-block;
            background: #2563eb;
            color: white;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .queue-item .token.waiting { background: #f59e0b; }
        .queue-item .name { font-weight: 600; color: #1e293b; }
        .queue-item .info {
            font-size: 0.85rem;
            color: #64748b;
            margin-top: 5px;
        }
        .queue-item .complaint {
            font-size: 0.8rem;
            color: #475569;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px dashed #e2e8f0;
        }

        /* Consultation Area */
        .consultation-card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            overflow: hidden;
        }
        .consultation-header {
            background: #f8fafc;
            padding: 20px;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .consultation-header h2 {
            font-size: 1.1rem;
            color: #1e293b;
        }

        .patient-header {
            padding: 20px;
            background: linear-gradient(135deg, #dbeafe, #ede9fe);
            border-bottom: 1px solid #e2e8f0;
        }
        .patient-header h3 {
            font-size: 1.3rem;
            color: #1e293b;
            margin-bottom: 10px;
        }
        .patient-badges {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        .badge.id { background: #e0e7ff; color: #4338ca; }
        .badge.age { background: #fce7f3; color: #be185d; }
        .badge.blood { background: #fee2e2; color: #991b1b; }
        .badge.warning { background: #fef3c7; color: #92400e; }

        .alerts-section {
            padding: 15px 20px;
            background: #fef2f2;
            border-bottom: 1px solid #e2e8f0;
        }
        .alerts-section .alert-item {
            display: flex;
            align-items: center;
            gap: 10px;
            color: #991b1b;
            font-size: 0.9rem;
            margin-bottom: 5px;
        }

        .consultation-content {
            padding: 20px;
        }

        .form-section {
            margin-bottom: 24px;
        }
        .form-section h4 {
            font-size: 0.9rem;
            color: #64748b;
            text-transform: uppercase;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        textarea, input[type="text"] {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-family: inherit;
            font-size: 0.95rem;
            transition: border-color 0.2s;
        }
        textarea { min-height: 100px; resize: vertical; }
        textarea:focus, input:focus {
            outline: none;
            border-color: #2563eb;
        }

        .vitals-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
        }
        .vital-input label {
            display: block;
            font-size: 0.8rem;
            color: #64748b;
            margin-bottom: 5px;
        }
        .vital-input input {
            padding: 10px;
            font-size: 0.9rem;
        }

        .medicine-row {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr auto;
            gap: 10px;
            margin-bottom: 10px;
        }
        .medicine-row input {
            padding: 10px;
        }
        .btn-add {
            background: #dbeafe;
            color: #2563eb;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
        }

        .action-buttons {
            display: flex;
            gap: 15px;
            padding: 20px;
            border-top: 1px solid #e2e8f0;
            background: #f8fafc;
        }
        .btn {
            padding: 14px 30px;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            border: none;
            transition: all 0.2s;
        }
        .btn-primary {
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            color: white;
            flex: 1;
        }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3); }
        .btn-secondary {
            background: white;
            color: #475569;
            border: 2px solid #e2e8f0;
        }

        /* Patient Timeline Sidebar */
        .timeline-card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            overflow: hidden;
        }
        .timeline-header {
            background: #f8fafc;
            padding: 20px;
            border-bottom: 1px solid #e2e8f0;
        }
        .timeline-header h2 {
            font-size: 1.1rem;
            color: #1e293b;
        }

        .timeline-content { padding: 20px; }

        .timeline-year {
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 15px;
        }

        .timeline-item {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px dashed #e2e8f0;
        }
        .timeline-item:last-child {
            border-bottom: none;
            margin-bottom: 0;
        }
        .timeline-icon {
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            flex-shrink: 0;
        }
        .timeline-icon.consultation { background: #dbeafe; }
        .timeline-icon.lab { background: #fce7f3; }
        .timeline-icon.imaging { background: #d1fae5; }

        .timeline-details h4 {
            font-size: 0.95rem;
            color: #1e293b;
            margin-bottom: 5px;
        }
        .timeline-details p {
            font-size: 0.85rem;
            color: #64748b;
            margin-bottom: 3px;
        }
        .timeline-date {
            font-size: 0.75rem;
            color: #94a3b8;
        }

        /* AI Assist Panel */
        .ai-panel {
            background: linear-gradient(135deg, #f0fdf4, #ecfdf5);
            border: 1px solid #bbf7d0;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .ai-panel h4 {
            color: #166534;
            font-size: 0.9rem;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .ai-panel p {
            font-size: 0.85rem;
            color: #166534;
            line-height: 1.6;
        }

        /* Loading State */
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 60px;
            color: #64748b;
        }
    </style>
</head>
<body>
    <header class="header">
        <h1>👨‍⚕️ MedCare Hospital - Doctor Dashboard</h1>
        <div class="doctor-info">
            <div>
                <div id="doctor-name" style="font-weight: 600;">Loading...</div>
                <div id="doctor-specialty" style="font-size: 0.9rem; opacity: 0.9;">Loading...</div>
            </div>
            <div class="avatar">👨‍⚕️</div>
        </div>
    </header>

    <div class="main-container" id="app">
        <!-- Patient Queue -->
        <div class="queue-card">
            <div class="queue-header">
                <h2>📋 Patient Queue</h2>
                <div id="queue-stats" style="font-size: 0.85rem; color: #64748b;">
                    <span id="waiting-count">0</span> waiting
                </div>
            </div>
            <div class="queue-list" id="patient-queue">
                <div class="loading">Loading patients...</div>
            </div>
        </div>

        <!-- Consultation Form -->
        <div class="consultation-card">
            <div class="consultation-header">
                <h2>🩺 Consultation</h2>
                <button class="btn btn-secondary" onclick="loadPatientHistory()">📄 View History</button>
            </div>

            <div id="patient-header-section" style="display: none;">
                <div class="patient-header">
                    <h3 id="current-patient-name">Patient Name</h3>
                    <div class="patient-badges">
                        <span class="badge id" id="current-patient-id">PAT-000000</span>
                        <span class="badge age" id="current-patient-age">35 years</span>
                        <span class="badge blood" id="current-patient-blood">O+</span>
                    </div>
                </div>

                <div class="alerts-section" id="patient-alerts">
                    <!-- Dynamic alerts -->
                </div>

                <div class="consultation-content">
                    <!-- AI Summary -->
                    <div class="ai-panel">
                        <h4>🤖 AI-Powered Summary</h4>
                        <p id="ai-summary">Select a patient to see AI-generated summary of their medical history.</p>
                    </div>

                    <!-- Chief Complaint -->
                    <div class="form-section">
                        <h4>📝 Chief Complaint</h4>
                        <textarea id="chief-complaint" placeholder="Patient's main complaint..."></textarea>
                    </div>

                    <!-- Vitals -->
                    <div class="form-section">
                        <h4>💓 Vitals</h4>
                        <div class="vitals-grid">
                            <div class="vital-input">
                                <label>BP (mmHg)</label>
                                <input type="text" id="vital-bp" placeholder="120/80">
                            </div>
                            <div class="vital-input">
                                <label>Pulse (bpm)</label>
                                <input type="text" id="vital-pulse" placeholder="72">
                            </div>
                            <div class="vital-input">
                                <label>Temperature (°F)</label>
                                <input type="text" id="vital-temp" placeholder="98.6">
                            </div>
                            <div class="vital-input">
                                <label>SpO2 (%)</label>
                                <input type="text" id="vital-spo2" placeholder="98">
                            </div>
                            <div class="vital-input">
                                <label>Weight (kg)</label>
                                <input type="text" id="vital-weight" placeholder="70">
                            </div>
                            <div class="vital-input">
                                <label>Height (cm)</label>
                                <input type="text" id="vital-height" placeholder="170">
                            </div>
                        </div>
                    </div>

                    <!-- Diagnosis -->
                    <div class="form-section">
                        <h4>🔍 Diagnosis</h4>
                        <textarea id="primary-diagnosis" placeholder="Primary diagnosis..."></textarea>
                    </div>

                    <!-- Prescription -->
                    <div class="form-section">
                        <h4>💊 Prescription</h4>
                        <div id="medicine-list">
                            <div class="medicine-row" data-index="0">
                                <input type="text" placeholder="Medicine name" class="med-name">
                                <input type="text" placeholder="Dose (e.g. 500mg)" class="med-dose">
                                <input type="text" placeholder="Frequency" class="med-freq">
                                <input type="text" placeholder="Duration" class="med-duration">
                            </div>
                        </div>
                        <button class="btn-add" onclick="addMedicineRow()">+ Add Medicine</button>
                    </div>

                    <!-- Investigations -->
                    <div class="form-section">
                        <h4>🧪 Investigations</h4>
                        <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                            <label style="display: flex; align-items: center; gap: 5px; cursor: pointer;">
                                <input type="checkbox" value="CBC" class="investigation"> CBC
                            </label>
                            <label style="display: flex; align-items: center; gap: 5px; cursor: pointer;">
                                <input type="checkbox" value="LFT" class="investigation"> LFT
                            </label>
                            <label style="display: flex; align-items: center; gap: 5px; cursor: pointer;">
                                <input type="checkbox" value="Blood Sugar" class="investigation"> Blood Sugar
                            </label>
                            <label style="display: flex; align-items: center; gap: 5px; cursor: pointer;">
                                <input type="checkbox" value="X-Ray" class="investigation"> X-Ray
                            </label>
                            <label style="display: flex; align-items: center; gap: 5px; cursor: pointer;">
                                <input type="checkbox" value="ECG" class="investigation"> ECG
                            </label>
                            <label style="display: flex; align-items: center; gap: 5px; cursor: pointer;">
                                <input type="checkbox" value="MRI" class="investigation"> MRI
                            </label>
                        </div>
                    </div>
                </div>

                <div class="action-buttons">
                    <button class="btn btn-secondary" onclick="saveDraft()">💾 Save Draft</button>
                    <button class="btn btn-primary" onclick="completeConsultation()">
                        ✅ Complete Consultation
                    </button>
                </div>
            </div>

            <div id="no-patient-selected" style="padding: 60px; text-align: center; color: #64748b;">
                <div style="font-size: 4rem; margin-bottom: 20px;">🩺</div>
                <h3>Select a patient from the queue</h3>
                <p>Click on a patient to start consultation</p>
            </div>
        </div>

        <!-- Patient Timeline -->
        <div class="timeline-card">
            <div class="timeline-header">
                <h2>📅 Patient Timeline</h2>
            </div>
            <div class="timeline-content" id="patient-timeline">
                <div style="text-align: center; color: #64748b; padding: 40px;">
                    <p>Select a patient to view their timeline</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // State
        let currentDoctorId = 1; // Demo - get from auth
        let currentAppointment = null;
        let currentEncounter = null;

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadDoctorInfo();
            loadPatientQueue();
            // Refresh queue every 30 seconds
            setInterval(loadPatientQueue, 30000);
        });

        // Load Doctor Info
        async function loadDoctorInfo() {
            try {
                const response = await fetch(`/dashboard/doctor/${currentDoctorId}`);
                const data = await response.json();

                if (data.doctor) {
                    document.getElementById('doctor-name').textContent = `Dr. ${data.doctor.name}`;
                    document.getElementById('doctor-specialty').textContent = data.doctor.specialty;
                }
            } catch (error) {
                console.error('Error loading doctor info:', error);
            }
        }

        // Load Patient Queue
        async function loadPatientQueue() {
            try {
                const response = await fetch(`/dashboard/doctor/${currentDoctorId}`);
                const data = await response.json();

                const queueHTML = data.patients.map((patient, index) => `
                    <div class="queue-item ${patient.status === 'IN_PROGRESS' ? 'active' : ''}"
                         onclick="selectPatient(${patient.appointment_id})"
                         data-id="${patient.appointment_id}">
                        <span class="token ${patient.status === 'WAITING' ? 'waiting' : ''}">Token ${patient.token || index + 1}</span>
                        <div class="name">${patient.patient_name}</div>
                        <div class="info">
                            ${patient.age} years • ${patient.time}
                        </div>
                        <div class="complaint">📝 ${patient.chief_complaint || 'No complaint noted'}</div>
                    </div>
                `).join('');

                document.getElementById('patient-queue').innerHTML = queueHTML || '<div style="padding: 20px; text-align: center; color: #64748b;">No patients in queue</div>';
                document.getElementById('waiting-count').textContent = data.patients.filter(p => p.status === 'WAITING' || p.status === 'CHECKED_IN').length;
            } catch (error) {
                console.error('Error loading queue:', error);
            }
        }

        // Select Patient
        async function selectPatient(appointmentId) {
            // Highlight selected
            document.querySelectorAll('.queue-item').forEach(el => el.classList.remove('active'));
            document.querySelector(`[data-id="${appointmentId}"]`).classList.add('active');

            // Load consultation view
            try {
                const response = await fetch(`/dashboard/consultation/${appointmentId}`);
                const data = await response.json();

                currentAppointment = data.appointment;

                // Show patient form
                document.getElementById('no-patient-selected').style.display = 'none';
                document.getElementById('patient-header-section').style.display = 'block';

                // Fill patient info
                document.getElementById('current-patient-name').textContent = data.appointment.patient;
                document.getElementById('current-patient-id').textContent = data.appointment.patient_id;

                if (data.patient_summary) {
                    document.getElementById('current-patient-age').textContent =
                        `${data.patient_summary.demographics.age} years`;
                    document.getElementById('current-patient-blood').textContent =
                        data.patient_summary.demographics.blood_group || 'Unknown';

                    // Fill alerts
                    const alertsHTML = data.patient_summary.alerts.map(alert =>
                        `<div class="alert-item">${alert}</div>`
                    ).join('');
                    document.getElementById('patient-alerts').innerHTML = alertsHTML || '';

                    // AI Summary
                    const summary = data.patient_summary;
                    document.getElementById('ai-summary').innerHTML = `
                        <strong>Last Visit:</strong> ${summary.last_visit || 'First visit'}<br>
                        <strong>Allergies:</strong> ${summary.allergies.join(', ') || 'None known'}<br>
                        <strong>Conditions:</strong> ${summary.chronic_conditions.join(', ') || 'None'}
                    `;
                }

                // Chief complaint
                document.getElementById('chief-complaint').value = data.appointment.chief_complaint || '';

                // Load timeline
                loadTimeline(data.timeline);

                // Start consultation (create encounter)
                startConsultation(appointmentId);

            } catch (error) {
                console.error('Error loading patient:', error);
            }
        }

        // Start Consultation
        async function startConsultation(appointmentId) {
            try {
                const response = await fetch(`/dashboard/consultation/${appointmentId}/start`, {
                    method: 'POST'
                });
                const data = await response.json();
                if (data.success) {
                    currentEncounter = data.encounter_id;
                }
            } catch (error) {
                console.error('Error starting consultation:', error);
            }
        }

        // Load Timeline
        function loadTimeline(timeline) {
            if (!timeline || timeline.length === 0) {
                document.getElementById('patient-timeline').innerHTML =
                    '<div style="text-align: center; padding: 40px; color: #64748b;">No previous records</div>';
                return;
            }

            const icons = {
                'encounter': '🩺',
                'lab': '🧪',
                'imaging': '🩻',
                'prescription': '💊',
                'admission': '🏥',
                'emergency': '🚑'
            };

            const timelineHTML = `
                <div class="timeline-year">${new Date().getFullYear()}</div>
                ${timeline.map(item => `
                    <div class="timeline-item">
                        <div class="timeline-icon ${item.type}">${icons[item.type] || '📄'}</div>
                        <div class="timeline-details">
                            <h4>${item.title}</h4>
                            <p>${item.details.chief_complaint || item.details.diagnosis || 'No details'}</p>
                            <div class="timeline-date">${new Date(item.date).toLocaleDateString()}</div>
                        </div>
                    </div>
                `).join('')}
            `;

            document.getElementById('patient-timeline').innerHTML = timelineHTML;
        }

        // Add Medicine Row
        function addMedicineRow() {
            const container = document.getElementById('medicine-list');
            const index = container.children.length;
            const row = document.createElement('div');
            row.className = 'medicine-row';
            row.dataset.index = index;
            row.innerHTML = `
                <input type="text" placeholder="Medicine name" class="med-name">
                <input type="text" placeholder="Dose" class="med-dose">
                <input type="text" placeholder="Frequency" class="med-freq">
                <input type="text" placeholder="Duration" class="med-duration">
                <button onclick="this.parentElement.remove()" style="background: #fee2e2; border: none; border-radius: 5px; cursor: pointer; color: #991b1b;">🗑</button>
            `;
            container.appendChild(row);
        }

        // Save Draft
        async function saveDraft() {
            if (!currentEncounter) return;

            const data = collectFormData();

            try {
                const response = await fetch(`/dashboard/consultation/${currentEncounter}/save`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    alert('Draft saved!');
                }
            } catch (error) {
                console.error('Error saving draft:', error);
            }
        }

        // Complete Consultation
        async function completeConsultation() {
            if (!currentEncounter) {
                alert('Please select a patient first');
                return;
            }

            const data = collectFormData();

            try {
                const response = await fetch(`/dashboard/consultation/${currentEncounter}/complete`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    alert('Consultation completed! Prescription generated.');
                    loadPatientQueue(); // Refresh queue

                    // Reset form
                    document.getElementById('patient-header-section').style.display = 'none';
                    document.getElementById('no-patient-selected').style.display = 'block';
                    document.getElementById('patient-timeline').innerHTML =
                        '<div style="text-align: center; padding: 40px; color: #64748b;"><p>Select a patient to view their timeline</p></div>';
                }
            } catch (error) {
                console.error('Error completing consultation:', error);
            }
        }

        // Collect Form Data
        function collectFormData() {
            const medicines = [];
            document.querySelectorAll('.medicine-row').forEach(row => {
                const name = row.querySelector('.med-name').value;
                if (name) {
                    medicines.push({
                        medicine: name,
                        dosage: row.querySelector('.med-dose').value,
                        frequency: row.querySelector('.med-freq').value,
                        duration: row.querySelector('.med-duration').value
                    });
                }
            });

            const investigations = [];
            document.querySelectorAll('.investigation:checked').forEach(cb => {
                investigations.push(cb.value);
            });

            return {
                chief_complaint: document.getElementById('chief-complaint').value,
                vitals: {
                    bp: document.getElementById('vital-bp').value,
                    pulse: document.getElementById('vital-pulse').value,
                    temperature: document.getElementById('vital-temp').value,
                    spo2: document.getElementById('vital-spo2').value,
                    weight: document.getElementById('vital-weight').value
                },
                primary_diagnosis: document.getElementById('primary-diagnosis').value,
                prescriptions: medicines,
                lab_orders: investigations
            };
        }

        // Load Patient History
        function loadPatientHistory() {
            if (currentAppointment) {
                alert('Loading full patient history... (Feature coming soon)');
            }
        }
    </script>
</body>
</html>
"""


@app.get("/doctor")
async def doctor_dashboard():
    """Serve the Doctor Dashboard HTML page"""
    return HTMLResponse(content=DOCTOR_DASHBOARD_HTML)


@app.get("/")
async def admin_dashboard_redirect():
    """Redirect old admin route to new dashboard"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dashboard/admin/stats")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
