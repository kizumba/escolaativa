from db import db
from flask_login import UserMixin


class TipoUsuario(db.Model):
    __tablename__ = 'tipos_usuarios'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(30), unique=True, nullable=False)
    descricao = db.Column(db.String(100),nullable=False)

    usuarios = db.relationship('Usuario', backref='tipo_usuario', lazy=True, cascade='all, delete-orphan')

    # def __init__(self, nome, descricao):  
    #     self.nome = nome
    #     self.descricao = descricao

    def __repr__(self):
        return f'{self.nome}'



class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(50),nullable=False)
    telefone = db.Column(db.String(20),nullable=False)
    email = db.Column(db.String(50), unique=True,nullable=False)
    senha = db.Column(db.String(),nullable=False)
    ativo = db.Column(db.Boolean, default=True)

    ensina_turmas = db.relationship("Turma", secondary="ensinam", back_populates='ensina_usuarios')
    id_tipo_usuario = db.Column(db.Integer, db.ForeignKey('tipos_usuarios.id'), nullable=False)

    def __repr__(self):
        return f'{self.email}'
    
class Comportamento(db.Model):
    __tablename__ = 'comportamentos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(50),nullable=False)
    descricao = db.Column(db.String(50))
    pontos = db.Column(db.Integer, default = 0)
    ativo = db.Column(db.Boolean, default = True)

    def __repr__(self):
        return f'{self.nome}'

class Missao(db.Model):
    __tablename__ = 'missoes'

    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    nome = db.Column(db.String(30), nullable= False)
    descricao = db.Column(db.String(100))
    pontos = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'{self.nome}'

class Turma(db.Model):
    __tablename__ = 'turmas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    grau = db.Column(db.String(1))
    serie = db.Column(db.String(1))
    periodo = db.Column(db.String(10))
    ano = db.Column(db.Integer())

    equipes = db.relationship('Equipe', backref='turma', lazy=True, cascade='all, delete-orphan')
    torneios = db.relationship('Torneio', backref='turma', lazy=True, cascade='all, delete-orphan')

    ensina_usuarios = db.relationship('Usuario', secondary="ensinam", back_populates="ensina_turmas")

    def __init__(self, grau, serie, periodo, ano):
        self.grau = grau
        self.serie = serie
        self.periodo = periodo
        self.ano = ano


    def __repr__(self):
        return f'Turma: {self.grau}{self.serie} período: {self.periodo} ano: {self.ano}'

class Torneio(db.Model):
    __tablename__ = 'torneios'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # nome = db.Column(db.String(30))
    bimestre = db.Column(db.String(2))
    premiacao = db.Column(db.String(100))
    data_criacao = db.Column(db.Date)
    data_hora = db.Column(db.Time)

    disputa_equipes = db.relationship("Equipe", secondary="disputam",back_populates="disputa_torneios")
    id_turma = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=False)

    def __repr__(self):
        return f'Torneio do {self.bimestre} bimestre, premiação {self.premiacao}'

class Equipe(db.Model):
    __tablename__ = 'equipes'

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    nome = db.Column(db.String(30))
    lider = db.Column(db.String(30))

    disputa_torneios = db.relationship('Torneio', secondary="disputam", back_populates="disputa_equipes")

    id_turma = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=False)

    def __repr__(self):
        return f'Equipe: {self.nome}'

# class Disciplina(db.Model):
#     __tablename__ = 'disciplinas'

#     id = db.Column(db.Integer, primary_key=True)
#     nome = db.Column(db.String(30))

#     def __repr__(self):
#         return f'Disciplina {self.nome}'


class Equipe_Comportamento(db.Model):
    __tablename__ = 'equipes_comportamentos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    id_equipe = db.Column(db.Integer, db.ForeignKey('equipes.id'))
    id_comportamento = db.Column(db.Integer, db.ForeignKey('comportamentos.id'))

    data_criacao = db.Column(db.String(10))
    data_hora = db.Column(db.String(8))

    equipe = db.relationship('Equipe', backref=db.backref('equipe_comportamentos', lazy='dynamic'))
    comportamento = db.relationship('Comportamento', backref=db.backref('comportamento_equipes', lazy='dynamic'))

    def __repr__(self):
        return f'Equipe {self.equipe.nome} - Comportamento {self.comportamento.nome}'

class Equipe_Missao(db.Model):
    __tablename__ = 'equipes_missoes'

    id_equipe = db.Column(db.Integer, db.ForeignKey('equipes.id'), primary_key=True)
    id_missao = db.Column(db.Integer, db.ForeignKey('missoes.id'), primary_key=True)

    data_criacao = db.Column(db.String(10))
    data_hora = db.Column(db.String(8))

    concluida = db.Column(db.Boolean, default = False)

    equipe = db.relationship('Equipe', backref=db.backref('equipe_missoes', lazy='dynamic'))
    missao = db.relationship('Missao', backref=db.backref('missao_equipes', lazy='dynamic'))

    def __repr__(self):
        return f'{self.equipe} Missão: {self.missao} - Concluída: {self.concluida}'

ensina = db.Table('ensinam',
    db.Column('id_usuario', db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), primary_key=True),
    db.Column('id_turma', db.Integer, db.ForeignKey('turmas.id', ondelete='CASCADE'), primary_key=True)
    # db.Column('id_disciplina', db.Integer, db.ForeignKey('disciplinas.id'), primary_key=True)
)

disputa = db.Table('disputam',
    db.Column('id_equipe', db.Integer, db.ForeignKey('equipes.id', ondelete='CASCADE'), primary_key=True),
    db.Column('id_torneio', db.Integer, db.ForeignKey('torneios.id', ondelete='CASCADE'), primary_key=True)
)

