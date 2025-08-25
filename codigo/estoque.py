"""
============================================================
estoque.py
Módulo para gerenciamento do estoque.
Permite listar, editar e remover produtos.
============================================================
"""

from data import lista_produtos


def listar_produtos():
    """Lista todos os produtos cadastrados no estoque."""
    if not lista_produtos:
        print("Nenhum produto cadastrado.")
        return

    for i, produto in enumerate(lista_produtos, 1):
        print(f"[{i}] - {produto}")


def gerenciar_estoque():
    """Exibe o menu de gerenciamento do estoque para o usuário."""
    while True:
        print("[1] - Listar produtos")
        print("[2] - Voltar")
        op = input("Escolha: ")
        if op == "1":
            listar_produtos()
        elif op == "2":
            break


"""Final do módulo"""
