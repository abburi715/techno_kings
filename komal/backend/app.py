from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)

# Data file path
DATA_FILE = 'breath_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {'timings': [], 'sessions': [], 'profile': {}}

def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving data: {e}")

# Load initial data
storage = load_data()

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Breath Timing Stopwatch</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    :root {
      --primary-blue: #1e40af;
      --light-blue: #3b82f6;
      --sky-blue: #0ea5e9;
      --navy-blue: #1e3a8a;
      --pure-white: #ffffff;
      --off-white: #f8fafc;
      --light-grey: #f1f5f9;
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #9333ea;
      --text-dark: #1e293b;
      --text-muted: #64748b;
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }

    html, body { width: 100%; height: 100%; }

    body {
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      font-weight: 500;
      background: linear-gradient(135deg, var(--primary-blue) 0%, var(--sky-blue) 50%, var(--light-blue) 100%);
      background-attachment: fixed;
      color: var(--text-dark);
      overflow-x: hidden;
      position: relative;
    }

    body::before {
      content: '';
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: 
        radial-gradient(circle at 20% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(59, 130, 246, 0.2) 0%, transparent 50%),
        radial-gradient(circle at 40% 40%, rgba(30, 64, 175, 0.3) 0%, transparent 50%);
      pointer-events: none;
      z-index: -1;
    }

    header {
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(20px);
      border-bottom: 1px solid rgba(59, 130, 246, 0.2);
      padding: 1rem 2rem;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: 0 8px 32px rgba(30, 64, 175, 0.1);
    }

    .header-content {
      max-width: 1200px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
    }

    .logo {
      font-size: 1.5rem;
      font-weight: 800;
      background: linear-gradient(135deg, var(--primary-blue), var(--sky-blue));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      letter-spacing: 0.1em;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      text-shadow: 0 0 30px rgba(59, 130, 246, 0.3);
    }

    .nav-menu {
      display: flex;
      gap: 0.4rem;
      flex-wrap: wrap;
      justify-content: flex-end;
    }

    .nav-btn {
      padding: 0.6rem 1.2rem;
      background: rgba(59, 130, 246, 0.1);
      border: 1px solid rgba(59, 130, 246, 0.2);
      color: var(--primary-blue);
      border-radius: 50px;
      cursor: pointer;
      font-size: 0.9rem;
      font-weight: 600;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      white-space: nowrap;
      backdrop-filter: blur(10px);
    }

    .nav-btn:hover {
      background: rgba(59, 130, 246, 0.2);
      border-color: rgba(59, 130, 246, 0.5);
      transform: translateY(-2px);
      box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
    }

    .nav-btn.active {
      background: linear-gradient(135deg, var(--primary-blue), var(--light-blue));
      border-color: transparent;
      color: white;
      font-weight: 700;
      box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
    }

    .container {
      max-width: 1200px;
      margin: 1.6rem auto 2rem;
      padding: 0 1.2rem;
    }

    .content-section { display: none; }
    .content-section.active { display: block; animation: fadeIn 0.25s ease; }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .stopwatch-card {
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(20px);
      border-radius: 24px;
      border: 1px solid rgba(59, 130, 246, 0.2);
      padding: 3rem 2.5rem;
      text-align: center;
      margin-bottom: 2rem;
      box-shadow: 0 25px 50px rgba(30, 64, 175, 0.15);
      position: relative;
      overflow: hidden;
    }

    .stopwatch-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 1px;
      background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.4), transparent);
    }

    .stopwatch-card h2 {
      color: var(--primary-blue);
      font-size: 1.2rem;
      font-weight: 700;
    }

    .stopwatch-display {
      font-size: 4rem;
      font-weight: 800;
      background: linear-gradient(135deg, var(--primary-blue), var(--light-blue), var(--sky-blue));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      font-family: 'JetBrains Mono', monospace;
      letter-spacing: 0.2em;
      margin: 2rem 0;
      text-shadow: 0 0 50px rgba(59, 130, 246, 0.4);
      min-height: 80px;
      animation: glow 2s ease-in-out infinite alternate;
    }

    @keyframes glow {
      from { filter: drop-shadow(0 0 20px rgba(59, 130, 246, 0.4)); }
      to { filter: drop-shadow(0 0 30px rgba(14, 165, 233, 0.6)); }
    }

    .stopwatch-controls {
      display: flex;
      gap: 0.7rem;
      justify-content: center;
      margin: 1.4rem 0 0.6rem;
      flex-wrap: wrap;
    }

    .btn {
      padding: 0.8rem 2rem;
      border: none;
      border-radius: 50px;
      font-size: 0.95rem;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      text-transform: uppercase;
      letter-spacing: 0.1em;
      position: relative;
      overflow: hidden;
    }

    .btn::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
      transition: left 0.5s;
    }

    .btn:hover::before {
      left: 100%;
    }

    .btn-start { 
      background: linear-gradient(135deg, var(--success), #059669); 
      color: white;
      box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
    }
    .btn-start:hover { 
      transform: translateY(-3px) scale(1.05); 
      box-shadow: 0 15px 35px rgba(16, 185, 129, 0.6);
    }

    .btn-pause { 
      background: linear-gradient(135deg, var(--warning), #d97706); 
      color: white;
      box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
    }
    .btn-pause:hover { 
      transform: translateY(-3px) scale(1.05); 
      box-shadow: 0 15px 35px rgba(245, 158, 11, 0.6);
    }

    .btn-reset { 
      background: linear-gradient(135deg, #6b7280, #4b5563); 
      color: white;
      box-shadow: 0 4px 15px rgba(107, 114, 128, 0.4);
    }
    .btn-reset:hover { 
      transform: translateY(-3px) scale(1.05); 
      box-shadow: 0 15px 35px rgba(107, 114, 128, 0.6);
    }

    .btn-save { 
      background: linear-gradient(135deg, var(--light-blue), var(--sky-blue)); 
      color: white;
      box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    }
    .btn-save:hover { 
      transform: translateY(-3px) scale(1.05); 
      box-shadow: 0 15px 35px rgba(59, 130, 246, 0.6);
    }

    .btn-process { 
      background: linear-gradient(135deg, var(--primary-blue), var(--navy-blue)); 
      color: white;
      box-shadow: 0 4px 15px rgba(30, 64, 175, 0.4);
    }
    .btn-process:hover { 
      transform: translateY(-3px) scale(1.05); 
      box-shadow: 0 15px 35px rgba(30, 64, 175, 0.6);
    }

    .timing-selection {
      background: rgba(255, 255, 255, 0.95);
      border-radius: 14px;
      border: 1px solid rgba(59, 130, 246, 0.2);
      padding: 1.6rem 1.4rem 1.4rem;
      margin-top: 1.4rem;
      text-align: left;
    }

    .timing-selection h3 {
      color: var(--primary-blue);
      margin-bottom: 1rem;
      font-size: 1.05rem;
      font-weight: 700;
    }

    .timing-options {
      display: flex;
      gap: 0.8rem;
      flex-wrap: wrap;
      margin-bottom: 1rem;
    }

    .timing-option {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      cursor: pointer;
      padding: 0.6rem 0.9rem;
      border-radius: 999px;
      border: 1px solid rgba(59, 130, 246, 0.3);
      background: rgba(248, 250, 252, 0.8);
      transition: all 0.15s ease;
    }

    .timing-option:hover {
      border-color: var(--primary-blue);
      background: rgba(59, 130, 246, 0.1);
    }

    .timing-option input[type="radio"] {
      width: 18px;
      height: 18px;
      cursor: pointer;
      accent-color: var(--primary-blue);
    }

    .timing-option label {
      cursor: pointer;
      font-size: 0.9rem;
      font-weight: 600;
      color: var(--text-dark);
    }

    .selected-timing {
      background: rgba(59, 130, 246, 0.1);
      padding: 0.8rem 1rem;
      border-radius: 10px;
      border-left: 3px solid var(--primary-blue);
      color: var(--text-muted);
      font-size: 0.9rem;
    }

    .summary-bar {
      margin-top: 0.6rem;
      font-size: 0.85rem;
      color: var(--text-muted);
    }

    .data-table {
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(20px);
      border-radius: 20px;
      border: 1px solid rgba(59, 130, 246, 0.2);
      overflow: hidden;
      margin-top: 1rem;
      box-shadow: 0 20px 40px rgba(30, 64, 175, 0.1);
    }

    .data-table h3 {
      color: var(--primary-blue);
      padding: 1rem 1.3rem;
      border-bottom: 1px solid rgba(59, 130, 246, 0.2);
      font-size: 1rem;
      font-weight: 700;
    }

    table { width: 100%; border-collapse: collapse; }

    thead { background: rgba(59, 130, 246, 0.1); }

    th {
      padding: 0.75rem 1rem;
      text-align: left;
      color: var(--text-muted);
      font-size: 0.78rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      border-bottom: 1px solid rgba(59, 130, 246, 0.2);
    }

    td {
      padding: 0.7rem 1rem;
      border-bottom: 1px solid rgba(59, 130, 246, 0.1);
      font-size: 0.86rem;
      font-weight: 500;
      color: var(--text-dark);
      text-align: center;
    }

    tr:nth-child(even) { background: rgba(248, 250, 252, 0.8); }
    tr:nth-child(odd) { background: rgba(255, 255, 255, 0.9); }

    tr.highlight-good { background: rgba(22, 163, 74, 0.18); }
    tr.highlight-borderline { background: rgba(249, 115, 22, 0.18); }
    tr.highlight-bad { background: rgba(220, 38, 38, 0.18); color: #000000; }

    tr:hover { background: rgba(59, 130, 246, 0.2); }

    .delete-btn {
      background: #b91c1c;
      color: #000000;
      border: none;
      padding: 0.35rem 0.7rem;
      border-radius: 999px;
      cursor: pointer;
      font-size: 0.78rem;
      transition: all 0.18s ease;
    }

    .delete-btn:hover {
      background: #dc2626;
      color: #000000;
      transform: translateY(-1px);
    }

    .chip {
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
      padding: 0.18rem 0.55rem;
      border-radius: 999px;
      font-size: 0.72rem;
      border: 1px solid rgba(148, 163, 184, 0.6);
      color: var(--text-secondary);
    }

    .chip-good { border-color: #22c55e; color: #bbf7d0; }
    .chip-borderline { border-color: #f97316; color: #fed7aa; }
    .chip-bad { border-color: #9333ea; color: #000000; }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 1.1rem;
      margin-bottom: 1.4rem;
    }

    .stat-card {
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(20px);
      border-radius: 16px;
      border: 1px solid rgba(59, 130, 246, 0.2);
      padding: 1.5rem;
      position: relative;
      overflow: hidden;
      transition: transform 0.3s ease;
    }

    .stat-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 3px;
      background: linear-gradient(135deg, var(--primary-blue), var(--sky-blue));
    }

    .stat-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 20px 40px rgba(59, 130, 246, 0.2);
    }

    .stat-label {
      font-size: 0.78rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--text-muted);
      margin-bottom: 0.4rem;
    }

    .stat-value {
      font-size: 1.4rem;
      font-weight: 800;
      color: var(--primary-blue);
    }

    .profile-section {
      display: grid;
      grid-template-columns: 1.1fr 1.1fr;
      gap: 1.4rem;
    }

    @media (max-width: 820px) {
      .profile-section { grid-template-columns: 1fr; }
    }

    .profile-card {
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(20px);
      border-radius: 20px;
      border: 1px solid rgba(59, 130, 246, 0.2);
      padding: 2rem;
      box-shadow: 0 20px 40px rgba(30, 64, 175, 0.1);
    }

    .profile-card h3 {
      color: var(--primary-blue);
      margin-bottom: 1rem;
      font-size: 1.05rem;
      font-weight: 700;
    }

    .form-group { margin-bottom: 1rem; }

    .form-group label {
      display: block;
      color: var(--text-muted);
      margin-bottom: 0.25rem;
      font-size: 0.86rem;
      font-weight: 600;
    }

    .form-group input, .form-group select {
      width: 100%;
      padding: 0.8rem 1rem;
      background: rgba(255, 255, 255, 0.8);
      border: 1px solid rgba(59, 130, 246, 0.3);
      color: var(--text-dark);
      border-radius: 12px;
      font-size: 0.95rem;
      font-weight: 500;
      outline: none;
      transition: all 0.3s ease;
      backdrop-filter: blur(10px);
    }

    .form-group input:focus, .form-group select:focus {
      border-color: rgba(59, 130, 246, 0.6);
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
      background: rgba(255, 255, 255, 0.95);
    }

    footer {
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(20px);
      border-top: 1px solid rgba(59, 130, 246, 0.2);
      padding: 2rem 1rem;
      margin-top: 3rem;
      text-align: center;
    }

    .footer-brand {
      font-size: 1rem;
      color: var(--primary-blue);
      font-weight: 800;
      margin-bottom: 0.2rem;
    }

    .footer-text {
      font-size: 0.78rem;
      font-weight: 500;
      color: var(--text-muted);
    }

    @keyframes float {
      0%, 100% { transform: translateY(0px); }
      50% { transform: translateY(-10px); }
    }

    .stopwatch-card {
      animation: float 6s ease-in-out infinite;
    }

    @media (max-width: 720px) {
      .header-content { flex-direction: column; align-items: flex-start; }
      .stopwatch-display { font-size: 2.8rem; }
      .stopwatch-card { padding: 2rem 1.5rem; }
      .btn { padding: 0.7rem 1.5rem; font-size: 0.85rem; }
    }
  </style>
</head>
<body>
<header>
  <div class="header-content">
    <div class="logo">⏱️ BREATH TIMER</div>
    <div class="nav-menu">
      <button class="nav-btn active" onclick="showSection(event,'stopwatch')">Stopwatch</button>
      <button class="nav-btn" onclick="showSection(event,'past-data')">Past Data</button>
      <button class="nav-btn" onclick="showSection(event,'timing-save')">Breath Timing</button>
      <button class="nav-btn" onclick="showSection(event,'profile')">User Profile</button>
      <button class="nav-btn" onclick="showSection(event,'settings')">Settings</button>
    </div>
  </div>
</header>

<div class="container">
  <section id="stopwatch" class="content-section active">
    <div class="stopwatch-card">
      <h2>Breath Timing Stopwatch</h2>
      <div class="stopwatch-display" id="display">00:00.00</div>
      <div class="stopwatch-controls">
        <button class="btn btn-start" onclick="startTimer()">Start</button>
        <button class="btn btn-pause" onclick="pauseTimer()">Pause</button>
        <button class="btn btn-reset" onclick="resetTimer()">Reset</button>
        <button class="btn btn-save" onclick="saveCurrentTiming()">Save Timing</button>
        <button class="btn btn-process" onclick="saveBreathSession()">Save Session</button>
      </div>
      <div class="timing-selection">
        <h3>What are you measuring?</h3>
        <div class="timing-options">
          <div class="timing-option">
            <input type="radio" id="inhale" name="timing" value="Inhalation" onchange="updateTimingType()">
            <label for="inhale">🫁 Inhalation</label>
          </div>
          <div class="timing-option">
            <input type="radio" id="hold" name="timing" value="Breath-Hold" onchange="updateTimingType()">
            <label for="hold">⏸️ Breath-Hold</label>
          </div>
          <div class="timing-option">
            <input type="radio" id="exhale" name="timing" value="Exhalation" onchange="updateTimingType()">
            <label for="exhale">💨 Exhalation</label>
          </div>
        </div>
        <div class="selected-timing" id="selected-timing">Select a timing type to get started.</div>
        <div class="summary-bar" id="summary-bar"></div>
      </div>
    </div>
    <div class="data-table">
      <h3>Raw Saved Timings</h3>
      <table>
        <thead>
        <tr>
          <th>Date & Time</th>
          <th>Type</th>
          <th>Duration (s)</th>
          <th></th>
        </tr>
        </thead>
        <tbody id="past-data-table">
        <tr><td colspan="4">No records yet.</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <section id="past-data" class="content-section">
    <div class="data-table">
      <h3>Past Timing Records</h3>
      <table>
        <thead>
        <tr>
          <th>Date & Time</th>
          <th>Type</th>
          <th>Duration (s)</th>
          <th></th>
        </tr>
        </thead>
        <tbody id="past-data-table-2">
        <tr><td colspan="4">No records yet.</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <section id="timing-save" class="content-section">
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Total Timings</div>
        <div class="stat-value" id="total-sessions">0</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Avg Inhalation</div>
        <div class="stat-value" id="avg-inhale">0.0s</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Avg Breath-Hold</div>
        <div class="stat-value" id="avg-hold">0.0s</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Avg Exhalation</div>
        <div class="stat-value" id="avg-exhale">0.0s</div>
      </div>
    </div>
    <div class="data-table">
      <h3>
        Breath Sessions
        <button class="btn btn-process" style="float:right;margin-right:1rem;margin-top:-0.3rem;" onclick="processSessions()">Process Data</button>
      </h3>
      <table>
        <thead>
        <tr>
          <th>Session #</th>
          <th>Inhalation (s)</th>
          <th>Breath-Hold (s)</th>
          <th>Exhalation (s)</th>
          <th>Ratio h:e</th>
          <th>Deviation from 1:4:2</th>
          <th>Category</th>
          <th>Date</th>
        </tr>
        </thead>
        <tbody id="timing-save-table">
        <tr><td colspan="8">No complete sessions saved yet.</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <section id="profile" class="content-section">
    <div class="profile-card" style="max-width:600px;margin:0 auto;">
      <h3>Create User Profile</h3>
      <h4 style="color:var(--text-muted);font-size:0.9rem;margin-bottom:1.5rem;">Personal Information</h4>
      <div class="form-group">
        <label>Full Name</label>
        <input type="text" id="fullName" placeholder="Enter your name">
      </div>
      <div class="form-group">
        <label>Age (Years)</label>
        <input type="number" id="age" placeholder="Enter your age">
      </div>
      <div class="form-group">
        <label>Email</label>
        <input type="email" id="email" placeholder="Enter your email">
      </div>
      <div class="form-group">
        <label>Phone Number</label>
        <input type="tel" id="phone" placeholder="Enter your phone number">
      </div>
      <h4 style="color:var(--text-muted);font-size:0.9rem;margin:1.5rem 0 1rem;">Health Information</h4>
      <div class="form-group">
        <label>Height (cm)</label>
        <input type="number" id="height" placeholder="Enter your height">
      </div>
      <div class="form-group">
        <label>Weight (kg)</label>
        <input type="number" id="weight" placeholder="Enter your weight">
      </div>
      <div class="form-group">
        <label>Medical Conditions</label>
        <input type="text" id="medical" placeholder="e.g., Asthma, COPD">
      </div>
      <div class="form-group">
        <label>Notes</label>
        <input type="text" id="notes" placeholder="Additional notes">
      </div>
      <button class="btn btn-save" style="width:100%;margin-top:1.5rem;" onclick="submitProfile()">Create Account</button>
    </div>
  </section>

  <section id="settings" class="content-section">
    <div class="profile-card" style="max-width:520px;">
      <h3>Settings & Preferences</h3>
      <div class="form-group">
        <label>Backend URL</label>
        <input type="text" id="backendUrl" value="/api" placeholder="Backend URL">
      </div>
      <button class="btn btn-save" style="width:100%;margin-top:1.4rem;" onclick="clearAllData()">Clear All Data</button>
    </div>
  </section>
</div>

<footer>
  <div class="footer-brand">⚡ Powered by Technokings</div>
  <div class="footer-text">Smart Respiratory Health Monitoring</div>
  <div class="footer-text">© 2025 Health Care Rockers · Gudlavalleru Engineering College</div>
</footer>

<script>
const API_BASE = '/api';

let timerInterval = null;
let elapsedTime = 0;
let isRunning = false;
let currentTimingType = '';

function startTimer() {
  if (isRunning) return;
  isRunning = true;
  timerInterval = setInterval(() => {
    elapsedTime += 10;
    updateDisplay();
  }, 10);
}

function pauseTimer() {
  isRunning = false;
  clearInterval(timerInterval);
}

function resetTimer() {
  isRunning = false;
  clearInterval(timerInterval);
  elapsedTime = 0;
  updateDisplay();
}

function updateDisplay() {
  const minutes = Math.floor(elapsedTime / 60000);
  const seconds = Math.floor((elapsedTime % 60000) / 1000);
  const ms = Math.floor((elapsedTime % 1000) / 10);
  document.getElementById('display').textContent =
    String(minutes).padStart(2,'0') + ':' +
    String(seconds).padStart(2,'0') + '.' +
    String(ms).padStart(2,'0');
}

function updateTimingType() {
  const selected = document.querySelector('input[name="timing"]:checked');
  if (selected) {
    currentTimingType = selected.value;
    document.getElementById('selected-timing').textContent =
      '📍 Currently measuring: ' + currentTimingType;
  }
}

async function saveCurrentTiming() {
  if (!currentTimingType) {
    alert('Please select a timing type first.');
    return;
  }
  const seconds = (elapsedTime / 1000).toFixed(2);
  
  try {
    const response = await fetch(`${API_BASE}/timings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: currentTimingType,
        duration: seconds
      })
    });
    
    if (response.ok) {
      alert('Saved: ' + currentTimingType + ' = ' + seconds + 's');
      elapsedTime = 0;
      updateDisplay();
      loadPastData();
      loadStats();
    }
  } catch (error) {
    alert('Error saving timing. Check if backend is running.');
  }
}

async function loadPastData() {
  try {
    const response = await fetch(`${API_BASE}/timings`);
    const records = await response.json();
    
    const tbody1 = document.getElementById('past-data-table');
    const tbody2 = document.getElementById('past-data-table-2');

    if (records.length === 0) {
      const row = '<tr><td colspan="4">No records yet.</td></tr>';
      tbody1.innerHTML = row;
      tbody2.innerHTML = row;
      return;
    }

    const rows = records.map(r => `
      <tr>
        <td>${r.date}</td>
        <td>${r.type}</td>
        <td>${r.duration}</td>
        <td><button class="delete-btn" onclick="deleteRecord('${r._id}')">Delete</button></td>
      </tr>
    `).join('');
    tbody1.innerHTML = rows;
    tbody2.innerHTML = rows;
  } catch (error) {
    console.error('Error loading data:', error);
  }
}

async function deleteRecord(id) {
  try {
    await fetch(`${API_BASE}/timings/${id}`, { method: 'DELETE' });
    loadPastData();
    loadStats();
  } catch (error) {
    alert('Error deleting record');
  }
}

async function loadStats() {
  try {
    const response = await fetch(`${API_BASE}/timings`);
    const records = await response.json();
    
    document.getElementById('total-sessions').textContent = records.length;

    const inh = records.filter(r => r.type === 'Inhalation').map(r => parseFloat(r.duration));
    const hold = records.filter(r => r.type === 'Breath-Hold').map(r => parseFloat(r.duration));
    const ex = records.filter(r => r.type === 'Exhalation').map(r => parseFloat(r.duration));

    document.getElementById('avg-inhale').textContent =
      inh.length ? (inh.reduce((a,b)=>a+b,0)/inh.length).toFixed(2)+'s' : '0.0s';
    document.getElementById('avg-hold').textContent =
      hold.length ? (hold.reduce((a,b)=>a+b,0)/hold.length).toFixed(2)+'s' : '0.0s';
    document.getElementById('avg-exhale').textContent =
      ex.length ? (ex.reduce((a,b)=>a+b,0)/ex.length).toFixed(2)+'s' : '0.0s';
  } catch (error) {
    console.error('Error loading stats:', error);
  }
}

async function saveBreathSession() {
  try {
    const response = await fetch(`${API_BASE}/timings`);
    const records = await response.json();
    
    if (!records.length) {
      alert('No timings saved yet. Save inhale, hold, and exhale first.');
      return;
    }
    
    const lastInh = records.find(r => r.type === 'Inhalation');
    const lastHold = records.find(r => r.type === 'Breath-Hold');
    const lastEx = records.find(r => r.type === 'Exhalation');

    if (!lastInh || !lastHold || !lastEx) {
      alert('Need at least one Inhalation, Breath-Hold, and Exhalation timing to save a session.');
      return;
    }

    await fetch(`${API_BASE}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        inhale: lastInh.duration,
        hold: lastHold.duration,
        exhale: lastEx.duration
      })
    });
    
    alert('Breath session saved. Go to "Breath Timing" and click Process Data.');
    loadTimingSessions();
  } catch (error) {
    alert('Error saving session');
  }
}

