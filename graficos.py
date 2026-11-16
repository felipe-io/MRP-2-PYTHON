"""Módulo de geração de gráficos gerenciais e acompanhamento com Matplotlib (RF16)."""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from capacidade import calcular_crp_centro
from estoque import listar_saldos
from mps import HORIZONTE_SEMANAS
from mrp import obter_registro_mrp_item
from ordens import listar_ordens

DOCS_DIR = Path("docs")


def _preparar_saida(nome_arquivo: str) -> Path:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    return DOCS_DIR / nome_arquivo


def grafico_posicao_estoque(exibir: bool = True) -> Path:
    saldos = listar_saldos()
    codigos = [s["codigo"] for s in saldos]
    valores_saldo = [s["saldo"] for s in saldos]
    valores_es = [s["estoque_seguranca"] for s in saldos]

    x = np.arange(len(codigos))
    largura = 0.38

    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.bar(x - largura / 2, valores_saldo, largura, label="Saldo Atual", color="#2b6cb0")
    ax.bar(x + largura / 2, valores_es, largura, label="Estoque de Segurança", color="#ed8936")

    ax.set_title("Posição de Estoque: Saldo Atual vs. Estoque de Segurança", fontsize=13, fontweight="bold")
    ax.set_xlabel("Código do Item")
    ax.set_ylabel("Quantidade (log/unidades)")
    ax.set_yscale("symlog", linthresh=10)
    ax.set_xticks(x)
    ax.set_xticklabels(codigos, rotation=45, ha="right")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend()

    plt.tight_layout()
    destino = _preparar_saida("grafico_posicao_estoque.png")
    fig.savefig(destino, dpi=150)

    if exibir:
        plt.show()
    else:
        plt.close(fig)
    return destino


def grafico_estoque_projetado(codigo_item: str, exibir: bool = True) -> Path:
    registro = obter_registro_mrp_item(codigo_item)
    semanas = [f"S{i}" for i in range(1, HORIZONTE_SEMANAS + 1)]
    ep = registro["estoque_projetado"]
    es = registro["estoque_seguranca"]

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(semanas, ep, marker="o", linewidth=2.5, color="#2f855a", label="Estoque Projetado (EP)")
    ax.axhline(
        y=es,
        color="#e53e3e",
        linestyle="--",
        linewidth=2,
        label=f"Estoque de Segurança ({es:g} {registro['unidade']})",
    )

    for i, val in enumerate(ep):
        ax.annotate(f"{val:g}", (semanas[i], val), textcoords="offset points", xytext=(0, 8), ha="center")

    ax.set_title(
        f"Estoque Projetado (8 Semanas) - {registro['codigo']} ({registro['descricao']})",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlabel("Horizonte de Planejamento (Semanas)")
    ax.set_ylabel(f"Quantidade ({registro['unidade']})")
    ax.set_ylim(bottom=0, top=max(max(ep, default=0), es) * 1.25 + 5)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()

    plt.tight_layout()
    destino = _preparar_saida(f"grafico_estoque_projetado_{registro['codigo']}.png")
    fig.savefig(destino, dpi=150)

    if exibir:
        plt.show()
    else:
        plt.close(fig)
    return destino


def grafico_ordens_por_semana(exibir: bool = True) -> Path:
    ordens = listar_ordens()
    semanas = [f"S{i}" for i in range(1, HORIZONTE_SEMANAS + 1)]
    qtd_op = [0] * HORIZONTE_SEMANAS
    qtd_oc = [0] * HORIZONTE_SEMANAS

    for ordem in ordens:
        sem_entrega = int(ordem["semana_entrega"])
        if 1 <= sem_entrega <= HORIZONTE_SEMANAS:
            if ordem["tipo"] == "OP":
                qtd_op[sem_entrega - 1] += 1
            elif ordem["tipo"] == "OC":
                qtd_oc[sem_entrega - 1] += 1

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(semanas, qtd_op, label="Ordens de Produção (OP)", color="#3182ce")
    ax.bar(semanas, qtd_oc, bottom=qtd_op, label="Ordens de Compra (OC)", color="#38a169")

    ax.set_title("Ordens por Semana de Entrega (Chegada): OP vs. OC", fontsize=12, fontweight="bold")
    ax.set_xlabel("Semana de Entrega")
    ax.set_ylabel("Número de Ordens")
    ax.yaxis.get_major_locator().set_params(integer=True)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend()

    plt.tight_layout()
    destino = _preparar_saida("grafico_ordens_entrega.png")
    fig.savefig(destino, dpi=150)

    if exibir:
        plt.show()
    else:
        plt.close(fig)
    return destino


def grafico_carga_capacidade(
    codigo_centro: str,
    apenas_liberadas: bool = True,
    exibir: bool = True,
) -> Path:
    crp = calcular_crp_centro(codigo_centro, apenas_liberadas=apenas_liberadas)
    semanas = [f"S{s['semana']}" for s in crp["semanas"]]
    cargas = [s["carga_horas"] for s in crp["semanas"]]
    capacidade = crp["capacidade_semanal"]
    cores = ["#e53e3e" if s["sobrecarga"] else "#3182ce" for s in crp["semanas"]]

    fig, ax = plt.subplots(figsize=(9, 4.8))
    barras = ax.bar(semanas, cargas, color=cores, label="Carga Alocada (h)")
    ax.axhline(
        y=capacidade,
        color="#1a202c",
        linestyle="--",
        linewidth=2,
        label=f"Capacidade Máxima ({capacidade:g} h/sem)",
    )

    for barra, sem_info in zip(barras, crp["semanas"]):
        altura = barra.get_height()
        rotulo = f"{altura:g}h" + (" (!)" if sem_info["sobrecarga"] else "")
        ax.annotate(rotulo, (barra.get_x() + barra.get_width() / 2, altura), xytext=(0, 5),
                    textcoords="offset points", ha="center", fontsize=9, fontweight="bold")

    ax.set_title(
        f"Carga x Capacidade (CRP) - {crp['codigo']} ({crp['nome']})",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlabel("Semana")
    ax.set_ylabel("Horas de Trabalho (h)")
    ax.set_ylim(bottom=0, top=max(max(cargas, default=0), capacidade) * 1.25 + 2)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend()

    plt.tight_layout()
    destino = _preparar_saida(f"grafico_crp_{crp['codigo']}.png")
    fig.savefig(destino, dpi=150)

    if exibir:
        plt.show()
    else:
        plt.close(fig)
    return destino