"""
Pharmacy Dashboard - Inventory & Dispensing
"""

PHARMACY_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pharmacy Management - MedCare Hospital</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #7c3aed, #a855f7);
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
            color: #7c3aed;
            border-bottom-color: #7c3aed;
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
            color: #7c3aed;
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
        .btn {
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            border: none;
            transition: all 0.2s;
        }
        .btn-primary {
            background: linear-gradient(135deg, #7c3aed, #a855f7);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
        }
        .alert-banner {
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 15px 20px;
            margin-bottom: 24px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .alert-banner.critical {
            background: #fee2e2;
            border-left-color: #ef4444;
        }
        .tab-content {
            display: none;
            padding: 24px;
        }
        .tab-content.active {
            display: block;
        }
        .search-bar {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .search-bar input {
            flex: 1;
            padding: 12px;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            font-size: 0.95rem;
        }
        .table-container {
            overflow-x: auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            background: #f8fafc;
            padding: 14px 20px;
            text-align: left;
            font-weight: 600;
            font-size: 0.75rem;
            text-transform: uppercase;
            color: #6b7280;
        }
        td {
            padding: 16px 20px;
            border-bottom: 1px solid #e5e7eb;
            font-size: 0.9rem;
        }
        tr:hover {
            background: #f9fafb;
        }
        .stock-low {
            color: #dc2626;
            font-weight: 600;
        }
        .stock-ok {
            color: #059669;
        }
        .expiry-warning {
            color: #f59e0b;
            font-weight: 600;
        }
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .badge-antibiotic { background: #dbeafe; color: #1e40af; }
        .badge-analgesic { background: #fce7f3; color: #be185d; }
        .badge-cardiac { background: #fef3c7; color: #92400e; }
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
            max-width: 700px;
            max-height: 90vh;
            overflow-y: auto;
        }
        .modal-header {
            background: linear-gradient(135deg, #7c3aed, #a855f7);
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
        .form-group select {
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
        .dispense-card {
            background: #f8fafc;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .dispense-card h4 {
            color: #1e293b;
            margin-bottom: 15px;
        }
        .medicine-row {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr auto;
            gap: 10px;
            margin-bottom: 10px;
            align-items: center;
        }
        .interaction-warning {
            background: #fee2e2;
            border: 1px solid #ef4444;
            border-radius: 8px;
            padding: 12px;
            margin: 10px 0;
            color: #991b1b;
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
            <a href="/pharmacy" style="color: white; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; background: #7c3aed;">💊 Pharmacy</a>
            <a href="/billing" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">💰 Billing</a>
            <a href="/emergency" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🚨 ER</a>
            <a href="/patient" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🧑‍⚕️ Patient</a>
            <a href="/" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🚪 Exit</a>
        </div>
    </nav>
    <header class="header">
        <h1>💊 Pharmacy Management</h1>
        <div>
            <div style="font-weight: 600;">Pharmacist</div>
            <div style="font-size: 0.85rem; opacity: 0.9;">Inventory & Dispensing</div>
        </div>
    </header>

    <div class="nav-tabs">
        <div class="nav-tab active" onclick="showTab('inventory')">📦 Inventory</div>
        <div class="nav-tab" onclick="showTab('dispense')">💉 Dispense</div>
        <div class="nav-tab" onclick="showTab('prescriptions')">📋 Prescriptions</div>
        <div class="nav-tab" onclick="showTab('alerts')">⚠️ Alerts</div>
    </div>

    <div class="main-container">
        <!-- Alert Banners -->
        <div id="low-stock-alert" class="alert-banner" style="display: none;">
            <span>⚠️</span>
            <span><strong>Low Stock Warning:</strong> 5 medicines below reorder level</span>
        </div>

        <div id="expiry-alert" class="alert-banner critical" style="display: none;">
            <span>🚨</span>
            <span><strong>Expiry Alert:</strong> 3 medicines expiring within 30 days</span>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Medicines</h3>
                <div class="number" id="total-medicines">0</div>
            </div>
            <div class="stat-card">
                <h3>Low Stock</h3>
                <div class="number" id="low-stock-count" style="color: #dc2626;">0</div>
            </div>
            <div class="stat-card">
                <h3>Today's Sales</h3>
                <div class="number" id="today-sales">₹0</div>
            </div>
            <div class="stat-card">
                <h3>Pending Rx</h3>
                <div class="number" id="pending-rx">0</div>
            </div>
        </div>

        <!-- Inventory Tab -->
        <div id="inventory-tab" class="tab-content active">
            <div class="card">
                <div class="card-header">
                    <h2>Medicine Inventory</h2>
                    <div style="display: flex; gap: 10px;">
                        <button class="btn btn-primary" onclick="openAddMedicineModal()">+ Add Medicine</button>
                        <button class="btn" style="background: #e0e7ff; color: #4338ca;" onclick="openAddStockModal()">+ Add Stock</button>
                    </div>
                </div>
                <div style="padding: 24px;">
                    <div class="search-bar">
                        <input type="text" id="medicine-search" placeholder="Search medicine by name..." onkeyup="searchMedicines()">
                        <select id="category-filter" onchange="filterByCategory()">
                            <option value="">All Categories</option>
                            <option value="Antibiotic">Antibiotic</option>
                            <option value="Analgesic">Analgesic</option>
                            <option value="Cardiac">Cardiac</option>
                            <option value="Antidiabetic">Antidiabetic</option>
                        </select>
                    </div>
                    <div class="table-container">
                        <table id="medicine-table">
                            <thead>
                                <tr>
                                    <th>Medicine</th>
                                    <th>Category</th>
                                    <th>Stock</th>
                                    <th>Reorder Level</th>
                                    <th>MRP</th>
                                    <th>Expiry</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="medicine-tbody">
                                <tr>
                                    <td colspan="8" style="text-align: center; color: #64748b;">Loading medicines...</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- Dispense Tab -->
        <div id="dispense-tab" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <h2>Dispense Medicines</h2>
                </div>
                <div style="padding: 24px;">
                    <div class="dispense-card">
                        <h4>Search Prescription</h4>
                        <div class="form-row">
                            <div class="form-group" style="flex: 2;">
                                <label>Prescription Number or Patient ID</label>
                                <input type="text" id="rx-search" placeholder="Enter RX-2026-XXXXXX">
                            </div>
                            <div style="display: flex; align-items: end;">
                                <button class="btn btn-primary" onclick="searchPrescription()">Search</button>
                            </div>
                        </div>
                    </div>

                    <div id="prescription-details" style="display: none;">
                        <div class="dispense-card">
                            <h4>Prescription Details</h4>
                            <p><strong>Patient:</strong> <span id="dispense-patient-name"></span></p>
                            <p><strong>Doctor:</strong> <span id="dispense-doctor-name"></span></p>
                            <p><strong>Date:</strong> <span id="dispense-date"></span></p>
                        </div>

                        <div id="interaction-warnings"></div>

                        <h4 style="margin: 20px 0 15px;">Medicines to Dispense</h4>
                        <div id="medicines-to-dispense"></div>

                        <div style="background: #f0fdf4; padding: 20px; border-radius: 12px; margin-top: 20px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="color: #64748b; font-size: 0.9rem;">Total Amount</div>
                                    <div style="font-size: 1.8rem; font-weight: 700; color: #059669;">₹<span id="dispense-total">0</span></div>
                                </div>
                                <button class="btn btn-primary" style="padding: 15px 40px; font-size: 1.1rem;" onclick="confirmDispense()">
                                    ✅ Confirm Dispense
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Prescriptions Tab -->
        <div id="prescriptions-tab" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <h2>Pending Prescriptions</h2>
                </div>
                <div style="padding: 24px;">
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Rx Number</th>
                                    <th>Patient</th>
                                    <th>Doctor</th>
                                    <th>Date</th>
                                    <th>Medicines</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="prescriptions-tbody">
                                <tr>
                                    <td colspan="7" style="text-align: center; padding: 40px; color: #64748b;">
                                        <div style="font-size: 3rem; margin-bottom: 10px;">📋</div>
                                        <p>No pending prescriptions</p>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- Alerts Tab -->
        <div id="alerts-tab" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <h2>Stock Alerts</h2>
                </div>
                <div style="padding: 24px;">
                    <h4 style="margin-bottom: 15px; color: #dc2626;">🔴 Low Stock Medicines</h4>
                    <div id="low-stock-list"></div>

                    <h4 style="margin: 30px 0 15px; color: #f59e0b;">🟡 Expiring Soon (30 days)</h4>
                    <div id="expiring-list"></div>
                </div>
            </div>
        </div>
    </div>

    <!-- Add Medicine Modal -->
    <div id="add-medicine-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>+ Add New Medicine</h2>
            </div>
            <div class="modal-body">
                <div class="form-row">
                    <div class="form-group">
                        <label>Medicine Name *</label>
                        <input type="text" id="med-name" placeholder="e.g., Paracetamol">
                    </div>
                    <div class="form-group">
                        <label>Generic Name</label>
                        <input type="text" id="med-generic" placeholder="e.g., Acetaminophen">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Category *</label>
                        <select id="med-category">
                            <option value="">Select Category</option>
                            <option value="Antibiotic">Antibiotic</option>
                            <option value="Analgesic">Analgesic</option>
                            <option value="Antipyretic">Antipyretic</option>
                            <option value="Cardiac">Cardiac</option>
                            <option value="Antidiabetic">Antidiabetic</option>
                            <option value="Vitamin">Vitamin</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Form *</label>
                        <select id="med-form">
                            <option value="Tablet">Tablet</option>
                            <option value="Capsule">Capsule</option>
                            <option value="Syrup">Syrup</option>
                            <option value="Injection">Injection</option>
                            <option value="Cream">Cream</option>
                        </select>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Strength</label>
                        <input type="text" id="med-strength" placeholder="e.g., 500mg">
                    </div>
                    <div class="form-group">
                        <label>Manufacturer</label>
                        <input type="text" id="med-manufacturer" placeholder="e.g., Cipla">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>MRP (₹) *</label>
                        <input type="number" id="med-mrp" placeholder="0.00">
                    </div>
                    <div class="form-group">
                        <label>Sale Price (₹) *</label>
                        <input type="number" id="med-sale-price" placeholder="0.00">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Initial Stock</label>
                        <input type="number" id="med-stock" value="0">
                    </div>
                    <div class="form-group">
                        <label>Reorder Level</label>
                        <input type="number" id="med-reorder" value="10">
                    </div>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 24px;">
                    <button class="btn btn-primary" onclick="addMedicine()" style="flex: 1;">Add Medicine</button>
                    <button class="btn" onclick="closeModal('add-medicine-modal')" style="background: #e5e7eb; color: #374151;">Cancel</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let medicines = [];
        let currentRx = null;

        document.addEventListener('DOMContentLoaded', function() {
            loadMedicines();
            loadStats();
            loadAlerts();
            loadPrescriptions();
        });

        function showTab(tab) {
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tab + '-tab').classList.add('active');
        }

        async function loadMedicines() {
            try {
                const response = await fetch('/api/v1/pharmacy/medicines');
                const data = await response.json();
                medicines = data.medicines || [];
                renderMedicines();
            } catch (error) {
                console.error('Error loading medicines:', error);
                // Show sample data
                showSampleMedicines();
            }
        }

        function showSampleMedicines() {
            medicines = [
                { id: 1, name: 'Paracetamol', generic: 'Acetaminophen', category: 'Analgesic', form: 'Tablet', strength: '500mg', stock_quantity: 150, reorder_level: 20, mrp: 15, sale_price: 12, expiry: '2025-12-31' },
                { id: 2, name: 'Amoxicillin', generic: 'Amoxicillin', category: 'Antibiotic', form: 'Capsule', strength: '500mg', stock_quantity: 8, reorder_level: 15, mrp: 45, sale_price: 38, expiry: '2025-06-30' },
                { id: 3, name: 'Metformin', generic: 'Metformin HCl', category: 'Antidiabetic', form: 'Tablet', strength: '500mg', stock_quantity: 200, reorder_level: 25, mrp: 25, sale_price: 20, expiry: '2026-01-31' },
            ];
            renderMedicines();
        }

        function renderMedicines() {
            const tbody = document.getElementById('medicine-tbody');
            tbody.innerHTML = medicines.map(med => {
                const stockStatus = med.stock_quantity <= med.reorder_level ? 'stock-low' : 'stock-ok';
                const status = med.stock_quantity <= med.reorder_level ? 'Low Stock' : 'In Stock';
                const statusClass = med.stock_quantity <= med.reorder_level ? 'stock-low' : 'stock-ok';

                return `
                    <tr>
                        <td>
                            <strong>${med.name}</strong>
                            <div style="font-size: 0.8rem; color: #64748b;">${med.generic || '-'}</div>
                        </td>
                        <td><span class="badge badge-${med.category.toLowerCase()}">${med.category}</span></td>
                        <td class="${stockStatus}">${med.stock_quantity}</td>
                        <td>${med.reorder_level}</td>
                        <td>₹${med.sale_price}</td>
                        <td>${med.expiry || '-'}</td>
                        <td class="${statusClass}">${status}</td>
                        <td>
                            <button class="btn" style="background: #dbeafe; color: #1e40af; padding: 6px 12px; font-size: 0.85rem;" onclick="addStock(${med.id})">+ Stock</button>
                        </td>
                    </tr>
                `;
            }).join('');
        }

        async function loadStats() {
            try {
                const response = await fetch('/api/v1/pharmacy/low-stock');
                const data = await response.json();
                const lowStock = data.low_stock || [];

                document.getElementById('total-medicines').textContent = medicines.length;
                document.getElementById('low-stock-count').textContent = lowStock.length;

                if (lowStock.length > 0) {
                    document.getElementById('low-stock-alert').style.display = 'flex';
                }
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        function openAddMedicineModal() {
            document.getElementById('add-medicine-modal').classList.add('active');
        }

        function closeModal(id) {
            document.getElementById(id).classList.remove('active');
        }

        async function addMedicine() {
            const data = {
                name: document.getElementById('med-name').value,
                generic_name: document.getElementById('med-generic').value,
                category: document.getElementById('med-category').value,
                form: document.getElementById('med-form').value,
                strength: document.getElementById('med-strength').value,
                manufacturer: document.getElementById('med-manufacturer').value,
                mrp: parseFloat(document.getElementById('med-mrp').value),
                sale_price: parseFloat(document.getElementById('med-sale-price').value),
                stock_quantity: parseInt(document.getElementById('med-stock').value),
                reorder_level: parseInt(document.getElementById('med-reorder').value)
            };

            if (!data.name || !data.category) {
                alert('Please fill required fields');
                return;
            }

            try {
                const response = await fetch('/api/v1/pharmacy/medicine', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                if (result.success) {
                    alert('Medicine added successfully!');
                    closeModal('add-medicine-modal');
                    loadMedicines();
                }
            } catch (error) {
                console.error('Error adding medicine:', error);
                // Add to local list for demo
                medicines.push({ ...data, id: medicines.length + 1 });
                renderMedicines();
                closeModal('add-medicine-modal');
            }
        }

        function searchMedicines() {
            const query = document.getElementById('medicine-search').value.toLowerCase();
            const rows = document.querySelectorAll('#medicine-tbody tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        }

        function filterByCategory() {
            const category = document.getElementById('category-filter').value;
            const rows = document.querySelectorAll('#medicine-tbody tr');

            rows.forEach(row => {
                if (!category) {
                    row.style.display = '';
                } else {
                    const hasCategory = row.textContent.includes(category);
                    row.style.display = hasCategory ? '' : 'none';
                }
            });
        }

        async function searchPrescription() {
            const rxNumber = document.getElementById('rx-search').value;
            if (!rxNumber) return;

            // Simulate fetching prescription
            currentRx = {
                number: rxNumber,
                patient: 'Test Patient',
                patient_id: 'PAT-2026-000123',
                doctor: 'Dr. Sarah Smith',
                date: new Date().toLocaleDateString(),
                medicines: [
                    { name: 'Paracetamol', dosage: '500mg', frequency: '1-1-1', duration: '5 days', quantity: 15, available: true },
                    { name: 'Amoxicillin', dosage: '500mg', frequency: '1-0-1', duration: '7 days', quantity: 14, available: false, reason: 'Low stock' }
                ]
            };

            document.getElementById('prescription-details').style.display = 'block';
            document.getElementById('dispense-patient-name').textContent = currentRx.patient + ' (' + currentRx.patient_id + ')';
            document.getElementById('dispense-doctor-name').textContent = currentRx.doctor;
            document.getElementById('dispense-date').textContent = currentRx.date;

            renderMedicinesToDispense();
        }

        function renderMedicinesToDispense() {
            const container = document.getElementById('medicines-to-dispense');
            let total = 0;

            container.innerHTML = currentRx.medicines.map((med, index) => {
                const price = 12; // Example price
                const subtotal = med.quantity * price;
                total += subtotal;

                return `
                    <div class="medicine-row">
                        <div>
                            <strong>${med.name}</strong>
                            <div style="font-size: 0.8rem; color: #64748b;">${med.dosage} | ${med.frequency} | ${med.duration}</div>
                        </div>
                        <div>Qty: ${med.quantity}</div>
                        <div>₹${price}/unit</div>
                        <div>₹${subtotal}</div>
                        <div>
                            ${med.available
                                ? '<span style="color: #059669;">✓ Available</span>'
                                : '<span style="color: #dc2626;">✗ ' + med.reason + '</span>'
                            }
                        </div>
                    </div>
                `;
            }).join('');

            document.getElementById('dispense-total').textContent = total;
        }

        async function confirmDispense() {
            try {
                const response = await fetch('/api/v1/pharmacy/prescription/1/dispense', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ pharmacist_id: 1 })
                });

                const result = await response.json();
                if (result.success) {
                    alert('Medicines dispensed successfully! Receipt: ' + result.dispense_number);
                    document.getElementById('prescription-details').style.display = 'none';
                    loadMedicines();
                }
            } catch (error) {
                alert('Dispensed successfully! (Demo mode)');
                document.getElementById('prescription-details').style.display = 'none';
            }
        }

        async function loadAlerts() {
            // Would fetch from API
            const lowStockList = document.getElementById('low-stock-list');
            const expiringList = document.getElementById('expiring-list');

            lowStockList.innerHTML = `
                <div style="background: #fee2e2; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                    <div style="font-weight: 600; color: #991b1b;">Amoxicillin 500mg</div>
                    <div style="font-size: 0.9rem; color: #b91c1c;">Current: 8 | Reorder Level: 15</div>
                </div>
            `;

            expiringList.innerHTML = `
                <div style="background: #fef3c7; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                    <div style="font-weight: 600; color: #92400e;">Amoxicillin 500mg</div>
                    <div style="font-size: 0.9rem; color: #a16207;">Expiry: 2025-06-30 (25 days)</div>
                </div>
            `;
        }

        function loadPrescriptions() {
            // Would fetch pending prescriptions
        }
    </script>
</body>
</html>
"""
