from flask import Flask, render_template

app = Flask(__name__)

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/home-secret')
def homesecret():
    return render_template('home_secret.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')
    
if __name__ == '__main__':
    app.run(debug=True)