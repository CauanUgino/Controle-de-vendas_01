######## Sistema de Vendas #########
#Na parte de realizar compras mudar para cadastrar compras e imortar todas as vendas
#Importando Biblioteca
from datetime import datetime, date
import csv

# Listas para armazenar os produtos e as compras
lista_produtos = []
carrinho_de_compras = []

# Classe Produto
class Produto:
    def __init__(self, nome, preco, quantidade,validade):
        self.nome = nome
        self.preco = preco
        self.quantidade = max(quantidade, 0)  # Garante que a quantidade não seja negativa
        if isinstance(validade, str):
            try:
                self.validade = datetime.strptime(validade, "%d/%m/%Y").date()
            except ValueError:
                print(f"Data de validade inválida para o produto {nome}. Produto não cadastrado.")
                raise ValueError("Data de validade inválida.")
        else:
            self.validade = validade  # já é datetime.date

        self.data_cadastro = date.today()

    def __str__(self):
        return (f"{self.nome} - R$ {self.preco:.2f} | Estoque: {self.quantidade} | "
                f"Cadastrado em: {self.data_cadastro} | Validade: {self.validade}")
        
    def esta_vencido(self):
        return self.validade < date.today()
    
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

# Menu de opções do sistema
def menu():
    print('''[1] - Cadastrar vendas
[2] - Cadastrar Novo Produto
[3] - Gerenciar o estoque
[4] - Importar produtos de um arquivo CSV
[5] - Sair do sistema''')
    
def ImportarVendasCSV():
    caminho = input("Digite o caminho completo do arquivo CSV de vendas: ").strip()
    try:
        with open(caminho, newline='', encoding='utf-8') as csvfile:
            leitor = csv.DictReader(csvfile)
            vendas_importadas = 0
            for linha in leitor:
                try:
                    ####Lê os dados do CSV####
                    # Verifica se o nome do produto não está vazio
                    nome = linha['nome']
                    # Verifica se o nome do produto não está vazio
                    if not nome:
                        print("Nome do produto não pode ser vazio.")
                        continue
                    preco= float(linha['preco'])
                    # Verifica se o preço é um número positivo
                    if preco < 0:
                        print(f"Preço inválido para o produto {nome}.")
                        continue
                    # Verifica se a quantidade é um número inteiro positivo
                    if not linha['quantidade'].isdigit():
                        print(f"Quantidade inválida para o produto {nome}.")
                        continue
                    quantidade = int(linha['quantidade'])

                    # Verifica se a validade não está vazia
                    # Se a validade não estiver no formato correto, ignora a venda
                    if not linha['data_validade']:
                        print(f"Data de validade não pode ser vazia para o produto {nome}.")
                        continue
                    validade = linha['data_validade']

                    # Verifica se a data de validade está no formato correto
                    #######PROLEMA NA VALIDAÇÃO DE DATA######
                    #BUG: A data de validade não está sendo validada corretamente
                    try:
                        validade = datetime.strptime(validade, "%d/%m/%Y").date()
                    except ValueError:
                        print(f"Data de validade inválida para o produto {nome}.")
                        continue
                    data_venda = datetime.strptime(linha['data'], "%d/%m/%Y").date()
            
                    

                    # Verifica se a data de venda é válida
                    # Se a data de venda for uma data futura, ignora a venda
                    date_hoje = date.today()
                    if data_venda > date_hoje:
                        print(f" Data de venda inválida: {data_venda} (maior que a data atual)")
                        continue
                    
                    # Verifica se o produto existe no estoque
                    # Se o produto não existir, ignora a venda
                    # Se o produto estiver vencido, ignora a venda
                    produto = next((p for p in lista_produtos if p.nome == nome), None)

                    # Se o produto não existir, ignora a venda
                    if not produto:
                        print(f" Produto não encontrado no estoque: {nome}")
                        continue

                    # Se o produto estiver vencido, ignora a venda
                    if produto.esta_vencido():
                        print(f" Produto vencido ignorado na venda: {nome}")
                        continue
                    
                    # Verifica se a quantidade solicitada é maior que a disponível
                    if quantidade > produto.quantidade:
                        print(f" Estoque insuficiente para {nome} (pedido: {quantidade}, disponível: {produto.quantidade})")
                        continue

                    # Subtrai do estoque
                    produto.quantidade -= quantidade
                    vendas_importadas += 1
                    print(f" Venda registrada: {nome} | Preço unitário: R$ {preco:.2f} | Quantidade: {quantidade} | Data: {data_venda.strftime('%d/%m/%Y')}")

                except Exception as e:
                    print(f"Erro ao importar linha: {linha} -> {e}")
            
            print(f"\n {vendas_importadas} venda(s) registrada(s) com sucesso!\n")

    except FileNotFoundError:
        print("Arquivo não encontrado.")
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")



