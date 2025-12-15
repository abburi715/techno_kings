# Breath Timer Backend

Flask API with MongoDB for breath timing data.

## Setup

1. Install MongoDB and start service
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python app.py`

Backend runs on http://localhost:5000

## API Endpoints

- POST /api/timings - Save timing
- GET /api/timings - Get all timings  
- DELETE /api/timings/<id> - Delete timing
- POST /api/sessions - Save session
- GET /api/sessions - Get sessions
- POST /api/profile - Save profile
- GET /api/profile - Get profile
- DELETE /api/clear - Clear all data