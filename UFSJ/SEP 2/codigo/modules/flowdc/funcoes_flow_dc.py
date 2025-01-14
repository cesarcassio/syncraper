import numpy as np
import pandas as pd


def matriz_susceptancia(DCIR, DBAR):
    num_barras = DBAR["BARRA"].max()
    B = np.zeros((num_barras, num_barras))
    for i in DCIR.index[DCIR["LIG(L)DESL(D)"] == "L"]:
        k = DCIR.loc[i, "BDE"] - 1
        m = DCIR.loc[i, "BPARA"] - 1
        b = -(1 / DCIR.loc[i, "REAT(PU)"])
        B[k][k] += b
        B[k][m] = -b
        B[m][k] = -b
        B[m][m] += b

    Ref = DBAR[DBAR["TIPO"] == "SW"].index
    B = np.delete(B, Ref, axis=0)
    B = np.delete(B, Ref, axis=1)

    # return np.linalg.inv(B)
    try:
        return np.linalg.inv(B)
    except np.linalg.LinAlgError:
        x = DCIR["NCIR"][DCIR["LIG(L)DESL(D)"] != "L"].tolist()
        print(f"Erro: Matriz singular - Circuitos: {", ".join(map(str, x))}")
        return None


def calc_perdas(DCIR, Theta):
    Perdas = np.zeros(len(DCIR))
    for i in DCIR.index[DCIR["LIG(L)DESL(D)"] == "L"]:
        k = DCIR.loc[i, "BDE"] - 1
        m = DCIR.loc[i, "BPARA"] - 1
        r = DCIR.loc[i, "RES(PU)"]
        x = DCIR.loc[i, "REAT(PU)"]
        g = r / (r**2 + x**2)
        Perdas[i] += g * (Theta[k] - Theta[m]) ** 2
    DCIR["Perdas (MW)"] = Perdas


def calc_sum_perdas(DCIR, DBAR):
    perdas_bde = DCIR[["BDE", "Perdas (MW)"]].rename(columns={"BDE": "BARRA"})
    perdas_bpara = DCIR[["BPARA", "Perdas (MW)"]].rename(columns={"BPARA": "BARRA"})
    perdas_combinadas = pd.concat([perdas_bde, perdas_bpara], ignore_index=True)

    somas_perdas = perdas_combinadas.groupby("BARRA", as_index=False)[
        "Perdas (MW)"
    ].sum()

    somas_perdas["Perdas (MW)"] /= 2

    Ref = DBAR[DBAR["TIPO"] == "SW"].index
    # print(~somas_perdas["BARRA"].isin(Ref))
    somas_perdas = somas_perdas[~somas_perdas.index.isin(Ref)]
    # print(somas_perdas)
    return somas_perdas["Perdas (MW)"].to_numpy()


def calc_theta(B, P, Ref):
    theta = -B @ P
    theta = np.insert(theta, Ref, 0, axis=0)
    return theta


def calc_flow_dc(DCIR, theta, s_base):
    DCIR["Pkm (MW)"] = 0.0
    DCIR["Pmk (MW)"] = 0.0

    for i in DCIR.index[DCIR["LIG(L)DESL(D)"] == "L"]:
        k = DCIR.loc[i, "BDE"] - 1
        m = DCIR.loc[i, "BPARA"] - 1
        x = DCIR.loc[i, "REAT(PU)"]
        perdas_km = DCIR.loc[i, "Perdas (MW)"] / 2
        # tap = DCIR.loc[i, "TAP(PU)"]
        # defa = np.rad2deg(DCIR.loc[i, "DEF(GRAUS)"])

        DCIR.loc[i, "Pkm (MW)"] += ((theta[k] - theta[m])) / x + perdas_km
        DCIR.loc[i, "Pmk (MW)"] += ((theta[m] - theta[k])) / x + perdas_km

    DCIR["CAP(MW)"] = DCIR["CAP(PU)"] * s_base
    DCIR["Perdas (MW)"] *= s_base  # DCIR["Perdas (MW)"] * s_base
    DCIR["Pkm (MW)"] *= s_base  # DCIR["Pkm (MW)"] * s_base
    DCIR["Pmk (MW)"] *= s_base  # DCIR["Pmk (MW)"] * s_base


def calc_sobrecarga(DCIR):
    DCIR["Sobrecarga"] = 0.0000
    for i in DCIR.index[DCIR["LIG(L)DESL(D)"] == "L"]:
        Pkm = np.abs(DCIR.loc[i, "Pkm (MW)"])
        Pmk = np.abs(DCIR.loc[i, "Pmk (MW)"])
        cap = DCIR.loc[i, "CAP(MW)"]
        if Pkm >= Pmk and Pkm > cap:
            DCIR.loc[i, "Sobrecarga"] = (Pkm - cap) / cap
        elif Pmk >= Pkm and Pmk > cap:
            DCIR.loc[i, "Sobrecarga"] = (Pmk - cap) / cap
        else:
            continue