async function processSessions() {
  try {
    const response = await fetch(`${API_BASE}/sessions`);
    const sessions = await response.json();
    
    if (!sessions.length) {
      alert('No sessions to process. Save a session first.');
      return;
    }

    const tbody = document.getElementById('timing-save-table');
    tbody.innerHTML = '';
    let idx = 1;

    sessions.forEach(s => {
      const h = s.hold / s.inhale;
      const e = s.exhale / s.inhale;
      const D = Math.sqrt((h - 4)**2 + (e - 2)**2);
      let category = 'Needs Attention';
      let chipClass = 'chip-bad';
      let rowClass = 'highlight-bad';

      if (D <= 1) {
        category = 'Healthy';
        chipClass = 'chip-good';
        rowClass = 'highlight-good';
      } else if (D <= 2) {
        category = 'Borderline';
        chipClass = 'chip-borderline';
        rowClass = 'highlight-borderline';
      }

      const row = document.createElement('tr');
      row.className = rowClass;
      row.innerHTML = `
        <td>#${idx++}</td>
        <td>${s.inhale.toFixed(2)}</td>
        <td>${s.hold.toFixed(2)}</td>
        <td>${s.exhale.toFixed(2)}</td>
        <td>${h.toFixed(2)} : ${e.toFixed(2)}</td>
        <td>${D.toFixed(2)}</td>
        <td><span class="chip ${chipClass}">${category}</span></td>
        <td>${s.date}</td>
      `;
      tbody.appendChild(row);
    });
  } catch (error) {
    console.error('Error processing sessions:', error);
  }
}

