# coding: utf8
from cmath import nan
import sys
import os
from coleta import coleta_pb2 as Coleta

CONTRACHEQUE_2018 = "contracheque"
CONTRACHEQUE_2019_DEPOIS = "contracheque1"
INDENIZACOES = "indenizações"

HEADERS = {
    CONTRACHEQUE_2018: {
        "Remuneração do Cargo Efetivo": 3,
        "Outras Verbas Remuneratórias, Legais ou Judiciais": 4,
        "Função de Confiança ou Cargo em Comissão": 5,
        "Gratificação Natalina": 6,
        "Férias (1/3 constitucional)": 7,
        "Abono de Permanência": 8,
        "Contribuição Previdenciária": 10,
        "Imposto de Renda": 11,
        "Retenção por Teto Constitucional": 12,
        "Verbas Indenizações": 15,
        "Outras Remunerações Retroativas / Temporárias": 16,
    },
    CONTRACHEQUE_2019_DEPOIS: {
        "Remuneração do Cargo Efetivo": 3,
        "Outras Verbas Remuneratórias, Legais ou Judiciais": 4,
        "Função de Confiança ou Cargo em Comissão": 5,
        "Gratificação Natalina": 6,
        "Férias (1/3 constitucional)": 7,
        "Abono de Permanência": 8,
        "Contribuição Previdenciária": 10,
        "Imposto de Renda": 11,
        "Retenção por Teto Constitucional": 12,
        "Outras Remunerações Temporárias": 14,
    },
    INDENIZACOES: {
        "Auxílio-Saúde": 4,
        "Auxílio-Doença": 5,
        "Auxílio-Moradia": 6,
        "Auxílio-Alimentação": 7,
        "Lincença Prêmio": 8,
        "Indenização de Férias": 9,
        "Abono Pecuniário": 10,
        "Recesso Administrativo": 11,
        "Diferença Indenizada": 12,
        "Plantão Indenizado": 13,
        "Substituição": 15,
        "Hora Extra": 16,
        "Plantão": 17,
        "Diferença de Recebimentos": 18,
        "Cumulação": 19,
        "Devoluções de Descontos": 20,
        "Gratificações": 21,
    },
}


def parse_employees(fn, chave_coleta, mes, ano):
    employees = {}
    counter = 1
    forbidden_words = ["Ministério", "Remuneração", "Fonte", "ANO", "GRUPO", "NOME"]
    for row in fn:
        print(row)
        for word in forbidden_words:
            if word in row[0]:
                name = nan
                break
            else:
                name = row[0]
        funcao = row[1]
        local_trabalho = row[2]
        if not is_nan(name):
            membro = Coleta.ContraCheque()
            membro.id_contra_cheque = chave_coleta + "/" + str(counter)
            membro.chave_coleta = chave_coleta
            membro.nome = str(name)
            membro.funcao = funcao
            membro.local_trabalho = local_trabalho
            membro.tipo = Coleta.ContraCheque.Tipo.Value("MEMBRO")
            membro.ativo = True
            if int(ano) == 2018 or (int(ano) == 2019 and int(mes) < 7):
                membro.remuneracoes.CopyFrom(cria_remuneracao(row, CONTRACHEQUE_2018))
            else:
                membro.remuneracoes.CopyFrom(
                    cria_remuneracao(row, CONTRACHEQUE_2019_DEPOIS)
                )
            employees[name] = membro
            counter += 1
    return employees


def cria_remuneracao(row, categoria):
    remu_array = Coleta.Remuneracoes()
    items = list(HEADERS[categoria].items())
    for i in range(len(items)):
        key, value = items[i][0], items[i][1]
        remuneracao = Coleta.Remuneracao()
        remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("R")
        if categoria == INDENIZACOES:
            remuneracao.categoria = categoria
        else:
            remuneracao.categoria = "contracheque"
        remuneracao.item = key
        remuneracao.valor = format_value(row[value])
        if categoria == CONTRACHEQUE_2018:
            if value == 3:
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("B")
            elif value in [10, 11, 12]:
                remuneracao.valor = remuneracao.valor * (-1)
                remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("D")
            elif value in [4, 5, 6, 7, 8, 15, 16]:
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
        elif categoria == CONTRACHEQUE_2019_DEPOIS:
            if value == 3:
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("B")
            elif value in [10, 11, 12]:
                remuneracao.valor = remuneracao.valor * (-1)
                remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("D")
            elif value in [4, 5, 6, 7, 8, 14]:
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
        else:
            remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")

        remu_array.remuneracao.append(remuneracao)
    return remu_array


def update_employees(fn, employees, categoria):
    for row in fn:
        name = str(row[1]).rstrip()
        if name in employees.keys():
            emp = employees[name]
            remu = cria_remuneracao(row, categoria)
            emp.remuneracoes.MergeFrom(remu)
            employees[name] = emp
    return employees


def is_nan(string):
    return string != string


def parse(data, chave_coleta, mes, ano):
    employees = {}
    folha = Coleta.FolhaDePagamento()
    if int(ano) == 2018 or (int(ano) == 2019 and int(mes) < 7):
        try:
            employees.update(parse_employees(data.contracheque, chave_coleta, mes, ano))

        except KeyError as e:
            sys.stderr.write(
                "Registro inválido ao processar contracheque: {}".format(e)
            )
            os._exit(1)
    else:
        try:
            employees.update(parse_employees(data.contracheque, chave_coleta, mes, ano))
            update_employees(data.indenizatorias, employees, INDENIZACOES)

        except KeyError as e:
            sys.stderr.write(
                "Registro inválido ao processar contracheque ou indenizações: {}".format(
                    e
                )
            )
            os._exit(1)
    for i in employees.values():
        folha.contra_cheque.append(i)
    return folha


def format_value(element):
    # A value was found with incorrect formatting. (3,045.99 instead of 3045.99)
    if is_nan(element):
        return 0.0
    if type(element) == str:
        if "." in element and "," in element:
            element = element.replace(".", "").replace(",", ".")
        elif "," in element:
            element = element.replace(",", ".")
        elif "-" in element:
            element = 0.0

    return float(element)