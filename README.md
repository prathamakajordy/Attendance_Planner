# Attendance Planner AI (Version 1.0)

A deterministic, rule-based recommendation engine that builds optimal attendance strategies for university students. 

Unlike traditional attendance trackers that only tell you where you stand today, **Attendance Planner AI** looks at your entire semester timetable, academic rules (like Honors and Practical batches), and holidays to generate a complete, day-by-day plan of exactly which lectures you must attend to satisfy your university's attendance policy.

## Core Features

- **Setup Wizard**: Quickly onboard by entering your semester dates, subjects, timetable slots, and holidays.
- **Academic Eligibility Engine**: Automatically handles complex academic structures like Practical Batches, Honors, Minor, and Open Elective subjects.
- **Deterministic Recommendation Engine**: Evaluates every slot in the semester and guarantees an optimal plan.
- **Interactive Calendar**: Visualize your generated plan on a clean, responsive calendar with instant client-side filtering.
- **Feasibility Analysis**: Instantly know if it's mathematically impossible to achieve your required attendance and precisely why.

## Screenshots

*(See artifacts for screenshots demonstrating Setup Wizard, Dashboard, Calendar, and Details Panel)*

## Tech Stack

- **Frontend**: React, Vite, Tailwind CSS, React Router
- **Backend**: FastAPI (Python), SQLAlchemy, SQLite
- **Architecture**: Decoupled Client-Server

---

## Clean Installation Guide

Follow these steps to run the application locally from scratch.

### Prerequisites
- Node.js (v18+)
- Python (3.10+)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/attendance-planner.git
cd attendance-planner
```

### 2. Backend Setup
Navigate to the backend directory, set up your virtual environment, and install dependencies.
```bash
cd backend
python -m venv venv

# On Windows
.\venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Set up your environment variables:
```bash
cp .env.example .env
```

Run database migrations to initialize SQLite:
```bash
alembic upgrade head
```

Start the FastAPI server:
```bash
uvicorn app.main:app --reload --port 8000
```
*The backend API is now running at `http://localhost:8000`*

### 3. Frontend Setup
Open a new terminal window, navigate to the frontend directory, and install dependencies.
```bash
cd frontend
npm install
```

Start the Vite development server:
```bash
npm run dev
```
*The frontend is now running at `http://localhost:5173`*

### 4. Generate Your First Plan
1. Open your browser and navigate to `http://localhost:5173`.
2. Follow the 5-step Setup Wizard to define your semester.
3. Click "Finish Setup" to instantly generate and view your personalized Attendance Calendar!

---

## Architecture & Rules

- **Engine Architecture**: For details on how the Recommendation Engine evaluates constraints, see [ENGINE_ARCHITECTURE.md](./ENGINE_ARCHITECTURE.md).
- **Development Rules**: To contribute, strictly follow the [AI_DEVELOPMENT_RULES.md](./AI_DEVELOPMENT_RULES.md).

## Future Roadmap (Post v1.0)
- Support for managing multiple semesters simultaneously.
- Interactive Dashboard editing (modifying events and timetables without API/DB resets).
- User Authentication (OAuth).
- Push notifications for attendance warnings.
- Real-time attendance logging (marking present/absent on a specific past day).
