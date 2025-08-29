def ProdutoMaisVendidoPordata():
    print("\n--- Relatório de vendas ---")
    if not lista_produtos:
        print("Nenhuma venda registrada ainda.")
        return
    
    print("Escolha o filtro para o relatório:")
    print("1 - Dia específico")
    print("2 - Mês específico")
    print("3 - Semana específica")
    opcao = input("Opção (1/2/3): ").strip()

    filtro_nome = ""
    vendas_filtradas = []

    # DIA
    if opcao == '1':
        data_str = input("Digite o dia (dd/mm/aaaa): ").strip()
        try:
            data_filtro = datetime.strptime(data_str, "%d/%m/%Y").date()
        except ValueError:
            print("Data inválida!")
            return
        vendas_filtradas = [v for v in lista_vendas if v.data_venda == data_filtro]
        filtro_nome = f"dia_{data_filtro.strftime('%d-%m-%Y')}"

    # MÊS
    elif opcao == '2':
        mes_ano = input("Digite o mês e ano (mm/aaaa): ").strip()
        try:
            mes, ano = mes_ano.split("/")
            mes = int(mes)
            ano = int(ano)
            if not (1 <= mes <= 12):
                print("Mês inválido! Digite entre 01 e 12.")
                return
        except ValueError:
            print("Formato inválido! Use mm/aaaa.")
            return

        # Filtra vendas pelo mês e ano
        vendas_filtradas = [v for v in lista_vendas if v.data_venda.month == mes and v.data_venda.year == ano]
        filtro_nome = f"mes_{mes:02d}_{ano}"

    # SEMANA
    elif opcao == '3':
        data_str = input("Digite um dia da semana desejada (dd/mm/aaaa): ").strip()
        try:
            data_base = datetime.strptime(data_str, "%d/%m/%Y").date()
        except ValueError:
            print("Data inválida!")
            return
        inicio_semana = data_base - timedelta(days=data_base.weekday())
        fim_semana = inicio_semana + timedelta(days=6)
        vendas_filtradas = [v for v in lista_vendas if inicio_semana <= v.data_venda <= fim_semana]
        filtro_nome = f"semana_{inicio_semana.strftime('%d-%m-%Y')}_a_{fim_semana.strftime('%d-%m-%Y')}"
    
    else:
        print("Opção inválida!")
        return

    if not vendas_filtradas:
        print("Nenhuma venda encontrada para o período.")
        return

    # Gera CSV
    total_vendas = sum(v.preco * v.quantidade for v in vendas_filtradas)
    nome_arquivo = f"relatorio_vendas_{filtro_nome}.csv"
    caminho_arquivo = os.path.join(PASTA_RELATORIOS, nome_arquivo)
    with open(caminho_arquivo, mode='w', newline='', encoding='utf-8') as arquivo_csv:
        escritor = csv.writer(arquivo_csv)
        escritor.writerow(['Produto','Preço Unitário','Quantidade','Data da Venda','Subtotal','Vendedor'])
        for venda in vendas_filtradas:
            subtotal = venda.preco * venda.quantidade
            escritor.writerow([
                venda.produto.nome,
                f"{venda.preco:.2f}",
                venda.quantidade,
                venda.data_venda.strftime('%d/%m/%Y'),
                f"{subtotal:.2f}",
                venda.vendedor if venda.vendedor else "N/A"
            ])
        escritor.writerow([])
        escritor.writerow(['','','','Total Geral', f"{total_vendas:.2f}"])
    
    usuario = input("Digite o seu nome: ")
    registrar_log(nome_arquivo, usuario)
    print(f"Relatório CSV gerado com sucesso: {caminho_arquivo}")
######## Sistema de Vendas #########
#Importando Biblioteca
from datetime import datetime, date
from datetime import timedelta
import csv
import re
import os

# Cria pasta de relatórios se não existir
PASTA_RELATORIOS = "relatorios"
os.makedirs(PASTA_RELATORIOS, exist_ok=True)

# Listas para armazenar os produtos e as compras
lista_produtos = []
carrinho_de_compras = []
lista_vendas = []
registro_vendas = {}
    
