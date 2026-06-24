import os
import re
import urllib3
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import vertexai
from google.adk.sessions.vertex_ai_session_service import VertexAiSessionService
from vertexai.preview.reasoning_engines import ReasoningEngine
from google.cloud.aiplatform_v1beta1.types import reasoning_engine_execution_service as aip_types
from vertexai.reasoning_engines import _utils

# Disable urllib3 warnings for SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Auto-configure SSL variables if not present and we detect the workspace path
cert_path = r"C:\Users\steve\OneDrive\Desktop\Data projects\Kaggle AI Agents\Day05\ADK-Agents\ambient-expense-agent\system_certs.pem"
if os.path.exists(cert_path):
    if "SSL_CERT_FILE" not in os.environ:
        os.environ["SSL_CERT_FILE"] = cert_path
    if "REQUESTS_CA_BUNDLE" not in os.environ:
        os.environ["REQUESTS_CA_BUNDLE"] = cert_path
    if "GRPC_DEFAULT_SSL_ROOTS_FILE_PATH" not in os.environ:
        os.environ["GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"] = cert_path

# Auto-configure credentials if not present
creds_path = r"C:\Users\steve\AppData\Roaming\gcloud\legacy_credentials\steventapscott2@gmail.com\adc.json"
if os.path.exists(creds_path) and "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path

# Read environment variables
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT") or "project-2c6026af-6a18-4d62-a5c"
agent_runtime_id = os.environ.get("AGENT_RUNTIME_ID") or "projects/151543826805/locations/us-east1/reasoningEngines/2663773626473381888"
location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-east1")

# Initialize vertexai
vertexai.init(project=project_id, location=location)

def get_numeric_engine_id(engine_id: str) -> str:
    if engine_id.isdigit():
        return engine_id
    pattern = r'^projects/([a-zA-Z0-9-_]+)/locations/([a-zA-Z0-9-_]+)/reasoningEngines/(\d+)$'
    match = re.fullmatch(pattern, engine_id)
    if match:
        return match.group(3)
    return engine_id

session_service = VertexAiSessionService(
    project=project_id,
    location=location,
    agent_engine_id=get_numeric_engine_id(agent_runtime_id)
)

app = FastAPI(title="Manager Dashboard Service")

