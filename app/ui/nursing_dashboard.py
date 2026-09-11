"""
Nursing Dashboard - Vitals & Care Management
"""

NURSING_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nursing Station - MedCare Hospital</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #db2777, #ec4899);
            color: white;
            padding: 20px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
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
            color: #db2777;
            border-bottom-color: #db2777;
        }
        .main-container {
            padding: 24px 30px;
            max-width: 1600px;
            margin: 0 auto;
        }
        .ward-selector {
            background: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        .patient-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }
        .patient-card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            overflow: hidden;
        }
        .patient-header {
            background: linear-gradient(135deg, #fce7f3, #fbcfe8);
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: start;
        }
        .patient-name {
            font-size: 1.2rem;
            font-weight: 600;
            color: #831843;
        }
        .bed-number {
            background: #db2777;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        .patient-body {
            padding: 20px;
        }
        .vitals-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 15px;
        }
        .vital-box {
            background: #f9fafb;
            padding: 12px;
            border-radius: 10px;
            text-align: center;
        }
        .vital-label {
            font-size: 0.7rem;
            color: #6b7280;
            text-transform: uppercase;
        }
        .vital-value {
            font-size: 1.2rem;
            font-weight: 700;
            color: #1e293b;
            margin-top: 4px;
        }
        .vital-value.alert {
            color: #dc2626;
        }
        .btn {
            padding: 10px 16px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            border: none;
            font-size: 0.9rem;
        }
        .btn-primary {
            background: linear-gradient(135deg, #db2777, #ec4899);
            color: white;
        }
        .btn-secondary {
            background: #fce7f3;
            color: #831843;
        }
        .medication-list {
            background: #f9fafb;
            border-radius: 10px;
            padding: 15px;
            margin-top: 15px;
        }
        .med-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #e5e7eb;
        }
        .med-item:last-child {
            border-bottom: none;
        }
        .status-given {
            background: #d1fae5;
            color: #065f46;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.7rem;
        }
        .status-pending {
            background: #fef3c7;
            color: #92400e;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.7rem;
        }
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        .modal.active {
            display: flex;
        }
        .modal-content {
            background: white;
            border-radius: 16px;
            width: 90%;
            max-width: 500px;
            padding: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #374151;
        }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
        }
        .form-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
        }
        .quick-actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        .shift-indicator {
            background: #fce7f3;
            color: #831843;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
    </style>
</head>
<body>
    <!-- Global Navigation -->
    <nav style="background: #1e293b; padding: 8px 30px; display: flex; justify-content: space-between; align-items: center;">
        <a href="/" style="color: white; text-decoration: none; font-weight: 600; font-size: 1.1rem;">🏥 MedCare HMS</a>
        <div style="display: flex; gap: 5px;">
            <a href="/admin" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">📊 Admin</a>
            <a href="/doctor" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">👨‍⚕️ Doctor</a>
            <a href="/ipd" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🛏️ IPD</a>
            <a href="/nursing" style="color: white; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; background: #db2777;">👩‍⚕️ Nursing</a>
            <a href="/pharmacy" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">💊 Pharmacy</a>
            <a href="/billing" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">💰 Billing</a>
            <a href="/emergency" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🚨 ER</a>
            <a href="/patient" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🧑‍⚕️ Patient</a>
            <a href="/" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🚪 Exit</a>
        </div>
    </nav>
    <header class="header">
        <h1>👩‍⚕️ Nursing Station</h1>
        <div style="display: flex; align-items: center; gap: 20px;">
            <div class="shift-indicator">
                <span>🌅</span>
                <span>Morning Shift (7AM - 2PM)</span>
            </div>
            <div>
                <div style="font-weight: 600;">Head Nurse</div>
                <div style="font-size: 0.85rem; opacity: 0.9;">Ward A & B</div>
            </div>
        </div>
    </header>

    <div class="nav-tabs">
        <div class="nav-tab active" onclick="showTab('patients')">👥 My Patients</div>
        <div class="nav-tab" onclick="showTab('vitals')">🩺 Vitals Entry</div>
        <div class="nav-tab" onclick="showTab('medications')">💊 Medications</div>
        <div class="nav-tab" onclick="showTab('notes')">📝 Notes</div>
    </div>

    <div class="main-container">
        <!-- Ward Selector -->
        <div class="ward-selector">
            <strong style="margin-right: 15px;">Select Ward:</strong>
            <select style="padding: 8px 15px; border: 1px solid #e2e8f0; border-radius: 6px;">
                <option>General Ward A</option>
                <option>General Ward B</option>
                <option>ICU</option>
                <option>Private Ward</option>
            </select>
            <span style="margin-left: 20px; color: #64748b;">
                Total Patients: <strong style="color: #1e293b;">12</strong>
            </span>
        </div>

        <!-- Patients Tab -->
        <div id="patients-tab" class="tab-content active">
            <div class="patient-grid">
                <!-- Patient 1 -->
                <div class="patient-card">
                    <div class="patient-header">
                        <div>
                            <div class="patient-name">Rahul Sharma</div>
                            <div style="font-size: 0.85rem; color: #9d174d; margin-top: 5px;">Age: 45 | Admitted: 2 days</div>
                        </div>
                        <div class="bed-number">Bed 101</div>
                    </div>
                    <div class="patient-body">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                            <span style="color: #64748b;">ID: PAT-2026-000001</span>
                            <span style="background: #d1fae5; color: #065f46; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem;">Stable</span>
                        </div>

                        <strong style="font-size: 0.85rem; color: #6b7280;">Last Vitals (30 min ago)</strong>
                        <div class="vitals-grid">
                            <div class="vital-box">
                                <div class="vital-label">BP</div>
                                <div class="vital-value">120/80</div>
                            </div>
                            <div class="vital-box">
                                <div class="vital-label">Pulse</div>
                                <div class="vital-value">72</div>
                            </div>
                            <div class="vital-box">
                                <div class="vital-label">SpO2</div>
                                <div class="vital-value alert">92%</div>
                            </div>
                            <div class="vital-box">
                                <div class="vital-label">Temp</div>
                                <div class="vital-value">98.4</div>
                            </div>
                            <div class="vital-box">
                                <div class="vital-label">Resp</div>
                                <div class="vital-value">18</div>
                            </div>
                            <div class="vital-box">
                                <div class="vital-label">Pain</div>
                                <div class="vital-value">2/10</div>
                            </div>
                        </div>

                        <div class="medication-list">
                            <strong style="font-size: 0.85rem; color: #6b7280;">Upcoming Medications</strong>
                            <div class="med-item">
                                <div>
                                    <div style="font-weight: 500;">Paracetamol 500mg</div>
                                    <div style="font-size: 0.8rem; color: #64748b;">1-1-1 | After food</div>
                                </div>
                                <span class="status-pending">10:00 AM</span>
                            </div>
                            <div class="med-item">
                                <div>
                                    <div style="font-weight: 500;">Amoxicillin 500mg</div>
                                    <div style="font-size: 0.8rem; color: #64748b;">1-0-1</div>
                                </div>
                                <span class="status-given">8:00 AM ✓</span>
                            </div>
                        </div>

                        <div class="quick-actions">
                            <button class="btn btn-primary" onclick="openVitalsModal('Rahul Sharma')">Record Vitals</button>
                            <button class="btn btn-secondary" onclick="openMedModal('Rahul Sharma')">Give Med</button>
                            <button class="btn btn-secondary">Notes</button>
                        </div>
                    </div>
                </div>

                <!-- Patient 2 -->
                <div class="patient-card">
                    <div class="patient-header">
                        <div>
                            <div class="patient-name">Sunita Devi</div>
                            <div style="font-size: 0.85rem; color: #9d174d; margin-top: 5px;">Age: 62 | Admitted: 5 days</div>
                        </div>
                        <div class="bed-number">Bed 102</div>
                    </div>
                    <div class="patient-body">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                            <span style="color: #64748b;">ID: PAT-2026-000002</span>
                            <span style="background: #fef3c7; color: #92400e; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem;">Requires Attention</span>
                        </div>

                        <strong style="font-size: 0.85rem; color: #6b7280;">Last Vitals (1 hour ago)</strong>
                        <div class="vitals-grid">
                            <div class="vital-box">
                                <div class="vital-label">BP</div>
                                <div class="vital-value alert">160/95</div>
                            </div>
                            <div class="vital-box">
                                <div class="vital-label">Pulse</div>
                                <div class="vital-value alert">105</div>
                            </div>
                            <div class="vital-box">
                                <div class="vital-label">SpO2</div>
                                <div class="vital-value">96%</div>
                            </div>
                            <div class="vital-box">
                                <div class="vital-label">Temp</div>
                                <div class="vital-value">99.2</div>
                            </div>
                            <div class="vital-box">
                                <div class="vital-label">Resp</div>
                                <div class="vital-value">22</div>
                            </div>
                            <div class="vital-box">
                                <div class="vital-label">Pain</div>
                                <div class="vital-value alert">7/10</div>
                            </div>
                        </div>

                        <div class="quick-actions">
                            <button class="btn btn-primary" onclick="openVitalsModal('Sunita Devi')">Record Vitals</button>
                            <button class="btn btn-secondary" onclick="openMedModal('Sunita Devi')">Give Med</button>
                            <button class="btn btn-secondary">Notes</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Other tabs would have similar content -->
        <div id="vitals-tab" class="tab-content">
            <div style="text-align: center; padding: 60px; color: #64748b;">
                <div style="font-size: 3rem; margin-bottom: 20px;">🩺</div>
                <h3>Vitals Entry Form</h3>
                <p>Select a patient from "My Patients" tab to record vitals</p>
            </div>
        </div>

        <div id="medications-tab" class="tab-content">
            <div style="text-align: center; padding: 60px; color: #64748b;">
                <div style="font-size: 3rem; margin-bottom: 20px;">💊</div>
                <h3>Medication Schedule</h3>
                <p>View and administer medications by shift</p>
            </div>
        </div>

        <div id="notes-tab" class="tab-content">
            <div style="text-align: center; padding: 60px; color: #64748b;">
                <div style="font-size: 3rem; margin-bottom: 20px;">📝</div>
                <h3>Nursing Notes</h3>
                <p>Record patient observations and handover notes</p>
            </div>
        </div>
    </div>

    <!-- Vitals Modal -->
    <div id="vitals-modal" class="modal">
        <div class="modal-content">
            <h3 style="margin-bottom: 20px;">Record Vitals - <span id="vitals-patient-name"></span></h3>
            <div class="form-row">
                <div class="form-group">
                    <label>BP (mmHg)</label>
                    <input type="text" placeholder="120/80">
                </div>
                <div class="form-group">
                    <label>Pulse</label>
                    <input type="number" placeholder="72">
                </div>
                <div class="form-group">
                    <label>SpO2 (%)</label>
                    <input type="number" placeholder="98">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Temperature (°F)</label>
                    <input type="number" placeholder="98.6">
                </div>
                <div class="form-group">
                    <label>Resp Rate</label>
                    <input type="number" placeholder="18">
                </div>
                <div class="form-group">
                    <label>Pain Score (0-10)</label>
                    <input type="number" placeholder="0" min="0" max="10">
                </div>
            </div>
            <div class="form-group">
                <label>Notes</label>
                <input type="text" placeholder="Any observations...">
            </div>
            <div style="display: flex; gap: 10px;">
                <button class="btn btn-primary" style="flex: 1;" onclick="saveVitals()">Save Vitals</button>
                <button class="btn" style="background: #e5e7eb;" onclick="closeModal('vitals-modal')">Cancel</button>
            </div>
        </div>
    </div>

    <script>
        function showTab(tab) {
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tab + '-tab').classList.add('active');
        }

        function openVitalsModal(patientName) {
            document.getElementById('vitals-patient-name').textContent = patientName;
            document.getElementById('vitals-modal').classList.add('active');
        }

        function openMedModal(patientName) {
            alert('Medication administration for ' + patientName);
        }

        function closeModal(id) {
            document.getElementById(id).classList.remove('active');
        }

        function saveVitals() {
            alert('Vitals recorded successfully!');
            closeModal('vitals-modal');
        }

        // Close modal on outside click
        document.getElementById('vitals-modal').addEventListener('click', function(e) {
            if (e.target === this) closeModal('vitals-modal');
        });
    </script>
</body>
</html>
"""
