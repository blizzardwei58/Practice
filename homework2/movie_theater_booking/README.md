# Movie Theater Booking Application

A RESTful Movie Theater Booking Application built with Flask.

## Features

- View movie listings via the API
- Book seats via the API
- Check booking history via the API
- Attractive Bootstrap-based user interface

## Setup Instructions

### 1. Create a Virtual Environment

Open PowerShell/Terminal in the `movie_theater_booking` directory and run:

```bash
# Create virtual environment
python -m venv myenv

# Activate virtual environment (Windows PowerShell)
.\myenv\Scripts\Activate.ps1

# OR for Command Prompt (Windows)
myenv\Scripts\activate.bat

# OR for Git Bash / Linux / Mac
source myenv/bin/activate
```

### 2. Install Dependencies

With the virtual environment activated:

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/movies` | Get all movies |
| GET | `/api/movies/<id>` | Get a specific movie |
| POST | `/api/bookings` | Create a new booking |
| GET | `/api/bookings` | Get all bookings |
| GET | `/api/bookings/<id>` | Get a specific booking |

## Project Structure

```
movie_theater_booking/
├── app.py              # Main application entry point
├── models.py           # Database models
├── requirements.txt    # Python dependencies
├── static/             # Static files (CSS, JS)
├── templates/          # HTML templates
└── myenv/              # Virtual environment (after setup)
```


