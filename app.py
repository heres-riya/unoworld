from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
import csv
from datetime import datetime

load_dotenv()

app = Flask(__name__)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'postgresql://postgres:postgres@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define Player model
class Player(db.Model):
    __tablename__ = 'players'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(50))
    team = db.Column(db.String(100))
    jersey_number = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    def __repr__(self):
        return f'<Player {self.name}>'

# Define Match model
class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(255))
    match_number = db.Column(db.String(50), unique=True)
    team1 = db.Column(db.String(255))
    team2 = db.Column(db.String(255))    
    group = db.Column(db.String(50))
    stadium = db.Column(db.String(255))
    date_dt = db.Column(db.Date)
    win = db.Column(db.Numeric(precision=5, scale=2))
    loss = db.Column(db.Numeric(precision=5, scale=2))
    draw = db.Column(db.Numeric(precision=5, scale=2))
    
    def __repr__(self):
        return f'<Match {self.match_number}>'

@app.route('/')
def index():
    """Display all players"""
    try:
        matches = Match.query.order_by(Match.id).all()
        return render_template('index.html', matches=matches)
    except Exception as e:
        return f"<h1>Error fetching data</h1><p>{str(e)}</p>", 500

@app.route('/create', methods=['GET', 'POST'])
def create_player():
    """Create a new player"""
    if request.method == 'POST':
        try:
            name = request.form['name']
            position = request.form.get('position')
            team = request.form.get('team')
            jersey_number = request.form.get('jersey_number', type=int)
            
            player = Player(name=name, position=position, team=team, jersey_number=jersey_number)
            db.session.add(player)
            db.session.commit()
            
            return redirect('/')
        except Exception as e:
            db.session.rollback()
            return f"<h1>Error creating player</h1><p>{str(e)}</p>", 500
    
    return render_template('create.html')

@app.route('/dummy')
def add_dummy():
    """Add a dummy player record"""
    try:
        dummy_player = Player(
            name='Dummy Player',
            position='Midfielder',
            team1='Test Team',
            team2='Opponent Team',
            jersey_number=99
        )
        db.session.add(dummy_player)
        db.session.commit()
        
        return f"<h1>✅ Dummy player added!</h1><p>Name: {dummy_player.name}</p><p><a href='/'>Back to players</a></p>", 201
    except Exception as e:
        db.session.rollback()
        return f"<h1>❌ Error adding dummy player</h1><p>{str(e)}</p>", 500

@app.route('/initdb')
def initdb():
    return
    """Initialize database with tables and sample data"""
    try:
        # Create all tables


    # Replace 'matches' with your actual model class name
        db.metadata.tables['matches'].drop(db.engine)
        print("Matches table dropped.")

        db.create_all()
        
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
            
            return f"<h1>✅ Database initialized!</h1><p>Tables created and {len(sample_players)} sample players added.</p><p><a href='/'>View players</a></p>", 201
        else:
            return f"<h1>ℹ️ Database already initialized</h1><p>Tables exist with {Player.query.count()} players.</p><p><a href='/'>View players</a></p>", 200
    except Exception as e:
        db.session.rollback()
        return f"<h1>❌ Error initializing database</h1><p>{str(e)}</p>", 500

@app.route('/initmatches')
def initmatches():
    """Create the matches table with the specified schema"""
    try:
        db.create_all()
        return "<h1>✅ Matches table created (if not exists)</h1><p>Schema: id, date, match_number, teams, group, stadium, date_dt</p>", 201
    except Exception as e:
        return f"<h1>❌ Error creating matches table</h1><p>{str(e)}</p>", 500


@app.route('/submit-prediction', methods=['POST'])
def submit_prediction():
    match_id = request.form.get('match_id')
    prediction = request.form.get('prediction')  # '1', '2', or '3'
    
    # Store prediction in session (in production, use database)
    if 'predictions' not in session:
        session['predictions'] = {}
    
    session['predictions'][match_id] = prediction
    session.modified = True
    
    # Find the match and check result
    match = next((m for m in matches_data if str(m['id']) == match_id), None)
    
    if not match:
        return jsonify({'success': False, 'message': 'Match not found'})
    
    is_correct = None
    if match['actual_result'] is not None:
        is_correct = (prediction == match['actual_result'])
    
    return jsonify({
        'success': True,
        'is_correct': is_correct,
        'actual_result': match['actual_result'],
        'team1_name': match['team1'],
        'team2_name': match['team2']
    })

if __name__ == '__main__':
    app.run(debug=True)
    
@app.route('/dummymatches')
def dummymatches():
    return
    """Parse matches.csv and insert records into the matches table"""
    try:
        # Create table if it doesn't exist
        db.create_all()
        
        # Read and parse CSV file
        csv_path = os.path.join(os.path.dirname(__file__), 'matches.csv')
        
        if not os.path.exists(csv_path):
            return f"<h1>❌ matches.csv not found</h1><p>Expected at: {csv_path}</p>", 404
        
        matches_added = 0
        errors = []
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Parse date_dt string to date object
                    date_dt = None
                    if row.get('date_dt'):
                        date_dt = datetime.strptime(row['date_dt'], '%Y-%m-%d').date()
                    teams_string = row.get('teams')
                    home_team, away_team = [team.strip() for team in teams_string.split(' v ')]
                    match = Match(
                        date=row.get('date'),
                        match_number=row.get('match_number'),
                        team1=home_team,
                        team2=away_team,
                        group=row.get('group'),
                        stadium=row.get('stadium'),
                        date_dt=date_dt
                    )
                    db.session.add(match)
                    matches_added += 1
                except Exception as e:
                    errors.append(f"Row {reader.line_num}: {str(e)}")
                    db.session.rollback()
        
        db.session.commit()
        
        if errors:
            return f"<h1>⚠️ Partial Import</h1><p>Added {matches_added} matches with {len(errors)} errors.</p><p>Errors: {errors}</p><p><a href='/'>Back</a></p>", 207
        
        return f"<h1>✅ Matches imported!</h1><p>Successfully added {matches_added} matches from CSV.</p><p><a href='/'>Back</a></p>", 201
    
    except Exception as e:
        db.session.rollback()
        return f"<h1>❌ Error importing matches</h1><p>{str(e)}</p>", 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
