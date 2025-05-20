######## Sistema de Vendas #########
#Na parte de realizar compras mudar para cadastrar compras e imortar todas as vendas
#Importando Biblioteca
from datetime import datetime, date
import csv

# Essa é a lista que armazena os produtos disponíveis
lista_produtos = []
# Essa lista armazena as compras realizadas no momento
carrinho_de_compras = []


# Classe Produto -> Como se fosse um molde dos produtos que serão armazenados
class Produto:
    def __init__(self, nome, preco, quantidade):
        self.nome = nome
        self.preco = preco
        self.quantidade = max(quantidade, 0)  # Garante que a quantidade não seja negativa
        self.data_cadastro = date.today() # Data de cadastro do produto

    def __str__(self):
        return (f"{self.nome} - R$ {self.preco:.2f} | Estoque: {self.quantidade} | "
                f"Cadastrado em: {self.data_cadastro} | Validade: {self.validade}")
    def atualizar_estoque(self, quantidade_comprada: int):
        # referencia a lista_produtos
        global lista_produtos
        #Pecorre a lista de produtos e remove os produtos vencidos
        lista_produtos = [p for p in lista_produtos if not p.esta_vencido()]
        # reduz a quantidade do produto no estoque
        if quantidade_comprada <= self.quantidade:
            self.quantidade -= quantidade_comprada
        else:
            print(f"Quantidade solicitada ({quantidade_comprada}) maior que a disponível ({self.quantidade}).")
            raise ValueError("Quantidade solicitada maior que a disponível.")
        
    def estoque_disponivel(self) -> bool:
        # verifica se o produto está disponível em estoque
        return self.quantidade > 0

print('Bem-vindo ao sistema de compras!')

# Essa função é o menu que o usuário irá ver na hora de realizar as compras
def menu():
    print('''[1] - Cadastrar vendas
[2] - Cadastrar Novo Produto
[3] - Importar produtos de um arquivo CSV
[4] - Sair do sistema''')

# Essa é a função responsável por adcionar novos produtos
def CadastroProduto():
    nome_produto = input('Digite o nome do produto: ')
    preco_produto = float(input('Digite o preço do produto: '))
    quantidade = int(input("Digite a quantidade disponível: "))

    novo_produto = Produto(nome_produto, preco_produto, quantidade)
    lista_produtos.append(novo_produto)

    print('---' * 20)
    print(f'Produto "{nome_produto}" cadastrado com sucesso por R${preco_produto:.2f}!')
    print(f"Data de cadastro: {novo_produto.data_cadastro}")


# Listar produtos (incluindo vencidos)
def ListarProdutos():
    print('---' * 20)
    if not lista_produtos:
        print("Nenhum produto cadastrado.")
        return

    for i, produto in enumerate(lista_produtos, 1):
        print(f"[{i}] - {produto}")

    print('---' * 20)


# Compra d produtos
def ComprarProduto():
    while True:
        print('---' * 20)
        if not lista_produtos:
            print("Nenhum produto cadastrado.")
            return

        for i, item in enumerate(lista_produtos, 1):
            print(f"[{i}] -> {item.nome} | R${item.preco:.2f} | Estoque: {item.quantidade}")
        print('---' * 20)

        try:
            resposta = int(input('Digite o número do produto que deseja cadastrar a venda: '))
            produto_escolhido = lista_produtos[resposta - 1]
        except (IndexError, ValueError):
            print("Opção inválida. Tente novamente.")
            continue

        if produto_escolhido.quantidade == 0:
            print(f'O produto "{produto_escolhido.nome}" está sem estoque!')
            if input('Deseja comprar outro produto? [s/n]: ').upper() == 'N':
                break
            continue

        quantidade_desejada = int(input('Digite a quantidade que deseja: '))
        if quantidade_desejada > produto_escolhido.quantidade:
            print(f"Quantidade indisponível. Só temos {produto_escolhido.quantidade} unidade(s) em estoque.")
        else:
            produto_escolhido.quantidade -= quantidade_desejada
            carrinho_de_compras.append((produto_escolhido.nome, produto_escolhido.preco, quantidade_desejada))
            print('Produto adicionado com sucesso!')

        print('---' * 20)
        print('Produtos:')
        for i in carrinho_de_compras:
            print(f'{i[0]} | Preço: R${i[1]:.2f} | Quantidade: {i[2]}')
        print('---' * 20)

        if input('Deseja realizar outra venda? [s/n]: ').upper() == 'N':
            if not carrinho_de_compras:
                print("Seu carrinho está vazio.")
                if input("Deseja tentar comprar novamente? [s/n]: ").upper() == 'S':
                    ComprarProduto()
            else:
                FinalizarOuCancelarCompra()
            break

