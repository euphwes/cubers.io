from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
	user = {'username': app.config['REDDIT_CLIENT_ID']}
	return render_template('index.html', title='Home', user=user)