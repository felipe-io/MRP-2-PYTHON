"""Módulo responsável pela persistência de dados em JSON e CSV na pasta data/."""

import csv
import json
from pathlib import Path
from typing import Any

DATA_DIR = Path("data")

ARQUIVOS_JSON = {
    "itens": DATA_DIR / "itens.json",
    "estrutura": DATA_DIR / "estrutura.json",
    "estoque": DATA_DIR / "estoque.json",
    "centros": DATA_DIR / "centros.json",
    "roteiros": DATA_DIR / "roteiros.json",
    "mps": DATA_DIR / "mps.json",
    "ordens": DATA_DIR / "ordens.json",
}

ARQUIVO_MOVIMENTOS = DATA_DIR / "movimentos.csv"
CABECALHO_MOVIMENTOS = ["id", "data", "codigo_item", "tipo", "quantidade", "saldo_apos", "documento"]


def garantir_diretorio() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for caminho in ARQUIVOS_JSON.values():
        if not caminho.exists() or caminho.stat().st_size == 0:
            salvar_json(caminho, {})

    if not ARQUIVO_MOVIMENTOS.exists() or ARQUIVO_MOVIMENTOS.stat().st_size == 0:
        with open(ARQUIVO_MOVIMENTOS, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CABECALHO_MOVIMENTOS)
            writer.writeheader()


def carregar_json(chave: str) -> dict[str, Any]:
    garantir_diretorio()
    caminho = ARQUIVOS_JSON[chave]
    try:
        with open(caminho, mode="r", encoding="utf-8") as f:
            conteudo = json.load(f)
            return conteudo if isinstance(conteudo, dict) else {}
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def salvar_json(chave_ou_caminho: str | Path, dados: dict[str, Any]) -> None:
    """Salva um dicionário formatado em JSON."""
    caminho = (
        ARQUIVOS_JSON[chave_ou_caminho]
        if isinstance(chave_ou_caminho, str) and chave_ou_caminho in ARQUIVOS_JSON
        else Path(chave_ou_caminho)
    )
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, mode="w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


def carregar_movimentos() -> list[dict[str, Any]]:
    garantir_diretorio()
    movimentos = []
    with open(ARQUIVO_MOVIMENTOS, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for linha in reader:
            linha["quantidade"] = float(linha["quantidade"])
            linha["saldo_apos"] = float(linha["saldo_apos"])
            movimentos.append(linha)
    return movimentos


def registrar_movimento_csv(movimento: dict[str, Any]) -> None:
    garantir_diretorio()
    with open(ARQUIVO_MOVIMENTOS, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CABECALHO_MOVIMENTOS)
        writer.writerow(movimento)


def carregar_todos_dados() -> dict[str, Any]:
    garantir_diretorio()
    dados = {chave: carregar_json(chave) for chave in ARQUIVOS_JSON}
    dados["movimentos"] = carregar_movimentos()
    return dados