# Finalização da compra
def FinalizarCompra():
    print("\nCompra finalizada com sucesso!")
    print("Resumo da compra:")
    total = 0
    nota= []

    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")    
    nota.append(f"Data da compra: {data_hora}\n")
    nota.append("Itens comprados:")

    for nome, preco, qtd in carrinho_de_compras:
        subtotal = preco * qtd
        nota.append(f"{nome} | Preço: R${preco:.2f} | Quantidade: {qtd} | Subtotal: R${subtotal:.2f}")
        total += subtotal

    nota.append(f"\nTotal a pagar: R${total:.2f}")
    
    
    for linha in nota:
        print(linha)
    
     # Salva em arquivo
    with open("nota_fiscal.txt", "w", encoding="utf-8") as arquivo:
        arquivo.write("NOTA FISCAL\n")
        arquivo.write("="*40 + "\n")
        for linha in nota:
            arquivo.write(linha + "\n")
        arquivo.write("="*40 + "\n")
        arquivo.write("Obrigado pela sua compra!\n")

    print("\n Nota Fiscal gerada com sucesso!")
    carrinho_de_compras.clear()
    

# Confirmação ou cancelamento da compra
def FinalizarOuCancelarCompra():
    while True:
        print("\nDeseja confirmar a venda ou cancelar?")
        print("[1] Confirmar venda")
        print("[2] Cancelar venda")
        decisao = input("Digite sua escolha: ")
    
        if decisao == '1':
            FinalizarCompra()
            break
        elif decisao == '2':
            confirmar = input("Você tem certeza que deseja cancelar a compra? [s/n]: ").upper()
            if confirmar == 'S':
                CancelarCompra()
            else:
                print("Compra não cancelada.")
            CancelarCompra()
            break
        else:
            print("Opção inválida. Tente novamente.")


# Cancelamento de compra
def CancelarCompra():
    if not carrinho_de_compras:
        print("Seu carrinho está vazio.")
        return
    print('Cancelando sua compra...')
    for nome, preco, qtd in carrinho_de_compras:
        for produto in lista_produtos:
            if produto.nome == nome:
                produto.quantidade += qtd
                break
    carrinho_de_compras.clear()
    print("Compra cancelada e produtos devolvidos ao estoque com sucesso!")


# Produtos pré-cadastrados para realizar os testes necessários
lista_produtos.append(Produto("Arroz 5kg", 25.90, 10))
lista_produtos.append(Produto("Feijão 1kg", 8.50, 15))
lista_produtos.append(Produto("Macarrão 500g", 4.20, 20))
lista_produtos.append(Produto("Óleo de Soja 900ml", 6.80, 12))
lista_produtos.append(Produto("Café 500g", 16.75, 8))


# Loop principal do sistema onde os menus irão rodar até que a compra seja finalizada
while True:
    print('=-=' * 20)
    menu()
    print('=-=' * 20)
    try:
        resposta = int(input('Digite sua resposta: '))
    except ValueError:
        print("Entrada inválida. Digite um número.")
        continue

    if resposta == 1:
        carrinho_de_compras.clear()
        ComprarProduto()
    elif resposta == 2:
        CadastroProduto()
    #elif resposta == 3:
        # CSV
    elif resposta == 4:
        print('Volte sempre!')
        break
    else:
        print("Opção inválida. Tente novamente.")