async function loadTimingSessions() {
  try {
    const response = await fetch(`${API_BASE}/sessions`);
    const sessions = await response.json();
    
    const tbody = document.getElementById('timing-save-table');
    if (!sessions.length) {
      tbody.innerHTML = '<tr><td colspan="8">No complete sessions saved yet.</td></tr>';
      return;
    }
    processSessions();
  } catch (error) {
    console.error('Error loading sessions:', error);
  }
}

async function saveProfile() {
  const profile = {
    fullName: document.getElementById('fullName').value,
    age: document.getElementById('age').value,
    email: document.getElementById('email').value,
    phone: document.getElementById('phone').value,
    height: document.getElementById('height').value,
    weight: document.getElementById('weight').value,
    medical: document.getElementById('medical').value,
    notes: document.getElementById('notes').value
  };
  
  try {
    await fetch(`${API_BASE}/profile`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile)
    });
  } catch (error) {
    console.error('Error saving profile:', error);
  }
}

async function submitProfile() {
  const profile = {
    fullName: document.getElementById('fullName').value,
    age: document.getElementById('age').value,
    email: document.getElementById('email').value,
    phone: document.getElementById('phone').value,
    height: document.getElementById('height').value,
    weight: document.getElementById('weight').value,
    medical: document.getElementById('medical').value,
    notes: document.getElementById('notes').value
  };
  
  try {
    const response = await fetch(`${API_BASE}/profile`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile)
    });
    
    if (response.ok) {
      alert('Account creation successful! Your profile has been saved.');
    } else {
      alert('Error creating account. Please try again.');
    }
  } catch (error) {
    alert('Error creating account. Check if backend is running.');
    console.error('Error saving profile:', error);
  }
}

