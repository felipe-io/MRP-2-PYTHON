"""Módulo de cálculo de Custo Padrão dos produtos fabricados (materiais + mão de obra)."""

from typing import Any
from persistencia import carregar_json


def calcular_custo_padrao(
    codigo_item: str,
    itens: dict[str, Any] | None = None,
    estrutura: dict[str, Any] | None = None,
    roteiros: dict[str, Any] | None = None,
    centros: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if itens is None:
        itens = carregar_json("itens")
    if estrutura is None:
        estrutura = carregar_json("estrutura")
    if roteiros is None:
        roteiros = carregar_json("roteiros")
    if centros is None:
        centros = carregar_json("centros")

    cod = codigo_item.strip().upper()
    if cod not in itens:
        raise ValueError(f"Item {cod} não encontrado.")

    item = itens[cod]

    if item["tipo"] == "MP":
        custo_un = float(item["custo_unitario"])
        return {
            "codigo": cod,
            "descricao": item["descricao"],
            "tipo": "MP",
            "linhas": [],
            "custo_materiais": custo_un,
            "custo_mao_obra": 0.0,
            "custo_total": custo_un,
        }

    linhas_detalhamento = []
    total_materiais = 0.0

    for comp in estrutura.get(cod, []):
        cod_comp = comp["componente"]
        qtd = float(comp["quantidade"])
        info_comp = itens[cod_comp]

        res_comp = calcular_custo_padrao(cod_comp, itens, estrutura, roteiros, centros)
        custo_un_comp = res_comp["custo_total"]
        subtotal = qtd * custo_un_comp
        total_materiais += subtotal

        linhas_detalhamento.append(
            {
                "codigo": cod_comp,
                "descricao": info_comp["descricao"],
                "quantidade": qtd,
                "unidade": info_comp["unidade"],
                "custo_unitario": round(custo_un_comp, 2),
                "total": round(subtotal, 2),
            }
        )

    custo_mo = 0.0
    roteiro = roteiros.get(cod)
    if roteiro:
        cod_ct = roteiro["centro"]
        tempo_h = float(roteiro["tempo_unitario"])
        custo_hora = float(centros.get(cod_ct, {}).get("custo_hora", 0.0))
        custo_mo = tempo_h * custo_hora

        linhas_detalhamento.append(
            {
                "codigo": f"MO-{cod_ct}",
                "descricao": f"Mão de obra {cod_ct}",
                "quantidade": tempo_h,
                "unidade": "h",
                "custo_unitario": round(custo_hora, 2),
                "total": round(custo_mo, 2),
            }
        )

    custo_total = total_materiais + custo_mo

    return {
        "codigo": cod,
        "descricao": item["descricao"],
        "tipo": item["tipo"],
        "linhas": linhas_detalhamento,
        "custo_materiais": round(total_materiais, 2),
        "custo_mao_obra": round(custo_mo, 2),
        "custo_total": round(custo_total, 2),
    }