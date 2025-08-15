from db import db
from models import *

# Inserir dados na tabela associativa disputas

def nova_disputa(equipe, torneio):
    disputa = disputa.insert().values(
        id_equipe=equipe,  # ID do professor
        id_torneio=torneio  # ID da disciplina
    )

    db.session.execute(disputa)
    db.session.commit()

def consultar_disputas():
    disputas = db.session.execute(db.select(disputa)).all()
    return disputas

def novo_ensino(professor, turma):
    ensino = ensina.insert().values(
        id_usuario=professor,  # ID do professor
        id_turma=turma  # ID da disciplina
    )
    db.session.execute(ensino)
    db.session.commit()


def consultar_ensino():
    ensinam = db.session.execute(db.select(ensina)).all()
    return ensinam

lista_equipes = ('Hashtag', 'Underline', 'Web', 'Share', 'Byte')