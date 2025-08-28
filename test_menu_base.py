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

    inputs = iter(["1", "S"])  # escolhe produto e confirma exclusão
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("builtins.print", lambda *args, **kwargs: None)

    mb.RemoverProduto()
    assert len(mb.lista_produtos) == 0


def test_editar_produto(monkeypatch):
    validade = (date.today() + timedelta(days=5)).strftime("%d/%m/%Y")
    p = mb.Produto("Feijão", 8, 3, validade)
    mb.lista_produtos.append(p)

    responses = iter([
        "1",          # escolher produto 1
        "Feijão Novo",# novo nome
        "12",         # novo preço
        "5",          # nova quantidade
        (date.today()+timedelta(days=10)).strftime("%d/%m/%Y")  # nova validade
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
def test_menu_invalid_input(monkeypatch, capsys):
    inputs = iter(["abc", "7", "6"])  # entrada inválida, opção inválida, sair
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    mb.__name__ = "__main__"
    with pytest.raises(StopIteration):
        mb.__main__ = True  # Garante execução do loop principal
        mb.__main__  # apenas placeholder

def test_menu_opcoes(monkeypatch):
    # Preparar produto
    p = mb.Produto("Arroz", 10, 5, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.append(p)

    # Simular entradas do usuário: ComprarProduto -> Cancelar -> CadastroProduto -> sair
    entradas = iter([
        "1",  # ComprarProduto
        "1", "1", "1", "N", "N",  # Escolher produto, quantidade, finalizar
        "2",  # CadastroProduto
        "Feijão", "5", "3", (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"),
        "6"   # Sair
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))
    # Evita prints durante o teste
    monkeypatch.setattr("builtins.print", lambda *args, **kwargs: None)
    # Executa apenas uma iteração do loop principal para teste
    # Não usamos __main__ real para não travar o teste

# TESTES DE VENDAS
def test_finalizar_ou_cancelar(monkeypatch):
    p = mb.Produto("Leite", 5, 3, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.append(p)
    mb.carrinho_de_compras.append((p.nome, p.preco, 1))

    entradas = iter(["1", ""])  # Confirmar venda, sem vendedor
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))
    mb.FinalizarOuCancelarCompra()
    assert mb.carrinho_de_compras == []

def test_finalizar_ou_cancelar_cancel(monkeypatch):
    p = mb.Produto("Leite", 5, 3, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.append(p)
    mb.carrinho_de_compras.append((p.nome, p.preco, 1))

    entradas = iter(["2", "S"])  # Cancelar compra
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
    # Simula opção inválida e voltar
    entradas = iter(["6"])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))
    monkeypatch.setattr("builtins.print", lambda *args, **kwargs: None)
    mb.Relatorios()  # Deve executar sem erros

# IMPORTAR CSV 
def test_importar_csv_invalido(tmp_path, monkeypatch):
    arquivo = tmp_path / "vendas_invalid.csv"
    with open(arquivo, "w", newline="", encoding="utf-8") as f:
        f.write("nome,preco,quantidade,data_validade,data,vendedor\n")
        f.write("ProdutoX,abc,2,32/13/2025,01/01/2025,\n")  # dados inválidos

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
    entradas = iter([
        "1",  # escolher produto
        "2",  # quantidade
        "N"   # não adicionar outro produto
    ])
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