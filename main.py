"""Ponto de entrada do Sistema MRP II - Pedal Forte Bicicletas Ltda."""

from menu import iniciar_interface
from persistencia import garantir_diretorio


def main() -> None:
    garantir_diretorio()
    iniciar_interface()


if __name__ == "__main__":
    main()