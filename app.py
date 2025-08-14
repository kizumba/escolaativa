from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from markupsafe import escape
from db import db
from models import *
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
    print('Senha hash')
    print(hash('123'))

    usuarios = Usuario.query.all() 
    tipos_usuarios = TipoUsuario.query.all()

    return render_template('index.html', usuarios=usuarios, tipos_usuarios=tipos_usuarios)

#========
#=TURMAS=
#========
@app.route('/turmas', methods=['GET','POST'])
def turmas():
    if request.method == 'GET':

        turmas = Turma.query.all()
        return render_template('turmas.html', turmas=turmas)

    if request.method == 'POST':
        ano_atual = datetime.now().year
        
        grau = request.form['grau']
        serie = request.form['serie']
        ano = ano_atual

        periodo = request.form['periodo']

        print(f'Grau:{grau}, Série: {serie}, Período: {periodo} Ano: {ano}')

        nova_turma = Turma(grau, serie, periodo, ano)
        db.session.add(nova_turma)
        db.session.commit()

        return redirect(url_for('turmas'))

@app.route('/turma_editar/<int:id>', methods=['GET','POST'])
def turma_editar(id):
    
    turma = Turma.query.get(id)
    
    if request.method == 'GET':
        return render_template("turma_editar.html",turma=turma)
    
    elif request.method == 'POST':

        turma.grau = request.form['grau']
        turma.serie = request.form['serie']
        turma.periodo = request.form['periodo']

        db.session.add(turma)
        db.session.commit()

        return redirect(url_for('turmas'))

@app.route('/turma_apagar/<int:id>',methods=['GET','POST'])
def turma_apagar(id):
    turma = Turma.query.get(id)

    if request.method == 'GET':
        return render_template('turma_apagar.html',turma=turma)
    
    elif request.method == 'POST':
        db.session.delete(turma)
        db.session.commit()
        return redirect(url_for('turmas'))

#========================
#=REGISTRAR NOVO USUARIO=
#========================
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

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/teste')
@login_required
def teste():

    return render_template('auth/teste.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)