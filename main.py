from flask import Flask, render_template
from markupsafe import escape

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        return(f'Hello, {escape(name)}')
    return render_template('index.html')