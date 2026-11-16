"""Funções utilitárias de validação, formatação e regras gerais."""

from datetime import datetime
import re


PADRAO_CODIGO_ITEM = re.compile(r"^(PA|SA|MP)-\d{3}$")


def validar_codigo_item(codigo: str) -> tuple[bool, str]:
    codigo_limpo = codigo.strip().upper()
    if not PADRAO_CODIGO_ITEM.match(codigo_limpo):
        return False, "Código inválido. Use o formato PA-001, SA-010 ou MP-100."
    return True, codigo_limpo


def extrair_tipo_item(codigo: str) -> str:
    return codigo.strip().upper().split("-")[0]


def validar_float_positivo(valor_str: str, permitir_zero: bool = True) -> float:
    try:
        valor = float(str(valor_str).strip().replace(",", "."))
    except ValueError as exc:
        raise ValueError("Digite um número válido.") from exc

    if permitir_zero and valor < 0:
        raise ValueError("O valor não pode ser negativo.")
    if not permitir_zero and valor <= 0:
        raise ValueError("O valor deve ser maior que zero.")
    return valor


def validar_int_positivo(valor_str: str, permitir_zero: bool = True) -> int:
    try:
        valor = int(str(valor_str).strip())
    except ValueError as exc:
        raise ValueError("Digite um número inteiro válido.") from exc

    if permitir_zero and valor < 0:
        raise ValueError("O valor não pode ser negativo.")
    if not permitir_zero and valor <= 0:
        raise ValueError("O valor deve ser maior que zero.")
    return valor


def formatar_moeda(valor: float) -> str:
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def data_hoje_str() -> str:
    return datetime.now().strftime("%d/%m/%Y")


def validar_data(data_str: str) -> str:
    data_limpa = data_str.strip()
    try:
        datetime.strptime(data_limpa, "%d/%m/%Y")
        return data_limpa
    except ValueError as exc:
        raise ValueError("Data inválida. Utilize o formato DD/MM/AAAA.") from exc