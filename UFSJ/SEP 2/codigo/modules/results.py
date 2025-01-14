from tabulate import tabulate


def results(DBAR, fluxo, s_base, SAVEPATH, CONTINGENCIA=False):
    """
    Crie um arquivo txt com parte da solução do fluxo AC.

    Argumento:
        DBAR: Dados de barra.
        fluxo: DataFrame com a solução do fluxo de potência do circuito.
        s_base: Base das potências.
        SAVEPATH: Caminho em que o arquivo criado será salvo.
    """
    # Filtra e ajusta os dados de barra
    DBAR_Results = DBAR.drop(DBAR.columns[[3, 4, 8, 9, 10]], axis=1)
    DBAR_Results["PG(PU)"] += DBAR_Results["PGesp(PU)"]
    DBAR_Results.drop("PGesp(PU)", axis=1, inplace=True)
    DBAR_Results = DBAR_Results.filter(
        ["BARRA", "Vesp(PU)", "Oesp(GRAUS)", "PG(PU)", "QG(PU)", "PD(PU)", "QD(PU)"]
    )
    DBAR_Results = DBAR_Results.rename(
        columns={
            "Vesp(PU)": "V(PU)",
            "Oesp(GRAUS)": "Def.(GRAUS)",
            "PG(PU)": "PG(MW)",
            "QG(PU)": "QG(MVAr)",
            "PD(PU)": "PD(MW)",
            "QD(PU)": "QD(MVAr)",
        }
    )
    # Converte as potências para a base especificada
    DBAR_Results["PG(MW)"] *= s_base
    DBAR_Results["QG(MVAr)"] *= s_base
    DBAR_Results["PD(MW)"] *= s_base
    DBAR_Results["QD(MVAr)"] *= s_base

    # Calcula as potências totais
    PGTotal = DBAR_Results["PG(MW)"].sum()
    QGTotal = DBAR_Results["QG(MVAr)"].sum()
    PDTotal = DBAR_Results["PD(MW)"].sum()
    QDTotal = DBAR_Results["QD(MVAr)"].sum()
    PPTotal = fluxo["Perdas(MW)"].sum()
    PQTotal = fluxo["Perdas(MVAr)"].sum()

    # Cria o relatório em um arquivo txt
    if CONTINGENCIA:
        report = f"{'!'*55}\n{'S I S T E M A     S O B R E    C O N T I N G Ê N C I A'.center(50)}\n{'!'*55}\n"
    else:
        report = ""
    report += "Relatório das barras:\n\n"
    report += tabulate(
        DBAR_Results,
        headers="keys",
        numalign="decimal",
        tablefmt="github",
        floatfmt=[".0f"] + [".4f"] * (len(DBAR_Results.columns) - 1),
        showindex=False,
    )

    report += "\n\nPotências totais:\n"
    report += f"Ativa Gerada (MW):{PGTotal:17.2f}\n"
    report += f"Ativa Demandada (MW):{PDTotal:14.2f}\n"
    report += f"Reativa Gerada (MVAr):{QGTotal:13.2f}\n"
    report += f"Reativa Demandada (MVAr):{QDTotal:10.2f}\n"
    report += "\n\nRelatório dos circuitos:\n\n"

    report += tabulate(
        fluxo,
        headers="keys",
        numalign="decimal",
        tablefmt="github",
        floatfmt=[".0f", ".0f", ".0f"] + [".4f"] * (len(fluxo.columns) - 1),
        showindex=False,
    )

    report += "\n\nPotências totais:\n"
    report += f"Perdas ativas (MW):{PPTotal:17.2f}\n"
    report += f"Perdas reativas (MVAr):{PQTotal:14.2f}\n"

    with open(SAVEPATH, "w") as file:
        file.write(report)

    # Salva os resultados em arquivos CSV
    DBAR_Results.to_csv(
        SAVEPATH.replace(".txt", "DBAR.csv"), decimal=",", index=False, sep=";"
    )
    fluxo.to_csv(
        SAVEPATH.replace(".txt", "fluxo.csv"), decimal=",", index=False, sep=";"
    )
