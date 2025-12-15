# Breath Timing Stopwatch

A professional web application for monitoring and analyzing breathing patterns, designed for respiratory health tracking and yogic breathing exercises.

## Project Structure

```
breath-timer/
├── frontend/           # Web interface
│   ├── index.html     # Main HTML page
│   ├── styles.css     # CSS styling
│   ├── script.js      # JavaScript functionality
│   └── README.md      # Frontend guide
│
└── breath-timer-backend/  # API server
    ├── app.py            # Flask application
    ├── requirements.txt  # Python dependencies
    └── README.md         # Backend setup
```

## Features

- **Precision Stopwatch**: High-accuracy timing for breath measurements
- **Multi-Type Tracking**: Monitor inhalation, breath-hold, and exhalation phases
- **Data Analytics**: Analyze breathing patterns against the optimal 1:4:2 ratio
- **Health Categorization**: Automatic classification of breathing health
- **User Profiles**: Store personal and health information
- **MongoDB Storage**: Persistent data storage with Flask API
- **Responsive Design**: Works on desktop and mobile devices

## Quick Start

### Backend Setup:
```bash
cd breath-timer-backend
pip install -r requirements.txt
python app.py
```

### Frontend Setup:
```bash
cd frontend
# Open index.html in browser
```

## Health Analysis

The application analyzes your breathing patterns against the optimal yogic ratio of 1:4:2 (Inhalation:Hold:Exhalation) and categorizes your breathing health as:

- **Healthy**: Close to optimal ratio
- **Borderline**: Moderate deviation
- **Needs Attention**: Significant deviation from optimal

## Technology Stack

**Frontend:**
- HTML5, CSS3, JavaScript
- Responsive design
- Fetch API for backend communication

**Backend:**
- Flask (Python)
- MongoDB
- REST API
- CORS enabled

## License

© 2025 Health Care Rockers · Gudlavalleru Engineering College

---

**Powered by Technokings** - Smart Respiratory Health Monitoring