import numpy as np
import pandas as pd
from modules.flowdc import *


def flow_dc(DCIR, DBAR):
    tol = 0.001
    erro = 1
    s_base = 100
    Ref = DBAR[DBAR["TIPO"] == "SW"].index

    B = matriz_susceptancia(DCIR, DBAR)
    if B is None:
        return

    PG = DBAR["PGesp(PU)"].drop(Ref).to_numpy()
    PD = DBAR["PD(PU)"].drop(Ref).to_numpy()
    P = PG - PD
    theta = calc_theta(B, P, Ref)

    while erro > tol:
        calc_perdas(DCIR, theta)

        perdas = calc_sum_perdas(DCIR, DBAR)
        P = PG - (PD + perdas)
        theta_nv = calc_theta(B, P, Ref)

        erro = abs(theta_nv - theta).max()
        theta = theta_nv

    calc_flow_dc(DCIR, theta, s_base)
    calc_sobrecarga(DCIR)
    circuitos = list(DCIR["NCIR"][DCIR["Sobrecarga"] != 0])
    return DCIR["Sobrecarga"].sum(), circuitos
