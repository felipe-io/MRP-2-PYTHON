"""Módulo de controle de estoque, movimentações e histórico Kardex."""

from typing import Any
from persistencia import (
    carregar_json,
    carregar_movimentos,
    registrar_movimento_csv,
    salvar_json,
)
from utils import data_hoje_str, validar_data


def consultar_saldo(codigo_item: str) -> float:
    codigo = codigo_item.strip().upper()
    itens = carregar_json("itens")
    if codigo not in itens:
        raise ValueError(f"Item {codigo} não encontrado.")
    estoque = carregar_json("estoque")
    return float(estoque.get(codigo, 0.0))


def listar_saldos() -> list[dict[str, Any]]:
    itens = carregar_json("itens")
    estoque = carregar_json("estoque")
    resultado = []

    for codigo in sorted(itens.keys()):
        item = itens[codigo]
        saldo = float(estoque.get(codigo, 0.0))
        es = float(item["estoque_seguranca"])
        resultado.append(
            {
                "codigo": codigo,
                "descricao": item["descricao"],
                "tipo": item["tipo"],
                "unidade": item["unidade"],
                "saldo": saldo,
                "estoque_seguranca": es,
                "abaixo_seguranca": saldo < es,
            }
        )
    return resultado


def consultar_kardex(codigo_item: str) -> dict[str, Any]:
    codigo = codigo_item.strip().upper()
    itens = carregar_json("itens")
    if codigo not in itens:
        raise ValueError(f"Item {codigo} não encontrado.")

    item = itens[codigo]
    saldo = consultar_saldo(codigo)
    es = float(item["estoque_seguranca"])
    movimentos = [m for m in carregar_movimentos() if m["codigo_item"] == codigo]

    return {
        "codigo": codigo,
        "descricao": item["descricao"],
        "unidade": item["unidade"],
        "saldo": saldo,
        "estoque_seguranca": es,
        "abaixo_seguranca": saldo < es,
        "movimentos": movimentos,
    }


def registrar_movimentacao(
    codigo_item: str,
    tipo: str,
    quantidade: float,
    documento: str,
    data: str | None = None,
) -> dict[str, Any]:
    codigo = codigo_item.strip().upper()
    tipo_upper = tipo.strip().upper()

    if tipo_upper not in ("ENTRADA", "SAIDA", "AJUSTE"):
        raise ValueError("Tipo de movimentação inválido. Use ENTRADA, SAIDA ou AJUSTE.")

    doc_limpo = documento.strip()
    if not doc_limpo:
        raise ValueError("Informe o documento ou motivo da movimentação.")

    data_mov = validar_data(data) if data else data_hoje_str()

    itens = carregar_json("itens")
    if codigo not in itens:
        raise ValueError(f"Item {codigo} não encontrado.")

    estoque = carregar_json("estoque")
    saldo_atual = float(estoque.get(codigo, 0.0))

    if tipo_upper == "ENTRADA":
        if quantidade <= 0:
            raise ValueError("A quantidade de entrada deve ser maior que zero.")
        variacao = float(quantidade)
    elif tipo_upper == "SAIDA":
        if quantidade <= 0:
            raise ValueError("A quantidade de saída deve ser maior que zero.")
        variacao = -float(quantidade)
    else:
        if quantidade == 0:
            raise ValueError("A quantidade de ajuste não pode ser zero.")
        variacao = float(quantidade)

    novo_saldo = saldo_atual + variacao

    if novo_saldo < 0:
        unidade = itens[codigo]["unidade"]
        raise ValueError(
            f"Saldo insuficiente (saldo atual: {saldo_atual:g} {unidade}). Operação cancelada."
        )

    estoque[codigo] = novo_saldo
    salvar_json("estoque", estoque)

    todos_movs = carregar_movimentos()
    novo_id = f"MOV-{len(todos_movs) + 1:04d}"

    registro = {
        "id": novo_id,
        "data": data_mov,
        "codigo_item": codigo,
        "tipo": tipo_upper,
        "quantidade": variacao,
        "saldo_apos": novo_saldo,
        "documento": doc_limpo,
    }
    registrar_movimento_csv(registro)
    return registro