const API_BASE = 'http://localhost:5000/api';

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