class Venda:
    def __init__(self, produto, quantidade, data_venda, vendedor=None):
        self.produto = produto  # objeto Produto
        self.quantidade = quantidade
        self.data_venda = data_venda  # datetime.date
        self.preco = produto.preco
        self.vendedor = vendedor  # opcional, pode ser None

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
    print()
    print("MENU PRINCIPAL!")
    print()
    print('''[1] - Cadastrar vendas
[2] - Cadastrar Novo Produto
[3] - Gerenciar o estoque
[4] - Importar produtos de um arquivo CSV
[5] - Relatórios         
[6] - Sair do sistema''')
    
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
                    
                    vendedor = linha.get('vendedor', '').strip() or None
                   
                    # Subtrai do estoque
                    produto.quantidade -= quantidade
                    venda = Venda(produto, quantidade, data_venda, vendedor=vendedor)
                    lista_vendas.append(venda)
                    # Atualiza o registro de vendas
                    if nome in registro_vendas:
                        registro_vendas[nome] += quantidade
                    else:
                        registro_vendas[nome] = quantidade
                    
                    print(f" Venda registrada: {nome} | Preço unitário: R$ {preco:.2f} | Quantidade: {quantidade} | Data: {data_venda.strftime('%d/%m/%Y')}")

                    if vendedor:
                        print(f"| Vendedor: {vendedor}")
                    else:
                        print("| Vendedor: Não informado")
                    
                    vendas_importadas += 1


                except Exception as e:
                    print(f"Erro ao importar linha: {linha} -> {e}")
            
            print(f"\n {vendas_importadas} venda(s) registrada(s) com sucesso!\n")

    except FileNotFoundError:
        print("Arquivo não encontrado.")
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")



# Cadastro de novos produtos
def CadastroProduto():
    print()
    print("CADASTRO DE NOVO PRODUTO!")
    print()
    while True: # Loop para garantir que o nome seja válido
        nome_produto = str(input('Digite o nome do produto: ')).strip()

        # Verifica se o nome não está vazio E se não contém nenhum dígito
        if not nome_produto:
            print("O nome do produto não pode ser vazio. Por favor, digite um nome válido.")
        elif any(char.isdigit() for char in nome_produto):
            print("Nome inválido! O nome do produto não pode conter números. Por favor, digite um nome válido.")
        else:
            # Se o nome for válido, sai do loop
            break

    while True: # Loop para garantir que o preço seja válido
        try:
            preco_produto = float(input('Digite o preço do produto: '))
            if preco_produto < 0:
                print("Preço inválido! O preço não pode ser negativo.")
            else:
                break # Sai do loop se o preço for válido
        except ValueError:
            print("Entrada inválida para o preço. Por favor, digite apenas números.")

    while True: # Loop para garantir que a quantidade seja válida
        try:
            quantidade = int(input("Digite a quantidade disponível: "))
            if quantidade < 0:
                print("Quantidade inválida! A quantidade não pode ser negativa.")
            else:
                break # Sai do loop se a quantidade for válida
        except ValueError:
            print("Entrada inválida para a quantidade. Por favor, digite apenas números inteiros.")

    while True: # Loop para garantir que a validade seja válida
        validade_str = input("Digite a data de validade do produto (dd/mm/aaaa): ")
        try:
            validade_obj = datetime.strptime(validade_str, "%d/%m/%Y").date()
            if validade_obj < date.today():
                print("Data de validade inválida! O produto já está vencido. Não pode cadastrar.")
            else:
                break # Sai do loop se a validade for válida e não estiver vencida
        except ValueError:
            print("Data inválida! Por favor, digite a data no formato dd/mm/aaaa.")

    novo_produto = Produto(nome_produto, preco_produto, quantidade, validade_obj)
    lista_produtos.append(novo_produto)
    print(f"\nProduto: '{nome_produto}' cadastrado com sucesso!")
    print(f"Preço: R${preco_produto:.2f} | Quantidade: {quantidade} | Validade: {validade_obj.strftime('%d/%m/%Y')}")
   
   
