import pandas as pd
from io import StringIO


def dados(filepath):
    """
    Captura os dados de barra e circuito do problema.

    Argumento:
        filepath: Caminho para o arquivo contendo os dados do problema
    Retorna:
        DBAR: Dados de barra.
        DCIR: Dados dos circuitos.
        savepath: Caminho/nome do arquivo a ser salvo após analise
    """
    savepath = filepath.split(".txt")[0] + "_relatorio.txt"

    with open(filepath, "r", encoding="latin-1") as file:
        content = file.read()

    ultimo_x_index = content.find("x")
    primeiro_hash_index = content.find("#")

    if (
        ultimo_x_index != -1
        and primeiro_hash_index != -1
        and ultimo_x_index < primeiro_hash_index
    ):
        filtered_content = content[ultimo_x_index:primeiro_hash_index]
        restante = content[primeiro_hash_index:]
    # DBAR
    content_io = StringIO(filtered_content)

    DBAR = pd.read_csv(
        content_io, delimiter=r"\s+", skiprows=2, encoding="latin-1", header=None
    )
    DBAR.columns = [
        "BARRA",
        "PD(PU)",
        "QD(PU)",
        "Bsh(PU)",
        "TIPO",
        "Vesp(PU)",
        "Oesp(°)",
        "PGesp(PU)",
        "Cus($/MW)",
        "CGmin(PU)",
        "CGmax(PU)",
    ]

    ultimo_x_index = restante.find("R")
    primeiro_hash_index = restante.rfind("#")

    if (
        ultimo_x_index != -1
        and primeiro_hash_index != -1
        and ultimo_x_index < primeiro_hash_index
    ):
        # Extrai o conteúdo entre o último 'x' e o primeiro '#'
        filtered_content = restante[ultimo_x_index +
                                    1: primeiro_hash_index - 3]

    content_io = StringIO(filtered_content)
    # Leia o conteúdo como DataFrame, assumindo que está separado por espaços
    DCIR = pd.read_csv(content_io, delimiter=r"\s+",
                       skiprows=2, encoding="latin-1")

    return [DBAR, DCIR, savepath, filepath.split(".txt")[0]]
