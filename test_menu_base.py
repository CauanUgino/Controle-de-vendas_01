import pytest
from datetime import datetime, timedelta, date
import menu_base as mb
import builtins
import io
import csv
import os

@pytest.fixture(autouse=True)
def limpar_listas():
    """Limpa listas globais antes de cada teste"""
    mb.lista_produtos.clear()
    mb.carrinho_de_compras.clear()
    mb.lista_vendas.clear()
    mb.registro_vendas.clear()
    yield
    mb.lista_produtos.clear()
    mb.carrinho_de_compras.clear()
    mb.lista_vendas.clear()
    mb.registro_vendas.clear()


# ------------------------- PRODUTO -------------------------
def test_produto_valido():
    validade = (date.today() + timedelta(days=10)).strftime("%d/%m/%Y")
    p = mb.Produto("Arroz", 10, 5, validade)
    assert p.nome == "Arroz"
    assert p.quantidade == 5
    assert p.estoque_disponivel()
    assert not p.esta_vencido()


def test_produto_validade_invalida():
    with pytest.raises(ValueError):
        mb.Produto("Feijão", 5, 2, "31/02/2024")  # data inválida


def test_atualizar_estoque():
    validade = (date.today() + timedelta(days=1)).strftime("%d/%m/%Y")
    p = mb.Produto("Macarrão", 5, 10, validade)
    mb.lista_produtos.append(p)
    p.atualizar_estoque(5)
    assert p.quantidade == 5


def test_atualizar_estoque_excede():
    validade = (date.today() + timedelta(days=1)).strftime("%d/%m/%Y")
    p = mb.Produto("Suco", 5, 3, validade)
    mb.lista_produtos.append(p)
    with pytest.raises(ValueError):
        p.atualizar_estoque(10)