#Relatórios
def Relatorios():
   while True:
        print('---' * 20) 
        print()
        print("RELATÓRIOS!")
        print()
        print("[1] - Produto mais vendido")
        print("[2] - Relatório de vendas por data")
        print("[3] - Relatório de vendas totais")
        print("[4] - Relatório de vendas p/ produto")
        print("[5] - Relatório agrupado para melhor visualização")
        print("[6] - Voltar ao menu principal")

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            ProdutoMaisVendido()

        elif opcao == '2':
            ProdutoMaisVendidoPordata()
            
        elif opcao == '3':
            GerarRelatorioVendasTotais()

        elif opcao == '4':
            RelatorioVendasPorProduto()

        elif opcao== '5':
            RelatorioAgrupado()
        
        elif opcao== '6':    
            print("Voltando ao menu principal...")
            break
        else:
            print("Opção inválida! Tente novamente.")

def registrar_log(nome_arquivo, usuario):
    caminho_log = os.path.join(PASTA_RELATORIOS, "log_de_geracoes.txt")
    with open(caminho_log, mode="a", encoding="utf-8") as log:
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        log.write(f"[{data_hora}] Relatório gerado: {nome_arquivo} | Usuário: {usuario}\n")

# Gerenciar o estoque (Listar, Remover e Editar)
def GerenciarEstoque():
    while True:
        print('---' * 20)
        print()
        print("GERENCIAR ESTOQUE!")
        print()
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

# Função para gerar o relatório de vendas totais
def GerarRelatorioVendasTotais():
    print("\n--- Relatório de Vendas Totais ---")
    if not lista_vendas:
        print("Nenhuma venda registrada ainda.")
        return
    total_vendas = sum(venda.preco * venda.quantidade for venda in lista_vendas)
    total_produtos_vendidos = len(lista_vendas)
    total_unidades_vendidas = sum(venda.quantidade for venda in lista_vendas)
    
    nome_arquivo = f"relatorio_vendas_totais_{date.today().strftime('%d-%m-%Y')}.csv"
    caminho_arquivo = os.path.join(PASTA_RELATORIOS, nome_arquivo)
    with open(caminho_arquivo, mode='w', newline='', encoding='utf-8') as arquivo_csv:
        escritor = csv.writer(arquivo_csv)
        escritor.writerow(['Produto','Preço unitário','Quantidade','Data da Venda','Subtotal','Vendedor'])
        for venda in lista_vendas:
            escritor.writerow([
                venda.produto.nome,
                f"{venda.preco:.2f}",
                venda.quantidade,
                venda.data_venda.strftime('%d/%m/%Y'),
                f"{venda.preco * venda.quantidade:.2f}",
                venda.vendedor if venda.vendedor else "Não informado"
            ])
        escritor.writerow([len(lista_vendas), total_produtos_vendidos, total_unidades_vendidas, f"{total_vendas:.2f}"])
    print(f"\nRelatório CSV gerado com sucesso: {caminho_arquivo}")
    usuario = input("Digite o seu nome: ")
    registrar_log(nome_arquivo, usuario)
    print(f"Relatório de vendas totais gerado com sucesso por {usuario}!")
    
    # Gerar arquivo CSV
    nome_arquivo = f"relatorio_vendas_totais_{date.today().strftime('%d-%m-%Y')}.csv"
    with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as arquivo_csv:
        escritor = csv.writer(arquivo_csv)

        escritor.writerow([
        'Produto',
        'Preço unitário',
        'Quantidade',
        'Data da Venda',
        'Subtotal',
        'Vendedor'
    ])
        for venda in lista_vendas:
            escritor.writerow([
            venda.produto.nome,
            f"{venda.preco:.2f}",
            venda.quantidade,
            venda.data_venda.strftime('%d/%m/%Y'),
            f"{venda.preco * venda.quantidade:.2f}",
            venda.vendedor if venda.vendedor else "Não informado"
        ])

        escritor.writerow([len(lista_vendas), total_produtos_vendidos, total_unidades_vendidas, f"{total_vendas:.2f}"])
    print(f"\nRelatório CSV gerado com sucesso: {nome_arquivo}")

    # Registrar log
    usuario = input("Digite o seu nome: ")
    registrar_log=(nome_arquivo, usuario)
    print(f"Relatório de vendas totais gerado com sucesso por {usuario}!")

