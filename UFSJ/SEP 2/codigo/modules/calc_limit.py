import numpy as np


def limite_v(DBAR, SAVEPATH, FILEPATH, contingencia=False):
    """
    Adiciona ao arquvio 'SAVEPATH' o relatório de limites das tensões.

    Argumento:
        DBAR: Dados de barra.
        SAVEPATH: Caminho do arquivo.
        FILEPATH: Caminho do arquivo original sem extensao
        contingencia: Define os limites operativos de acordo com o ONS
    """
    R500, R440, R345, R230, R138 = regioes_v(FILEPATH)

    # adicionando a tensão em suas respectivas barras, caso nao listadas, o default é 138kV
    DBAR["V nom(kV)"] = np.select(
        [
            DBAR["BARRA"].isin(R500),  # Se "BARRA" está em R500
            DBAR["BARRA"].isin(R440),  # Se "BARRA" está em R440
            DBAR["BARRA"].isin(R345),  # Se "BARRA" está em R345
            DBAR["BARRA"].isin(R230),  # Se "BARRA" está em R230
            DBAR["BARRA"].isin(R138),  # Se "BARRA" está em R138
        ],
        [
            500,  # Valor correspondente para R500
            440,  # Valor correspondente para R440
            345,  # Valor correspondente para R345
            230,  # Valor correspondente para R230
            138,  # Valor correspondente para R138
        ],
        default=138,  # Valor padrão
    )

    limites_tensao = {
        500: {True: {"max": 1.10, "min": 0.95}, False: {"max": 1.10, "min": 1.00}},
        440: {True: {"max": 1.046, "min": 0.90}, False: {"max": 1.046, "min": 0.95}},
        345: {True: {"max": 1.05, "min": 0.90}, False: {"max": 1.05, "min": 0.95}},
        230: {True: {"max": 1.05, "min": 0.90}, False: {"max": 1.05, "min": 0.95}},
        138: {True: {"max": 1.05, "min": 0.90}, False: {"max": 1.05, "min": 0.95}},
    }

    # Inicializando dicionário para armazenar os relatorios de tensao
    mensagens = {
        500: {"acima": [], "abaixo": []},
        440: {"acima": [], "abaixo": []},
        345: {"acima": [], "abaixo": []},
        230: {"acima": [], "abaixo": []},
        138: {"acima": [], "abaixo": []},
    }

    for k in DBAR.index:
        barra = DBAR.loc[k, "BARRA"]
        v_esp = DBAR.loc[k, "Vesp(PU)"]
        v_nominal = DBAR.loc[k, "V nom(kV)"]
        limites = limites_tensao.get(v_nominal, {}).get(contingencia, {})

        if limites:
            if v_esp > limites["max"]:
                mensagens[v_nominal]["acima"].append(
                    f"\nBarra {barra} → {v_esp:.4f} pu"
                )
            elif v_esp < limites["min"]:
                mensagens[v_nominal]["abaixo"].append(
                    f"\nBarra {barra} → {v_esp:.4f} pu"
                )

    with open(SAVEPATH, "a") as file:
        if not mensagens[v_nominal]["acima"] and not mensagens[v_nominal]["abaixo"]:
            file.write("\n\nNão há limites de tensão sendo violados.\n\n")
        else:
            for tensao, valores in mensagens.items():
                file.write(
                    f"\n\nBarras que estão acima do limite máximo de tensão na região de {tensao}kV:\n{''.join(valores["acima"])}"
                    if valores["acima"]
                    else ""
                )
                file.write(
                    f"\n\nBarras que estão abaixo do limite mínimo de tensão na região de {tensao}kV:\n{''.join(valores["abaixo"])}"
                    if valores["abaixo"]
                    else ""
                )


