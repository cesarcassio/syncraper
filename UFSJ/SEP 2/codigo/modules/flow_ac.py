# ruff: noqa: F403, F405 #apenas corrige um erro de extensão do vscode
import numpy as np
from modules import *


def flow_ac(DBAR, DCIR):
    # Base, Tolerância e max iterações
    s_base = 100  # potencia base em MVA
    tol = 1e-3  # tolerância
    max_itera = 100  # maximo de iterações
    itera = 0  # iteração atual

    contingencia = False  # True or False
    DCIR["DEF(RAD)"] = np.radians(DCIR["DEF(GRAUS)"])
    ybus = make_ybus(DBAR, DCIR)

    # Cria uma lista das Barras SW
    Ref = DBAR[DBAR["TIPO"] == "SW"].index.to_list()
    # Cria uma lista das barras PV
    PV = DBAR[DBAR["TIPO"] == "PV"].index.to_list()
    # Cria uma lista das barras PQ
    PQ = DBAR[DBAR["TIPO"] == "PQ"].index.to_list()

    while itera < max_itera:
        theta = np.radians(DBAR["Oesp(°)"].values)
        vbus = DBAR["Vesp(PU)"].values
        delta_p, delta_q = calc_delta_pq(DBAR, vbus, theta, ybus)

        # verifica se o delta p e delta q estão dentro da tolerância, se estiver, o código sai do while e tem Vbus e Theta como solução
        if abs(delta_p[sorted(PV + PQ)].max()) < tol and abs(delta_q[PQ].max()) < tol:
            break

        jacob = jacobiana(DBAR, vbus, theta, ybus)
        delta_theta, delta_v = calc_delta_theta_v(DBAR, delta_p, delta_q, jacob)
        theta += delta_theta
        vbus += delta_v
        itera += 1
        # atualizando DBAR com o angulo encontrado
        DBAR["Oesp(°)"] = np.degrees(theta)
        DBAR["Vesp(PU)"] = vbus  # atualizando DBAR com a tensão encontrada
    DBAR["QG(PU)"] = 0
    DBAR["PG(PU)"] = 0
    calc_pot(DBAR, vbus, theta, ybus)

    fluxo = calc_fluxo(DBAR, DCIR, s_base)
    calc_sobrecarga_ac(DCIR, fluxo)
    circuitos = list(fluxo["NCIR"][fluxo["Sobrecarga"] != 0])
    fluxo["Sobrecarga"].sum()
    return fluxo["Sobrecarga"].sum(), circuitos
