"""
Database initialization script - creates tables and sample data
"""
from app import app, db, Player
import os
from dotenv import load_dotenv

load_dotenv()

def init_database():
    """Initialize database with sample data"""
    with app.app_context():
    # Replace 'matches' with your actual model class name
        db.metadata.tables['matches'].drop(db.engine)
        print("Matches table dropped.")
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Tables created successfully!")
        
        # Check if we have any existing players
        if Player.query.first() is None:
            # Insert sample data
            sample_players = [
                Player(name='Cristiano Ronaldo', position='Forward', team='Manchester United', jersey_number=7),
                Player(name='Lionel Messi', position='Forward', team='Paris Saint-Germain', jersey_number=30),
                Player(name='Neymar Jr', position='Forward', team='Paris Saint-Germain', jersey_number=10),
                Player(name='Kevin De Bruyne', position='Midfielder', team='Manchester City', jersey_number=17),
            ]
            
            db.session.add_all(sample_players)
            db.session.commit()
            print("✅ Sample players inserted successfully!")
        else:
            print("ℹ️  Database already contains players")

if __name__ == '__main__':
    init_database()
