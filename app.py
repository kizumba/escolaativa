from datetime import *
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from markupsafe import escape
from db import db
from models import *
import hashlib

from funcoes_bd import lista_equipes

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

    usuarios = Usuario.query.all() 
    tipos_usuarios = TipoUsuario.query.all()

    return render_template('index.html', usuarios=usuarios, tipos_usuarios=tipos_usuarios)

#=========
# TURMAS =
#=========
@app.route('/turmas', methods=['GET','POST'])
def turmas():
    turmas = current_user.ensina_turmas
    
    if request.method == 'GET':
        return render_template('turmas.html', turmas=turmas)

    if request.method == 'POST':
        ano_atual = datetime.now().year
        
        grau = request.form['grau']
        serie = request.form['serie']
        ano = ano_atual

        periodo = request.form['periodo']

        nova_turma = Turma(grau, serie, periodo, ano)
        db.session.add(nova_turma)
        db.session.commit()

        current_user.ensina_turmas.append(nova_turma)
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

    torneios = Torneio.query.filter_by(id_turma=turma.id).all()
                
    
    if request.method == 'GET':
        return render_template('turma_apagar.html',turma=turma)
    
    elif request.method == 'POST':

        for t in torneios:
            for e in t.disputa_equipes:
                if e:
                    comportamentos = Equipe_Comportamento.query.filter_by(id_equipe=e.id).all()
                    for c in comportamentos:
                        db.session.delete(c)
                        db.session.commit()

        db.session.delete(turma)
        db.session.commit()
        return redirect(url_for('turmas'))

#====================
# TIPOS DE USUÁRIOS =
#====================
@app.route('/tipos_usuarios', methods=['GET','POST'])
def tipos_usuarios():
    tipos_usuarios = TipoUsuario.query.all()

    if request.method == 'GET': 
        return render_template('tipos_usuarios.html',tipos_usuarios=tipos_usuarios)
    
    elif request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']

        tipo_usuario = TipoUsuario(nome=nome, descricao=descricao)

        db.session.add(tipo_usuario)
        db.session.commit()

        return redirect(url_for('tipos_usuarios'))

@app.route('/tipo_usuario_editar/<int:id>',methods=['GET','POST'])
def tipo_usuario_editar(id):
    tipo_usuario = TipoUsuario.query.get(id)

    if request.method == 'GET':
        return render_template("tipo_usuario_editar.html",tipo_usuario=tipo_usuario)
    
    elif request.method == 'POST':

        tipo_usuario.nome = request.form['nome']
        tipo_usuario.descricao = request.form['descricao']

        db.session.add(tipo_usuario)
        db.session.commit()

        return redirect(url_for('tipos_usuarios'))

#===============
# SALA DE AULA =
#===============
@app.route('/sala_aula/<int:id>', methods=['GET','POST'])
def sala_aula(id):
    turma = Turma.query.get(id)
    equipes = Equipe.query.filter_by(id_turma=turma.id)
    torneios = Torneio.query.filter_by(id_turma=turma.id)

    if request.method == 'GET':
        return render_template('sala_aula.html', turma=turma, equipes=equipes, torneios=torneios)
    elif request.method == 'POST':
        bimestre = request.form['bimestre']
        premiacao = request.form['premiacao']
        data_criacao = date.today()
        data_hora = datetime.now().time()
        id_turma = turma.id

        novo_torneio = Torneio(bimestre=bimestre, premiacao=premiacao, data_criacao=data_criacao, data_hora=data_hora, id_turma=id_turma)

        db.session.add(novo_torneio)
        db.session.commit()

        return redirect(url_for('sala_aula', id=turma.id))

# DISPUTA
@app.route('/disputas/<int:id>')
def disputas(id):
    torneio = db.session.get(Torneio, id)
    comportamentos = Comportamento.query.all()
    equipes = torneio.disputa_equipes

    registros = []

    for e in equipes:
        registros.append(Equipe_Comportamento.query.get(e.id))

    return render_template('disputas.html', torneio=torneio, equipes=equipes, comportamentos=comportamentos,registros=registros)

# CRIAR EQUIPE
@app.route('/criar_equipe',methods=['POST'])
def criar_equipe():
    
    if request.method == 'POST':
        nome = request.form['nome']
        lider = request.form['lider']
        id_torneio = request.form['id_torneio']
        id_turma = request.form['id_turma']

        nova_equipe = Equipe(nome=nome, lider=lider, id_turma=id_turma)
        print(nova_equipe)
        if nova_equipe:
            try:
                db.session.add(nova_equipe)
                db.session.commit()
                
                torneio = db.session.get(Torneio,id_torneio)
                if torneio:
                    torneio.disputa_equipes.append(nova_equipe)
                    db.session.commit()
                

            except:
                print("Deu erro na criação da equipe.")
    
    return redirect(url_for('disputas',id=id_torneio))

