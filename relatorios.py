"""Módulo de exportação de relatórios gerenciais em formato CSV."""

from pathlib import Path
import pandas as pd
from estoque import listar_saldos
from ordens import listar_ordens

DOCS_DIR = Path("docs")


def exportar_posicao_estoque_csv(caminho_saida: str | Path | None = None) -> Path:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    destino = Path(caminho_saida) if caminho_saida else DOCS_DIR / "relatorio_posicao_estoque.csv"

    saldos = listar_saldos()
    df = pd.DataFrame(saldos)

    if not df.empty:
        df["situacao"] = df["abaixo_seguranca"].apply(
            lambda alerta: "ABAIXO DO ESTOQUE DE SEGURANCA" if alerta else "OK"
        )
        df = df[
            [
                "codigo",
                "descricao",
                "tipo",
                "unidade",
                "saldo",
                "estoque_seguranca",
                "situacao",
            ]
        ]
        df.columns = [
            "Codigo",
            "Descricao",
            "Tipo",
            "Unidade",
            "Saldo Atual",
            "Estoque de Seguranca",
            "Situacao",
        ]

    df.to_csv(destino, index=False, sep=";", encoding="utf-8-sig")
    return destino


def exportar_ordens_csv(caminho_saida: str | Path | None = None) -> Path:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    destino = Path(caminho_saida) if caminho_saida else DOCS_DIR / "relatorio_ordens.csv"

    ordens = listar_ordens()
    df = pd.DataFrame(ordens)

    if not df.empty:
        df["prazo"] = df["atrasada"].apply(lambda atr: "ATRASADA" if atr else "NO PRAZO")
        df = df[
            [
                "codigo",
                "tipo",
                "item",
                "quantidade",
                "semana_liberacao",
                "semana_entrega",
                "status",
                "prazo",
            ]
        ]
        df.columns = [
            "Codigo Ordem",
            "Tipo",
            "Item",
            "Quantidade",
            "Semana Liberacao",
            "Semana Entrega",
            "Status",
            "Situacao Prazo",
        ]

    df.to_csv(destino, index=False, sep=";", encoding="utf-8-sig")
    return destino