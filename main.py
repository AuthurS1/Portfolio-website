"""
Flask single-file portfolio website
Features: home, about, projects (list + detail), blog (list + post), hobbies, contact (form -> saved to DB)
How to run:
  1) pip install flask
  2) python portfolio_flask_app.py
  3) Open http://127.0.0.1:5000

Notes:
 - This is a demo single-file app using SQLite for simplicity.
 - For production, use a proper template structure, static files, and authentication for admin actions.
"""
from flask import Flask, g, render_template_string, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime

DATABASE = 'portfolio.db'
app = Flask(__name__)
app.secret_key = os.urandom(24)

# ----------------- Database helpers -----------------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    cur = db.cursor()
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        details TEXT,
        url TEXT,
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT,
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        message TEXT,
        created_at TEXT
    );
    ''')
    db.commit()

    # Insert sample data if empty
    cur.execute('SELECT COUNT(*) FROM projects')
    if cur.fetchone()[0] == 0:
        cur.execute('INSERT INTO projects (title, description, details, url, created_at) VALUES (?, ?, ?, ?, ?)',
                    ('Sample Project', 'Một dự án ví dụ', 'Chi tiết dự án ví dụ: sử dụng Flask + SQLite', 'https://example.com', datetime.utcnow().isoformat()))
    cur.execute('SELECT COUNT(*) FROM posts')
    if cur.fetchone()[0] == 0:
        cur.execute('INSERT INTO posts (title, content, created_at) VALUES (?, ?, ?)',
                    ('Welcome to my blog', 'Đây là bài viết đầu tiên trên blog của tôi. Viết gì đó thú vị ở đây!', datetime.utcnow().isoformat()))
    db.commit()

# ----------------- Templates (inline for single-file demo) -----------------
BASE_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ title or 'Portfolio' }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
      body { padding-top: 56px; }
      .hero { padding: 4rem 0; background: linear-gradient(90deg,#eef2ff,#ffffff); }
      footer { padding: 2rem 0; margin-top: 3rem; background:#f8f9fa }
    </style>
  </head>
  <body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light fixed-top">
      <div class="container">
        <a class="navbar-brand" href="{{ url_for('home') }}">My Portfolio</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navmenu">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navmenu">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item"><a class="nav-link" href="{{ url_for('projects') }}">Projects</a></li>
            <li class="nav-item"><a class="nav-link" href="{{ url_for('blog') }}">Blog</a></li>
            <li class="nav-item"><a class="nav-link" href="{{ url_for('hobbies') }}">Hobbies</a></li>
            <li class="nav-item"><a class="nav-link" href="{{ url_for('about') }}">About</a></li>
            <li class="nav-item"><a class="nav-link" href="{{ url_for('contact') }}">Contact</a></li>
          </ul>
        </div>
      </div>
    </nav>

    <main class="container">
      {% with messages = get_flashed_messages() %}
        {% if messages %}
          <div class="alert alert-success mt-3">{{ messages[0] }}</div>
        {% endif %}
      {% endwith %}

      {{ body|safe }}
    </main>

    <footer class="text-center">
      <div class="container">
        <p class="mb-0">&copy; {{ year }} — Your Name</p>
      </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>
"""

# ----------------- Routes -----------------
@app.route('/')
def home():
    db = get_db()
    cur = db.execute('SELECT id, title, description FROM projects ORDER BY id DESC LIMIT 3')
    recent_projects = cur.fetchall()
    cur = db.execute('SELECT id, title, created_at FROM posts ORDER BY id DESC LIMIT 3')
    recent_posts = cur.fetchall()

    body = render_template_string('''
    <section class="hero text-center">
      <h1>Hello — I'm Your Name</h1>
      <p class="lead">Junior DevOps / Developer. Tôi xây dựng dự án, viết blog và học mọi thứ về hệ thống.</p>
      <p><a href="{{ url_for('projects') }}" class="btn btn-primary">See my projects</a></p>
    </section>

    <div class="row mt-4">
      <div class="col-md-6">
        <h3>Recent Projects</h3>
        <ul class="list-group">
        {% for p in projects %}
          <li class="list-group-item"><a href="{{ url_for('project_detail', project_id=p['id']) }}">{{ p['title'] }}</a> — {{ p['description'] }}</li>
        {% endfor %}
        </ul>
      </div>
      <div class="col-md-6">
        <h3>Latest Blog Posts</h3>
        <ul class="list-group">
        {% for post in posts %}
          <li class="list-group-item"><a href="{{ url_for('post_detail', post_id=post['id']) }}">{{ post['title'] }}</a> — {{ post['created_at'][:10] }}</li>
        {% endfor %}
        </ul>
      </div>
    </div>
    ''', projects=recent_projects, posts=recent_posts)

    return render_template_string(BASE_HTML, title='Home', body=body, year=datetime.utcnow().year)

@app.route('/about')
def about():
    body = render_template_string('''
    <h2>About me</h2>
    <p>Viết vài dòng về bản thân: học ngành gì, kỹ năng, mục tiêu nghề nghiệp. Ví dụ:</p>
    <ul>
      <li>Ngôn ngữ: Python, C++</li>
      <li>Tools: Docker, Git, Linux</li>
      <li>Interests: DevOps, embedded systems, IoT</li>
    </ul>
    ''')
    return render_template_string(BASE_HTML, title='About', body=body, year=datetime.utcnow().year)

@app.route('/projects')
def projects():
    db = get_db()
    cur = db.execute('SELECT * FROM projects ORDER BY id DESC')
    projects = cur.fetchall()
    body = render_template_string('''
    <h2>Projects</h2>
    <div class="row">
      {% for p in projects %}
      <div class="col-md-6">
        <div class="card mb-3">
          <div class="card-body">
            <h5 class="card-title">{{ p['title'] }}</h5>
            <p class="card-text">{{ p['description'] }}</p>
            <a href="{{ url_for('project_detail', project_id=p['id']) }}" class="btn btn-outline-primary">Details</a>
          </div>
        </div>
      </div>
      {% endfor %}
    </div>
    <hr>
    <h4>Add Project (demo admin)</h4>
    <form method="post" action="{{ url_for('add_project') }}">
      <div class="mb-3"><input class="form-control" name="title" placeholder="Title"></div>
      <div class="mb-3"><input class="form-control" name="description" placeholder="Short description"></div>
      <div class="mb-3"><input class="form-control" name="url" placeholder="URL (optional)"></div>
      <div class="mb-3"><textarea class="form-control" name="details" placeholder="Details"></textarea></div>
      <button class="btn btn-success">Add</button>
    </form>
    ''', projects=projects)
    return render_template_string(BASE_HTML, title='Projects', body=body, year=datetime.utcnow().year)

@app.route('/projects/add', methods=['POST'])
def add_project():
    title = request.form.get('title')
    description = request.form.get('description')
    details = request.form.get('details')
    url = request.form.get('url')
    db = get_db()
    db.execute('INSERT INTO projects (title, description, details, url, created_at) VALUES (?, ?, ?, ?, ?)',
               (title, description, details, url, datetime.utcnow().isoformat()))
    db.commit()
    flash('Project added (demo).')
    return redirect(url_for('projects'))

@app.route('/projects/<int:project_id>')
def project_detail(project_id):
    db = get_db()
    cur = db.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
    p = cur.fetchone()
    if not p:
        return redirect(url_for('projects'))
    body = render_template_string('''
    <h2>{{ p['title'] }}</h2>
    <p>{{ p['description'] }}</p>
    <pre>{{ p['details'] }}</pre>
    {% if p['url'] %}<p>URL: <a href="{{ p['url'] }}" target="_blank">{{ p['url'] }}</a></p>{% endif %}
    ''', p=p)
    return render_template_string(BASE_HTML, title=p['title'], body=body, year=datetime.utcnow().year)

# ----------------- Blog -----------------
@app.route('/blog')
def blog():
    db = get_db()
    cur = db.execute('SELECT id, title, created_at FROM posts ORDER BY id DESC')
    posts = cur.fetchall()
    body = render_template_string('''
    <h2>Blog</h2>
    <ul class="list-group">
      {% for post in posts %}
        <li class="list-group-item"><a href="{{ url_for('post_detail', post_id=post['id']) }}">{{ post['title'] }}</a> — {{ post['created_at'][:10] }}</li>
      {% endfor %}
    </ul>

    <hr>
    <h4>Add Post (demo admin)</h4>
    <form method="post" action="{{ url_for('add_post') }}">
      <div class="mb-3"><input class="form-control" name="title" placeholder="Title"></div>
      <div class="mb-3"><textarea class="form-control" name="content" placeholder="Content"></textarea></div>
      <button class="btn btn-success">Add Post</button>
    </form>
    ''', posts=posts)
    return render_template_string(BASE_HTML, title='Blog', body=body, year=datetime.utcnow().year)

@app.route('/blog/add', methods=['POST'])
def add_post():
    title = request.form.get('title')
    content = request.form.get('content')
    db = get_db()
    db.execute('INSERT INTO posts (title, content, created_at) VALUES (?, ?, ?)',
               (title, content, datetime.utcnow().isoformat()))
    db.commit()
    flash('Post added (demo).')
    return redirect(url_for('blog'))

@app.route('/blog/<int:post_id>')
def post_detail(post_id):
    db = get_db()
    cur = db.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
    post = cur.fetchone()
    if not post:
        return redirect(url_for('blog'))
    body = render_template_string('''
    <h2>{{ post['title'] }}</h2>
    <p class="text-muted">{{ post['created_at'][:10] }}</p>
    <div>{{ post['content'] }}</div>
    ''', post=post)
    return render_template_string(BASE_HTML, title=post['title'], body=body, year=datetime.utcnow().year)

# ----------------- Hobbies -----------------
@app.route('/hobbies')
def hobbies():
    # You can later make this dynamic or editable
    my_hobbies = [
        {'name': 'Coding', 'desc': 'Xây dựng project, automations, scripting.'},
        {'name': '3D Modeling', 'desc': 'Học cơ bản Blender/SketchUp.'},
        {'name': 'Reading', 'desc': 'Technical blogs and fiction.'}
    ]
    body = render_template_string('''
    <h2>Hobbies</h2>
    <div class="row">
      {% for h in hobbies %}
      <div class="col-md-4">
        <div class="card mb-3">
          <div class="card-body">
            <h5 class="card-title">{{ h.name }}</h5>
            <p class="card-text">{{ h.desc }}</p>
          </div>
        </div>
      </div>
      {% endfor %}
    </div>
    ''', hobbies=my_hobbies)
    return render_template_string(BASE_HTML, title='Hobbies', body=body, year=datetime.utcnow().year)

# ----------------- Contact -----------------
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        db = get_db()
        db.execute('INSERT INTO messages (name, email, message, created_at) VALUES (?, ?, ?, ?)',
                   (name, email, message, datetime.utcnow().isoformat()))
        db.commit()
        flash('Thanks! Your message has been received.')
        return redirect(url_for('contact'))

    # Show contact form and recent messages (demo)
    db = get_db()
    cur = db.execute('SELECT name, message, created_at FROM messages ORDER BY id DESC LIMIT 5')
    messages = cur.fetchall()
    body = render_template_string('''
    <h2>Contact</h2>
    <form method="post">
      <div class="mb-3"><input class="form-control" name="name" placeholder="Your name"></div>
      <div class="mb-3"><input class="form-control" name="email" placeholder="Email"></div>
      <div class="mb-3"><textarea class="form-control" name="message" placeholder="Message"></textarea></div>
      <button class="btn btn-primary">Send</button>
    </form>

    <hr>
    <h4>Recent messages (demo)</h4>
    <ul class="list-group">
      {% for m in messages %}
        <li class="list-group-item"><strong>{{ m['name'] }}</strong>: {{ m['message'] }} <br><small class="text-muted">{{ m['created_at'][:10] }}</small></li>
      {% endfor %}
    </ul>
    ''', messages=messages)
    return render_template_string(BASE_HTML, title='Contact', body=body, year=datetime.utcnow().year)

# ----------------- Initialization -----------------
if __name__ == '__main__':
    # Create DB and sample data if needed
    if not os.path.exists(DATABASE):
        open(DATABASE, 'a').close()
    with app.app_context():
        init_db()
    app.run(debug=True)