async function loadProfile() {
  try {
    const response = await fetch(`${API_BASE}/profile`);
    const profile = await response.json();
    
    document.getElementById('fullName').value = profile.fullName || '';
    document.getElementById('age').value = profile.age || '';
    document.getElementById('email').value = profile.email || '';
    document.getElementById('phone').value = profile.phone || '';
    document.getElementById('height').value = profile.height || '';
    document.getElementById('weight').value = profile.weight || '';
    document.getElementById('medical').value = profile.medical || '';
    document.getElementById('notes').value = profile.notes || '';
  } catch (error) {
    console.error('Error loading profile:', error);
  }
}

async function clearAllData() {
  if (confirm('This will delete all saved timings, sessions, and profile. Continue?')) {
    try {
      await fetch(`${API_BASE}/clear`, { method: 'DELETE' });
      location.reload();
    } catch (error) {
      alert('Error clearing data');
    }
  }
}

function showSection(ev, id) {
  document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  ev.target.classList.add('active');

  if (id === 'past-data') loadPastData();
  if (id === 'timing-save') { loadStats(); loadTimingSessions(); }
  if (id === 'profile') loadProfile();
}

window.addEventListener('DOMContentLoaded', () => {
  updateDisplay();
  loadPastData();
  loadStats();
  loadProfile();
  loadTimingSessions();
});
</script>
</body>
</html>'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api')
def api_info():
    return jsonify({
        'message': 'Breath Timing Stopwatch API', 
        'status': 'running',
        'version': '1.0',
        'endpoints': ['/api/timings', '/api/sessions', '/api/profile']
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timings_count': len(storage['timings']),
        'sessions_count': len(storage['sessions'])
    })

