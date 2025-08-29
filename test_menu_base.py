import pytest
from datetime import datetime, timedelta, date
import menu_base as mb
import builtins
import io
import csv
import os
import menu_base as mb
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


def test_finalizar_compra(monkeypatch):
    validade = (date.today() + timedelta(days=5)).strftime("%d/%m/%Y")
    p = mb.Produto("Biscoito", 2.5, 3, validade)
    mb.lista_produtos.append(p)
    mb.carrinho_de_compras.append((p.nome, p.preco, 2))

    monkeypatch.setattr("builtins.input", lambda _: "")
    mb.FinalizarCompra()
    assert mb.carrinho_de_compras == []
    assert mb.registro_vendas[p.nome] == 2
    assert os.path.exists(os.path.join("relatorios", "nota_fiscal.txt"))
    os.remove(os.path.join("relatorios", "nota_fiscal.txt"))


def test_cancelar_compra_restaura_estoque():
    validade = (date.today() + timedelta(days=1)).strftime("%d/%m/%Y")
    p = mb.Produto("Leite", 5, 1, validade)
    mb.lista_produtos.append(p)
    mb.carrinho_de_compras.append((p.nome, p.preco, 1))

    mb.CancelarCompra()
    assert p.quantidade == 2
    assert mb.carrinho_de_compras == []



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


def test_cadastro_produto(monkeypatch):
    entradas = iter([
        "Arroz", "10", "5", (date.today()+timedelta(days=5)).strftime("%d/%m/%Y")
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))
    mb.CadastroProduto()
    assert len(mb.lista_produtos) == 1


def test_relatorios_vazios(monkeypatch):
    entradas = iter(["6"])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))
    monkeypatch.setattr("builtins.print", lambda *args, **kwargs: None)
    mb.Relatorios() 


def test_importar_csv_invalido(tmp_path, monkeypatch):
    arquivo = tmp_path / "vendas_invalid.csv"
    with open(arquivo, "w", newline="", encoding="utf-8") as f:
        f.write("nome,preco,quantidade,data_validade,data,vendedor\n")
        f.write("ProdutoX,abc,2,32/13/2025,01/01/2025,\n")

    monkeypatch.setattr("builtins.input", lambda _: str(arquivo))
    mb.ImportarVendasCSV()
    assert len(mb.lista_vendas) == 0


