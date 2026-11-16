"""Módulo de gestão de Ordens de Produção (OP), Ordens de Compra (OC) e Apontamento."""

from typing import Any
from estoque import consultar_saldo, registrar_movimentacao
from estrutura import obter_componentes
from persistencia import carregar_json, salvar_json
from utils import data_hoje_str


def listar_ordens(filtro_tipo: str | None = None, filtro_status: str | None = None) -> list[dict[str, Any]]:
    ordens = carregar_json("ordens")
    lista = list(ordens.values())

    if filtro_tipo:
        lista = [o for o in lista if o["tipo"] == filtro_tipo.upper()]
    if filtro_status:
        lista = [o for o in lista if o["status"] == filtro_status.upper()]

    return sorted(lista, key=lambda x: (x["semana_entrega"], x["codigo"]))


def alterar_status_ordem(codigo_ordem: str, novo_status: str) -> dict[str, Any]:
    cod = codigo_ordem.strip().upper()
    status_alvo = novo_status.strip().upper()

    ordens = carregar_json("ordens")
    if cod not in ordens:
        raise ValueError(f"Ordem {cod} não encontrada.")

    ordem = ordens[cod]
    status_atual = ordem["status"]

    transicoes_validas = {
        "PLANEJADA": ["FIRME", "LIBERADA"],
        "FIRME": ["LIBERADA"],
        "LIBERADA": ["ENCERRADA"],
        "ENCERRADA": [],
    }

    if status_alvo not in transicoes_validas.get(status_atual, []):
        raise ValueError(
            f"Transição inválida: uma ordem {status_atual} não pode passar diretamente para {status_alvo}."
        )

    if ordem["tipo"] == "OP" and status_alvo == "ENCERRADA":
        raise ValueError(
            "Para encerrar uma Ordem de Produção (OP), utilize a opção 'Apontar Produção' (RF11)."
        )

    if ordem["tipo"] == "OC" and status_alvo == "ENCERRADA":
        registrar_movimentacao(
            codigo_item=ordem["item"],
            tipo="ENTRADA",
            quantidade=float(ordem["quantidade"]),
            documento=f"RECEBIMENTO {cod}",
            data=data_hoje_str(),
        )

    ordem["status"] = status_alvo
    ordens[cod] = ordem
    salvar_json("ordens", ordens)
    return ordem


def apontar_producao(codigo_op: str, data_apontamento: str | None = None) -> dict[str, Any]:
    cod = codigo_op.strip().upper()
    ordens = carregar_json("ordens")
    if cod not in ordens:
        raise ValueError(f"Ordem {cod} não encontrada.")

    ordem = ordens[cod]
    if ordem["tipo"] != "OP":
        raise ValueError(f"A ordem {cod} é uma Ordem de Compra (OC), não uma Ordem de Produção (OP).")
    if ordem["status"] != "LIBERADA":
        raise ValueError(
            f"A OP {cod} está com status '{ordem['status']}'. Apenas ordens LIBERADAS podem ser apontadas."
        )

    item_pai = ordem["item"]
    qtd_produzida = float(ordem["quantidade"])
    componentes = obter_componentes(item_pai)
    itens = carregar_json("itens")

    faltas = []
    consumos_necessarios = []
    for comp in componentes:
        cod_comp = comp["componente"]
        qtd_necessaria = float(comp["quantidade"]) * qtd_produzida
        saldo_disp = consultar_saldo(cod_comp)
        if saldo_disp < qtd_necessaria:
            un = itens.get(cod_comp, {}).get("unidade", "un")
            faltas.append(
                f"{cod_comp} (necessário: {qtd_necessaria:g} {un}, disponível: {saldo_disp:g} {un})"
            )
        consumos_necessarios.append((cod_comp, qtd_necessaria))

    if faltas:
        detalhes = "; ".join(faltas)
        raise ValueError(f"Apontamento rejeitado por falta de componente(s): {detalhes}.")

    data_mov = data_apontamento if data_apontamento else data_hoje_str()

    for cod_comp, qtd_consumida in consumos_necessarios:
        registrar_movimentacao(
            codigo_item=cod_comp,
            tipo="SAIDA",
            quantidade=qtd_consumida,
            documento=f"{cod} ({item_pai})",
            data=data_mov,
        )

    registrar_movimentacao(
        codigo_item=item_pai,
        tipo="ENTRADA",
        quantidade=qtd_produzida,
        documento=f"PRODUCAO {cod}",
        data=data_mov,
    )

    ordem["status"] = "ENCERRADA"
    ordens[cod] = ordem
    salvar_json("ordens", ordens)
    return ordem