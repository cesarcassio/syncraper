import numpy as np
import pandas as pd


def calc_delta_pq(DBAR, vbus, theta, ybus):
    """
    Calcula o delta P e delta Q.

    Argumento:
        DBAR: Dados de barra.
        vbus: Tensões atuais das barras.
        theta: Angulos atuais das barras em radianos.
        ybus.
    Retorna:
        delta_p e delta_q
    """

    gbus, bbus = ybus.real, ybus.imag

    delta_p = np.zeros(len(DBAR))
    delta_q = np.zeros(len(DBAR))
    p_esp = DBAR["PGesp(PU)"].values - DBAR["PD(PU)"].values
    q_esp = 0 - DBAR["QD(PU)"].values
    for k in DBAR.index:
        p_calc = 0
        q_calc = 0
        for m in DBAR.index:
            p_calc += vbus[m] * (
                gbus[k][m] * np.cos(theta[k] - theta[m])
                + bbus[k][m] * np.sin(theta[k] - theta[m])
            )
            q_calc += vbus[m] * (
                gbus[k][m] * np.sin(theta[k] - theta[m])
                - bbus[k][m] * np.cos(theta[k] - theta[m])
            )

        delta_p[k] = p_esp[k] - vbus[k] * p_calc
        delta_q[k] = q_esp[k] - vbus[k] * q_calc

    return delta_p, delta_q


def calc_pot(DBAR, vbus, theta, ybus):
    """
    Calcula as potências do circuito.

    Argumento:
        DBAR: Dados de barra.
        vbus: Tensões que são solução do fluxo.
        theta: Angulos que são solução do fluxo em radianos.
        ybus.
    Retorna:
        Atualiza o DataFrame DBAR com as potências calculadas.
    """
    DBAR["PG(PU)"] = DBAR["PG(PU)"].astype(np.float64)
    DBAR["QG(PU)"] = DBAR["QG(PU)"].astype(np.float64)
    DBAR["PD(PU)"] = DBAR["PD(PU)"].astype(np.float64)
    DBAR["QD(PU)"] = DBAR["QD(PU)"].astype(np.float64)

    gbus, bbus = ybus.real, ybus.imag
    # pega o indice da referencia
    ref = DBAR[DBAR["TIPO"] == "SW"].index.to_list()
    pv = DBAR[DBAR["TIPO"] == "PV"].index.to_list()
    for k in DBAR.index:
        p_calc = 0
        q_calc = 0
        if k in ref:
            for m in DBAR.index:
                p_calc += vbus[m] * (
                    gbus[k][m] * np.cos(theta[k] - theta[m])
                    + bbus[k][m] * np.sin(theta[k] - theta[m])
                )
                q_calc += vbus[m] * (
                    gbus[k][m] * np.sin(theta[k] - theta[m])
                    - bbus[k][m] * np.cos(theta[k] - theta[m])
                )

            DBAR.loc[k, "PG(PU)"] = (vbus[k] * p_calc) + DBAR.loc[k, "PD(PU)"]
            DBAR.loc[k, "QG(PU)"] = (vbus[k] * q_calc) + DBAR.loc[k, "QD(PU)"]
        elif k in pv:
            for m in DBAR.index:
                q_calc += vbus[m] * (
                    gbus[k][m] * np.sin(theta[k] - theta[m])
                    - bbus[k][m] * np.cos(theta[k] - theta[m])
                )
                DBAR.loc[k, "QG(PU)"] = vbus[k] * q_calc + DBAR.loc[k, "QD(PU)"]


def calc_delta_theta_v(DBAR, delta_p, delta_q, jacobiana):
    """
    Calcula o vetor [delta_theta - delta_v].

    Argumento:
        DBAR: Dados de barra.
        delta_p.
        delta_q.
        jacobiana.
    Retorna:
        delta_theta e delta_v.
    """
    DeltaPQ = np.concatenate((delta_p, delta_q))
    inversa = np.linalg.inv(jacobiana)
    # try:
    #     inversa = np.linalg.inv(jacobiana)
    # except:  # noqa: E722
    #     inversa = np.linalg.pinv(jacobiana)
    delta_theta_v = np.dot(-inversa, DeltaPQ)
    delta_theta = delta_theta_v[0 : len(DBAR)]
    delta_v = delta_theta_v[len(DBAR) :]
    return delta_theta, delta_v
