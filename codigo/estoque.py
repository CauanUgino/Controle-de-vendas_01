"""============================================================
estoque.py
Módulo para gerenciamento do estoque.
Permite listar, editar e remover produtos.
============================================================"""
# Esta linha é responsável por trazer as informações do arquivo lista_produtos par cá
from data import lista_produtos
def ListarProdutos():
    """Esta Função é responsável por fazer a listagem dos produtos disponíveis"""
    if not lista_produtos:
        # Esta linha é responsável por retornar uma mensagem caso não tenha nenhum produto em estoque
        print("Nenhum produto cadastrado.")
        return
    # Esta linha é responsável por listar os produtos de forma enumerada
    for i, produto in enumerate(lista_produtos, 1):
        print(f"[{i}] - {produto}")
def GerenciarEstoque():
    """Esta função é Responsável por exibir o menu para listar os produtos ao usuário"""
    while True:
        print("[1] - Listar produtos")
        print("[2] - Voltar")
        op = input("Escolha: ")
        if op == "1":
            ListarProdutos()
        elif op == "2":
            break
"""Final do módulo"""