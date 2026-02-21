# Campus Automated Scheduling System

This is a full-stack application for automated scheduling in a campus setting, based on the provided blueprint.

## Architecture

- **Backend**: Python FastAPI with Google OR-Tools CP-SAT for constraint solving
- **Frontend**: React with TypeScript and Tailwind CSS
- **Database**: PostgreSQL (SQLite for dev)
- **Cache/Queue**: Redis
- **Export**: XlsxWriter for Excel generation

## Setup

1. Ensure Docker and Docker Compose are installed.

2. Clone the repository and navigate to the project directory.

3. Run the application:
   ```bash
   docker-compose up --build
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001
   - API Docs: http://localhost:8001/docs

## Development

### Backend
- Install dependencies: `pip install -r requirements.txt`
- Run: `uvicorn app.main:app --reload --port 8001`

### Frontend
- Install dependencies: `npm install`
- Run: `npm start`

## Key Features

- **Constraint Solver**: OR-Tools CP-SAT with hard constraints (no overlaps, room types, end-of-day limits, senior preferences, CWATS rules) and soft constraints (gap minimization, 2-unit clustering)
- **Master Data CRUD**: Manage buildings, rooms, teachers, sections, courses
- **Scheduling Engine**: Generate conflict-free schedules with optimization
- **Export**: Excel output with color-coded subjects and multiple sheets
- **Audit Logging**: Track all changes
- **Hidden Reset**: Admin-only system reset with confirmation

## API Endpoints

- `/api/master-data/*` - CRUD for master data
- `/api/scheduling/*` - Scheduling operations
- `/api/export/*` - Export functionality
- `/api/audit/*` - Audit logs

## Solver Logic

The system uses a cost function to optimize:

- Hard constraints: Must be satisfied (e.g., no double-booking, room matching)
- Soft constraints: Minimize student gaps (gravity rule), cluster 2-unit courses, Saturday-Weekday swap penalties

If constraints cannot be met, returns a conflict report instead of failing.