# Função para relatório de produtos mais vendidos por data
def ProdutoMaisVendidoPordata():
    print("\n--- Relatório de vendas ---")
    if not lista_produtos:
        print("Nenhuma venda registrada ainda.")
        return
    
    print("Escolha o filtro para o relatório:")
    print("1 - Dia específico")
    print("2 - Mês específico")
    print("3 - Semana específica")
    opcao = input("Opção (1/2/3): ").strip()


    filtro_nome = ""
    vendas_filtradas = []


    if opcao == '1':
        data_str = input("Digite o dia (dd/mm/aaaa): ").strip()
        try:
            data_filtro = datetime.strptime(data_str, "%d/%m/%Y").date()
        except ValueError:
            print("Data inválida!")
            return
        vendas_filtradas = [v for v in lista_vendas if v.data_venda == data_filtro]
        filtro_nome = f"dia_{data_filtro.strftime('%d-%m-%Y')}"
    elif opcao == '2':
        mes_ano_str = input("Digite o mês e ano (mm/aaaa): ").strip()
        try:
            mes_ano = datetime.strptime(mes_ano_str, "%m/%Y")
        except ValueError:
            print("Mês/Ano inválido!")
            return
        vendas_filtradas = [v for v in lista_vendas if v.data_venda.year == mes_ano.year and v.data_venda.month == mes_ano.month]
        filtro_nome = f"mes_{mes_ano.strftime('%m-%Y')}"
    elif opcao == '3':
        data_str = input("Digite uma data da semana desejada (dd/mm/aaaa): ").strip()
    try:
        data_base = datetime.strptime(data_str, "%d/%m/%Y").date()
    except ValueError:
        print("Data inválida!")
        return
    inicio_semana = data_base - timedelta(days=data_base.weekday())
    fim_semana = inicio_semana + timedelta(days=6)
    vendas_filtradas = [v for v in lista_vendas if inicio_semana <= v.data_venda <= fim_semana]
    filtro_nome = f"semana_{inicio_semana.strftime('%d-%m-%Y')}_a_{fim_semana.strftime('%d-%m-%Y')}"


    if not vendas_filtradas:
        print("Nenhuma venda encontrada para o período.")
        return


    total_vendas = sum(v.preco * v.quantidade for v in vendas_filtradas)
    nome_arquivo = f"relatorio_vendas_{filtro_nome}.csv"
    caminho_arquivo = os.path.join(PASTA_RELATORIOS, nome_arquivo)
    with open(caminho_arquivo, mode='w', newline='', encoding='utf-8') as arquivo_csv:
        escritor = csv.writer(arquivo_csv)
        escritor.writerow(['Produto','Preço Unitário','Quantidade','Data da Venda','Subtotal','Vendedor'])
        for venda in vendas_filtradas:
            subtotal = venda.preco * venda.quantidade
            escritor.writerow([
                venda.produto.nome,
                f"{venda.preco:.2f}",
                venda.quantidade,
                venda.data_venda.strftime('%d/%m/%Y'),
                f"{subtotal:.2f}",
                venda.vendedor if venda.vendedor else "N/A"
            ])
        escritor.writerow([])
        escritor.writerow(['','','','Total Geral', f"{total_vendas:.2f}"])
    usuario = input("Digite o seu nome: ")
    registrar_log(nome_arquivo, usuario)
    print(f"Relatório CSV gerado com sucesso: {caminho_arquivo}")

    # Gerar arquivo CSV
    nome_arquivo = f"relatorio_vendas_{filtro_nome}.csv"
    with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as arquivo_csv:
        escritor = csv.writer(arquivo_csv)
        escritor.writerow(['Produto', 'Preço Unitário', 'Quantidade', 'Data da Venda', 'Subtotal', 'Vendedor'])
        for venda in vendas_filtradas:
            subtotal = venda.preco * venda.quantidade
            escritor.writerow([
                venda.produto.nome,
                f"{venda.preco:.2f}",
                venda.quantidade,
                venda.data_venda.strftime('%d/%m/%Y'),
                f"{subtotal:.2f}",
                venda.vendedor if venda.vendedor else "N/A"
            ])
        escritor.writerow([])
        escritor.writerow(['', '', '', 'Total Geral', f"{total_vendas:.2f}"])

    usuario = input("Digite o seu nome: ")
    registrar_log(nome_arquivo, usuario)
    print(f"Relatório de vendas por {usuario} gerado com sucesso!")

    print(f"Relatório CSV gerado com sucesso: {nome_arquivo}")


