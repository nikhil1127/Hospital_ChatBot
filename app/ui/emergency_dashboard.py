"""
Emergency Dashboard - Triage & ER Management
"""

EMERGENCY_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emergency Department - MedCare Hospital</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #dc2626, #ef4444);
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
            color: #dc2626;
            border-bottom-color: #dc2626;
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
            color: #dc2626;
        }
        .triage-queue {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 24px;
        }
        .triage-column {
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            overflow: hidden;
        }
        .triage-header {
            padding: 15px;
            text-align: center;
            font-weight: 700;
            color: white;
        }
        .triage-header.red { background: #dc2626; }
        .triage-header.yellow { background: #f59e0b; }
        .triage-header.green { background: #059669; }
        .triage-header.black { background: #374151; }
        .triage-content {
            padding: 15px;
            min-height: 300px;
        }
        .patient-ticket {
            background: #f9fafb;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #e5e7eb;
            cursor: pointer;
            transition: all 0.2s;
        }
        .patient-ticket:hover {
            transform: translateX(5px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .ticket-time {
            font-size: 0.75rem;
            color: #64748b;
        }
        .ticket-name {
            font-weight: 600;
            color: #1e293b;
            margin: 5px 0;
        }
        .ticket-complaint {
            font-size: 0.85rem;
            color: #6b7280;
        }
        .btn {
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            border: none;
        }
        .btn-primary {
            background: linear-gradient(135deg, #dc2626, #ef4444);
            color: white;
        }
        .timer {
            font-size: 2rem;
            font-weight: 700;
            font-family: monospace;
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
            max-width: 600px;
            padding: 30px;
            max-height: 90vh;
            overflow-y: auto;
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
        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
        }
        .triage-options {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin: 15px 0;
        }
        .triage-option {
            padding: 15px;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            cursor: pointer;
            text-align: center;
        }
        .triage-option:hover {
            border-color: #dc2626;
        }
        .triage-option.selected {
            background: #fee2e2;
            border-color: #dc2626;
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
            <a href="/nursing" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">👩‍⚕️ Nursing</a>
            <a href="/pharmacy" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">💊 Pharmacy</a>
            <a href="/billing" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">💰 Billing</a>
            <a href="/emergency" style="color: white; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; background: #dc2626;">🚨 ER</a>
            <a href="/patient" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🧑‍⚕️ Patient</a>
            <a href="/" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🚪 Exit</a>
        </div>
    </nav>
    <header class="header">
        <h1>🚨 Emergency Department</h1>
        <div style="display: flex; align-items: center; gap: 20px;">
            <div style="background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 10px;">
                <div style="font-size: 0.85rem;">Current Wait Time</div>
                <div class="timer" style="font-size: 1.5rem;">00:12:45</div>
            </div>
            <div>
                <div style="font-weight: 600;">ED Physician</div>
                <div style="font-size: 0.85rem; opacity: 0.9;">Dr. Emergency</div>
            </div>
        </div>
    </header>

    <div class="nav-tabs">
        <div class="nav-tab active" onclick="showTab('triage')">🚦 Triage Queue</div>
        <div class="nav-tab" onclick="showTab('patients')">👥 Active Patients</div>
        <div class="nav-tab" onclick="showTab('register')">📝 Registration</div>
        <div class="nav-tab" onclick="showTab('stats')">📊 Statistics</div>
    </div>

    <div class="main-container">
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Today's Visits</h3>
                <div class="number">24</div>
            </div>
            <div class="stat-card">
                <h3>Waiting</h3>
                <div class="number">8</div>
            </div>
            <div class="stat-card">
                <h3>Critical</h3>
                <div class="number" style="color: #dc2626;">2</div>
            </div>
            <div class="stat-card">
                <h3>Avg Wait Time</h3>
                <div class="number">18m</div>
            </div>
        </div>

        <!-- Triage Queue Tab -->
        <div id="triage-tab" class="tab-content active">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2 style="color: #1e293b;">Triage Queue</h2>
                <button class="btn btn-primary" onclick="openRegisterModal()">+ New Patient</button>
            </div>

            <div class="triage-queue">
                <!-- RED - Immediate -->
                <div class="triage-column">
                    <div class="triage-header red">
                        🔴 IMMEDIATE<br>
                        <small>Life Threatening</small>
                    </div>
                    <div class="triage-content">
                        <div class="patient-ticket" style="border-left-color: #dc2626;">
                            <div class="ticket-time">10:23 AM - Waiting: 2 min</div>
                            <div class="ticket-name">Patient A</div>
                            <div class="ticket-complaint">Chest Pain, SOB</div>
                        </div>
                        <div class="patient-ticket" style="border-left-color: #dc2626;">
                            <div class="ticket-time">10:30 AM - Waiting: 0 min</div>
                            <div class="ticket-name">Patient B</div>
                            <div class="ticket-complaint">Severe Bleeding</div>
                        </div>
                    </div>
                </div>

                <!-- YELLOW - Urgent -->
                <div class="triage-column">
                    <div class="triage-header yellow">
                        🟡 URGENT<br>
                        <small>Potentially Serious</small>
                    </div>
                    <div class="triage-content">
                        <div class="patient-ticket" style="border-left-color: #f59e0b;">
                            <div class="ticket-time">10:15 AM - Waiting: 15 min</div>
                            <div class="ticket-name">Patient C</div>
                            <div class="ticket-complaint">Abdominal Pain</div>
                        </div>
                        <div class="patient-ticket" style="border-left-color: #f59e0b;">
                            <div class="ticket-time">10:20 AM - Waiting: 10 min</div>
                            <div class="ticket-name">Patient D</div>
                            <div class="ticket-complaint">High Fever</div>
                        </div>
                    </div>
                </div>

                <!-- GREEN - Less Urgent -->
                <div class="triage-column">
                    <div class="triage-header green">
                        🟢 LESS URGENT<br>
                        <small>Minor Conditions</small>
                    </div>
                    <div class="triage-content">
                        <div class="patient-ticket" style="border-left-color: #059669;">
                            <div class="ticket-time">10:00 AM - Waiting: 30 min</div>
                            <div class="ticket-name">Patient E</div>
                            <div class="ticket-complaint">Sprained Ankle</div>
                        </div>
                        <div class="patient-ticket" style="border-left-color: #059669;">
                            <div class="ticket-time">10:05 AM - Waiting: 25 min</div>
                            <div class="ticket-name">Patient F</div>
                            <div class="ticket-complaint">Minor Cut</div>
                        </div>
                        <div class="patient-ticket" style="border-left-color: #059669;">
                            <div class="ticket-time">10:10 AM - Waiting: 20 min</div>
                            <div class="ticket-name">Patient G</div>
                            <div class="ticket-complaint">Cough & Cold</div>
                        </div>
                    </div>
                </div>

                <!-- BLACK - Deceased/Expectant -->
                <div class="triage-column">
                    <div class="triage-header black">
                        ⚫ EXPECTANT<br>
                        <small>Deceased/Comfort Care</small>
                    </div>
                    <div class="triage-content">
                        <p style="color: #9ca3af; text-align: center; padding: 40px 20px;">None</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Other tabs would have content here -->
        <div id="patients-tab" class="tab-content">
            <div style="text-align: center; padding: 60px; color: #64748b;">
                <div style="font-size: 3rem; margin-bottom: 20px;">👥</div>
                <h3>Active Patients</h3>
                <p>Patients currently being treated</p>
            </div>
        </div>

        <div id="register-tab" class="tab-content">
            <div style="text-align: center; padding: 60px; color: #64748b;">
                <div style="font-size: 3rem; margin-bottom: 20px;">📝</div>
                <h3>Patient Registration</h3>
                <p>Register new emergency patients</p>
                <button class="btn btn-primary" style="margin-top: 20px;" onclick="openRegisterModal()">
                    Register New Patient
                </button>
            </div>
        </div>

        <div id="stats-tab" class="tab-content">
            <div style="text-align: center; padding: 60px; color: #64748b;">
                <div style="font-size: 3rem; margin-bottom: 20px;">📊</div>
                <h3>Emergency Statistics</h3>
                <p>Department performance metrics</p>
            </div>
        </div>
    </div>

    <!-- Register Patient Modal -->
    <div id="register-modal" class="modal">
        <div class="modal-content">
            <h2 style="margin-bottom: 20px; color: #dc2626;">🚨 Emergency Patient Registration</h2>

            <div class="form-group">
                <label>Patient ID / Phone (if known)</label>
                <input type="text" placeholder="Enter PAT-2026-XXXXXX or phone">
            </div>

            <div class="form-group">
                <label>Patient Name *</label>
                <input type="text" placeholder="Enter patient name">
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div class="form-group">
                    <label>Age</label>
                    <input type="number" placeholder="Years">
                </div>
                <div class="form-group">
                    <label>Gender</label>
                    <select>
                        <option>Male</option>
                        <option>Female</option>
                        <option>Other</option>
                    </select>
                </div>
            </div>

            <div class="form-group">
                <label>Chief Complaint *</label>
                <textarea rows="2" placeholder="What brings the patient to ED?"></textarea>
            </div>

            <div class="form-group">
                <label>Vitals (if available)</label>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                    <input type="text" placeholder="BP (120/80)">
                    <input type="number" placeholder="Pulse">
                    <input type="number" placeholder="SpO2 %">
                </div>
            </div>

            <div class="form-group">
                <label>Triage Category *</label>
                <div class="triage-options">
                    <div class="triage-option" onclick="selectTriage(this, 'RED')">
                        <div style="font-size: 1.5rem;">🔴</div>
                        <div style="font-weight: 600;">RED</div>
                        <div style="font-size: 0.8rem; color: #64748b;">Immediate</div>
                    </div>
                    <div class="triage-option" onclick="selectTriage(this, 'YELLOW')">
                        <div style="font-size: 1.5rem;">🟡</div>
                        <div style="font-weight: 600;">YELLOW</div>
                        <div style="font-size: 0.8rem; color: #64748b;">Urgent</div>
                    </div>
                    <div class="triage-option" onclick="selectTriage(this, 'GREEN')">
                        <div style="font-size: 1.5rem;">🟢</div>
                        <div style="font-weight: 600;">GREEN</div>
                        <div style="font-size: 0.8rem; color: #64748b;">Less Urgent</div>
                    </div>
                    <div class="triage-option" onclick="selectTriage(this, 'BLACK')">
                        <div style="font-size: 1.5rem;">⚫</div>
                        <div style="font-weight: 600;">BLACK</div>
                        <div style="font-size: 0.8rem; color: #64748b;">Expectant</div>
                    </div>
                </div>
            </div>

            <div style="display: flex; gap: 10px; margin-top: 24px;">
                <button class="btn btn-primary" style="flex: 1;" onclick="registerPatient()">
                    🚨 Register Patient
                </button>
                <button class="btn" onclick="closeModal()" style="background: #e5e7eb;">
                    Cancel
                </button>
            </div>
        </div>
    </div>

    <script>
        let selectedTriage = null;

        function showTab(tab) {
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tab + '-tab').classList.add('active');
        }

        function openRegisterModal() {
            document.getElementById('register-modal').classList.add('active');
        }

        function closeModal() {
            document.getElementById('register-modal').classList.remove('active');
        }

        function selectTriage(element, category) {
            document.querySelectorAll('.triage-option').forEach(el => el.classList.remove('selected'));
            element.classList.add('selected');
            selectedTriage = category;
        }

        function registerPatient() {
            if (!selectedTriage) {
                alert('Please select a triage category');
                return;
            }
            alert('Patient registered successfully with triage: ' + selectedTriage);
            closeModal();
        }

        // Update timer
        let seconds = 765; // 12:45 in seconds
        setInterval(() => {
            seconds++;
            const hrs = Math.floor(seconds / 3600).toString().padStart(2, '0');
            const mins = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
            const secs = (seconds % 60).toString().padStart(2, '0');
            document.querySelector('.timer').textContent = `${hrs}:${mins}:${secs}`;
        }, 1000);

        // Close modal on outside click
        document.getElementById('register-modal').addEventListener('click', function(e) {
            if (e.target === this) closeModal();
        });
    </script>
</body>
</html>
"""
