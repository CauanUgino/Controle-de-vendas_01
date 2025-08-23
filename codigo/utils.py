"""
============================================================
utils.py
Funções auxiliares para o sistema.
Atualmente contém a função de registrar logs de geração de relatórios.
============================================================
"""

from datetime import datetime


def registrar_log(nome_arquivo, usuario):
    """Registra um histórico sempre que um relatório é criado."""
    with open("log_de_geracoes.txt", "a", encoding="utf-8") as log:
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        log.write(
            f"[{data_hora}] Relatório gerado: {nome_arquivo} | Usuário: {usuario}\n"
        )


"""Final do módulo"""