def ProdutoMaisVendido():
    print("\n--- Produtos Mais Vendidos ---")

    if not registro_vendas:
        print("Nenhuma venda registrada ainda.")
        print('---' * 20)
        return

    # Determina o produto mais vendido
    produto_mais_vendido = max(registro_vendas, key=registro_vendas.get)
    quantidade_mais_vendida = registro_vendas[produto_mais_vendido]

    print(f'Produto mais vendido: {produto_mais_vendido} | {quantidade_mais_vendida} unidades vendidas')
    print('---' * 20)
    print(f'Total de produtos vendidos: {len(registro_vendas)} itens e {sum(registro_vendas.values())} unidades no total')
    print('---' * 20)

    # Ordenar o dicionário por quantidade vendida (valor), em ordem decrescente
    produtos_ordenados = sorted(registro_vendas.items(), key=lambda item: item[1], reverse=True)

    for produto, quantidade in produtos_ordenados:
        print(f"Produto: {produto} | Quantidade vendida: {quantidade}")

#relatório agrupado, para melhor visualização dos dados
def RelatorioAgrupado():
    print("\n" + "="*60)
    print("📊 PAINEL DE RELATÓRIOS DE VENDAS".center(60))
    print("="*60)

    # Seção 1: Produto Mais Vendido
    print("\n🥇 PRODUTO MAIS VENDIDO (GERAL)")
    if not lista_vendas:
        print("Nenhuma venda registrada ainda.")
    else:
        # Agrupar vendas por produto: quantidade e total em reais
        vendas_por_produto = {}
        for venda in lista_vendas:
            nome = venda.produto.nome
            if nome not in vendas_por_produto:
                vendas_por_produto[nome] = {"quantidade": 0, "total_reais": 0.0}
            vendas_por_produto[nome]["quantidade"] += venda.quantidade
            vendas_por_produto[nome]["total_reais"] += venda.quantidade * venda.preco

        produto_mais_vendido = max(vendas_por_produto, key=lambda k: vendas_por_produto[k]["quantidade"])
        quantidade_mais_vendida = vendas_por_produto[produto_mais_vendido]["quantidade"]

        print(f"- Produto mais vendido: {produto_mais_vendido}")
        print(f"- Quantidade total vendida: {quantidade_mais_vendida} unidade(s)")

        # Ranking de vendas por quantidade + valor total vendido
        print("\n📦 Ranking de vendas:")
        produtos_ordenados = sorted(vendas_por_produto.items(), key=lambda item: item[1]["quantidade"], reverse=True)
        for idx, (produto, dados) in enumerate(produtos_ordenados, 1):
            print(f"{idx}º - {produto}: {dados['quantidade']} unidade(s) - R$ {dados['total_reais']:.2f}")

        print(f"\n- Total de produtos distintos vendidos: {len(vendas_por_produto)}")
        print(f"- Total geral de unidades vendidas: {sum(d['quantidade'] for d in vendas_por_produto.values())}")

    # Seção 2: Vendas Totais
    print("\n" + "-"*60)
    print("💰 RELATÓRIO DE VENDAS TOTAIS")
    print("-"*60)
    if not lista_vendas:
        print("Nenhuma venda registrada ainda.")
    else:
        total_faturamento = sum(venda.preco * venda.quantidade for venda in lista_vendas)
        total_vendas = len(lista_vendas)
        total_unidades_vendidas = sum(venda.quantidade for venda in lista_vendas)
        produtos_distintos = set(venda.produto.nome for venda in lista_vendas)

        print(f"- Total de vendas registradas: {total_vendas}")
        print(f"- Total de produtos distintos vendidos: {len(produtos_distintos)}")
        print(f"- Total de unidades vendidas: {total_unidades_vendidas}")
        print(f"- Faturamento total: R$ {total_faturamento:.2f}")

    print("\n📁 Os relatórios detalhados por data ainda devem ser gerados separadamente.")
    print("Use a opção [2] do menu de relatórios para aplicar filtros por dia/semana/mês.")
    print("="*60)

