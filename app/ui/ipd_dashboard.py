"""
IPD Dashboard - Bed Management & Admissions
"""

IPD_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IPD Management - MedCare Hospital</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #059669, #10b981);
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
            color: #059669;
            border-bottom-color: #059669;
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
            color: #059669;
        }
        .card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 24px;
        }
        .card-header {
            background: #f8fafc;
            padding: 20px;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .card-header h2 {
            font-size: 1.2rem;
            color: #1e293b;
        }
        .btn {
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            border: none;
        }
        .btn-primary {
            background: linear-gradient(135deg, #059669, #10b981);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
        }
        .tab-content {
            display: none;
            padding: 24px;
        }
        .tab-content.active {
            display: block;
        }
        .ward-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        .ward-card {
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
        }
        .ward-card h3 {
            color: #1e293b;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .ward-type {
            font-size: 0.75rem;
            padding: 4px 10px;
            border-radius: 20px;
            background: #d1fae5;
            color: #065f46;
        }
        .bed-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
            margin-top: 15px;
        }
        .bed {
            aspect-ratio: 1;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        .bed.available {
            background: #d1fae5;
            color: #065f46;
            border: 2px solid #10b981;
        }
        .bed.occupied {
            background: #fee2e2;
            color: #991b1b;
            border: 2px solid #ef4444;
        }
        .bed.maintenance {
            background: #f3f4f6;
            color: #6b7280;
            border: 2px solid #9ca3af;
        }
        .admissions-table {
            width: 100%;
            border-collapse: collapse;
        }
        .admissions-table th {
            background: #f8fafc;
            padding: 14px 20px;
            text-align: left;
            font-weight: 600;
            font-size: 0.75rem;
            text-transform: uppercase;
            color: #6b7280;
        }
        .admissions-table td {
            padding: 16px 20px;
            border-bottom: 1px solid #e5e7eb;
            font-size: 0.9rem;
        }
        .admissions-table tr:hover {
            background: #f9fafb;
        }
        .status-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .status-admitted {
            background: #d1fae5;
            color: #065f46;
        }
        .status-critical {
            background: #fee2e2;
            color: #991b1b;
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
            max-height: 90vh;
            overflow-y: auto;
        }
        .modal-header {
            background: linear-gradient(135deg, #059669, #10b981);
            color: white;
            padding: 20px;
            border-radius: 16px 16px 0 0;
        }
        .modal-body {
            padding: 24px;
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
            font-size: 0.95rem;
        }
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
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
            <a href="/ipd" style="color: white; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; background: #059669;">🛏️ IPD</a>
            <a href="/nursing" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">👩‍⚕️ Nursing</a>
            <a href="/pharmacy" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">💊 Pharmacy</a>
            <a href="/billing" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">💰 Billing</a>
            <a href="/emergency" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🚨 ER</a>
            <a href="/patient" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🧑‍⚕️ Patient</a>
            <a href="/" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🚪 Exit</a>
        </div>
    </nav>
    <header class="header">
        <h1>🏥 IPD Management</h1>
        <div>
            <div style="font-weight: 600;">Ward Master</div>
            <div style="font-size: 0.85rem; opacity: 0.9;">Bed Allocation & Admissions</div>
        </div>
    </header>

    <div class="nav-tabs">
        <div class="nav-tab active" onclick="showTab('beds')">🛏️ Bed Status</div>
        <div class="nav-tab" onclick="showTab('admissions')">👥 Admissions</div>
        <div class="nav-tab" onclick="showTab('discharges')">🏃 Discharges</div>
        <div class="nav-tab" onclick="showTab('occupancy')">📊 Occupancy</div>
    </div>

    <div class="main-container">
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Beds</h3>
                <div class="number" id="total-beds">0</div>
            </div>
            <div class="stat-card">
                <h3>Occupied</h3>
                <div class="number" id="occupied-beds">0</div>
            </div>
            <div class="stat-card">
                <h3>Available</h3>
                <div class="number" id="available-beds">0</div>
            </div>
            <div class="stat-card">
                <h3>Today Admissions</h3>
                <div class="number" id="today-admissions">0</div>
            </div>
        </div>

        <!-- Bed Status Tab -->
        <div id="beds-tab" class="tab-content active">
            <div class="card">
                <div class="card-header">
                    <h2>Ward Overview</h2>
                    <button class="btn btn-primary" onclick="openAdmitModal()">+ Admit Patient</button>
                </div>
                <div style="padding: 24px;">
                    <div class="ward-grid" id="ward-grid">
                        <!-- Wards loaded dynamically -->
                        <p style="color: #64748b; text-align: center;">Loading wards...</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Admissions Tab -->
        <div id="admissions-tab" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <h2>Current Admissions</h2>
                    <input type="text" placeholder="Search patient..." style="padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 6px;">
                </div>
                <table class="admissions-table">
                    <thead>
                        <tr>
                            <th>Admission #</th>
                            <th>Patient</th>
                            <th>Bed</th>
                            <th>Admitted</th>
                            <th>Doctor</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="admissions-tbody">
                        <tr>
                            <td colspan="7" style="text-align: center; color: #64748b;">Loading admissions...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Discharges Tab -->
        <div id="discharges-tab" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <h2>Today's Discharges</h2>
                </div>
                <div style="padding: 24px;">
                    <p style="color: #64748b; text-align: center;">Discharge functionality coming soon...</p>
                </div>
            </div>
        </div>

        <!-- Occupancy Tab -->
        <div id="occupancy-tab" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <h2>Ward Occupancy Statistics</h2>
                </div>
                <div style="padding: 24px;">
                    <div id="occupancy-stats">
                        <p style="color: #64748b; text-align: center;">Loading occupancy data...</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Admit Patient Modal -->
    <div id="admit-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>📝 Admit New Patient</h2>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label>Patient ID or Phone *</label>
                    <input type="text" id="patient-search" placeholder="Enter PAT-2026-XXXXXX or phone number">
                    <button type="button" onclick="searchPatient()" style="margin-top: 8px; padding: 8px 16px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer;">Search</button>
                </div>

                <div id="patient-info" style="display: none; background: #f0fdf4; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <h4 style="color: #065f46;">Patient Found</h4>
                    <p id="patient-details"></p>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label>Admission Type *</label>
                        <select id="admission-type">
                            <option value="PLANNED">Planned</option>
                            <option value="EMERGENCY">Emergency</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Select Ward *</label>
                        <select id="ward-select" onchange="loadAvailableBeds()">
                            <option value="">Select Ward</option>
                        </select>
                    </div>
                </div>

                <div class="form-group">
                    <label>Select Bed *</label>
                    <select id="bed-select">
                        <option value="">Select Bed</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Primary Doctor *</label>
                    <select id="doctor-select">
                        <option value="">Select Doctor</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Chief Complaint *</label>
                    <textarea id="chief-complaint" rows="2" placeholder="Patient's main complaint"></textarea>
                </div>

                <div class="form-group">
                    <label>Provisional Diagnosis</label>
                    <input type="text" id="provisional-diagnosis" placeholder="Initial diagnosis">
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label>Blood Pressure</label>
                        <input type="text" id="admission-bp" placeholder="120/80">
                    </div>
                    <div class="form-group">
                        <label>Pulse</label>
                        <input type="number" id="admission-pulse" placeholder="72">
                    </div>
                </div>

                <div style="display: flex; gap: 10px; margin-top: 24px;">
                    <button class="btn btn-primary" onclick="admitPatient()" style="flex: 1;">Admit Patient</button>
                    <button class="btn" onclick="closeModal()" style="background: #e5e7eb; color: #374151;">Cancel</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // State
        let wards = [];
        let admissions = [];
        let doctors = [];

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadWards();
            loadAdmissions();
            loadStats();
            loadDoctors();
        });

        function showTab(tab) {
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tab + '-tab').classList.add('active');

            if (tab === 'occupancy') loadOccupancyStats();
        }

        async function loadWards() {
            try {
                const response = await fetch('/api/v1/ipd/wards/occupancy');
                const data = await response.json();
                wards = data.ward_stats || [];

                const grid = document.getElementById('ward-grid');
                grid.innerHTML = wards.map(ward => `
                    <div class="ward-card">
                        <h3>
                            ${ward.ward_name}
                            <span class="ward-type">${ward.ward_type}</span>
                        </h3>
                        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #64748b; margin-bottom: 10px;">
                            <span>Occupancy: ${ward.occupancy_rate}%</span>
                            <span>${ward.occupied}/${ward.total_beds} beds</span>
                        </div>
                        <div class="bed-grid">
                            ${generateBeds(ward)}
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Error loading wards:', error);
            }
        }

        function generateBeds(ward) {
            // Generate sample bed display
            const beds = [];
            for (let i = 1; i <= ward.total_beds; i++) {
                const isOccupied = i <= ward.occupied;
                const status = isOccupied ? 'occupied' : 'available';
                beds.push(`
                    <div class="bed ${status}" onclick="showBedDetails('${ward.ward_name}', ${i}, ${isOccupied})">
                        <div style="font-size: 1.2rem;">🛏️</div>
                        <div>${i}</div>
                    </div>
                `);
            }
            return beds.join('');
        }

        async function loadAdmissions() {
            try {
                // This would fetch from API
                const tbody = document.getElementById('admissions-tbody');
                tbody.innerHTML = `
                    <tr>
                        <td colspan="7" style="text-align: center; padding: 40px; color: #64748b;">
                            <div style="font-size: 3rem; margin-bottom: 10px;">🏥</div>
                            <p>No active admissions found</p>
                        </td>
                    </tr>
                `;
            } catch (error) {
                console.error('Error loading admissions:', error);
            }
        }

        async function loadStats() {
            try {
                const response = await fetch('/api/v1/admin/dashboard');
                const data = await response.json();

                document.getElementById('today-admissions').textContent = data.today?.admissions || 0;
                // Would fetch bed stats from API
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        async function loadDoctors() {
            try {
                // Would fetch from API
                doctors = [
                    { id: 1, name: 'Dr. Sarah Smith' },
                    { id: 2, name: 'Dr. James Wilson' },
                ];

                const select = document.getElementById('doctor-select');
                select.innerHTML = '<option value="">Select Doctor</option>' +
                    doctors.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
            } catch (error) {
                console.error('Error loading doctors:', error);
            }
        }

        function openAdmitModal() {
            document.getElementById('admit-modal').classList.add('active');
            loadWardOptions();
        }

        function closeModal() {
            document.getElementById('admit-modal').classList.remove('active');
        }

        function loadWardOptions() {
            const select = document.getElementById('ward-select');
            select.innerHTML = '<option value="">Select Ward</option>' +
                wards.map(w => `<option value="${w.ward_id}">${w.ward_name}</option>`).join('');
        }

        async function loadAvailableBeds() {
            const wardId = document.getElementById('ward-select').value;
            if (!wardId) return;

            try {
                const response = await fetch(`/api/v1/ipd/beds/available?ward_id=${wardId}`);
                const data = await response.json();

                const select = document.getElementById('bed-select');
                select.innerHTML = '<option value="">Select Bed</option>' +
                    (data.beds || []).map(b => `<option value="${b.bed_id}">${b.bed_number}</option>`).join('');
            } catch (error) {
                console.error('Error loading beds:', error);
            }
        }

        async function searchPatient() {
            const query = document.getElementById('patient-search').value;
            if (!query) return;

            try {
                const response = await fetch(`/api/v1/search/patients?q=${query}`);
                const data = await response.json();

                if (data && data.length > 0) {
                    const patient = data[0];
                    document.getElementById('patient-info').style.display = 'block';
                    document.getElementById('patient-details').innerHTML = `
                        <strong>Name:</strong> ${patient.name}<br>
                        <strong>ID:</strong> ${patient.patient_id}<br>
                        <strong>Age:</strong> ${patient.age} years
                    `;
                } else {
                    alert('Patient not found. Please register first.');
                }
            } catch (error) {
                console.error('Error searching patient:', error);
            }
        }

        async function admitPatient() {
            const data = {
                patient_id: document.getElementById('patient-search').value,
                bed_id: document.getElementById('bed-select').value,
                doctor_id: document.getElementById('doctor-select').value,
                type: document.getElementById('admission-type').value,
                chief_complaint: document.getElementById('chief-complaint').value,
                provisional_diagnosis: document.getElementById('provisional-diagnosis').value,
                bp: document.getElementById('admission-bp').value,
                pulse: document.getElementById('admission-pulse').value
            };

            if (!data.bed_id || !data.doctor_id || !data.chief_complaint) {
                alert('Please fill all required fields');
                return;
            }

            try {
                const response = await fetch('/api/v1/ipd/admit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                if (result.success) {
                    alert(`Patient admitted successfully! Admission: ${result.admission_number}`);
                    closeModal();
                    loadWards();
                    loadAdmissions();
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                console.error('Error admitting patient:', error);
            }
        }

        function showBedDetails(ward, bedNumber, isOccupied) {
            if (isOccupied) {
                alert(`Bed ${bedNumber} in ${ward} is currently occupied`);
            } else {
                alert(`Bed ${bedNumber} in ${ward} is available for admission`);
            }
        }

        function loadOccupancyStats() {
            const stats = document.getElementById('occupancy-stats');
            let html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">';

            wards.forEach(ward => {
                const percent = ward.occupancy_rate;
                const color = percent > 90 ? '#ef4444' : percent > 70 ? '#f59e0b' : '#10b981';

                html += `
                    <div style="background: #f8fafc; padding: 20px; border-radius: 12px;">
                        <h4 style="margin-bottom: 10px;">${ward.ward_name}</h4>
                        <div style="display: flex; align-items: center; gap: 15px;">
                            <div style="width: 60px; height: 60px; border-radius: 50%; background: conic-gradient(${color} ${percent}%, #e5e7eb 0); display: flex; align-items: center; justify-content: center;">
                                <div style="width: 45px; height: 45px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600;">${percent}%</div>
                            </div>
                            <div>
                                <div style="font-size: 0.9rem; color: #64748b;">${ward.occupied} occupied</div>
                                <div style="font-size: 0.9rem; color: #64748b;">${ward.available} available</div>
                            </div>
                        </div>
                    </div>
                `;
            });

            html += '</div>';
            stats.innerHTML = html;
        }

        // Close modal on outside click
        document.getElementById('admit-modal').addEventListener('click', function(e) {
            if (e.target === this) closeModal();
        });
    </script>
</body>
</html>
"""
