# ============================================================
# vendas.py
# Módulo responsável pelo processo de vendas.
# Contém funções para:
# - ComprarProduto: adicionar produtos ao carrinho.
# - FinalizarCompra: gerar nota fiscal e registrar a venda.
# - FinalizarOuCancelarCompra: confirmar ou cancelar.
# - CancelarCompra: devolve produtos ao estoque.
# ============================================================


from datetime import date, datetime
import re
from models import Venda
from data import lista_produtos, carrinho_de_compras, lista_vendas, registro_vendas

def ComprarProduto():
    if not lista_produtos:
        print("Nenhum produto cadastrado.")
        return
    
    while True:
        for i, item in enumerate(lista_produtos, 1):
            print(f"[{i}] -> {item.nome} | R${item.preco:.2f} | Estoque: {item.quantidade}")
        escolha = input("Digite o número do produto (ou 0 para sair): ").strip()
        if not escolha.isdigit():
            print("Entrada inválida.")
            continue
        escolha = int(escolha)
        if escolha == 0:
            break
        if not (1 <= escolha <= len(lista_produtos)):
            print("Número inválido!")
            continue
        
        produto = lista_produtos[escolha - 1]
        qtd = int(input("Quantidade: "))
        if qtd <= 0 or qtd > produto.quantidade:
            print("Quantidade inválida!")
            continue

        produto.quantidade -= qtd
        carrinho_de_compras.append((produto.nome, produto.preco, qtd))
        lista_vendas.append(Venda(produto, qtd, date.today()))
        print(f"{qtd}x {produto.nome} adicionado ao carrinho!")

        continuar = input("Adicionar outro produto? (s/n): ").strip().lower()
        if continuar != "s":
            resultado = FinalizarOuCancelarCompra()
            if resultado == "continuar":
                continue
            break


def FinalizarCompra():
    total = 0
    nota = []
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Nome do vendedor
    while True:
        vendedor = input("Digite o nome do vendedor (ou deixe em branco): ").strip()
        if vendedor == "" or re.fullmatch(r"[A-Za-zÀ-ÿ\\s]+", vendedor):
            break
        print("Nome inválido! Use apenas letras e espaços.")
    
    print("\nCompra finalizada com sucesso!\nResumo da compra:")

    nota.append(f"Data da compra: {data_hora}")
    if vendedor:
        nota.append(f"Vendedor: {vendedor}")
    else:
        nota.append("Vendedor: Não informado")

    for nome, preco, qtd in carrinho_de_compras:
        subtotal = preco * qtd
        nota.append(f"{nome} | R${preco:.2f} x{qtd} = R${subtotal:.2f}")
        total += subtotal
        registro_vendas[nome] = registro_vendas.get(nome, 0) + qtd

    nota.append(f"Total a pagar: R${total:.2f}")

    # Imprime e salva nota fiscal
    for linha in nota:
        print(linha)
    with open("nota_fiscal.txt", "w", encoding="utf-8") as f:
        f.write("NOTA FISCAL\n" + "="*40 + "\n")
        f.write("\n".join(nota))
        f.write("\n" + "="*40 + "\nObrigado pela sua compra!\n")

    print("Nota fiscal salva em 'nota_fiscal.txt'")
    carrinho_de_compras.clear()


def FinalizarOuCancelarCompra():
    while True:
        print("\nDeseja confirmar a compra ou cancelar?")
        print("[1] Confirmar compra")
        print("[2] Cancelar compra")
        escolha = input("Opção: ").strip()
        if escolha == "1":
            FinalizarCompra()
            return "finalizado"
        elif escolha == "2":
            confirmar = input("Tem certeza que deseja cancelar? (s/n): ").strip().lower()
            if confirmar == "s":
                CancelarCompra()
                return "cancelado"
            else:
                return "continuar"
        else:
            print("Opção inválida.")


def CancelarCompra():
    if not carrinho_de_compras:
        print("Carrinho vazio, nada a cancelar.")
        return
    for nome, preco, qtd in carrinho_de_compras:
        for produto in lista_produtos:
            if produto.nome == nome:
                produto.quantidade += qtd
                break
    carrinho_de_compras.clear()
    print("Compra cancelada e produtos devolvidos ao estoque.")
