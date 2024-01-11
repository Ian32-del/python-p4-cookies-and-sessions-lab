#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, session
from flask_migrate import Migrate

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/clear')
def clear_session():
    session['page_views'] = 0
    return {'message': '200: Successfully cleared session data.'}, 200

@app.route('/articles')
def index_articles():

    with app.test_client() as client:
        # Ensure that the session is clear before starting the test
        client.get('/clear')
        
        # Make a GET request to view an article
        client.get('/articles/1')
        
        # Ensure that the page_views session variable is 1 after viewing the first article
        with client.session_transaction() as sess:
            assert sess['page_views'] == 1

        # for _ in range(2, 5):
        #     client.get(f'/articles/{_}')

        # response = client.get('/articles/5')
        # assert response.status_code == 401

        # assert 'Maximum pageview limit reached ' in response.json['message']

@app.route('/articles/<int:id>')
def show_article(id):
    if 'page_views' not in session:
        session['page_views'] = 0
    else:
        session['page_views'] += 1

    if session['page_views'] <= 3:
        # Render JSON response with article data
        article = Article.query.get(id)
        if article:
            return jsonify(article.to_dict()), 200
        else:
            return jsonify({'error': 'Article not found'}), 404
    else:
        # Render JSON response with error message
        return jsonify({'message': 'Maximum pageview limit reached'}), 401


if __name__ == '__main__':
    app.run(port=5555)
