"""
============================================================
produtos.py
Módulo responsável pelo cadastro de novos produtos no sistema.
Faz validações e adiciona os produtos à lista global.
============================================================
"""

from datetime import datetime, date
from models import Produto
from data import lista_produtos


def cadastro_produto():
    """Reúne as informações necessárias e cadastra um novo produto no sistema."""
    print("CADASTRO DE NOVO PRODUTO!")
    nome = input("Digite o nome do produto: ").strip()
    preco = float(input("Digite o preço: "))
    qtd = int(input("Digite a quantidade: "))
    validade_obj = datetime.strptime(
        input("Digite a validade (dd/mm/aaaa): "), "%d/%m/%Y"
    ).date()

    if validade_obj < date.today():
        print("Produto vencido, não cadastrado!")
        return

    novo = Produto(nome, preco, qtd, validade_obj)
    lista_produtos.append(novo)
    print(f"Produto '{nome}' cadastrado com sucesso!")


"""Final do módulo"""
