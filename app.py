from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

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

@app.route('/')
def index():
    """Display all players"""
    try:
        players = Player.query.all()
        return render_template('index.html', players=players)
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