# Served HTML Content
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ambient Expense Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --success: #10b981;
            --success-glow: rgba(16, 185, 129, 0.15);
            --danger: #f43f5e;
            --danger-glow: rgba(244, 63, 94, 0.15);
            --bg: #0b0f19;
            --card-bg: rgba(255, 255, 255, 0.03);
            --card-border: rgba(255, 255, 255, 0.08);
            --card-hover: rgba(255, 255, 255, 0.06);
            --text: #f3f4f6;
            --text-secondary: #9ca3af;
        }

        body {
            background-color: var(--bg);
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(236, 72, 153, 0.15) 0%, transparent 40%);
            background-attachment: fixed;
            font-family: 'Outfit', sans-serif;
            color: var(--text);
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        header {
            width: 100%;
            max-width: 1200px;
            padding: 30px 20px;
            box-sizing: border-box;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo-section h1 {
            margin: 0;
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(to right, #818cf8, #f472b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        }

        .logo-section p {
            margin: 5px 0 0 0;
            font-size: 0.9rem;
            color: var(--text-secondary);
        }

        .actions-header {
            display: flex;
            gap: 12px;
        }

        .btn {
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            padding: 10px 20px;
            border-radius: 12px;
            border: none;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            font-size: 0.9rem;
        }

        .btn-primary {
            background: var(--primary);
            color: white;
            box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
        }

        .btn-primary:hover {
            background: var(--primary-hover);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: var(--text);
        }

        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(-2px);
        }

        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none !important;
            box-shadow: none !important;
        }

        main {
            width: 100%;
            max-width: 1200px;
            padding: 0 20px 60px 20px;
            box-sizing: border-box;
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 24px;
            margin-top: 30px;
        }

        /* Glassmorphic Card */
        .card {
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 24px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 250px;
        }

        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(to right, #6366f1, #a855f7);
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .card:hover {
            background: var(--card-hover);
            transform: translateY(-5px);
            border-color: rgba(99, 102, 241, 0.25);
            box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.15);
        }

        .card:hover::before {
            opacity: 1;
        }

        .card-header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 20px;
        }

        .avatar {
            width: 44px;
            height: 44px;
            border-radius: 12px;
            background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.1rem;
            color: #ffffff;
            box-shadow: 0 4px 10px rgba(99, 102, 241, 0.2);
        }

        .submitter-info h3 {
            margin: 0;
            font-size: 1.1rem;
            font-weight: 600;
        }

        .submitter-info p {
            margin: 2px 0 0 0;
            font-size: 0.8rem;
            color: var(--text-secondary);
        }

        .card-body {
            flex-grow: 1;
            margin-bottom: 24px;
        }

        .amount {
            font-size: 2rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 12px;
            display: flex;
            align-items: baseline;
        }

        .amount::before {
            content: '$';
            font-size: 1.2rem;
            font-weight: 500;
            margin-right: 2px;
            color: var(--text-secondary);
        }

        .description {
            font-size: 0.95rem;
            line-height: 1.5;
            color: var(--text-secondary);
            margin: 0 0 16px 0;
        }

        .metadata-tags {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        .tag {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 0.75rem;
            color: var(--text-secondary);
            font-weight: 500;
        }

        .card-actions {
            display: flex;
            gap: 12px;
            margin-top: auto;
        }

        .card-actions .btn {
            flex: 1;
        }

        .btn-approve {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.2);
            color: #34d399;
        }

        .btn-approve:hover:not(:disabled) {
            background: var(--success);
            color: white;
            box-shadow: 0 4px 15px var(--success-glow);
            transform: translateY(-2px);
        }

        .btn-reject {
            background: rgba(244, 63, 94, 0.1);
            border: 1px solid rgba(244, 63, 94, 0.2);
            color: #fb7185;
        }

        .btn-reject:hover:not(:disabled) {
            background: var(--danger);
            color: white;
            box-shadow: 0 4px 15px var(--danger-glow);
            transform: translateY(-2px);
        }

        /* Empty State */
        .empty-state {
            grid-column: 1 / -1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 80px 40px;
            text-align: center;
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            min-height: 300px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
        }

        .empty-state svg {
            width: 80px;
            height: 80px;
            color: var(--primary);
            opacity: 0.6;
            margin-bottom: 20px;
            animation: float 4s ease-in-out infinite;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        .empty-state h2 {
            margin: 0;
            font-size: 1.5rem;
            font-weight: 600;
        }

        .empty-state p {
            margin: 8px 0 24px 0;
            color: var(--text-secondary);
            font-size: 0.95rem;
            max-width: 400px;
            line-height: 1.5;
        }

        /* Slide Out Modal Panel */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(5px);
            -webkit-backdrop-filter: blur(5px);
            z-index: 100;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.4s ease;
        }

        .modal-overlay.active {
            opacity: 1;
            pointer-events: auto;
        }

        .modal-panel {
            position: fixed;
            top: 0;
            right: -460px;
            width: 440px;
            height: 100%;
            background: rgba(11, 15, 25, 0.95);
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            border-left: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: -10px 0 40px rgba(0, 0, 0, 0.6);
            z-index: 101;
            padding: 40px 30px;
            box-sizing: border-box;
            transition: right 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            display: flex;
            flex-direction: column;
        }

        .modal-panel.active {
            right: 0;
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }

        .modal-header h2 {
            margin: 0;
            font-size: 1.4rem;
            font-weight: 700;
            background: linear-gradient(to right, #818cf8, #f472b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .close-btn {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.05);
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            color: var(--text);
            transition: all 0.3s ease;
        }

        .close-btn:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: scale(1.1);
        }

        .modal-body {
            flex-grow: 1;
            overflow-y: auto;
            margin-bottom: 30px;
            line-height: 1.6;
        }

        .review-box {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 24px;
        }

        .review-status {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 16px;
        }

        .review-status.approved {
            background: rgba(16, 185, 129, 0.1);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.15);
        }

        .review-status.rejected {
            background: rgba(244, 63, 94, 0.1);
            color: #fb7185;
            border: 1px solid rgba(244, 63, 94, 0.15);
        }

        .review-text {
            color: var(--text-secondary);
            font-size: 0.95rem;
            white-space: pre-wrap;
        }

        /* Loading Spinner */
        .spinner {
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-top: 2px solid currentColor;
            border-radius: 50%;
            width: 16px;
            height: 16px;
            animation: spin 0.8s linear infinite;
            display: inline-block;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .btn-loading-text {
            display: none;
        }

        .loading .btn-normal-text {
            display: none;
        }

        .loading .btn-loading-text {
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        /* Toast Notifications */
        #toast-container {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 200;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .toast {
            background: rgba(17, 24, 39, 0.9);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 12px 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            color: white;
            font-weight: 500;
            font-size: 0.9rem;
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }

        .toast.show {
            transform: translateY(0);
            opacity: 1;
        }
    </style>
</head>
<body>

    <header>
        <div class="logo-section">
            <h1>Ambient Expense</h1>
            <p>Real-Time Agentic Compliance & Manager Dashboard</p>
        </div>
        <div class="actions-header">
            <button class="btn btn-secondary" onclick="generateDemoExpense()" id="demo-btn">
                <span class="btn-normal-text">✨ Generate Demo Expense</span>
                <span class="btn-loading-text"><span class="spinner"></span> Generating...</span>
            </button>
            <button class="btn btn-secondary" onclick="loadPendingApprovals()">Refresh</button>
        </div>
    </header>

    <main>
        <div class="dashboard-grid" id="dashboard-grid">
            <!-- Loading Indicator -->
            <div style="grid-column: 1/-1; text-align: center; padding: 40px;" id="grid-loader">
                <span class="spinner" style="width: 32px; height: 32px; border-width: 3px;"></span>
                <p style="margin-top: 12px; color: var(--text-secondary);">Querying Agent Runtime...</p>
            </div>
        </div>
    </main>

    <!-- Side Slide Out Modal -->
    <div class="modal-overlay" id="modal-overlay" onclick="closeModal()"></div>
    <div class="modal-panel" id="modal-panel">
        <div class="modal-header">
            <h2>Compliance Report</h2>
            <div class="close-btn" onclick="closeModal()">✕</div>
        </div>
        <div class="modal-body">
            <div class="review-box">
                <div class="review-status" id="review-status"></div>
                <div class="review-text" id="review-text"></div>
            </div>
        </div>
        <button class="btn btn-primary" onclick="closeModal()" style="width: 100%;">Done</button>
    </div>

    <!-- Toast container -->
    <div id="toast-container"></div>

    <script>
        // Load pending approvals on startup
        document.addEventListener('DOMContentLoaded', () => {
            loadPendingApprovals();
        });

        async function loadPendingApprovals() {
            const grid = document.getElementById('dashboard-grid');
            const loader = document.getElementById('grid-loader');
            
            if (loader) loader.style.display = 'block';
            
            try {
                const response = await fetch('/api/pending');
                const data = await response.json();
                
                // Clear grid except loader
                grid.innerHTML = '';
                
                if (data.length === 0) {
                    grid.innerHTML = `
                        <div class="empty-state">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 0 1-1.043 3.296 3.745 3.745 0 0 1-3.296 1.043A3.745 3.745 0 0 1 12 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 0 1-3.296-1.043 3.745 3.745 0 0 1-1.043-3.296A3.745 3.745 0 0 1 3 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 0 1 1.043-3.296 3.746 3.746 0 0 1 3.296-1.043A3.746 3.746 0 0 1 12 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 0 1 3.296 1.043 3.746 3.746 0 0 1 1.043 3.296A3.745 3.745 0 0 1 21 12Z" />
                            </svg>
                            <h2>All Caught Up!</h2>
                            <p>No expenses are currently pending manager review. Excellent work keeping up with the compliance queue.</p>
                        </div>
                    `;
                    return;
                }
                
                data.forEach(item => {
                    const card = document.createElement('div');
                    card.className = 'card';
                    card.id = `card-${item.session_id}`;
                    
                    const firstLetter = (item.expense.submitter || 'U').charAt(0).toUpperCase();
                    
                    card.innerHTML = `
                        <div>
                            <div class="card-header">
                                <div class="avatar">${firstLetter}</div>
                                <div class="submitter-info">
                                    <h3>${item.expense.submitter}</h3>
                                    <p>Session: ${item.session_id.substring(0, 12)}...</p>
                                </div>
                            </div>
                            <div class="card-body">
                                <div class="amount">${item.expense.amount.toFixed(2)}</div>
                                <p class="description">${item.expense.description}</p>
                                <div class="metadata-tags">
                                    <span class="tag">ID: ${item.interrupt_id}</span>
                                    <span class="tag">Requires Review</span>
                                </div>
                            </div>
                        </div>
                        <div class="card-actions">
                            <button class="btn btn-reject" onclick="handleAction('${item.session_id}', '${item.interrupt_id}', false, this)">
                                <span class="btn-normal-text">Reject</span>
                                <span class="btn-loading-text"><span class="spinner"></span> Rejecting...</span>
                            </button>
                            <button class="btn btn-approve" onclick="handleAction('${item.session_id}', '${item.interrupt_id}', true, this)">
                                <span class="btn-normal-text">Approve</span>
                                <span class="btn-loading-text"><span class="spinner"></span> Approving...</span>
                            </button>
                        </div>
                    `;
                    grid.appendChild(card);
                });
                
            } catch (err) {
                console.error(err);
                grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: var(--danger);">Failed to load pending approvals from backend.</div>';
            }
        }

        async function handleAction(sessionId, interruptId, approved, btn) {
            const card = document.getElementById(`card-${sessionId}`);
            const buttons = card.querySelectorAll('.btn');
            
            // Disable buttons and show loading spinner on clicked button
            buttons.forEach(b => b.disabled = true);
            btn.classList.add('loading');
            
            try {
                const response = await fetch(`/api/action/${sessionId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        approved: approved,
                        interrupt_id: interruptId
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showToast(approved ? 'Expense Approved!' : 'Expense Rejected!');
                    openModal(approved, data.review || 'No review details returned by the agent.');
                    // Refresh approvals list
                    setTimeout(loadPendingApprovals, 1500);
                } else {
                    showToast('Action failed: ' + (data.detail || 'Unknown error'));
                    buttons.forEach(b => b.disabled = false);
                    btn.classList.remove('loading');
                }
            } catch (err) {
                console.error(err);
                showToast('Network error processing request');
                buttons.forEach(b => b.disabled = false);
                btn.classList.remove('loading');
            }
        }

        async function generateDemoExpense() {
            const btn = document.getElementById('demo-btn');
            btn.disabled = true;
            btn.classList.add('loading');
            
            try {
                const response = await fetch('/api/demo', { method: 'POST' });
                if (response.ok) {
                    showToast('Demo expense successfully generated!');
                    setTimeout(() => {
                        btn.disabled = false;
                        btn.classList.remove('loading');
                        loadPendingApprovals();
                    }, 2000);
                } else {
                    showToast('Failed to generate demo expense');
                    btn.disabled = false;
                    btn.classList.remove('loading');
                }
            } catch (err) {
                console.error(err);
                showToast('Error generating demo expense');
                btn.disabled = false;
                btn.classList.remove('loading');
            }
        }

        function openModal(approved, reviewText) {
            const overlay = document.getElementById('modal-overlay');
            const panel = document.getElementById('modal-panel');
            const status = document.getElementById('review-status');
            const text = document.getElementById('review-text');
            
            status.className = `review-status ${approved ? 'approved' : 'rejected'}`;
            status.innerHTML = approved ? '✓ APPROVED BY AGENT' : '✕ REJECTED BY AGENT';
            text.textContent = reviewText;
            
            overlay.classList.add('active');
            panel.classList.add('active');
        }

        function closeModal() {
            const overlay = document.getElementById('modal-overlay');
            const panel = document.getElementById('modal-panel');
            overlay.classList.remove('active');
            panel.classList.remove('active');
        }

        function showToast(message) {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.textContent = message;
            container.appendChild(toast);
            
            // Force reflow
            toast.offsetHeight;
            
            toast.classList.add('show');
            
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => {
                    container.removeChild(toast);
                }, 300);
            }, 3000);
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return HTMLResponse(content=html_content)

@app.get("/api/pending")
async def list_pending():
    try:
        list_resp = await session_service.list_sessions(app_name="app")
        pending = []
        for s in list_resp.sessions:
            full_session = await session_service.get_session(app_name="app", user_id=s.user_id, session_id=s.id)
            if not full_session or not full_session.events:
                continue
            
            # Find unresolved adk_request_input events
            calls = {}
            responses = set()
            for event in full_session.events:
                for call in event.get_function_calls():
                    if call.name == "adk_request_input":
                        calls[call.id] = call
                for resp in event.get_function_responses():
                    if resp.name == "adk_request_input":
                        responses.add(resp.id)
            
            unresolved = set(calls.keys()) - responses
            for call_id in unresolved:
                call = calls[call_id]
                message_text = call.args.get("message", "")
                
                # Parse details from message
                submitter_match = re.search(r"Submitter:\s*([^\n]+)", message_text)
                amount_match = re.search(r"Amount:\s*\$?([0-9.,]+)", message_text)
                desc_match = re.search(r"Description:\s*([^\n]+)", message_text)
                
                submitter = submitter_match.group(1).strip() if submitter_match else "Unknown"
                amount = float(amount_match.group(1).replace(",", "").strip()) if amount_match else 0.0
                description = desc_match.group(1).strip() if desc_match else "No description"
                
                # Try getting from state if available
                expense_state = full_session.state.get("expense")
                if expense_state and isinstance(expense_state, dict):
                    submitter = expense_state.get("submitter", submitter)
                    amount = expense_state.get("amount", amount)
                    description = expense_state.get("description", description)
                
                pending.append({
                    "session_id": s.id,
                    "interrupt_id": call_id,
                    "expense": {
                        "submitter": submitter,
                        "amount": amount,
                        "description": description
                    }
                })
        return pending
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")

@app.post("/api/action/{session_id}")
async def process_action(session_id: str, action_data: dict):
    approved = action_data.get("approved", True)
    interrupt_id = action_data.get("interrupt_id", "approve_decision")
    
    try:
        re_instance = ReasoningEngine(agent_runtime_id)
        
        # Structure payload to satisfy both SDK parameter and agent parsing checks
        decision_str = "approve" if approved else "reject"
        response_dict = {
            "approved": approved,
            "response": decision_str
        }
        
        kwargs = {
            "message": {
                "role": "user",
                "parts": [
                    {
                        "function_response": {
                            "id": interrupt_id,
                            "name": "adk_request_input",
                            "response": response_dict
                        }
                    }
                ]
            },
            "user_id": "default-user",
            "session_id": session_id
        }
        
        request = aip_types.StreamQueryReasoningEngineRequest(
            name=re_instance.resource_name,
            input=kwargs,
            class_method="stream_query",
        )
        
        response_stream = re_instance.execution_api_client.stream_query_reasoning_engine(request=request)
        
        review_text = ""
        for chunk in response_stream:
            for parsed_json in _utils.yield_parsed_json(chunk):
                if parsed_json and isinstance(parsed_json, dict):
                    content = parsed_json.get("content")
                    if content and isinstance(content, dict):
                        parts = content.get("parts", [])
                        for p in parts:
                            if p and isinstance(p, dict) and p.get("text"):
                                review_text += p.get("text") + "\n"
        
        return {
            "status": "success",
            "review": review_text.strip()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/demo")
async def generate_demo():
    try:
        import uuid
        demo_session_id = f"demo-session-{uuid.uuid4().hex[:6]}"
        
        # Create session
        await session_service.create_session(app_name="app", user_id="default-user", session_id=demo_session_id)
        
        re_instance = ReasoningEngine(agent_runtime_id)
        
        # Submit high expense to trigger interrupt
        payload = {
            "amount": 250.00,
            "submitter": "Sarah Jenkins",
            "description": "Annual Software Licenses Renewal"
        }
        
        kwargs = {
            "message": json.dumps(payload),
            "user_id": "default-user",
            "session_id": demo_session_id
        }
        
        request = aip_types.StreamQueryReasoningEngineRequest(
            name=re_instance.resource_name,
            input=kwargs,
            class_method="stream_query",
        )
        
        # Send initial query, which triggers review_agent node and pauses
        response_stream = re_instance.execution_api_client.stream_query_reasoning_engine(request=request)
        
        # Consume the stream to ensure the agent finishes parsing and pauses
        for _ in response_stream:
            pass
            
        return {"status": "success", "session_id": demo_session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