# Cadastro de novos produtos
def CadastroProduto():
    nome_produto = input('Digite o nome do produto: ')
    preco_produto = float(input('Digite o preço do produto: '))
    quantidade = int(input("Digite a quantidade disponível: "))
    validade = str (input("Digite a data de validade do produto (dd/mm/aaaa): "))

    # Verifica se o produto está na validade
    try:
        validade = datetime.strptime(validade, "%d/%m/%Y").date()
    except ValueError:
        print("Data inválida! Produto não cadastrado.")
        return

    if validade < date.today():
        print("Produto vencido! Não é pode cadastrar no estoque.")
        return

    novo_produto = Produto(nome_produto, preco_produto, quantidade, validade)
    lista_produtos.append(novo_produto)

    print('---' * 20)
    print(f'Produto "{nome_produto}" cadastrado com sucesso por R${preco_produto:.2f}!')
    print(f"Data de cadastro: {novo_produto.data_cadastro}")
    print(f"Validade: {novo_produto.validade}")


# Gerenciar o estoque (Listar, Remover e Editar)
def GerenciarEstoque():
    while True:
        print('---' * 20)
        if not lista_produtos:
            print("Nenhum produto cadastrado.")
            return

        print("[1] - Listar produtos")
        print("[2] - Remover produto")
        print("[3] - Editar produto")
        print("[4] - Voltar ao menu principal")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            ListarProdutos()

        elif opcao == '2':
            RemoverProduto()

        elif opcao == '3':
            EditarProduto()

        elif opcao == '4':
            break
        else:
            print("Opção inválida! Tente novamente.")

# Listar produtos (incluindo vencidos)
def ListarProdutos():
    print('---' * 20)
    if not lista_produtos:
        print("Nenhum produto cadastrado.")
        return

    for i, produto in enumerate(lista_produtos, 1):
        print(f"[{i}] - {produto}")

    print('---' * 20)


# Remover produto pelo índice ou nome
def RemoverProduto():
    print('---' * 20)
    ListarProdutos()

    try:
        escolha = int(input("Escolha o número do produto a remover: "))
        produto = lista_produtos[escolha - 1]
        # Confirmação de remoção
        confirmar = input(f"Você tem certeza que deseja remover o produto '{produto.nome}'? [s/n]: ").upper()
        if confirmar != 'S':
            print("Remoção cancelada.")
            return
        #Remove o produto da lista
        lista_produtos.remove(produto)
        print(f"Produto {produto.nome} removido com sucesso!")
    except (IndexError, ValueError):
        print("Opção inválida. Tente novamente.")
    
    print('---' * 20)


# Editar um produto
def EditarProduto():
    print('---' * 20)
    ListarProdutos()

    try:
        escolha = int(input("Escolha o número do produto para editar: "))
        produto = lista_produtos[escolha - 1]
        
        print(f"Editando produto: {produto}")
        
        nome = input(f"Nome do produto: (atualmente '{produto.nome}'): ")
        preco = float(input(f"Novo preço (atualmente R${produto.preco}): "))
        quantidade = int(input(f"Nova quantidade (atualmente {produto.quantidade}): "))
        validade = input(f"Nova validade (atualmente {produto.validade}) (dd/mm/aaaa): ")

        try:
            validade = datetime.strptime(validade, "%d/%m/%Y").date()
        except ValueError:
            print("Data inválida! Produto não editado.")
            return

        produto.nome = nome if nome else produto.nome
        produto.preco = preco if preco >= 0 else produto.preco
        produto.quantidade = max(quantidade, 0) if quantidade >= 0 else produto.quantidade
        produto.validade = validade if validade >= date.today() else produto.validade

        print(f"Produto {produto.nome} editado com sucesso!")
    except (IndexError, ValueError):
        print("Opção inválida. Tente novamente.")
    
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


# Produtos pré-cadastrados
lista_produtos.append(Produto("Arroz 5kg", 25.90, 10, "30/12/2025"))
lista_produtos.append(Produto("Feijão 1kg", 8.50, 15, "15/01/2026"))
lista_produtos.append(Produto("Macarrão 500g", 4.20, 20, "20/11/2025"))
lista_produtos.append(Produto("Óleo de Soja 900ml", 6.80, 12, "10/10/2025"))
lista_produtos.append(Produto("Café 500g", 16.75, 8, "05/06/2026"))


#####Loop principal essencial do sistema######
#Ele deve ficar no final do código, após todas as definições de funções e classes.
#O loop principal deve ser o último bloco de código a ser executado.
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
    elif resposta == 3:
        GerenciarEstoque()
    elif resposta == 4:
        ImportarVendasCSV()
    elif resposta == 5:
        print('Volte sempre!')
        break
    else:
        print("Opção inválida. Tente novamente.")
