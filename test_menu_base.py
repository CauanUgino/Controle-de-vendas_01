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
