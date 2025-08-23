"""============================================================
main.py
Este arquivo é o ponto de entrada do sistema.
Ele é rsponsável por iniciar o menu principal e chamar as funções dos outros módulos (produtos, vendas, estoque e relatórios).
============================================================"""
# Esta sequência de linhas é responsável por trazer as informações dos demais arquivos para cá
from produtos import CadastroProduto
from estoque import ListarProdutos, GerenciarEstoque
from vendas import ComprarProduto
from relatorios import Relatorios
from data import lista_produtos
from models import Produto
def menu():
    """Esta função é responsável por exibir o menu rincipal com as principais opções disponíveis"""
    print("MENU PRINCIPAL!")
    print("[1] - Cadastrar vendas")
    print("[2] - Cadastrar Novo Produto")
    print("[3] - Gerenciar estoque")
    print("[4] - Relatórios")
    print("[5] - Sair")
"""Esta Sequência de linhas é responsável por adcionar produtos para a lista que contém os produtos em estoque"""
if __name__ == "__main__":
    lista_produtos.extend([
        Produto("Arroz 5kg", 25.90, 10, "30/12/2025"),
        Produto("Feijão 1kg", 8.50, 15, "15/01/2026"),
        Produto("Macarrão 500g", 4.20, 20, "20/11/2025"),
        Produto("Óleo de Soja 900ml", 6.80, 12, "10/10/2025"),
        Produto("Café 500g", 16.75, 8, "05/06/2026"),
    ])
    while True:
        """Esta sequência de linhas é responsável por fazer um loop de escolhas ao usuário"""
        print("="*40)
        menu()
        print("="*40)
        """Campo a baixo é onde o usuário irá digitar sua resposta"""
        op = input("Digite sua resposta: ")
        if op == "1":
            ComprarProduto()
        if op == "2":
            CadastroProduto()
        if op == "3":
            GerenciarEstoque()
        if op == "4":
            Relatorios()
        if op == "5":
            """Caso sua resposta seja igual a 5 o loop irá se encerrar"""
            print("Saindo do sistema. Até logo!")
            break
        else:
            print("Opção inválida.")
    print("Obrigado por usar o sistema de vendas!")
"""Final do Módulo"""