def RelatorioVendasPorProduto():
    print("\nRelatório de vendas por produto:")
    
    if not lista_vendas:
        print("Nenhuma venda registrada ainda.")
        return

    vendas_por_produto = {}
    
    # Agrupa as vendas por nome do produto
    for venda in lista_vendas:
        nome_produto = venda.produto.nome
        if nome_produto not in vendas_por_produto:
            vendas_por_produto[nome_produto] = {
                "quantidade": 0,
                "total_reais": 0.0,
                "preco_unitario": venda.produto.preco
            }
        vendas_por_produto[nome_produto]["quantidade"] += venda.quantidade
        vendas_por_produto[nome_produto]["total_reais"] += venda.quantidade * venda.produto.preco

    # Determina o produto mais vendido
    produto_mais_vendido = max(vendas_por_produto.items(), key=lambda item: item[1]["quantidade"])
    nome_mais_vendido = produto_mais_vendido[0]
    quantidade_mais_vendida = produto_mais_vendido[1]["quantidade"]

    print(f"- Produto mais vendido: {nome_mais_vendido}")
    print(f"- Quantidade total vendida: {quantidade_mais_vendida} unidades\n")

    print("📦 Ranking de vendas (por quantidade):")
    ranking = sorted(vendas_por_produto.items(), key=lambda item: item[1]["quantidade"], reverse=True)

    total_geral_unidades = 0
    total_geral_reais = 0.0

    for idx, (produto, dados) in enumerate(ranking, 1):
        qtd = dados["quantidade"]
        total = dados["total_reais"]
        total_geral_unidades += qtd
        total_geral_reais += total
        print(f"{idx}º - {produto}: {qtd} unidade(s) - R$ {total:.2f}")

    print(f"\n- Total de produtos distintos vendidos: {len(vendas_por_produto)}")
    print(f"- Total geral de unidades vendidas: {total_geral_unidades}")
    print(f"- Total geral em vendas (R$): R$ {total_geral_reais:.2f}")

# Listar produtos (incluindo vencidos)
def ListarProdutos():
    print('---' * 20)
    # Verifica se há produtos cadastrados
    if not lista_produtos:
        print("Nenhum produto cadastrado.")
        return

    # Exibe os produtos cadastrados
    for i, produto in enumerate(lista_produtos, 1):
        print(f"[{i}] - {produto}")

    print('---' * 20)


