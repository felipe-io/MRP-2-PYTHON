"""Módulo de cadastro, consulta e alteração de itens (PA, SA, MP)."""

from typing import Any
from persistencia import carregar_json, salvar_json
from utils import extrair_tipo_item, validar_codigo_item

TIPOS_VALIDOS = {
    "PA": "Produto Acabado",
    "SA": "Semiacabado",
    "MP": "Matéria-Prima",
}


def listar_itens(filtro_tipo: str | None = None) -> list[dict[str, Any]]:
    itens = carregar_json("itens")
    lista = list(itens.values())
    if filtro_tipo:
        lista = [item for item in lista if item["tipo"] == filtro_tipo.upper()]
    return sorted(lista, key=lambda x: x["codigo"])


def buscar_item(codigo: str) -> dict[str, Any] | None:
    itens = carregar_json("itens")
    return itens.get(codigo.strip().upper())


def cadastrar_item(
    codigo: str,
    descricao: str,
    unidade: str,
    custo_unitario: float,
    lead_time: int,
    estoque_seguranca: float,
    lote_minimo: float,
    saldo_inicial: float = 0.0,
) -> dict[str, Any]:
    valido, codigo_ou_erro = validar_codigo_item(codigo)
    if not valido:
        raise ValueError(codigo_ou_erro)

    codigo_limpo = codigo_ou_erro
    itens = carregar_json("itens")
    if codigo_limpo in itens:
        raise ValueError(f"O item {codigo_limpo} já está cadastrado.")

    descricao_limpa = descricao.strip()
    if not descricao_limpa:
        raise ValueError("A descrição do item não pode ficar vazia.")

    unidade_limpa = unidade.strip().lower()
    if not unidade_limpa:
        raise ValueError("Informe a unidade de medida (ex: un, m, L, kg).")

    if custo_unitario < 0 or lead_time < 0 or estoque_seguranca < 0 or lote_minimo <= 0:
        raise ValueError("Valores numéricos inválidos (lote mínimo deve ser > 0).")

    tipo = extrair_tipo_item(codigo_limpo)
    novo_item = {
        "codigo": codigo_limpo,
        "descricao": descricao_limpa,
        "tipo": tipo,
        "unidade": unidade_limpa,
        "custo_unitario": float(custo_unitario),
        "lead_time": int(lead_time),
        "estoque_seguranca": float(estoque_seguranca),
        "lote_minimo": float(lote_minimo),
    }

    itens[codigo_limpo] = novo_item
    salvar_json("itens", itens)

    estoque = carregar_json("estoque")
    if codigo_limpo not in estoque:
        estoque[codigo_limpo] = float(saldo_inicial)
        salvar_json("estoque", estoque)

    return novo_item


def alterar_item(
    codigo: str,
    descricao: str | None = None,
    unidade: str | None = None,
    custo_unitario: float | None = None,
    lead_time: int | None = None,
    estoque_seguranca: float | None = None,
    lote_minimo: float | None = None,
) -> dict[str, Any]:
    codigo_limpo = codigo.strip().upper()
    itens = carregar_json("itens")
    if codigo_limpo not in itens:
        raise ValueError(f"Item {codigo_limpo} não encontrado.")

    item = itens[codigo_limpo]

    if descricao is not None and descricao.strip():
        item["descricao"] = descricao.strip()
    if unidade is not None and unidade.strip():
        item["unidade"] = unidade.strip().lower()
    if custo_unitario is not None:
        if custo_unitario < 0:
            raise ValueError("Custo unitário não pode ser negativo.")
        item["custo_unitario"] = float(custo_unitario)
    if lead_time is not None:
        if lead_time < 0:
            raise ValueError("Lead time não pode ser negativo.")
        item["lead_time"] = int(lead_time)
    if estoque_seguranca is not None:
        if estoque_seguranca < 0:
            raise ValueError("Estoque de segurança não pode ser negativo.")
        item["estoque_seguranca"] = float(estoque_seguranca)
    if lote_minimo is not None:
        if lote_minimo <= 0:
            raise ValueError("Lote mínimo deve ser maior que zero.")
        item["lote_minimo"] = float(lote_minimo)

    itens[codigo_limpo] = item
    salvar_json("itens", itens)
    return item