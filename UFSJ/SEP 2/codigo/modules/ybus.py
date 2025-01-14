import numpy as np
import pandas as pd


def make_ybus(DBAR, DCIR):
    """
    Cria a Ybus através dos dados de barra e circuito.

    Argumento:
        DBAR: Dados de barra.
        DCIR: Dados dos circuitos.
    Retorna:
        Ybus.
    """
    # Inicializa a matriz Ybus com zeros complexos
    num_barras = DBAR["BARRA"].max()
    Ybus = np.zeros((num_barras, num_barras), dtype="complex")

    # Preenche a matriz Ybus com os dados dos circuitos
    for i in DCIR.index[DCIR["LIG(L)DESL(D)"] == "L"]:
        ibf = DCIR.loc[i,"BDE"] - 1  # Barra DE
        ibt = DCIR.loc[i,"BPARA"] - 1  # Barra PARA
        y = 1 / (DCIR.loc[i,"RES(PU)"] + 1j * DCIR.loc[i,"REAT(PU)"])  # 1/(r + jx)
        bsh = (1j * DCIR.loc[i,"SUCsh(PU)"]) / 2  # shunt/2
        tap = DCIR.loc[i,"TAP(PU)"]  # Tap
        phi = DCIR.loc[i,"DEF(RAD)"]  # Defasagem

        Ybus[ibf, ibf] += tap**2 * y + bsh
        Ybus[ibt, ibt] += y + bsh
        Ybus[ibt, ibf] -= tap * y * np.exp(1j * phi)
        Ybus[ibf, ibt] -= tap * y * np.exp(1j * -phi)

    # Inclui susceptância shunt nas barras
    for i in DBAR.index:
        ibus = DBAR.loc[i,"BARRA"] - 1
        Bsh = DBAR.loc[i,"Bsh(PU)"] * 1j
        if Bsh != 0:
            Ybus[ibus, ibus] += Bsh

    return Ybus
