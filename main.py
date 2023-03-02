from flask import Flask, render_template

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        return(f'Hello, {name}')
    return render_template('index.html')