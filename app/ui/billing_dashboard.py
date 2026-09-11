"""
Billing Dashboard - Invoicing & Payments
"""

BILLING_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Billing & Insurance - MedCare Hospital</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #d97706, #f59e0b);
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
            color: #d97706;
            border-bottom-color: #d97706;
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
            font-size: 2rem;
            font-weight: 700;
            color: #d97706;
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
        }
        .tab-content {
            display: none;
            padding: 24px;
        }
        .tab-content.active {
            display: block;
        }
        .btn {
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            border: none;
        }
        .btn-primary {
            background: linear-gradient(135deg, #d97706, #f59e0b);
            color: white;
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
        .amount {
            font-weight: 600;
            color: #1e293b;
        }
        .status-paid {
            background: #d1fae5;
            color: #065f46;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
        }
        .status-pending {
            background: #fef3c7;
            color: #92400e;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
        }
        .invoice-card {
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
        }
        .invoice-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f3f4f6;
        }
        .invoice-totals {
            background: #f8fafc;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }
        .total-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
        }
        .grand-total {
            font-size: 1.3rem;
            font-weight: 700;
            color: #059669;
            border-top: 2px solid #e2e8f0;
            padding-top: 12px;
            margin-top: 8px;
        }
        .insurance-card {
            background: linear-gradient(135deg, #dbeafe, #ede9fe);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
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
            <a href="/billing" style="color: white; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; background: #d97706;">💰 Billing</a>
            <a href="/emergency" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🚨 ER</a>
            <a href="/patient" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🧑‍⚕️ Patient</a>
            <a href="/" style="color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">🚪 Exit</a>
        </div>
    </nav>
    <header class="header">
        <h1>💰 Billing & Insurance</h1>
        <div>
            <div style="font-weight: 600;">Billing Department</div>
            <div style="font-size: 0.85rem; opacity: 0.9;">Invoices, Payments & Claims</div>
        </div>
    </header>

    <div class="nav-tabs">
        <div class="nav-tab active" onclick="showTab('invoices')">📄 Invoices</div>
        <div class="nav-tab" onclick="showTab('payments')">💳 Payments</div>
        <div class="nav-tab" onclick="showTab('insurance')">🛡️ Insurance Claims</div>
    </div>

    <div class="main-container">
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Today's Collection</h3>
                <div class="number">₹<span id="today-collection">0</span></div>
            </div>
            <div class="stat-card">
                <h3>Pending Bills</h3>
                <div class="number" id="pending-bills">0</div>
            </div>
            <div class="stat-card">
                <h3>Pending Claims</h3>
                <div class="number" id="pending-claims">0</div>
            </div>
            <div class="stat-card">
                <h3>Monthly Revenue</h3>
                <div class="number">₹<span id="monthly-revenue">0</span></div>
            </div>
        </div>

        <!-- Invoices Tab -->
        <div id="invoices-tab" class="tab-content active">
            <div class="card">
                <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
                    <h2>Recent Invoices</h2>
                    <div style="display: flex; gap: 10px;">
                        <input type="text" placeholder="Search patient..." style="padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 6px;">
                        <button class="btn btn-primary">Search</button>
                    </div>
                </div>
                <div style="padding: 24px;">
                    <table>
                        <thead>
                            <tr>
                                <th>Invoice #</th>
                                <th>Patient</th>
                                <th>Type</th>
                                <th>Date</th>
                                <th>Total</th>
                                <th>Paid</th>
                                <th>Balance</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="invoices-tbody">
                            <tr>
                                <td>INV-2026-0001</td>
                                <td>Rahul Sharma</td>
                                <td>OPD</td>
                                <td>2026-01-15</td>
                                <td class="amount">₹850</td>
                                <td>₹850</td>
                                <td>₹0</td>
                                <td><span class="status-paid">Paid</span></td>
                                <td><button class="btn" style="background: #dbeafe; color: #1e40af; padding: 6px 12px; font-size: 0.85rem;">View</button></td>
                            </tr>
                            <tr>
                                <td>INV-2026-0002</td>
                                <td>Priya Patel</td>
                                <td>IPD</td>
                                <td>2026-01-15</td>
                                <td class="amount">₹25,400</td>
                                <td>₹15,000</td>
                                <td>₹10,400</td>
                                <td><span class="status-pending">Partial</span></td>
                                <td><button class="btn btn-primary" style="padding: 6px 12px; font-size: 0.85rem;">Pay</button></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Sample Invoice View -->
            <div class="invoice-card">
                <div class="invoice-header">
                    <div>
                        <h3>MedCare Hospital</h3>
                        <p style="color: #64748b;">123 Health Street, New Delhi</p>
                        <p style="color: #64748b;">GST: 07AABCU9603R1ZX</p>
                    </div>
                    <div style="text-align: right;">
                        <h2 style="color: #1e293b;">INVOICE</h2>
                        <p><strong>INV-2026-0001</strong></p>
                        <p style="color: #64748b;">Date: 15 Jan 2026</p>
                    </div>
                </div>

                <div style="margin-bottom: 20px;">
                    <strong>Bill To:</strong><br>
                    Rahul Sharma<br>
                    Patient ID: PAT-2026-000001<br>
                    Phone: +91 98765 43210
                </div>

                <table style="margin: 20px 0;">
                    <thead>
                        <tr>
                            <th style="text-align: left;">Description</th>
                            <th style="text-align: right;">Qty</th>
                            <th style="text-align: right;">Rate</th>
                            <th style="text-align: right;">Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Consultation - Dr. Sarah Smith</td>
                            <td style="text-align: right;">1</td>
                            <td style="text-align: right;">₹500</td>
                            <td style="text-align: right;">₹500</td>
                        </tr>
                        <tr>
                            <td>Registration Charges</td>
                            <td style="text-align: right;">1</td>
                            <td style="text-align: right;">₹100</td>
                            <td style="text-align: right;">₹100</td>
                        </tr>
                        <tr>
                            <td>Lab Tests - CBC</td>
                            <td style="text-align: right;">1</td>
                            <td style="text-align: right;">₹250</td>
                            <td style="text-align: right;">₹250</td>
                        </tr>
                    </tbody>
                </table>

                <div class="invoice-totals">
                    <div class="total-row">
                        <span>Subtotal</span>
                        <span>₹850</span>
                    </div>
                    <div class="total-row">
                        <span>GST (0% on healthcare)</span>
                        <span>₹0</span>
                    </div>
                    <div class="total-row">
                        <span>Discount</span>
                        <span>-₹0</span>
                    </div>
                    <div class="total-row grand-total">
                        <span>Grand Total</span>
                        <span>₹850</span>
                    </div>
                </div>

                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #e2e8f0; text-align: center; color: #64748b;">
                    <p>Thank you for choosing MedCare Hospital</p>
                    <p style="font-size: 0.85rem;">This is a computer-generated invoice</p>
                </div>
            </div>
        </div>

        <!-- Payments Tab -->
        <div id="payments-tab" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <h2>Record Payment</h2>
                </div>
                <div style="padding: 24px;">
                    <div style="max-width: 600px;">
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; font-weight: 500;">Invoice Number</label>
                            <input type="text" placeholder="INV-2026-XXXX" style="width: 100%; padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px;">
                        </div>
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; font-weight: 500;">Payment Amount (₹)</label>
                            <input type="number" placeholder="0.00" style="width: 100%; padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px;">
                        </div>
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; font-weight: 500;">Payment Method</label>
                            <select style="width: 100%; padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px;">
                                <option>Cash</option>
                                <option>Card</option>
                                <option>UPI</option>
                                <option>Insurance</option>
                            </select>
                        </div>
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; font-weight: 500;">Reference Number</label>
                            <input type="text" placeholder="Transaction ID / Cheque Number" style="width: 100%; padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px;">
                        </div>
                        <button class="btn btn-primary" style="width: 100%; padding: 15px;">Record Payment</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Insurance Tab -->
        <div id="insurance-tab" class="tab-content">
            <div class="card">
                <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
                    <h2>Insurance Claims</h2>
                    <button class="btn btn-primary">+ New Claim</button>
                </div>
                <div style="padding: 24px;">
                    <div class="insurance-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h4>Claim #CLM-2026-0001</h4>
                                <p style="color: #64748b; margin-top: 5px;">Patient: Rahul Sharma | Admission: IP-2026-0001</p>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.3rem; font-weight: 600; color: #1e293b;">₹45,000</div>
                                <div style="font-size: 0.85rem; color: #64748b;">Claimed Amount</div>
                            </div>
                        </div>
                        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #c7d2fe;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <span style="background: #dbeafe; color: #1e40af; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">Under Review</span>
                                    <span style="margin-left: 10px; color: #64748b; font-size: 0.9rem;">Star Health Insurance</span>
                                </div>
                                <button class="btn" style="background: white; color: #4338ca;">View Details</button>
                            </div>
                        </div>
                    </div>

                    <h4 style="margin: 30px 0 20px;">Claim Status Summary</h4>
                    <table>
                        <thead>
                            <tr>
                                <th>Status</th>
                                <th>Count</th>
                                <th>Total Amount</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Submitted</td>
                                <td>5</td>
                                <td class="amount">₹2,25,000</td>
                            </tr>
                            <tr>
                                <td>Under Review</td>
                                <td>3</td>
                                <td class="amount">₹1,50,000</td>
                            </tr>
                            <tr>
                                <td>Approved</td>
                                <td>8</td>
                                <td class="amount">₹3,20,000</td>
                            </tr>
                            <tr>
                                <td>Settled</td>
                                <td>12</td>
                                <td class="amount">₹4,80,000</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
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

        // Load stats
        document.getElementById('today-collection').textContent = '45,600';
        document.getElementById('pending-bills').textContent = '12';
        document.getElementById('pending-claims').textContent = '8';
        document.getElementById('monthly-revenue').textContent = '8,45,000';
    </script>
</body>
</html>
"""
