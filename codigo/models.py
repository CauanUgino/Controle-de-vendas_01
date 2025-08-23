"""
============================================================
models.py
Contém as classes principais do sistema.
As classes funcionam como moldes que definem as
características dos itens em questão.
============================================================
"""

from datetime import datetime, date


class Venda:
    """Representa uma venda realizada, contendo informações
    sobre produto, quantidade, data, preço e vendedor.
    """

    def __init__(self, produto, quantidade, data_venda, vendedor=None):
        self.produto = produto
        self.quantidade = quantidade
        self.data_venda = data_venda
        self.preco = produto.preco
        self.vendedor = vendedor


class Produto:
    """Representa um produto no estoque, contendo nome,
    preço, quantidade, validade e data de cadastro.
    """

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
        return (
            f"{self.nome} - R$ {self.preco:.2f} | "
            f"Estoque: {self.quantidade} | "
            f"Cadastrado em: {self.data_cadastro} | "
            f"Validade: {self.validade}"
        )

    def esta_vencido(self):
        """Retorna True se o produto estiver vencido, False caso contrário."""
        return self.validade < date.today()

    def atualizar_estoque(self, quantidade_comprada: int, lista_produtos):
        """Atualiza o estoque após uma compra e remove produtos vencidos."""
        lista_produtos[:] = [p for p in lista_produtos if not p.esta_vencido()]
        if quantidade_comprada <= self.quantidade:
            self.quantidade -= quantidade_comprada
        else:
            raise ValueError("Quantidade solicitada maior que a disponível.")

    def estoque_disponivel(self):
        """Retorna True se ainda houver unidades disponíveis do produto."""
        return self.quantidade > 0


"""Final do módulo"""
