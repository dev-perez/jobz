from distutils.log import debug
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import json

from helpers import *

app = Flask(__name__)

app.config.from_pyfile("config.py")
db = SQLAlchemy(app)

db.create_all()


class Empresas(db.Model):
    __tablename__ = "empresas"

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    nome = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    cnpj = db.Column(db.String(14), unique=True, nullable=False)
    senha = db.Column(db.String(32), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    cidade = db.Column(db.String(30), nullable=False)
    site = db.Column(db.String(30), nullable=False)
    telefone = db.Column(db.String(11), nullable=False)

    def get_id(self):
        return str(self.id)

    def __init__(self, nome, email, cnpj, senha, estado,
                 cidade, site, telefone):
        self.nome = nome
        self.email = email
        self.cnpj = cnpj
        self.senha = senha
        self.estado = estado
        self.cidade = cidade
        self.site = site
        self.telefone = telefone


class Usuarios(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    nome = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    senha = db.Column(db.String(32), nullable=False)
    linkedin = db.Column(db.String(30), nullable=False)
    telefone = db.Column(db.String(11), nullable=False)

    def get_id(self):
        return str(self.id)

    def __init__(self, nome, email, cpf, senha, linkedin, telefone):
        self.nome = nome
        self.email = email
        self.cpf = cpf
        self.senha = senha
        self.linkedin = linkedin
        self.telefone = telefone


class Vagas(db.Model):
    __tablename__ = "vagas"

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    cargo = db.Column(db.String(30), nullable=False)
    id_empresa = db.Column(db.Integer, db.ForeignKey('empresas.id'))
    tipo_contrato = db.Column(db.String(3), nullable=False)
    senioridade = db.Column(db.String(30), nullable=False)
    qtd_vagas = db.Column(db.SmallInteger, nullable=False)
    descricao = db.Column(db.Text, nullable=False)

    def get_id(self):
        return str(self.id)

    def __init__(self, cargo, id_empresa, tipo_contrato, senioridade, qtd_vagas, descricao):
        self.cargo = cargo
        self.id_empresa = id_empresa
        self.tipo_contrato = tipo_contrato
        self.senioridade = senioridade
        self.qtd_vagas = qtd_vagas
        self.descricao = descricao


class Candidaturas(db.Model):
    __tablename__ = "candidaturas"

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    id_vaga = db.Column(db.Integer, db.ForeignKey('vagas.id'))
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    data_inscricao = db.Column(db.DateTime(
        timezone=True), server_default=func.now())

    def get_id(self):
        return str(self.id)

    def __init__(self, id_vaga, id_usuario):
        self.id_vaga = id_vaga
        self.id_usuario = id_usuario


@app.route("/empresa/cadastro", methods=["POST"])
def cadastro_empresa():
    try:
        nome = request.json['nome']
        email = request.json['email']
        cnpj = request.json['cnpj']
        senha = criptografa_senha(request.json['senha'])
        estado = request.json['estado']
        cidade = request.json['cidade']
        site = request.json['site']
        telefone = request.json['telefone']

        empresa = Empresas(nome, email, cnpj, senha,
                           estado, cidade, site, telefone)

        valida = empresa_valida(empresa)
        if valida != True:
            return valida

        db.session.add(empresa)
        db.session.commit()
        print(empresa)
        return json.dumps({"Ok": "Empresa criada com sucesso"})
    except Exception as e:
        db.session.rollback()
        return json.dumps({"Error": str(e)})


@app.route("/empresa/<int:id>", methods=["GET"])
def get_empresa(id):
    empresa = Empresas.query.get(id)
    if empresa == None:
        return json.dumps({"Error": "404 - Empresa não encontrada"})
    return json.dumps(
        {
            "nome": empresa.nome,
            "email": empresa.email,
            "cnpj": empresa.cnpj,
            "estado": empresa.estado,
            "cidade": empresa.cidade,
            "site": empresa.site,
            "telefone": empresa.telefone
        }
    )


@app.route("/empresa/criar-vaga", methods=["POST"])
def cadastro_vaga():
    try:
        cargo = request.json['cargo']
        id_empresa = request.json['id_empresa']
        tipo_contrato = request.json['tipo_contrato']
        senioridade = request.json['senioridade']
        qtd_vagas = request.json['qtd_vagas']
        descricao = request.json['descricao']

        if Empresas.query.get(id_empresa) == None:
            return json.dumps({"Error": "Empresa inválida"})

        vaga = Vagas(cargo, id_empresa, tipo_contrato,
                     senioridade, qtd_vagas, descricao)

        db.session.add(vaga)
        db.session.commit()
        return json.dumps({"Ok": "Vaga cadastrada com sucesso"})
    except Exception as e:
        db.session.rollback()
        return json.dumps({"Error": str(e)})


@app.route("/empresa/<int:id>/vagas", methods=["GET"])
def get_vagas_empresa(id):
    vagas = Vagas.query.filter_by(id_empresa=id).all()
    print(vagas)

    if vagas == []:
        return json.dumps({"Info": "Nenhuma vaga encontrada para esta empresa"})

    parsed_vagas = parse_vagas(vagas)

    return json.dumps(parsed_vagas)


@app.route("/vagas", methods=["GET"])
def get_vagas():
    vagas = Vagas.query.all()
    parsed_vagas = parse_vagas(vagas)
    return json.dumps(parsed_vagas)


@app.route("/vagas/editar", methods=["PUT"])
def edita_vaga():
    try:
        id = request.json["id"]
        vaga = Vagas.query.get(id)
        if vaga == None:
            return json.dumps({"Error": "Vaga não encontrada"})

        print(vaga)

        if vaga.id_empresa != request.json.get("id_empresa"):
            return json.dumps({"Error": "Não autorizado"})

        vaga.cargo = request.json.get("cargo") or vaga.cargo
        vaga.tipo_contrato = request.json.get(
            "tipo_contrato") or vaga.tipo_contrato
        vaga.senioridade = request.json.get("senioridade") or vaga.senioridade
        vaga.qtd_vagas = request.json.get("qtd_vagas") or vaga.qtd_vagas
        vaga.descricao = request.json.get("descricao") or vaga.descricao

        db.session.commit()

        return json.dumps({"info": "Vaga atualizada com sucesso"})
    except Exception as e:
        db.session.rollback()
        return json.dumps({"Error": str(e)})


@app.route("/usuario/cadastro", methods=["POST"])
def cadastro_usuario():
    try:
        nome = request.json['nome']
        email = request.json['email']
        cpf = request.json['cpf']
        senha = criptografa_senha(request.json['senha'])
        linkedin = request.json['linkedin']
        telefone = request.json['telefone']

        usuario = Usuarios(nome, email, cpf, senha, linkedin, telefone)

        db.session.add(usuario)
        db.session.commit()
        return json.dumps({"Ok": "Usuário criada com sucesso"})
    except Exception as e:
        db.session.rollback()
        return json.dumps({"Error": str(e)})


@app.route("/usuario/<int:id>", methods=["GET"])
def get_usuario(id):
    try:
        usuario = Usuarios.query.get(id)
        if not usuario:
            return json.dumps({"Info": "Usuário não encontrado"})

        return json.dumps(
            {
                "nome": usuario.nome,
                "email": usuario.email,
                "cpf": usuario.cpf,
                "linkedin": usuario.linkedin,
                "telefone": usuario.telefone
            })

    except Exception as e:
        db.session.rollback()
        return json.dumps({"Error": str(e)})


@app.route("/usuario/<int:id>/candidaturas", methods=["GET"])
def get_usuario_candidaturas(id):
    try:
        candidaturas = Candidaturas.query.filter_by(id_usuario=id).all()
        if candidaturas == []:
            return json.dumps({"Info": "Nenhuma candidatura encontrada"})

        return json.dumps(parse_candidaturas(candidaturas))

    except Exception as e:
        db.session.rollback()
        return json.dumps({"Error": str(e)})


@app.route("/usuario/aplicar", methods=["POST"])
def aplicar_vaga():
    try:
        id_vaga = request.json['id_vaga']
        id_usuario = request.json['id_usuario']

        if Vagas.query.get(id_vaga) == None:
            return json.dumps({"Error": "Vaga inválida"})

        if Usuarios.query.get(id_usuario) == None:
            return json.dumps({"Error": "Usuário inválido"})

        candidatura = Candidaturas(id_vaga, id_usuario)

        db.session.add(candidatura)
        db.session.commit()
        return json.dumps({"Ok": "Inscrição realizada com sucesso"})
    except Exception as e:
        db.session.rollback()
        return json.dumps({"Error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
