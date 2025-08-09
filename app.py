from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from markupsafe import escape
from db import db
from models import Usuario
import hashlib

#=============================
# CONFIGURAÇÕES DA APLICAÇÃO =
#=============================

app = Flask(__name__)

lm = LoginManager(app)
lm.login_view = 'login'

app.secret_key = 'lancode'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
db.init_app(app)

@lm.user_loader
def user_louder(id):
    usuario = db.session.query(Usuario).filter_by(id=id).first()
    return usuario

def hash(txt):
    hash_obj = hashlib.sha256(txt.encode('utf-8'))
    return hash_obj.hexdigest()


#=============================
# ROTAS                      =
#=============================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/base')
def base():
    return render_template('base.html')


@app.route('/registrar', methods=['GET','POST'])
def registrar():
    if request.method == 'GET':
        return render_template('auth/registrar.html')
    elif request.method == 'POST':
        nome = request.form['nomeForm']
        senha = request.form['senhaForm']

        novo_usuario = Usuario(nome=nome, senha=hash(senha))
        db.session.add(novo_usuario)
        db.session.commit()

        login_user(novo_usuario)

        return redirect(url_for('index'))


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    elif request.method == 'POST':
        nome = request.form['nomeForm']
        senha = request.form['senhaForm']

        user = db.session.query(Usuario).filter_by(nome=nome, senha=hash(senha)).first()
        if not user:
            return 'Nome ou senha incorretos.'

        login_user(user)
        return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Essa rota só pode ser acessada por usuário logado
@app.route('/teste')
@login_required
def teste():
    print(hash(current_user.senha))
    return render_template('auth/teste.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)