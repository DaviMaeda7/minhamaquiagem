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

@app.route('/novidades')
def novidades():
    return render_template('novidades.html')

@app.route('/make')
def make():
    return render_template('make.html')

@app.route('/skincare')
def skincare():
    return render_template('skincare.html')

if __name__ == '__main__':
    app.run(debug=True)