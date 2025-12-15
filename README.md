# Breath Timer Frontend
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
Modern web interface for the breath timing application.

## Files

- `index.html` - Main HTML structure
- `styles.css` - CSS styling
- `script.js` - JavaScript functionality

## Setup

1. Ensure backend is running on http://localhost:5000
2. Open `index.html` in web browser
3. Start using the breath timer

## Features

- Precision stopwatch for breath timing
- Multi-phase tracking (inhalation, hold, exhalation)
- Data analytics with health categorization
- User profile management
- Responsive design

## Usage

1. Select timing type (Inhalation/Hold/Exhalation)
2. Start timer and measure breath
3. Save timing to database
4. Create sessions for complete breath cycles
5. Analyze data for health insights
