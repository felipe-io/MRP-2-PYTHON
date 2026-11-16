"""Módulo do Plano Mestre de Produção (MPS) no horizonte de 8 semanas."""

from typing import Any
from persistencia import carregar_json, salvar_json

HORIZONTE_SEMANAS = 8


def obter_mps_completo() -> dict[str, list[float]]:
    itens = carregar_json("itens")
    mps = carregar_json("mps")
    resultado: dict[str, list[float]] = {}

    for codigo, item in sorted(itens.items()):
        if item["tipo"] == "PA":
            semanas = mps.get(codigo, [0.0] * HORIZONTE_SEMANAS)
            semanas_ajustadas = [float(semanas[i]) if i < len(semanas) else 0.0 for i in range(HORIZONTE_SEMANAS)]
            resultado[codigo] = semanas_ajustadas

    return resultado


def obter_demanda_pa(codigo_pa: str) -> list[float]:
    codigo = codigo_pa.strip().upper()
    itens = carregar_json("itens")
    if codigo not in itens or itens[codigo]["tipo"] != "PA":
        raise ValueError(f"O item {codigo} não é um Produto Acabado (PA) válido.")

    mps = obter_mps_completo()
    return mps.get(codigo, [0.0] * HORIZONTE_SEMANAS)


def salvar_demanda_pa(codigo_pa: str, demandas: list[float]) -> list[float]:
    codigo = codigo_pa.strip().upper()
    itens = carregar_json("itens")
    if codigo not in itens or itens[codigo]["tipo"] != "PA":
        raise ValueError(f"O item {codigo} não é um Produto Acabado (PA) válido.")

    if len(demandas) != HORIZONTE_SEMANAS:
        raise ValueError(f"O MPS deve conter exatamente {HORIZONTE_SEMANAS} semanas.")

    demandas_validadas = []
    for valor in demandas:
        val_float = float(valor)
        if val_float < 0:
            raise ValueError("As quantidades de demanda no MPS não podem ser negativas.")
        demandas_validadas.append(val_float)

    mps = carregar_json("mps")
    mps[codigo] = demandas_validadas
    salvar_json("mps", mps)
    return demandas_validadas


def atualizar_semana_pa(codigo_pa: str, semana: int, quantidade: float) -> list[float]:
    if not 1 <= semana <= HORIZONTE_SEMANAS:
        raise ValueError(f"Semana inválida. Escolha entre 1 e {HORIZONTE_SEMANAS}.")
    if quantidade < 0:
        raise ValueError("A quantidade não pode ser negativa.")

    demandas = obter_demanda_pa(codigo_pa)
    demandas[semana - 1] = float(quantidade)
    return salvar_demanda_pa(codigo_pa, demandas)