# EQUIPE COMPORTAMENTO
@app.route('/equipe_comportamento/<id_torneio>/<id_equipe>/<id_comportamento>')
def equipe_comportamento(id_torneio, id_equipe, id_comportamento):
    torneio = Torneio.query.get(id_torneio)
    equipe = Equipe.query.get(id_equipe)
    comportamento = Comportamento.query.get(id_comportamento)

    data_criacao = date.today()
    data_hora = datetime.now().time()
    equipe.pontos += comportamento.pontos
    print(equipe.pontos)
    
    try:
        equipe_comportamento = Equipe_Comportamento(id_equipe=equipe.id, id_comportamento=comportamento.id, data_criacao=data_criacao, data_hora=data_hora)
        print(equipe_comportamento)

        db.session.add(equipe_comportamento)
        db.session.commit()
    except:
        print("Deu errado")
    
    return redirect(url_for('disputas', id=id_torneio))

#=================
# COMPORTAMENTOS =
#=================
@app.route('/comportamentos', methods=['GET','POST'])
def comportamentos():
    comportamentos = Comportamento.query.all()

    if request.method == 'GET':
        return render_template('comportamentos.html', comportamentos=comportamentos)
    else:
        nome = request.form['nome']
        descricao = request.form['descricao']
        pontos = request.form['pontos']

        try:
            c = Comportamento(nome=nome, descricao=descricao, pontos=pontos)
            db.session.add(c)
            db.session.commit()
        except:
            print('Deu erro ao criar um novo comportamento')

        print(f'{nome} -{descricao} - {pontos}')
        return redirect(url_for('comportamentos'))

# COMPORTAMENTO EDITAR
@app.route('/comportamento_editar/<int:id>',methods=['GET','POST'])
def comportamento_editar(id):
    c = Comportamento.query.get(id)
    if c:
        print(c.nome)
    if request.method == 'GET':
        return render_template('comportamento_editar.html', c=c)
    else:
        nome = request.form['nome']
        descricao = request.form['descricao']
        pontos = request.form['pontos']

        c.nome = nome
        c.descricao = descricao
        c.pontos = pontos

        try:
            db.session.add(c)
            db.session.commit()
        except:
            print(f"Erro ao editar {c.nome}.")

        return redirect(url_for('comportamentos'))

# COMPORTAMENTO APAGAR
@app.route('/comportamento_apagar/<int:id>', methods=['GET','POST'])
def comportamento_apagar(id):
    c = Comportamento.query.get(id)

    if request.method == 'GET':
        return render_template('comportamento_apagar.html', c=c)
    else:
        try:
            db.session.delete(c)
            db.session.commit()
        except:
            print(f'Não foi possível apagar o comportamento {c.nome}')

        return redirect(url_for('comportamentos'))

@app.route('/comportamento_desativar/<int:id>')
def comportamento_desativar(id):
    c = Comportamento.query.get(id)

    try:    
        c.ativo = not c.ativo
        db.session.add(c)
        db.session.commit()
    except:
        print(f'Erro ao alterar o valor de {c.ativo} em {c.nome}')
    return redirect(url_for('comportamentos'))

#=========================
# REGISTRAR NOVO USUARIO =
#=========================
@app.route('/registrar', methods=['GET','POST'])
def registrar():
    tipos_usuarios = TipoUsuario.query.all()
    usuarios = Usuario.query.all()

    if request.method == 'GET':
        return render_template('auth/registrar.html',tipos_usuarios=tipos_usuarios, usuarios=usuarios)
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

        #login_user(novo_usuario)

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

        tipo_usuario = TipoUsuario.query.filter_by(nome="Administrador").first()
        
        if not tipo_usuario:
            try:
                tipo_usuario = TipoUsuario(nome="Administrador", descricao="Responsável pelo sistema")
                db.session.add(tipo_usuario)
                db.session.commit()
                print("Tipo de usuário 'Administrador' criado com sucesso!")
            except:
                db.session.rollback()
                print("Tipo de usuário 'Administrador' já existe (erro capturado)")
        
        usuario = Usuario.query.filter_by(nome="Master").first()

        if not usuario:
            try:
                usuario = Usuario(
                    nome='Mestre', 
                    telefone='11988887777', 
                    email='mestre@email.com', 
                    senha=hash('123'), 
                    ativo=True, 
                    id_tipo_usuario=1)
                db.session.add(usuario)
                db.session.commit()
                print("Usuário 'Mestre' criado com sucesso!")
            except:
                db.session.rollback()
                print("Usuário 'Mestre' já existe (erro capturado)")


    app.run(debug=True)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)