# Remover produto pelo índice ou nome
def RemoverProduto():
    print('---' * 20)
    # Verifica se há produtos cadastrados
    ListarProdutos()
    if not lista_produtos:
        print("Nenhum produto cadastrado.")
        return
    
    # Exibe os produtos cadastrados
    try:
        escolha = int(input("Escolha o número do produto a remover: "))
        # Verifica se a escolha é válida não permintindo números negativos ou maiores que o número de produtos cadastrados
        # Se a escolha não for válida, exibe mensagem de erro e retorna ao menu principal de gerenciamento de estoque
        if escolha < 1 or escolha > len(lista_produtos):
            print("Opção inválida. Tente novamente.")
            return
        # Verifica se o produto existe na lista
        produto = lista_produtos[escolha - 1]
        # Confirmação de remoção
        confirmar = input(f"Você tem certeza que deseja remover o produto '{produto.nome}'? [s/n]: ").upper()
        if confirmar != 'S':
            print("Operação cancelada.")
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
        # Verifica se a escolha é válida
        if escolha < 1 or escolha > len(lista_produtos):
            # Se a escolha não for válida, exibe mensagem de erro e retorna ao menu principal de gerenciamento de estoque
            print("Opção inválida. Tente novamente.")
            return
        # Verifica se o produto existe na lista
        produto = lista_produtos[escolha - 1]
        
        print(f"Editando produto: {produto}")
        # Solicita os novos dados do produto
        # Se o usuário não digitar nada, mantém o valor atual
        # Se o preço for negativo, mantém o valor atual
        nome = input(f"Nome do produto: (atualmente '{produto.nome}'): ").strip()
        while nome and not re.fullmatch(r"[A-Za-zÀ-ÿ0-9 ]+", nome): 
            print("Nome inválido! O nome do produto não pode conter apenas números. Por favor, digite um nome válido.")
            nome = input(f"Nome do produto: (atualmente '{produto.nome}'): ").strip()
            if not nome:
                print("Nome não pode ser vazio. Produto não editado.")
                return

        if nome:
            if not nome.isdigit():
                produto.nome = nome
            else:
                print("Nome inválido! Produto não editado.")
                return
        # Se o preço for negativo, mantém o valor atual
        preco = float(input(f"Novo preço (atualmente R${produto.preco}): "))
        # Verifica se o preço é um número positivo
        if preco < 0:
            print("Preço inválido! Produto não editado.")
            return
        
        # Se a quantidade for negativa, mantém o valor atual
        quantidade = int(input(f"Nova quantidade (atualmente {produto.quantidade}): "))
        # Verifica se a quantidade é um número inteiro positivo
        if quantidade < 0:
            print("Quantidade inválida! Produto não editado.")
            return
        # Se a validade for inválida, mantém o valor atual
        validade = input(f"Nova validade (atualmente {produto.validade}) (dd/mm/aaaa): ")

        try:
            # Verifica se a validade não está vazia
            if not validade:
                print("Data de validade não pode ser vazia!.")
                return 
            # Verifica se a validade está no formato correto
            # Se a validade não estiver no formato correto, ignora a venda
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


# Compra de produtos
def ComprarProduto():
    global lista_produtos, carrinho_de_compras, lista_vendas  # Se forem globais

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
            if not (1 <= resposta <= len(lista_produtos)):
                print("Número inválido! Tente novamente.")
                continue
            produto_escolhido = lista_produtos[resposta - 1]
        except (ValueError, IndexError):
            print("Opção inválida. Tente novamente.")
            continue

        if produto_escolhido.quantidade == 0:
            print(f'O produto "{produto_escolhido.nome}" está sem estoque!')
            if input('Deseja comprar outro produto? [s/n]: ').strip().upper() == 'N':
                return
            continue

        while True:
            quantidade_input = input('Digite a quantidade que deseja: ').strip()
            if not quantidade_input.isdigit():
                print("Entrada inválida! Digite um número inteiro positivo.")
                continue

            quantidade_desejada = int(quantidade_input)

            if quantidade_desejada <= 0:
                print("Quantidade inválida! Digite um número maior que zero.")
                continue

            if quantidade_desejada > produto_escolhido.quantidade:
                print(f"Quantidade indisponível. Só temos {produto_escolhido.quantidade} unidade(s) em estoque.")
                continue

            break

        # Adiciona ao carrinho
        produto_escolhido.quantidade -= quantidade_desejada
        carrinho_de_compras.append((produto_escolhido.nome, produto_escolhido.preco, quantidade_desejada))
        lista_vendas.append(Venda(produto_escolhido, quantidade_desejada, date.today()))
        print(f'Produto "{produto_escolhido.nome}" adicionado ao carrinho!')

        print('---' * 20)
        print('Produtos no carrinho:')
        for i in carrinho_de_compras:
            print(f'{i[0]} | Preço: R${i[1]:.2f} | Quantidade: {i[2]}')
        print('---' * 20)

        while True:
            continuar = input('Deseja adicionar outro produto ao carrinho? [s/n]: ').strip().upper()
            if continuar not in ['S', 'N']:
                print("Opção inválida! Digite apenas 's' ou 'n'.")
                continue
            break

        if continuar == 'N':
            if not carrinho_de_compras:
                print('Seu carrinho está vazio')
                while True:
                    nova_venda = input('Deseja cadastrar uma nova venda? [s/n]: ').strip().upper()
                    if nova_venda not in ['S', 'N']:
                        print("Opção inválida. Digite apenas 's' ou 'n'.")
                        continue
                    if nova_venda == 'S':
                        ComprarProduto()
                    return
            else:
                resultado = FinalizarOuCancelarCompra()
                if resultado == 'continuar':
                    continue
                return

