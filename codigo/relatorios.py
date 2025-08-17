# ============================================================
# relatorios.py
# Módulo para geração de relatórios de vendas.
# Inclui funções para:
# - Relatórios gerais.
# - Produto mais vendido.
# - Relatórios filtrados (por data, agrupados etc.).
# ============================================================

from data import lista_vendas, registro_vendas

def Relatorios():
    while True:
        print("[1] Produto mais vendido")
        print("[2] Voltar")
        op = input("Escolha: ")
        if op == "1":
            ProdutoMaisVendido()
        elif op == "2":
            break

def ProdutoMaisVendido():
    if not registro_vendas:
        print("Nenhuma venda registrada.")
        return
    produto = max(registro_vendas, key=registro_vendas.get)
    print(f"Produto mais vendido: {produto} ({registro_vendas[produto]} unidades)")
