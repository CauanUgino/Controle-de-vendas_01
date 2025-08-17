# ============================================================
# models.py
# Contém as classes principais do sistema:
# As classes são como moldes que contém as características dos itens em questão
# ============================================================

from datetime import datetime, date

class Venda:
    def __init__(self, produto, quantidade, data_venda, vendedor=None):
        self.produto = produto  
        self.quantidade = quantidade
        self.data_venda = data_venda  
        self.preco = produto.preco
        self.vendedor = vendedor  

class Produto:
    def __init__(self, nome, preco, quantidade, validade):
        self.nome = nome
        self.preco = preco
        self.quantidade = max(quantidade, 0)
        if isinstance(validade, str):
            self.validade = datetime.strptime(validade, "%d/%m/%Y").date()
        else:
            self.validade = validade  
        self.data_cadastro = date.today()

    def __str__(self):
        return (f"{self.nome} - R$ {self.preco:.2f} | Estoque: {self.quantidade} | "
                f"Cadastrado em: {self.data_cadastro} | Validade: {self.validade}")

    def esta_vencido(self):
        return self.validade < date.today()

    def atualizar_estoque(self, quantidade_comprada: int, lista_produtos):
        lista_produtos[:] = [p for p in lista_produtos if not p.esta_vencido()]
        if quantidade_comprada <= self.quantidade:
            self.quantidade -= quantidade_comprada
        else:
            raise ValueError("Quantidade solicitada maior que a disponível.")

    def estoque_disponivel(self):
        return self.quantidade > 0
