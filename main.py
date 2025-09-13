from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html", title="Home", page_class="index-page", year=datetime.utcnow().year)

@app.route("/about")
def about():
    return render_template("about.html", title="About", page_class="about-page", year=datetime.utcnow().year)

@app.route("/projects")
def projects():
    return render_template("projects.html", title="Projects", page_class="projects-page", year=datetime.utcnow().year)

@app.route("/contact")
def contact():
    return render_template("contact.html", title="Contact", page_class="contact-page", year=datetime.utcnow().year)

if __name__ == "__main__":
    app.run(debug=True)
