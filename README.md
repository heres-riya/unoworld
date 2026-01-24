# Flask + SQLAlchemy PostgreSQL App

A Flask web application using SQLAlchemy ORM to connect to PostgreSQL and display player data. Designed to be deployed on Heroku.

## Features

- ⚽ Flask web framework with SQLAlchemy ORM
- 🗄️ PostgreSQL database integration
- 📊 View all players in a table
- ➕ Add new players with form
- 🎨 Beautiful, responsive UI
- 🚀 Heroku ready (Procfile + runtime.txt included)

## Project Structure

```
goal26/
├── app.py                 # Main Flask application with SQLAlchemy models
├── init_db.py            # Database initialization script
├── requirements.txt       # Python dependencies
├── Procfile              # Heroku process file
├── runtime.txt           # Python version for Heroku
├── .env.example          # Example environment variables
└── templates/
    ├── base.html         # Base template with styling
    ├── index.html        # Players display page
    └── create.html       # Add player form
```

## Prerequisites

- Python 3.11+
- PostgreSQL 12+
- pip (Python package manager)

## Local Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your PostgreSQL credentials (local development)
   # DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
   ```

4. **Initialize the database:**
   ```bash
   python init_db.py
   ```

5. **Run the Flask app:**
   ```bash
   python app.py
   ```

6. **Open your browser:**
   - Navigate to `http://localhost:5000`

## Heroku Deployment

1. **Create a Heroku app:**
   ```bash
   heroku create your-app-name
   ```

2. **Add PostgreSQL database:**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

3. **Deploy code:**
   ```bash
   git push heroku main
   ```

4. **Initialize database:**
   ```bash
   heroku run python init_db.py -a your-app-name
   ```

5. **Open the app:**
   ```bash
   heroku open -a your-app-name
   ```

## Database Models

### Player Table
- `id` - Primary key
- `name` - Player name (required)
- `position` - Playing position (e.g., Forward, Midfielder)
- `team` - Team name
- `jersey_number` - Jersey number
- `created_at` - Timestamp of creation

## Routes

- `GET /` - Display all players
- `GET /create` - Show add player form
- `POST /create` - Create a new player

## Environment Variables

```env
# Heroku automatically sets DATABASE_URL
# For local development:
DATABASE_URL=postgresql://username:password@localhost:5432/dbname
PORT=5000  # Optional, defaults to 5000
```

## Troubleshooting

### Connection Error on Local
- Ensure PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Verify database credentials

### Error on Heroku
- Check logs: `heroku logs --tail`
- Ensure database addon is provisioned: `heroku addons`
- Verify DATABASE_URL config var is set

## Dependencies

- **Flask** - Web framework
- **Flask-SQLAlchemy** - SQLAlchemy integration
- **SQLAlchemy** - ORM
- **psycopg2-binary** - PostgreSQL adapter
- **python-dotenv** - Environment variable management
- **gunicorn** - Production WSGI server

## License

This project is open source and available for educational purposes.
