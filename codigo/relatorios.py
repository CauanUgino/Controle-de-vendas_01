"""
============================================================
relatorios.py
Módulo para geração de relatórios de vendas.
Inclui funções para:
- Relatórios gerais.
- Produto mais vendido.
- Relatórios filtrados (por data, agrupados etc.).
============================================================
"""

from data import registro_vendas


def relatorios():
    """Exibe o menu de relatórios para o usuário."""
    while True:
        print("[1] Produto mais vendido")
        print("[2] Voltar")
        op = input("Escolha: ")
        if op == "1":
            produto_mais_vendido()
        elif op == "2":
            break


def produto_mais_vendido():
    """Apresenta o produto mais vendido até o momento."""
    if not registro_vendas:
        print("Nenhuma venda registrada.")
        return

    produto = max(registro_vendas, key=registro_vendas.get)
    print(f"Produto mais vendido: {produto} ({registro_vendas[produto]} unidades)")


"""Final do módulo"""
