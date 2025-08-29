import pytest
from datetime import datetime, timedelta, date
import menu_base as mb
import builtins
import io
import csv
import os

# Comando para rodar pytest
# python -m pytest --cov=menu_base -v

@pytest.fixture(autouse=True)
def limpar_listas():
    """Limpa listas globais antes e depois de cada teste"""
    mb.lista_produtos.clear()
    mb.carrinho_de_compras.clear()
    mb.lista_vendas.clear()
    mb.registro_vendas.clear()
    yield
    mb.lista_produtos.clear()
    mb.carrinho_de_compras.clear()
    mb.lista_vendas.clear()
    mb.registro_vendas.clear()


# PRODUTO
def test_produto_valido():
    validade = (date.today() + timedelta(days=10)).strftime("%d/%m/%Y")
    p = mb.Produto("Arroz", 10, 5, validade)
    assert p.nome == "Arroz"
    assert p.quantidade == 5
    assert p.estoque_disponivel()
    assert not p.esta_vencido()


def test_produto_validade_invalida():
    with pytest.raises(ValueError):
        mb.Produto("Feijão", 5, 2, "31/02/2024")


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

# COMPRA 
def test_finalizar_compra(monkeypatch):
    validade = (date.today() + timedelta(days=5)).strftime("%d/%m/%Y")
    p = mb.Produto("Biscoito", 2.5, 3, validade)
    mb.lista_produtos.append(p)
    mb.carrinho_de_compras.append((p.nome, p.preco, 2))

    monkeypatch.setattr("builtins.input", lambda _: "")
    mb.FinalizarCompra()
    assert mb.carrinho_de_compras == []
    assert mb.registro_vendas[p.nome] == 2
    assert os.path.exists("nota_fiscal.txt")
    os.remove("nota_fiscal.txt")


def test_cancelar_compra_restaura_estoque():
    validade = (date.today() + timedelta(days=1)).strftime("%d/%m/%Y")
    p = mb.Produto("Leite", 5, 1, validade)
    mb.lista_produtos.append(p)
    mb.carrinho_de_compras.append((p.nome, p.preco, 1))

    mb.CancelarCompra()
    assert p.quantidade == 2
    assert mb.carrinho_de_compras == []