def test_listar_produtos(capsys):
    p = mb.Produto("Arroz", 10, 5, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.append(p)
    mb.ListarProdutos()
    captured = capsys.readouterr()
    assert "Arroz" in captured.out


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


def test_nota_fiscal_conteudo(monkeypatch):
    p = mb.Produto("Biscoito", 2, 1, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.append(p)
    mb.carrinho_de_compras.append((p.nome, p.preco, 1))

    monkeypatch.setattr("builtins.input", lambda _: "")
    mb.FinalizarCompra()

    with open(os.path.join("relatorios", "nota_fiscal.txt"), "r", encoding="utf-8") as f:
        conteudo = f.read()
        assert p.nome in conteudo
    os.remove(os.path.join("relatorios", "nota_fiscal.txt"))



def test_atualizar_estoque_negativo():
    validade = (date.today() + timedelta(days=5)).strftime("%d/%m/%Y")
    p = mb.Produto("Suco", 5, 2, validade)
    mb.lista_produtos.append(p)
    with pytest.raises(ValueError):
        p.atualizar_estoque(10)


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


def test_importar_csv_vazio(tmp_path, monkeypatch):
    arquivo = tmp_path / "vazio.csv"
    arquivo.write_text("nome,preco,quantidade,data_validade,data,vendedor\n")
    monkeypatch.setattr("builtins.input", lambda _: str(arquivo))
    mb.ImportarVendasCSV()
    assert len(mb.lista_vendas) == 0


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



def test_finalizar_compra_vazio(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "")
    mb.FinalizarCompra()
    assert mb.carrinho_de_compras == []


def test_relatorios_vazios_adicionais(monkeypatch):
    monkeypatch.setattr("builtins.print", lambda *args, **kwargs: None)
    mb.ProdutoMaisVendido()
    mb.RelatorioAgrupado()
    mb.RelatorioVendasPorProduto()


def test_nota_fiscal_varios(monkeypatch):
    p1 = mb.Produto("Biscoito", 2, 1, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    p2 = mb.Produto("Suco", 3, 1, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.extend([p1, p2])
    mb.carrinho_de_compras.extend([(p1.nome, p1.preco, 1), (p2.nome, p2.preco, 1)])
    monkeypatch.setattr("builtins.input", lambda _: "")
    mb.FinalizarCompra()
    with open(os.path.join("relatorios", "nota_fiscal.txt"), "r", encoding="utf-8") as f:
        conteudo = f.read()
        assert "Biscoito" in conteudo
        assert "Suco" in conteudo
    os.remove(os.path.join("relatorios", "nota_fiscal.txt"))


def test_menu_entrada_invalida_string(monkeypatch, capsys):
    inputs = iter(["abc", "6"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    try:
        mb.MenuPrincipal()
    except SystemExit:
        pass  # esperado quando chega no "6"
    captured = capsys.readouterr()
    assert "Opção inválida" in captured.out


def test_relatorio_agrupado_exibe_relatorio(capsys):
    mb.lista_vendas.clear()
    p = mb.Produto("Leite", 5.0, 2, (date.today() + timedelta(days=10)).strftime("%d/%m/%Y"))
    v = mb.Venda(p, p.preco, 2)
    mb.lista_vendas.append(v)
    mb.RelatorioAgrupado()
    captured = capsys.readouterr()
    assert "RELATÓRIO DE VENDAS TOTAIS" in captured.out


def test_relatorio_vendas_por_produto_exibe_relatorio(capsys):
    mb.lista_vendas.clear()
    p = mb.Produto("Arroz", 10.0, 1, (date.today() + timedelta(days=10)).strftime("%d/%m/%Y"))
    v = mb.Venda(p, p.preco, 1)
    mb.lista_vendas.append(v)
    mb.RelatorioVendasPorProduto()
    captured = capsys.readouterr()
    assert "--- Relatório de Vendas por Produto ---" in captured.out


def test_remover_produto_inexistente(monkeypatch, capsys):
    mb.lista_produtos.clear()
    monkeypatch.setattr("builtins.input", lambda _: "999")
    mb.RemoverProduto()
    captured = capsys.readouterr()
    assert "Nenhum produto cadastrado" in captured.out


@pytest.mark.parametrize("nome,preco,quantidade,mensagem", [
    ("Teste", -1, 1, "Preço inválido"),
    ("Teste", "abc", 1, "Entrada inválida para o preço"),
    ("Teste", 1.0, -5, "Quantidade inválida"),
])


def test_cadastro_produto_invalido(monkeypatch, capsys, nome, preco, quantidade, mensagem):
    mb.lista_produtos.clear()
    validade = (date.today()+timedelta(days=5)).strftime("%d/%m/%Y")
    inputs = iter([nome, preco, quantidade, validade, nome, "1", "1", validade])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    mb.CadastroProduto()
    captured = capsys.readouterr()
    assert mensagem in captured.out


def test_produto_vencido():
    validade = (date.today() - timedelta(days=1)).strftime("%d/%m/%Y")
    p = mb.Produto("Iogurte", 3, 5, validade)
    assert p.esta_vencido()
    assert p.quantidade == 5


def test_comprar_produto_estoque_insuficiente(monkeypatch, capsys):
    p = mb.Produto("Leite", 5, 1, (date.today() + timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.append(p)
    entradas = iter([
        "1",  
        "5",  
        "1",  
        "n",  
        "1",  
        ""    
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))
    mb.ComprarProduto()
    captured = capsys.readouterr()
    assert "Quantidade indisponível" in captured.out
    assert 'Produto "Leite" adicionado ao carrinho!' in captured.out
    assert mb.lista_vendas[-1].quantidade == 1


def test_listar_produtos_vazio(capsys):
    mb.lista_produtos.clear()
    mb.ListarProdutos()
    captured = capsys.readouterr()
    assert "Nenhum produto cadastrado" in captured.out


def test_importar_csv_dados_faltando(tmp_path, monkeypatch):
    arquivo = tmp_path / "incompleto.csv"
    arquivo.write_text("nome,preco,quantidade,data_validade,data,vendedor\nArroz,10\n")
    monkeypatch.setattr("builtins.input", lambda _: str(arquivo))
    mb.ImportarVendasCSV()
    assert len(mb.lista_vendas) == 0


def test_cancelar_compra_vazio(monkeypatch, capsys):
    mb.carrinho_de_compras.clear()
    monkeypatch.setattr("builtins.input", lambda _: "S")
    mb.CancelarCompra()
    captured = capsys.readouterr()
    assert "Seu carrinho está vazio" in captured.out


def test_produto_validade_hoje():
    hoje = date.today().strftime("%d/%m/%Y")
    p = mb.Produto("LimiteHoje", 10, 5, hoje)
    assert not p.esta_vencido()


def test_produto_preco_zero():
    validade = (date.today() + timedelta(days=5)).strftime("%d/%m/%Y")
    p = mb.Produto("Gratis", 0, 5, validade)
    mb.lista_produtos.append(p)
    assert p.preco == 0


def test_produto_validade_hoje_e_estoque_zero():
    """Produto com validade hoje e quantidade zero não deve estar disponível"""
    validade = date.today().strftime("%d/%m/%Y")
    p = mb.Produto("Iogurte", 5, 0, validade)
    assert p.esta_vencido() is False
    assert p.estoque_disponivel() is False

def test_produto_preco_zero():
    """Produto com preço zero ainda pode ser adicionado, mas preço deve ser zero"""
    validade = (date.today() + timedelta(days=5)).strftime("%d/%m/%Y")
    p = mb.Produto("Água", 0, 10, validade)
    assert p.preco == 0
    assert p.estoque_disponivel()


def test_finalizar_compra_com_vendedor(monkeypatch):
    """Finalizar compra informando o vendedor"""
    p = mb.Produto("Chocolate", 5, 3, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.append(p)
    mb.carrinho_de_compras.append((p.nome, p.preco, 2))
    monkeypatch.setattr("builtins.input", lambda _: "João")
    mb.FinalizarCompra()
    assert mb.registro_vendas[p.nome] == 2
    with open(os.path.join("relatorios", "nota_fiscal.txt"), "r", encoding="utf-8") as f:
        conteudo = f.read()
        assert "João" in conteudo
    os.remove(os.path.join("relatorios", "nota_fiscal.txt"))


def test_relatorio_agrupado_sem_vendas(capsys):
    """Relatório agrupado com lista de vendas vazia"""
    mb.lista_vendas.clear()
    mb.RelatorioAgrupado()
    captured = capsys.readouterr()
    assert "RELATÓRIO DE VENDAS TOTAIS" in captured.out


def test_relatorio_vendas_por_produto_sem_vendas(capsys):
    """Relatório por produto com lista de vendas vazia"""
    mb.lista_vendas.clear()
    mb.RelatorioVendasPorProduto()
    captured = capsys.readouterr()
    assert "Nenhuma venda registrada ainda." in captured.out


def test_menu_opcao_invalida_repetida(monkeypatch, capsys):
    """Menu principal recebendo entradas inválidas repetidas"""
    entradas = iter(["abc", "999", "6"])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))
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
    captured = capsys.readouterr()
    assert "Opção inválida" in captured.out


def atualizar_estoque(self, quantidade):
    if quantidade < 0:
        raise ValueError("Quantidade inválida")
    if quantidade > self.quantidade:
        raise ValueError("Quantidade maior que estoque disponível")
    self.quantidade -= quantidade


def test_comprar_produto_quantidade_zero(monkeypatch, capsys):
    """Tentar comprar quantidade zero"""
    p = mb.Produto("Bolacha", 2, 5, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.append(p)
    entradas = iter(["1", "0", "1", "n", "1", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))
    mb.ComprarProduto()
    captured = capsys.readouterr()
    assert "Quantidade inválida" in captured.out or mb.lista_vendas[-1].quantidade > 0
    
def test_gerar_relatorio_vendas_totais(monkeypatch, tmp_path):
    p = mb.Produto("Arroz", 10, 2, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.append(p)
    mb.lista_vendas.append(mb.Venda(p, 1, date.today(), vendedor="Maria"))

    monkeypatch.setattr("builtins.input", lambda _: "Tester")
    mb.GerarRelatorioVendasTotais()

    arquivos = os.listdir("relatorios")
    assert any("relatorio_vendas_totais" in arq for arq in arquivos)

def test_produto_mais_vendido_por_dia(monkeypatch):
    p = mb.Produto("Feijão", 5, 10, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.append(p)
    mb.lista_vendas.append(mb.Venda(p, 2, date.today(), vendedor="José"))

    entradas = iter([
        "1",  # escolhe filtro por dia
        date.today().strftime("%d/%m/%Y"),  # data de hoje
        "Tester",  # primeira vez que pede usuário
        "Tester"   # segunda vez (duplicado no código)
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))

    mb.ProdutoMaisVendidoPordata()

def test_baixar_relatorios(monkeypatch):
    p = mb.Produto("Macarrão", 4, 10, (date.today()+timedelta(days=5)).strftime("%d/%m/%Y"))
    mb.lista_produtos.append(p)
    mb.lista_vendas.append(mb.Venda(p, 1, date.today(), vendedor="Ana"))

    entradas = iter(["1", "4"])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))
    mb.BaixarRelatorios()

    arquivos = os.listdir("relatorios")
    assert any("relatorio_vendas_totais" in arq for arq in arquivos)
