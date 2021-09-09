import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
import os
import sys
# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Myapp@123'
app.config['db_count']=0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    app.config['db_count'] += 1
    app.logger.info('Connection created successfull.')
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()   
    return post
# Function to get total count
def get_postcount():
    connection = get_db_connection()
    post_count = connection.execute('SELECT count(1) FROM posts').fetchone()[0]
    connection.close()
    return post_count


# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    app.logger.info('All posts are retrieved successfully.')
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info('Post not found.')
      return render_template('NotFound.html'), 404
    else:
      app.logger.info('%s'%post['title'] +' retreived successfully.' )
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About page rendered successfully.')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            app.logger.warning('ERROR: Title not provided.' )
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info('%s'%title +' submitted successfully.' )
            return redirect(url_for('index'))

    return render_template('create.html')
#health check that  returns json response 
@app.route('/healthz')
def healthz():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('Health check is successful.')
    return response
#app metrics returns json response 
@app.route('/metrics')
def metrics():
    response = app.response_class(
            response=json.dumps({"status":"success","code":0,"data":{"post_count":get_postcount(),"db_connection_count":app.config['db_count']}}),
            status=200,
            mimetype='application/json'
    )

    return response

@app.errorhandler(404)
def page_not_found404(e):
    return render_template("404.html")
# start the application on port 3111
if __name__ == "__main__":
     ## configure logs
    loglevel = os.getenv("LOGLEVEL", "DEBUG").upper()
    loglevel = (getattr(logging, loglevel)
        if loglevel in ["CRITICAL", "DEBUG", "ERROR", "INFO", "WARNING",]
        else logging.DEBUG
    )
    # Set logger to handle STDOUT and STDERR
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [stdout_handler]
    # format output
    format_output = '%(asctime)s %(levelname)s %(message)s'
    logging.basicConfig(format=format_output, level=loglevel, handlers=handlers)
    app.run(host='0.0.0.0', port='3111')