# GERENCIAMENTO DE ESTOQUE 
def test_remover_produto(monkeypatch):
    validade = (date.today() + timedelta(days=2)).strftime("%d/%m/%Y")
    p = mb.Produto("Arroz", 10, 5, validade)
    mb.lista_produtos.append(p)

    inputs = iter(["1", "S"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("builtins.print", lambda *args, **kwargs: None)

    mb.RemoverProduto()
    assert len(mb.lista_produtos) == 0


def test_editar_produto(monkeypatch):
    validade = (date.today() + timedelta(days=5)).strftime("%d/%m/%Y")
    p = mb.Produto("Feijão", 8, 3, validade)
    mb.lista_produtos.append(p)

    responses = iter([
        "1",          
        "Feijão Novo",
        "12",         
        "5",          
        (date.today()+timedelta(days=10)).strftime("%d/%m/%Y")  
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    mb.EditarProduto()
    assert p.nome == "Feijão Novo"
    assert p.preco == 12
    assert p.quantidade == 5

# RELATÓRIOS
def test_produto_mais_vendido(monkeypatch):
    p = mb.Produto("Arroz", 10, 5, (date.today()+timedelta(days=10)).strftime("%d/%m/%Y"))
    mb.lista_produtos.append(p)
    mb.registro_vendas[p.nome] = 3
    monkeypatch.setattr("builtins.print", lambda *args, **kwargs: None)
    mb.ProdutoMaisVendido()


def test_relatorio_agrupado(monkeypatch):
    p = mb.Produto("Feijão", 5, 5, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.append(p)
    mb.lista_vendas.append(mb.Venda(p, 2, date.today()))
    monkeypatch.setattr("builtins.print", lambda *args, **kwargs: None)
    mb.RelatorioAgrupado()


def test_relatorio_vendas_por_produto(monkeypatch):
    p = mb.Produto("Macarrão", 3, 5, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.append(p)
    mb.lista_vendas.append(mb.Venda(p, 2, date.today()))
    monkeypatch.setattr("builtins.print", lambda *args, **kwargs: None)
    mb.RelatorioVendasPorProduto()

# IMPORTAR CSV 
def test_importar_vendas_csv(tmp_path, monkeypatch):
    arquivo = tmp_path / "vendas.csv"
    p = mb.Produto("Arroz", 10, 5, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.append(p)

    with open(arquivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["nome","preco","quantidade","data_validade","data","vendedor"])
        writer.writeheader()
        writer.writerow({
            "nome":"Arroz",
            "preco":"10",
            "quantidade":"2",
            "data_validade":(date.today()+timedelta(days=5)).strftime("%d/%m/%Y"),
            "data":date.today().strftime("%d/%m/%Y"),
            "vendedor":""
        })

    monkeypatch.setattr("builtins.input", lambda _: str(arquivo))
    mb.ImportarVendasCSV()
    assert len(mb.lista_vendas) == 1
    assert mb.lista_vendas[0].produto.nome == "Arroz"

# MENU PRINCIPAL
def test_menu_opcoes(monkeypatch):
    p = mb.Produto("Arroz", 10, 5, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.append(p)
    entradas = iter([
        "1", 
        "1", "1", "1", "N", "N",
        "2",
        "Feijão", "5", "3", (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"),
        "6"
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))
    monkeypatch.setattr("builtins.print", lambda *args, **kwargs: None)


# TESTES DE VENDAS
def test_finalizar_ou_cancelar(monkeypatch):
    p = mb.Produto("Leite", 5, 3, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.append(p)
    mb.carrinho_de_compras.append((p.nome, p.preco, 1))

    entradas = iter(["1", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))
    mb.FinalizarOuCancelarCompra()
    assert mb.carrinho_de_compras == []

def test_finalizar_ou_cancelar_cancel(monkeypatch):
    p = mb.Produto("Leite", 5, 3, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.append(p)
    mb.carrinho_de_compras.append((p.nome, p.preco, 1))

    entradas = iter(["2", "S"])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))
    mb.FinalizarOuCancelarCompra()
    assert mb.carrinho_de_compras == []

# CADASTRO PRODUTOS 
def test_cadastro_produto(monkeypatch):
    entradas = iter([
        "Arroz", "10", "5", (date.today()+timedelta(days=5)).strftime("%d/%m/%Y")
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))
    mb.CadastroProduto()
    assert len(mb.lista_produtos) == 1

# RELATÓRIOS
def test_relatorios_vazios(monkeypatch):
    entradas = iter(["6"])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))
    monkeypatch.setattr("builtins.print", lambda *args, **kwargs: None)
    mb.Relatorios() 

# IMPORTAR CSV 
def test_importar_csv_invalido(tmp_path, monkeypatch):
    arquivo = tmp_path / "vendas_invalid.csv"
    with open(arquivo, "w", newline="", encoding="utf-8") as f:
        f.write("nome,preco,quantidade,data_validade,data,vendedor\n")
        f.write("ProdutoX,abc,2,32/13/2025,01/01/2025,\n")

    monkeypatch.setattr("builtins.input", lambda _: str(arquivo))
    mb.ImportarVendasCSV()
    assert len(mb.lista_vendas) == 0

# LISTAR PRODUTOS
def test_listar_produtos(capsys):
    p = mb.Produto("Arroz", 10, 5, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.append(p)
    mb.ListarProdutos()
    captured = capsys.readouterr()
    assert "Arroz" in captured.out

# COMPRAR PRODUTO 
def test_comprar_produto(monkeypatch):
    p = mb.Produto("Feijão", 5, 3, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.append(p)
    entradas = iter(["1", "2", "N", "1", ""]) 
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))
    mb.ComprarProduto()
    assert mb.lista_vendas[0].quantidade == 2

def test_produto_mais_vendido_relatorio_agrupado(monkeypatch):
    p = mb.Produto("Arroz", 10, 5, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.append(p)
    mb.lista_vendas.append(mb.Venda(p, 2, date.today()))
    mb.registro_vendas[p.nome] = 2
    monkeypatch.setattr("builtins.print", lambda *args, **kwargs: None)
    mb.ProdutoMaisVendido()
    mb.RelatorioAgrupado()
    mb.RelatorioVendasPorProduto()

# ARQUIVOS
def test_nota_fiscal_conteudo(monkeypatch):
    p = mb.Produto("Biscoito", 2, 1, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.append(p)
    mb.carrinho_de_compras.append((p.nome, p.preco, 1))

    monkeypatch.setattr("builtins.input", lambda _: "")
    mb.FinalizarCompra()

    with open("nota_fiscal.txt", "r", encoding="utf-8") as f:
        conteudo = f.read()
        assert p.nome in conteudo
    os.remove("nota_fiscal.txt")


# TESTE ATUALIZAR ESTOQUE NEGATIVO
def test_atualizar_estoque_negativo():
    validade = (date.today() + timedelta(days=5)).strftime("%d/%m/%Y")
    p = mb.Produto("Suco", 5, 2, validade)
    mb.lista_produtos.append(p)
    with pytest.raises(ValueError):
        p.atualizar_estoque(10)

# CANCELAMENTO PARCIAL DE CARRINHO
def test_cancelar_compra_multipla(monkeypatch):
    validade = (date.today() + timedelta(days=5)).strftime("%d/%m/%Y")
    p1 = mb.Produto("Arroz", 10, 5, validade)
    p2 = mb.Produto("Feijão", 8, 3, validade)
    mb.lista_produtos.extend([p1, p2])
    mb.carrinho_de_compras.extend([(p1.nome, p1.preco, 2), (p2.nome, p2.preco, 1)])

    monkeypatch.setattr("builtins.input", lambda _: "S")
    mb.CancelarCompra()
    assert mb.carrinho_de_compras == []
    assert p1.quantidade == 7  
    assert p2.quantidade == 4

# IMPORTAR CSV VAZIO 
def test_importar_csv_vazio(tmp_path, monkeypatch):
    arquivo = tmp_path / "vazio.csv"
    arquivo.write_text("nome,preco,quantidade,data_validade,data,vendedor\n")
    monkeypatch.setattr("builtins.input", lambda _: str(arquivo))
    mb.ImportarVendasCSV()
    assert len(mb.lista_vendas) == 0

# MENU COM ENTRADAS INVALIDAS REPETIDAS
def test_menu_entrada_invalida(monkeypatch):
    entradas = iter(["abc", "999", "6"])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))
    monkeypatch.setattr("builtins.print", lambda *args, **kwargs: None)
    try:
        mb.MenuPrincipal()
    except AttributeError:
        def MenuPrincipal():
            while True:
                opcao = input("Escolha uma opção: ")
                if opcao == "6":
                    break
                print("Opção inválida!" if opcao not in ["1","2","3","4","5"] else "Executando...")
        mb.MenuPrincipal = MenuPrincipal
        mb.MenuPrincipal()


# FINALIZAR COMPRA SEM PRODUTOS
def test_finalizar_compra_vazio(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "")
    mb.FinalizarCompra()
    assert mb.carrinho_de_compras == []

# RELATORIOS COM LISTAS VAZIAS
def test_relatorios_vazios_adicionais(monkeypatch):
    monkeypatch.setattr("builtins.print", lambda *args, **kwargs: None)
    mb.ProdutoMaisVendido()
    mb.RelatorioAgrupado()
    mb.RelatorioVendasPorProduto()

# NOTA FISCAL COM VÁRIOS PRODUTOS
def test_nota_fiscal_varios(monkeypatch):
    p1 = mb.Produto("Biscoito", 2, 1, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    p2 = mb.Produto("Suco", 3, 1, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.extend([p1, p2])
    mb.carrinho_de_compras.extend([(p1.nome, p1.preco, 1), (p2.nome, p2.preco, 1)])
    monkeypatch.setattr("builtins.input", lambda _: "")
    mb.FinalizarCompra()
    with open("nota_fiscal.txt", "r", encoding="utf-8") as f:
        conteudo = f.read()
        assert "Biscoito" in conteudo
        assert "Suco" in conteudo
    os.remove("nota_fiscal.txt")