"""Módulo de Centros de Trabalho, Roteiros e Planejamento de Capacidade (CRP)."""

from typing import Any
from mps import HORIZONTE_SEMANAS
from persistencia import carregar_json, salvar_json


def listar_centros() -> list[dict[str, Any]]:
    centros = carregar_json("centros")
    return sorted(centros.values(), key=lambda x: x["codigo"])


def cadastrar_centro(
    codigo: str,
    nome: str,
    capacidade_semanal: float,
    custo_hora: float,
) -> dict[str, Any]:
    cod = codigo.strip().upper()
    if not cod.startswith("CT-"):
        raise ValueError("O código do centro de trabalho deve seguir o formato CT-01.")
    if not nome.strip():
        raise ValueError("Informe o nome do centro de trabalho.")
    if capacidade_semanal <= 0:
        raise ValueError("A capacidade semanal (horas) deve ser maior que zero.")
    if custo_hora < 0:
        raise ValueError("O custo-hora não pode ser negativo.")

    centros = carregar_json("centros")
    centro = {
        "codigo": cod,
        "nome": nome.strip(),
        "capacidade_semanal": float(capacidade_semanal),
        "custo_hora": float(custo_hora),
    }
    centros[cod] = centro
    salvar_json("centros", centros)
    return centro


def listar_roteiros() -> dict[str, dict[str, Any]]:
    return carregar_json("roteiros")


def cadastrar_roteiro(codigo_item: str, codigo_centro: str, tempo_unitario: float) -> dict[str, Any]:
    cod_item = codigo_item.strip().upper()
    cod_ct = codigo_centro.strip().upper()

    itens = carregar_json("itens")
    if cod_item not in itens:
        raise ValueError(f"Item {cod_item} não encontrado.")
    if itens[cod_item]["tipo"] == "MP":
        raise ValueError("Matérias-Primas (MP) são compradas e não possuem roteiro de fabricação.")

    centros = carregar_json("centros")
    if cod_ct not in centros:
        raise ValueError(f"Centro de trabalho {cod_ct} não encontrado.")

    if tempo_unitario <= 0:
        raise ValueError("O tempo unitário (em horas) deve ser maior que zero.")

    roteiros = carregar_json("roteiros")
    roteiro = {
        "centro": cod_ct,
        "tempo_unitario": float(tempo_unitario),
    }
    roteiros[cod_item] = roteiro
    salvar_json("roteiros", roteiros)
    return roteiro


def calcular_crp_centro(
    codigo_centro: str,
    apenas_liberadas: bool = True,
) -> dict[str, Any]:
    cod_ct = codigo_centro.strip().upper()
    centros = carregar_json("centros")
    if cod_ct not in centros:
        raise ValueError(f"Centro de trabalho {cod_ct} não encontrado.")

    centro = centros[cod_ct]
    capacidade = float(centro["capacidade_semanal"])
    roteiros = carregar_json("roteiros")
    ordens = carregar_json("ordens")

    status_considerados = ("LIBERADA",) if apenas_liberadas else ("PLANEJADA", "FIRME", "LIBERADA")
    cargas_semanais = [0.0] * HORIZONTE_SEMANAS

    for ordem in ordens.values():
        if ordem["tipo"] != "OP":
            continue
        if ordem["status"] not in status_considerados:
            continue

        item_op = ordem["item"]
        roteiro = roteiros.get(item_op)
        if not roteiro or roteiro["centro"] != cod_ct:
            continue

        sem_lib = max(1, int(ordem["semana_liberacao"]))
        if 1 <= sem_lib <= HORIZONTE_SEMANAS:
            horas_op = float(ordem["quantidade"]) * float(roteiro["tempo_unitario"])
            cargas_semanais[sem_lib - 1] += horas_op

    semanas_detalhe = []
    semanas_sobrecarga = []

    for idx in range(HORIZONTE_SEMANAS):
        sem_num = idx + 1
        carga = cargas_semanais[idx]
        uso_pct = (carga / capacidade * 100.0) if capacidade > 0 else 0.0
        sobrecarga = carga > capacidade
        if sobrecarga:
            semanas_sobrecarga.append(sem_num)

        semanas_detalhe.append(
            {
                "semana": sem_num,
                "carga_horas": round(carga, 2),
                "capacidade_horas": capacidade,
                "uso_percentual": round(uso_pct, 1),
                "sobrecarga": sobrecarga,
            }
        )

    return {
        "codigo": cod_ct,
        "nome": centro["nome"],
        "capacidade_semanal": capacidade,
        "semanas": semanas_detalhe,
        "semanas_sobrecarga": semanas_sobrecarga,
    }