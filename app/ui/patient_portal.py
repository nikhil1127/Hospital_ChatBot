"""
Patient Portal - Patient Self-Service
"""

PATIENT_PORTAL_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Patient Portal - MedCare Hospital</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0ea5e9, #3b82f6);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .header {
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .header h1 {
            color: #1e293b;
            margin-bottom: 10px;
        }
        .patient-card {
            background: linear-gradient(135deg, #3b82f6, #0ea5e9);
            color: white;
            padding: 25px;
            border-radius: 16px;
            margin-bottom: 20px;
        }
        .patient-id {
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 10px;
        }
        .patient-info {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 15px;
        }
        .info-item {
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
        }
        .menu-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        .menu-item {
            background: white;
            padding: 25px;
            border-radius: 16px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .menu-item:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }
        .menu-icon {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        .menu-label {
            font-weight: 600;
            color: #1e293b;
        }
        .section {
            background: white;
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .section-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #1e293b;
        }
        .timeline-item {
            border-left: 3px solid #3b82f6;
            padding-left: 20px;
            padding-bottom: 20px;
            position: relative;
        }
        .timeline-item::before {
            content: '';
            position: absolute;
            left: -8px;
            top: 0;
            width: 14px;
            height: 14px;
            background: #3b82f6;
            border-radius: 50%;
        }
        .timeline-date {
            font-size: 0.85rem;
            color: #64748b;
        }
        .timeline-title {
            font-weight: 600;
            color: #1e293b;
            margin: 5px 0;
        }
        .btn {
            padding: 12px 24px;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            border: none;
            background: linear-gradient(135deg, #3b82f6, #0ea5e9);
            color: white;
        }
        .alert-box {
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
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
            <a href="/emergency" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🚨 ER</a>
            <a href="/patient" style="color: white; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; background: #0ea5e9;">🧑‍⚕️ Patient</a>
            <a href="/" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🚪 Exit</a>
        </div>
    </nav>
    <div class="container" style="margin-top: 16px;">
        <!-- Header -->
        <div class="header">
            <h1>🏥 MedCare Hospital</h1>
            <p style="color: #64748b;">Patient Portal</p>
        </div>

        <!-- Patient Card -->
        <div class="patient-card">
            <div class="patient-id">PAT-2026-000123</div>
            <div style="font-size: 1.5rem; font-weight: 600;">Rahul Sharma</div>
            <div class="patient-info">
                <div class="info-item">Age: 35</div>
                <div class="info-item">Blood: O+</div>
                <div class="info-item">Gender: Male</div>
            </div>
        </div>

        <!-- Alert -->
        <div class="alert-box">
            <strong>📅 Upcoming Appointment:</strong> Tomorrow at 10:00 AM with Dr. Sarah Smith (Cardiology)
        </div>

        <!-- Menu Grid -->
        <div class="menu-grid">
            <div class="menu-item" onclick="showSection('appointments')">
                <div class="menu-icon">📅</div>
                <div class="menu-label">Appointments</div>
            </div>
            <div class="menu-item" onclick="showSection('records')">
                <div class="menu-icon">📋</div>
                <div class="menu-label">Medical Records</div>
            </div>
            <div class="menu-item" onclick="showSection('lab')">
                <div class="menu-icon">🧪</div>
                <div class="menu-label">Lab Reports</div>
            </div>
            <div class="menu-item" onclick="showSection('billing')">
                <div class="menu-icon">💰</div>
                <div class="menu-label">Bills & Payments</div>
            </div>
            <div class="menu-item" onclick="showSection('prescriptions')">
                <div class="menu-icon">💊</div>
                <div class="menu-label">Prescriptions</div>
            </div>
            <div class="menu-item" onclick="showSection('insurance')">
                <div class="menu-icon">🛡️</div>
                <div class="menu-label">Insurance</div>
            </div>
        </div>

        <!-- Health Timeline -->
        <div class="section">
            <div class="section-header">
                <div class="section-title">📈 Health Timeline</div>
                <button class="btn">View All</button>
            </div>

            <div class="timeline-item">
                <div class="timeline-date">15 Jan 2026, 10:30 AM</div>
                <div class="timeline-title">Cardiology Consultation</div>
                <div style="color: #64748b; font-size: 0.9rem;">Dr. Sarah Smith | BP: 120/80, Pulse: 72</div>
            </div>

            <div class="timeline-item">
                <div class="timeline-date">10 Jan 2026</div>
                <div class="timeline-title">Blood Test Results</div>
                <div style="color: #64748b; font-size: 0.9rem;">CBC, Lipid Profile - All Normal</div>
            </div>

            <div class="timeline-item">
                <div class="timeline-date">5 Jan 2026</div>
                <div class="timeline-title">Annual Health Checkup</div>
                <div style="color: #64748b; font-size: 0.9rem;">General Physician | Overall Good Health</div>
            </div>
        </div>

        <!-- Quick Actions -->
        <div class="section">
            <div class="section-title" style="margin-bottom: 15px;">⚡ Quick Actions</div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <button class="btn">Book Appointment</button>
                <button class="btn" style="background: linear-gradient(135deg, #059669, #10b981);">Download Reports</button>
                <button class="btn" style="background: linear-gradient(135deg, #7c3aed, #a855f7);">Pay Bill</button>
                <button class="btn" style="background: linear-gradient(135deg, #dc2626, #ef4444);">Emergency</button>
            </div>
        </div>
    </div>

    <script>
        function showSection(section) {
            alert('Opening ' + section + ' section...\n\nThis would show the full ' + section + ' interface');
        }
    </script>
</body>
</html>
"""
