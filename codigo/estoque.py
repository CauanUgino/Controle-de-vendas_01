# ============================================================
# estoque.py
# Módulo para gerenciamento do estoque.
# Permite listar, editar e remover produtos.
# ============================================================

from data import lista_produtos

def ListarProdutos():
    if not lista_produtos:
        print("Nenhum produto cadastrado.")
        return
    for i, produto in enumerate(lista_produtos, 1):
        print(f"[{i}] - {produto}")

def GerenciarEstoque():
    while True:
        print("[1] - Listar produtos")
        print("[2] - Voltar")
        op = input("Escolha: ")
        if op == "1":
            ListarProdutos()
        elif op == "2":
            break