def limite_lt(fluxo, DCIR, S_BASE, SAVEPATH, contingencia=False):
    """
    Adiciona ao arquvio 'SAVEPATH' o relatório de limites das linhas de transmissão.

    Argumento:
        fluxo: DataFrame com a solução do fluxo de potência do circuito.
        DCIR: DataFrame com os dados dos circuitos.
        S_BASE: Base das potências.
        SAVEPATH: Caminho do arquivo.
        contingencia: Define os limites operativos de acordo com o ONS
    """
    DCIR["Carregamento k-m"] = 0.0
    DCIR["Carregamento m-k"] = 0.0
    DCIR["Carregamento k-m"] = (fluxo["Skm (MVA)"]) / (DCIR["CAP(PU)"] * S_BASE)
    DCIR["Carregamento m-k"] = (fluxo["Smk (MVA)"]) / (DCIR["CAP(PU)"] * S_BASE)
    CritCirc = ""

    for k in DCIR.index[DCIR["LIG(L)DESL(D)"] == "L"]:
        carregamento_km = DCIR.loc[k, "Carregamento k-m"]
        carregamento_mk = DCIR.loc[k, "Carregamento m-k"]
        NCIR = DCIR.loc[k, "NCIR"]
        bde = DCIR.loc[k, "BDE"]
        bpara = DCIR.loc[k, "BPARA"]
        cap_pu = DCIR.loc[k, "CAP(PU)"]

        if carregamento_km > 0.80 or carregamento_mk > 0.80:
            if carregamento_km > carregamento_mk:
                CritCirc += (
                    f"Circuito {NCIR:2} ({bde:2} - {bpara:2}) → {fluxo.loc[k, 'Skm (MVA)'] / S_BASE:7.4f} pu | "
                    f"{cap_pu:10.4f} pu de capacidade. {carregamento_km:12.2%}\n"
                )
            else:
                CritCirc += (
                    f"Circuito {NCIR:2} ({bpara:2} - {bde:2}) → {fluxo.loc[k, 'Smk (MVA)'] / S_BASE:7.4f} pu | "
                    f"{cap_pu:10.4f} pu de capacidade. {carregamento_mk:12.2%}\n"
                )

    with open(SAVEPATH, "a") as file:
        file.write(
            f"\n\nCircuitos sobrecarregados:\n{
                   CritCirc}"
            if CritCirc
            else "\n\nNão há circuitos sobrecarregados.\n"
        )

    with open(SAVEPATH, "a") as file:
        file.write(f"\n\nSeveridade:\n{fluxo["Sobrecarga"].sum():.4f}")

    mean_km = DCIR.loc[DCIR["LIG(L)DESL(D)"] == "L", "Carregamento k-m"].mean()
    mean_mk = DCIR.loc[DCIR["LIG(L)DESL(D)"] == "L", "Carregamento m-k"].mean()

    with open(SAVEPATH, "a") as file:
        file.write(
            f"\n\nMédia do carregamento dos circuitos:\n{mean_km:.2%}"
            if mean_km > mean_mk
            else f"\n\nMédia do carregamento dos circuitos:\n{mean_mk:.2%}"
        )


def limite_gen(DBAR, SAVEPATH):
    """
    Adiciona ao arquvio 'SAVEPATH' o relatório de limites dos geradores.

    Argumento:
        DBAR: DataFrame com os dados das barras.
        SAVEPATH: Caminho do arquivo.
    """
    geracao = {"acima": [], "abaixo": []}
    DBAR["PG(PU)"] = DBAR["PG(PU)"] + DBAR["PGesp(PU)"]

    for k in DBAR.index:
        pg_pu = DBAR.loc[k, "PG(PU)"]
        cgmax_pu = DBAR.loc[k, "CGmax(PU)"]
        cgmin_pu = DBAR.loc[k, "CGmin(PU)"]
        barra = DBAR.loc[k, "BARRA"]

        if pg_pu > cgmax_pu * 0.9:
            geracao["acima"].append(
                f"Gerador da barra {barra} → {
                                    pg_pu:.4f} pu: Capacidade {cgmax_pu:.4f} pu\n"
            )
        elif pg_pu < cgmin_pu * 1.1:
            geracao["abaixo"].append(
                f"Gerador da barra {barra} → {
                                     pg_pu:.4f} pu: Capacidade {cgmin_pu:.4f} pu\n"
            )

    with open(SAVEPATH, "a") as file:
        if not geracao["acima"] and not geracao["abaixo"]:
            file.write("\n\nNão há limites de geração sendo violados.\n")
        else:
            for key, valores in geracao.items():
                file.write(
                    f"\n\nGeradores que estão acima do limite máximo de geração de potência ativa:\n{''.join(valores)}"
                    if key == "acima" and valores
                    else ""
                )
                file.write(
                    f"\n\nGeradores que estão abaixo do limite mínimo de geração de potência ativa:\n{''.join(valores)}"
                    if key == "abaixo" and valores
                    else ""
                )


def regioes_v(FILEPATH):
    regioes = {}
    try:
        with open(FILEPATH + "_config.txt", "r") as file:
            linhas = file.read().splitlines()

        for linha in linhas:
            # Avaliar cada linha para transformar em uma lista
            try:
                nome, valores = linha.strip("\n").split("=")
                regioes[nome] = eval(valores)
            except ValueError:
                continue
    except FileNotFoundError:
        # Se o arquivo não for encontrado, retorna regioes vazias,
        # consequentemente as barras serao 138kV
        return [], [], [], [], []

    # Acessar as regioes
    R500 = regioes.get("R500", [])
    R440 = regioes.get("R440", [])
    R345 = regioes.get("R345", [])
    R230 = regioes.get("R230", [])
    R138 = regioes.get("R138", [])
    return R500, R440, R345, R230, R138
