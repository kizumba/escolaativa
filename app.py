from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from markupsafe import escape
from db import db
from models import Usuario, TipoUsuario
import hashlib

#=============================
# CONFIGURAÇÕES DA APLICAÇÃO =
#=============================

app = Flask(__name__)

lm = LoginManager(app)
lm.login_view = 'login'

app.secret_key = 'equipedev'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
db.init_app(app)

@lm.user_loader
def user_louder(id):
    usuario = db.session.query(Usuario).filter_by(id=id).first()
    return usuario

def hash(txt):
    hash_obj = hashlib.sha256(txt.encode('utf-8'))
    return hash_obj.hexdigest()


#========
# ROTAS =
#========

@app.route('/')
def index():
    print(hash('123'))
    usuarios = Usuario.query.all() 
    tipos_usuarios = TipoUsuario.query.all()

    return render_template('index.html', usuarios=usuarios, tipos_usuarios=tipos_usuarios)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/registrar', methods=['GET','POST'])
def registrar():
    tipos_usuarios = TipoUsuario.query.all()

    if request.method == 'GET':
        return render_template('auth/registrar.html',tipos_usuarios=tipos_usuarios)
    elif request.method == 'POST':
        nome = request.form['nomeForm']
        email = request.form['emailForm']
        telefone = request.form['telefoneForm']
        senha = request.form['senhaForm']
        ativo = True
        id_tipo_usuario = request.form['tipo_usuarioSelect']

        novo_usuario = Usuario(nome=nome, email=email, senha=hash(senha), telefone=telefone, ativo=ativo, id_tipo_usuario=id_tipo_usuario)
        db.session.add(novo_usuario)
        db.session.commit()

        login_user(novo_usuario)

        return redirect(url_for('index'))


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    elif request.method == 'POST':
        email = request.form['emailForm']
        senha = request.form['senhaForm']

        user = db.session.query(Usuario).filter_by(email=email, senha=hash(senha)).first()
        if not user:
            return 'Email ou senha incorretos.'

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
    nome = current_user.nome
    adm = Usuario.query.filter_by(id_tipo_usuario = 1).all()
    professor = Usuario.query.filter_by(id_tipo_usuario = 2).all()
    return render_template('auth/teste.html',nome=nome, adm=adm, professor=professor)

@app.route('/teste/<nome>')
def teste2(nome):
    nome = escape(nome)
    return f"<h1>{nome}</h1>"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)