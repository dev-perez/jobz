import hashlib
import json
import re
from app import Empresas, Vagas, Usuarios

from validate_docbr import CNPJ


def criptografa_senha(senha):
    return (hashlib.md5(senha.encode())).hexdigest()


def empresa_valida(empresa):
    result = ""
    if cnpj_existe(empresa.cnpj):
        result = json.dumps(
            {"Error": "Já existe uma empresa criada com este CNPJ."})
    if email_empresa_existe(empresa.email):
        result = json.dumps(
            {"Error": "Já existe uma empresa criada com este email."})

    cnpj = CNPJ()
    if not cnpj.validate(empresa.cnpj):
        result = json.dumps({"Erro": "CNPJ inválido."})

    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(email_regex, empresa.email):
        result = json.dumps({"Error": "E-mail inválido"})

    if result == "":
        return True
    else:
        return result


def cnpj_existe(cnpj):
    if Empresas.query.filter_by(cnpj=cnpj).first() != None:
        return True
    else:
        return False


def email_empresa_existe(email):
    if Empresas.query.filter_by(email=email).first() != None:
        return True
    else:
        return False


def nome_empresa(id):
    return Empresas.query.get(id).nome


def parse_vagas(vagas):
    response = []
    for vaga in vagas:
        response.append({
            "cargo": vaga.cargo,
            "empresa": nome_empresa(vaga.id_empresa),
            "tipo_contrato": vaga.tipo_contrato,
            "senioridade": vaga.senioridade,
            "qtd_vagas": vaga.qtd_vagas,
            "descricao": vaga.descricao
        })
    return response


def parse_candidaturas(candidaturas):
    response = []
    for c in candidaturas:
        vaga = Vagas.query.get(c.id_vaga)
        usuario = Usuarios.query.get(c.id_usuario)
        response.append({
            "nome_vaga": vaga.cargo,
            "senioridade_vaga": vaga.senioridade,
            "nome_candidato": usuario.nome,
            "data_inscricao": c.data_inscricao.strftime("%d/%m/%Y,  %H:%M:%S")
        })

    return response
