"""Motor de cálculo do MRP (Material Requirements Planning) em 8 semanas."""

from typing import Any
from estrutura import obter_componentes
from mps import HORIZONTE_SEMANAS, obter_mps_completo
from persistencia import carregar_json, salvar_json
from utils import data_hoje_str

ULTIMO_RESULTADO_MRP: dict[str, Any] = {}


def _gerar_proximo_codigo_ordem(prefixo: str, ordens_existentes: dict[str, Any]) -> str:
    """Gera um código sequencial único como OP-0002 ou OC-0001."""
    numeros = []
    for cod in ordens_existentes:
        if cod.startswith(f"{prefixo}-"):
            try:
                numeros.append(int(cod.split("-")[1]))
            except (IndexError, ValueError):
                continue
    proximo = max(numeros, default=0) + 1
    return f"{prefixo}-{proximo:04d}"


def executar_mrp() -> dict[str, Any]:
    """Executa o cálculo MRP completo (PA -> SA -> MP) e gera ordens planejadas (RF08, RF09)."""
    global ULTIMO_RESULTADO_MRP

    itens = carregar_json("itens")
    estoque = carregar_json("estoque")
    mps = obter_mps_completo()
    ordens_atuais = carregar_json("ordens")

    ordens_mantidas = {
        cod: ord_data
        for cod, ord_data in ordens_atuais.items()
        if ord_data.get("status") != "PLANEJADA"
    }

    rp_por_item: dict[str, list[float]] = {
        cod: [0.0] * HORIZONTE_SEMANAS for cod in itens
    }
    for ord_data in ordens_mantidas.values():
        if ord_data.get("status") in ("FIRME", "LIBERADA"):
            cod_item = ord_data["item"]
            sem_entrega = int(ord_data["semana_entrega"])
            if cod_item in rp_por_item and 1 <= sem_entrega <= HORIZONTE_SEMANAS:
                rp_por_item[cod_item][sem_entrega - 1] += float(ord_data["quantidade"])

    nb_por_item: dict[str, list[float]] = {
        cod: [0.0] * HORIZONTE_SEMANAS for cod in itens
    }

    for cod_pa, demandas in mps.items():
        if cod_pa in nb_por_item:
            nb_por_item[cod_pa] = list(demandas)

    registros_mrp: dict[str, dict[str, Any]] = {}
    mensagens_excecao: list[str] = []
    novas_ordens: list[dict[str, Any]] = []

    for tipo_atual in ("PA", "SA", "MP"):
        codigos_do_tipo = sorted(
            [cod for cod, info in itens.items() if info["tipo"] == tipo_atual]
        )

        for cod in codigos_do_tipo:
            info = itens[cod]
            es = float(info["estoque_seguranca"])
            lote_min = float(info["lote_minimo"])
            lead_time = int(info["lead_time"])
            saldo_inicial = float(estoque.get(cod, 0.0))

            nb = nb_por_item[cod]
            rp = rp_por_item[cod]
            ep = [0.0] * HORIZONTE_SEMANAS
            nl = [0.0] * HORIZONTE_SEMANAS
            rec_plan = [0.0] * HORIZONTE_SEMANAS
            lib_plan = [0.0] * HORIZONTE_SEMANAS

            ep_anterior = saldo_inicial

            for t in range(HORIZONTE_SEMANAS):
                disponivel = ep_anterior + rp[t]
                necessidade_liq = max(0.0, nb[t] + es - disponivel)
                nl[t] = necessidade_liq

                if necessidade_liq > 0:
                    rec_plan[t] = max(necessidade_liq, lote_min)
                else:
                    rec_plan[t] = 0.0

                ep[t] = disponivel + rec_plan[t] - nb[t]
                ep_anterior = ep[t]

                if rec_plan[t] > 0:
                    semana_entrega = t + 1  # 1-indexed (1 a 8)
                    semana_liberacao = semana_entrega - lead_time
                    atrasada = semana_liberacao < 1

                    idx_lib = max(0, semana_liberacao - 1)
                    lib_plan[idx_lib] += rec_plan[t]

                    prefixo = "OP" if info["tipo"] in ("PA", "SA") else "OC"
                    cod_ordem = _gerar_proximo_codigo_ordem(prefixo, ordens_mantidas)

                    nova_ordem = {
                        "codigo": cod_ordem,
                        "tipo": prefixo,
                        "item": cod,
                        "quantidade": rec_plan[t],
                        "semana_liberacao": semana_liberacao,
                        "semana_entrega": semana_entrega,
                        "status": "PLANEJADA",
                        "atrasada": atrasada,
                    }
                    ordens_mantidas[cod_ordem] = nova_ordem
                    novas_ordens.append(nova_ordem)

                    if atrasada:
                        mensagens_excecao.append(
                            f"EXCEÇÃO ({cod_ordem}): Item {cod} ({info['descricao']}) com liberação "
                            f"na semana S{semana_liberacao} (antes da S1) para entrega na S{semana_entrega} -> ATRASADA."
                        )

            componentes = obter_componentes(cod)
            for comp in componentes:
                cod_filho = comp["componente"]
                qtd_por_un = float(comp["quantidade"])
                if cod_filho in nb_por_item:
                    for t in range(HORIZONTE_SEMANAS):
                        nb_por_item[cod_filho][t] += lib_plan[t] * qtd_por_un

            registros_mrp[cod] = {
                "codigo": cod,
                "descricao": info["descricao"],
                "tipo": info["tipo"],
                "unidade": info["unidade"],
                "lead_time": lead_time,
                "estoque_seguranca": es,
                "lote_minimo": lote_min,
                "estoque_inicial": saldo_inicial,
                "necessidade_bruta": nb,
                "recebimentos_programados": rp,
                "estoque_projetado": ep,
                "necessidade_liquida": nl,
                "recebimentos_planejados": rec_plan,
                "liberacoes_planejadas": lib_plan,
            }

    salvar_json("ordens", ordens_mantidas)

    ULTIMO_RESULTADO_MRP = {
        "data_execucao": data_hoje_str(),
        "registros": registros_mrp,
        "ordens_geradas": novas_ordens,
        "excecoes": mensagens_excecao,
    }
    return ULTIMO_RESULTADO_MRP


def obter_registro_mrp_item(codigo_item: str) -> dict[str, Any]:
    codigo = codigo_item.strip().upper()
    if not ULTIMO_RESULTADO_MRP:
        executar_mrp()

    registros = ULTIMO_RESULTADO_MRP.get("registros", {})
    if codigo not in registros:
        raise ValueError(f"Item {codigo} não encontrado no cálculo MRP.")
    return registros[codigo]