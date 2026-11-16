"""Módulo de Estrutura de Produto (BOM) e explosão recursiva em até 3 níveis."""

from typing import Any
from persistencia import carregar_json, salvar_json


def obter_componentes(codigo_pai: str) -> list[dict[str, Any]]:
    estrutura = carregar_json("estrutura")
    return estrutura.get(codigo_pai.strip().upper(), [])


def cadastrar_componente(codigo_pai: str, codigo_comp: str, quantidade: float) -> None:
    pai = codigo_pai.strip().upper()
    comp = codigo_comp.strip().upper()

    if pai == comp:
        raise ValueError("Um item não pode ser componente de si mesmo.")
    if quantidade <= 0:
        raise ValueError("A quantidade por unidade deve ser maior que zero.")

    itens = carregar_json("itens")
    if pai not in itens:
        raise ValueError(f"Item pai {pai} não cadastrado.")
    if comp not in itens:
        raise ValueError(f"Componente {comp} não cadastrado.")

    tipo_pai = itens[pai]["tipo"]
    tipo_comp = itens[comp]["tipo"]

    if tipo_pai == "MP":
        raise ValueError("Matéria-Prima (MP) é comprada e não pode possuir estrutura.")
    if tipo_pai == "SA" and tipo_comp != "MP":
        raise ValueError("Um Semiacabado (SA) só pode ter Matérias-Primas (MP) como componentes.")
    if tipo_pai == "PA" and tipo_comp not in ("SA", "MP"):
        raise ValueError("Um Produto Acabado (PA) só pode ter componentes SA ou MP.")

    estrutura = carregar_json("estrutura")
    lista_comp = estrutura.get(pai, [])

    atualizado = False
    for item_bom in lista_comp:
        if item_bom["componente"] == comp:
            item_bom["quantidade"] = float(quantidade)
            atualizado = True
            break

    if not atualizado:
        lista_comp.append({"componente": comp, "quantidade": float(quantidade)})

    estrutura[pai] = lista_comp
    salvar_json("estrutura", estrutura)


def remover_componente(codigo_pai: str, codigo_comp: str) -> bool:
    pai = codigo_pai.strip().upper()
    comp = codigo_comp.strip().upper()
    estrutura = carregar_json("estrutura")
    if pai not in estrutura:
        return False

    nova_lista = [c for c in estrutura[pai] if c["componente"] != comp]
    if len(nova_lista) == len(estrutura[pai]):
        return False

    if nova_lista:
        estrutura[pai] = nova_lista
    else:
        del estrutura[pai]
    salvar_json("estrutura", estrutura)
    return True


def explodir_bom_recursivo(
    codigo_raiz: str,
    nivel: int = 0,
    multiplicador: float = 1.0,
    itens: dict[str, Any] | None = None,
    estrutura: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if itens is None:
        itens = carregar_json("itens")
    if estrutura is None:
        estrutura = carregar_json("estrutura")

    codigo = codigo_raiz.strip().upper()
    if codigo not in itens:
        raise ValueError(f"Item {codigo} não encontrado.")

    info_item = itens[codigo]
    resultado = [
        {
            "nivel": nivel,
            "codigo": codigo,
            "descricao": info_item["descricao"],
            "tipo": info_item["tipo"],
            "unidade": info_item["unidade"],
            "qtd_unitaria": multiplicador,
        }
    ]

    for filho in estrutura.get(codigo, []):
        comp_cod = filho["componente"]
        qtd_filho = float(filho["quantidade"])
        resultado.extend(
            explodir_bom_recursivo(
                codigo_raiz=comp_cod,
                nivel=nivel + 1,
                multiplicador=qtd_filho,
                itens=itens,
                estrutura=estrutura,
            )
        )

    return resultado


def formatar_arvore_bom(codigo_raiz: str) -> str:
    arvore = explodir_bom_recursivo(codigo_raiz)
    linhas = []
    for no in arvore:
        if no["nivel"] == 0:
            linhas.append(f"{no['codigo']} {no['descricao']}")
        else:
            indentacao = "  " * no["nivel"]
            qtd_fmt = f"{no['qtd_unitaria']:g}".replace(".", ",")
            linhas.append(
                f"{indentacao}- {no['codigo']} {no['descricao']} ........ {qtd_fmt} {no['unidade']}"
            )
    return "\n".join(linhas)