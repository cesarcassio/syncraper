import numpy as np
import pandas as pd


def calc_fluxo(DBAR, DCIR, Sbase):
    """
    Calcula o fluxo de potência dos circuitos.
    Argumento:
        DBAR: Dados de barra.
        DBAR: Dados dos circuitos.
        Sbase: Base das potências.
    Retorna:
        Fluxo: DataFrame com o fluxo de potência calculado.
    """
    Theta = np.radians(DBAR["Oesp(°)"])
    colunas = [
        "DE",
        "PARA",
        "NCIR",
        "Pkm (MW)",
        "Qkm (MVAr)",
        "Skm (MVA)",
        "Pmk (MW)",
        "Qmk (MVAr)",
        "Smk (MVA)",
        "Perdas(MW)",
        "Perdas(MVAr)",
        "Capacidade (MVA)",
    ]
    Fluxo = pd.DataFrame(
        np.zeros(((DCIR["NCIR"].max()), len(colunas))), columns=colunas
    )
    Fluxo["NCIR"] = DCIR["NCIR"]
    Fluxo["DE"] = DCIR["BDE"]
    Fluxo["PARA"] = DCIR["BPARA"]
    Fluxo["Capacidade (MVA)"] = DCIR["CAP(PU)"] * Sbase
    Fluxo["Carregamento (%)"] = 0.0
    for i in DCIR.index[DCIR["LIG(L)DESL(D)"] == "L"]:

        k = DCIR.loc[i, "BDE"] - 1  # Barra DE
        m = DCIR.loc[i, "BPARA"] - 1  # Barra PARA

        r = DCIR.loc[i, "RES(PU)"]
        x = DCIR.loc[i, "REAT(PU)"]

        bsh = (DCIR.loc[i, "SUCsh(PU)"]) / 2  # shunt/2
        tap = DCIR.loc[i, "TAP(PU)"]  # Tap
        phi = DCIR.loc[i, "DEF(RAD)"]  # defasagem

        gkm = r/(r**2+x**2)
        bkm = -x/(r**2+x**2)

        Vk = DBAR.loc[k, "Vesp(PU)"]
        Vm = DBAR.loc[m, "Vesp(PU)"]

        # Equações do Fluxo Sentido K --> M
        Pkm = (
            ((tap * Vk) ** 2) * gkm
            - (tap * Vk) * Vm * gkm * np.cos((Theta[k] - Theta[m]) + phi)
            - (tap * Vk) * Vm * bkm * np.sin((Theta[k] - Theta[m]) + phi)
        )

        Qkm = (
            -((tap * Vk) ** 2) * (bkm + bsh)
            + (tap * Vk) * Vm * bkm * np.cos((Theta[k] - Theta[m]) + phi)
            - (tap * Vk) * Vm * gkm * np.sin((Theta[k] - Theta[m]) + phi)
        )

        # Equações do Fluxo Sentido M --> K
        Pmk = (
            (Vm**2) * gkm
            - (tap * Vk) * Vm * gkm * np.cos((Theta[m] - Theta[k]) - phi)
            - (tap * Vk) * Vm * bkm * np.sin((Theta[m] - Theta[k]) - phi)
        )

        Qmk = (
            -(Vm**2) * (bkm + bsh)
            + (tap * Vk) * Vm * bkm * np.cos((Theta[m] - Theta[k]) - phi)
            - (tap * Vk) * Vm * gkm * np.sin((Theta[m] - Theta[k]) - phi)
        )

        Skm = np.sqrt(Pkm**2 + Qkm**2)
        Smk = np.sqrt(Pmk**2 + Qmk**2)
        if Skm >= Smk:
            Fluxo.loc[i, "Carregamento (%)"] = (Skm/DCIR.loc[i, "CAP(PU)"])*100
        else:
            Fluxo.loc[i, "Carregamento (%)"] = (Smk/DCIR.loc[i, "CAP(PU)"])*100

        Fluxo.loc[i, "Pkm (MW)"] = Pkm * Sbase  # Fluxo ativo Pkm
        Fluxo.loc[i, "Pmk (MW)"] = Pmk * Sbase
        Fluxo.loc[i, "Qkm (MVAr)"] = Qkm * Sbase  # Fluxo reativo Qkm
        Fluxo.loc[i, "Skm (MVA)"] = Skm * Sbase  # Fluxo aparente Skm
        Fluxo.loc[i, "Smk (MVA)"] = Smk * Sbase  # Fluxo aparente Smk
        Fluxo.loc[i, "Qmk (MVAr)"] = Qmk * Sbase  # Fluxo reativo Qmk
        Fluxo.loc[i, "Perdas(MVAr)"] = (Qkm + Qmk) * Sbase  # Perdas reativas
        Fluxo.loc[i, "Perdas(MW)"] = (Pkm + Pmk) * Sbase

    return Fluxo


def calc_sobrecarga_ac(DCIR, fluxo):
    fluxo["Sobrecarga"] = 0.0000
    for i in DCIR.index[DCIR["LIG(L)DESL(D)"] == "L"]:
        Skm = np.abs(fluxo.loc[i, "Skm (MVA)"])
        Smk = np.abs(fluxo.loc[i, "Smk (MVA)"])
        cap = fluxo.loc[i, "Capacidade (MVA)"]
        if Skm >= Smk and Skm > cap:
            fluxo.loc[i, "Sobrecarga"] = (Skm-cap)/cap
        elif Smk >= Skm and Smk > cap:
            fluxo.loc[i, "Sobrecarga"] = (Smk-cap)/cap
        else:
            continue
