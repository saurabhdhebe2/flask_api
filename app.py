from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS 
from datetime import datetime
from sqlalchemy import text  
from dotenv import load_dotenv 
import os 

load_dotenv()
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')

db = SQLAlchemy(app)

# Check database connection
@app.before_request
def check_database_connection():
    try:
        db.session.execute(text('SELECT 1'))  
        print("Database connected successfully!")
    except Exception as e:
        print(f"Database connection failed: {e}")

class Post(db.Model):
    __tablename__ = 'posts' 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# Create post
@app.route('/create-post', methods=['POST'])
def create_post():
    data = request.get_json()
    new_post = Post(title=data['title'], content=data['content'])
    db.session.add(new_post)
    db.session.commit()
    return jsonify({'message': 'Post created!', 'id': new_post.id}), 201

# Get all posts
@app.route('/get-posts', methods=['GET'])  
def get_posts():
    posts = Post.query.all()
    return jsonify([{
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'created_at': post.created_at.isoformat(),
        'updated_at': post.updated_at.isoformat()
    } for post in posts]), 200

# Get single post by id
@app.route('/get-post/<int:id>', methods=['GET'])
def get_post_by_id(id):
    post = Post.query.get(id)
    if post:
        return jsonify({
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'created_at': post.created_at.isoformat(),
            'updated_at': post.updated_at.isoformat()
        }), 200
    else:
        return jsonify({'message': 'Post not found!'}), 404

# Update post
@app.route('/update-post/<int:id>', methods=['POST'])  
def update_post(id): 
    data = request.get_json()
    post = Post.query.get(id)

    if post:
        post.title = data['title']
        post.content = data['content']
        db.session.commit()
        return jsonify({'message': 'Post updated!'}), 200
    else:
        return jsonify({'message': 'Post not found!'}), 404

if __name__ == "__main__": 
    app.run(debug=True)