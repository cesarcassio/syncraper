import numpy as np
import pandas as pd


def jacobiana(DBAR, vbus, theta, ybus):
    """
    Cria a matriz jacobiana.

    Argumento:
        DBAR: Dados de barra.
        vbus: Tensões atuais das barras.
        theta: Angulos atuais das barras em radianos.
        ybus.
    Retorna:
        J: Matriz jacobiana.
    """

    gbus, bbus = ybus.real, ybus.imag
    Ref = DBAR[DBAR["TIPO"] == "SW"].index[0]  # pega o indice da referencia
    # pega uma lista com as barras PV
    PV = DBAR[DBAR["TIPO"] == "PV"].index.to_list()

    H = np.zeros((len(DBAR), len(DBAR)))
    N = np.zeros((len(DBAR), len(DBAR)))
    M = np.zeros((len(DBAR), len(DBAR)))
    L = np.zeros((len(DBAR), len(DBAR)))

    ### Matriz H #####################
    for k in DBAR.index:
        H_somatorio = 0
        for m in DBAR.index:
            H[k][m], H_somatorio = dp_dtheta(
                k, m, vbus, theta, ybus, H_somatorio)
        H[k][k] = -vbus[k] ** 2 * bbus[k][k] - vbus[k] * H_somatorio

    ### Matriz N #####################
    for k in DBAR.index:
        N_somatorio = 0
        for m in DBAR.index:
            N[k][m], N_somatorio = dp_dv(k, m, vbus, theta, ybus, N_somatorio)
        N[k][k] = vbus[k] * gbus[k][k] + N_somatorio

    ### Matriz M #####################
    for k in DBAR.index:
        M_somatorio = 0
        for m in DBAR.index:
            M[k][m], M_somatorio = dq_dtheta(
                k, m, vbus, theta, ybus, M_somatorio)
        M[k][k] = -(vbus[k] ** 2) * gbus[k][k] + (vbus[k] * M_somatorio)

    ### Matriz L #####################
    for k in DBAR.index:
        L_somatorio = 0
        for m in DBAR.index:
            L[k][m], L_somatorio = dq_dv(k, m, vbus, theta, ybus, L_somatorio)
        L[k][k] = -vbus[k] * bbus[k][k] + L_somatorio

    Jacob = np.block([[H, N], [M, L]])

    Jacob[Ref, :] = 0
    Jacob[:, Ref] = 0
    Jacob[Ref][Ref] = 1e7
    Jacob[len(DBAR) + Ref, :] = 0
    Jacob[:, len(DBAR) + Ref] = 0
    Jacob[len(DBAR) + Ref][len(DBAR) + Ref] = 1e100

    for i in PV:
        Jacob[len(DBAR) + i, :] = 0
        Jacob[:, len(DBAR) + i] = 0
        Jacob[len(DBAR) + i][len(DBAR) + i] = 1e100

    Jacob = np.round(-Jacob, 4)  # Aplicando o negativo
    J = pd.DataFrame(Jacob)
    return J

# Matriz H


def dp_dtheta(k, m, vbus, theta, ybus, h_somatorio):
    gbus, bbus = ybus.real, ybus.imag
    h_somatorio += vbus[m] * (
        (gbus[k][m] * np.sin(theta[k] - theta[m]))
        - (bbus[k][m] * np.cos(theta[k] - theta[m]))
    )
    return (
        vbus[k]
        * vbus[m]
        * (
            gbus[k][m] * np.sin(theta[k] - theta[m])
            - bbus[k][m] * np.cos(theta[k] - theta[m])
        ),
        h_somatorio,
    )


# Matriz N
def dp_dv(k, m, vbus, theta, ybus, n_somatorio):
    gbus, bbus = ybus.real, ybus.imag
    n_somatorio += vbus[m] * (
        (gbus[k][m] * np.cos(theta[k] - theta[m]))
        + (bbus[k][m] * np.sin(theta[k] - theta[m]))
    )
    return (
        vbus[k]
        * (
            gbus[k][m] * np.cos(theta[k] - theta[m])
            + bbus[k][m] * np.sin(theta[k] - theta[m])
        ),
        n_somatorio,
    )


# Matriz M
def dq_dtheta(k, m, vbus, theta, ybus, m_somatorio):
    gbus, bbus = ybus.real, ybus.imag
    m_somatorio += vbus[m] * (
        (gbus[k][m] * np.cos(theta[k] - theta[m]))
        + (bbus[k][m] * np.sin(theta[k] - theta[m]))
    )
    return (
        -vbus[k]
        * vbus[m]
        * (
            gbus[k][m] * np.cos(theta[k] - theta[m])
            + bbus[k][m] * np.sin(theta[k] - theta[m])
        ),
        m_somatorio,
    )


# Matriz L
def dq_dv(k, m, vbus, theta, ybus, l_somatorio):
    gbus, bbus = ybus.real, ybus.imag
    l_somatorio += vbus[m] * (
        (gbus[k][m] * np.sin(theta[k] - theta[m]))
        - (bbus[k][m] * np.cos(theta[k] - theta[m]))
    )
    return (
        vbus[k]
        * (
            gbus[k][m] * np.sin(theta[k] - theta[m])
            - bbus[k][m] * np.cos(theta[k] - theta[m])
        ),
        l_somatorio,
    )
