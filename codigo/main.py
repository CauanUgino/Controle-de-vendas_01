# ============================================================
# main.py
# Este arquivo é o ponto de entrada do sistema.
# ele é rsponsável por iniciar o menu principal e chamar as funções
# dos outros módulos (produtos, vendas, estoque e relatórios).
# ============================================================

from produtos import CadastroProduto
from estoque import ListarProdutos, GerenciarEstoque
from vendas import ComprarProduto
from relatorios import Relatorios
from data import lista_produtos
from models import Produto

def menu():
    print("MENU PRINCIPAL!")
    print("[1] - Cadastrar vendas")
    print("[2] - Cadastrar Novo Produto")
    print("[3] - Gerenciar estoque")
    print("[4] - Relatórios")
    print("[5] - Sair")

if __name__ == "__main__":
    lista_produtos.extend([
        Produto("Arroz 5kg", 25.90, 10, "30/12/2025"),
        Produto("Feijão 1kg", 8.50, 15, "15/01/2026"),
        Produto("Macarrão 500g", 4.20, 20, "20/11/2025"),
        Produto("Óleo de Soja 900ml", 6.80, 12, "10/10/2025"),
        Produto("Café 500g", 16.75, 8, "05/06/2026"),
    ])
    while True:
        print("="*40)
        menu()
        print("="*40)
        op = input("Digite sua resposta: ")
        if op == "1":
            ComprarProduto()
        elif op == "2":
            CadastroProduto()
        elif op == "3":
            GerenciarEstoque()
        elif op == "4":
            Relatorios()
        elif op == "5":
            print("Saindo do sistema. Até logo!")
            break
        else:
            print("Opção inválida.")
    print("Obrigado por usar o sistema de vendas!")