# Finalização da compra
def FinalizarCompra():
    total = 0
    nota = []
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    while True:
        nome_vendedor = input('Digite o nome do vendedor (ou deixe em branco): ').strip()
        if nome_vendedor == "":
            nota.append("Vendedor: Não informado\n")
            break
        elif re.fullmatch(r"[A-Za-zÀ-ÿ\s]+", nome_vendedor):
            nota.append(f"Vendedor: {nome_vendedor}\n")
            break
        else:
            print("Nome inválido! Use apenas letras e espaços.")
    nota.append(f"Data da compra: {data_hora}\n")
    nota.append("Itens comprados:")
    for nome, preco, qtd in carrinho_de_compras:
        subtotal = preco * qtd
        nota.append(f"{nome} | Preço: R${preco:.2f} | Quantidade: {qtd} | Subtotal: R${subtotal:.2f}")
        total += subtotal
        if nome in registro_vendas:
            registro_vendas[nome] += qtd
        else:
            registro_vendas[nome] = qtd
    nota.append(f"\nTotal a pagar: R${total:.2f}")
    for linha in nota:
        print(linha)
    caminho_nota = os.path.join(PASTA_RELATORIOS, "nota_fiscal.txt")
    with open(caminho_nota, "w", encoding="utf-8") as arquivo:
        arquivo.write("NOTA FISCAL\n")
        arquivo.write("="*40 + "\n")
        for linha in nota:
            arquivo.write(linha + "\n")
        arquivo.write("="*40 + "\n")
        arquivo.write("Obrigado pela sua compra!\n")
    print(f"\nNota Fiscal gerada com sucesso: {caminho_nota}")
    carrinho_de_compras.clear()


# Confirmação ou cancelamento da compra
def FinalizarOuCancelarCompra():
    while True:
        print("\nDeseja confirmar a venda ou cancelar?")
        print("[1] Confirmar venda")
        print("[2] Cancelar venda")
        decisao = input("Digite sua escolha: ").strip().upper()
           
        if decisao == '1':
            FinalizarCompra()
            break
        elif decisao == '2':
            while True:
                confirmar = input("Você tem certeza que deseja cancelar a compra? [s/n]: ").strip().upper()
                if confirmar not in ['S', 'N']:
                    print("Opção inválida, digite apenas 's' ou 'n'.")
                    continue

                if confirmar == 'S':
                    CancelarCompra()
                else:
                    print("Compra não cancelada. Retornando a produto")
                    return 'continuar'
                
                break  # Sai da confirmação

            break  # Sai da função após a decisão
        else:
            print("Opção inválida. Tente novamente.")



# Cancelamento de compra
## Cancela a compra e devolve os produtos ao estoque
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
# Loop principal
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
        # ComprarProduto() (mantém função original)
    elif resposta == 2:
        # CadastroProduto()
        pass
    elif resposta == 3:
        # GerenciarEstoque()
        pass
    elif resposta == 4:
        # ImportarVendasCSV()
        pass
    elif resposta == 5:
        # Relatorios()
        pass
    elif resposta == 6:
        print('Saindo do sistema. Até logo!')
        break
    else:
        print("Opção inválida. Tente novamente.")


print('=-=' * 20)
print("Obrigado por usar o sistema de vendas!")