@app.route('/api/timings', methods=['POST'])
def save_timing():
    try:
        data = request.get_json()
        if not data or 'type' not in data or 'duration' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
            
        timing = {
            '_id': str(len(storage['timings'])),
            'timestamp': datetime.now().isoformat(),
            'type': data['type'],
            'duration': float(data['duration']),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        storage['timings'].append(timing)
        save_data(storage)
        return jsonify({'success': True, 'id': timing['_id']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/timings', methods=['GET'])
def get_timings():
    try:
        timings = sorted(storage['timings'], key=lambda x: x['timestamp'], reverse=True)
        return jsonify(timings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/timings/<timing_id>', methods=['DELETE'])
def delete_timing(timing_id):
    try:
        storage['timings'] = [t for t in storage['timings'] if t['_id'] != timing_id]
        save_data(storage)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions', methods=['POST'])
def save_session():
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['inhale', 'hold', 'exhale']):
            return jsonify({'error': 'Missing required fields'}), 400
            
        session = {
            '_id': str(len(storage['sessions'])),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'inhale': float(data['inhale']),
            'hold': float(data['hold']),
            'exhale': float(data['exhale']),
            'timestamp': datetime.now().isoformat()
        }
        
        storage['sessions'].append(session)
        save_data(storage)
        return jsonify({'success': True, 'id': session['_id']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    try:
        sessions = sorted(storage['sessions'], key=lambda x: x['timestamp'], reverse=True)
        return jsonify(sessions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile', methods=['POST'])
def save_profile():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        storage['profile'] = {
            'fullName': data.get('fullName', ''),
            'age': data.get('age', ''),
            'email': data.get('email', ''),
            'phone': data.get('phone', ''),
            'height': data.get('height', ''),
            'weight': data.get('weight', ''),
            'medical': data.get('medical', ''),
            'notes': data.get('notes', ''),
            'updated': datetime.now().isoformat()
        }
        
        save_data(storage)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile', methods=['GET'])
def get_profile():
    try:
        return jsonify(storage.get('profile', {}))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['DELETE'])
def clear_all_data():
    try:
        storage['timings'] = []
        storage['sessions'] = []
        storage['profile'] = {}
        save_data(storage)
        return jsonify({'success': True, 'message': 'All data cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        timings = storage['timings']
        inhale_times = [float(t['duration']) for t in timings if t['type'] == 'Inhalation']
        hold_times = [float(t['duration']) for t in timings if t['type'] == 'Breath-Hold']
        exhale_times = [float(t['duration']) for t in timings if t['type'] == 'Exhalation']
        
        stats = {
            'total_timings': len(timings),
            'total_sessions': len(storage['sessions']),
            'avg_inhale': sum(inhale_times) / len(inhale_times) if inhale_times else 0,
            'avg_hold': sum(hold_times) / len(hold_times) if hold_times else 0,
            'avg_exhale': sum(exhale_times) / len(exhale_times) if exhale_times else 0
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print('=' * 50)
    print('BREATH TIMING STOPWATCH WEBSITE')
    print('=' * 50)
    print('Website: http://localhost:5000')
    print('API Info: http://localhost:5000/api')
    print('Health Check: http://localhost:5000/health')
    print('=' * 50)
    app.run(debug=True, host='127.0.0.1', port=5000)