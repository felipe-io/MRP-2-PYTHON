# Sistema MRP II — Pedal Forte Bicicletas Ltda.

Sistema de Planejamento dos Recursos de Manufatura (**MRP II**) desenvolvido em Python 3.10+ para a fábrica fictícia **Pedal Forte Bicicletas Ltda.**, como projeto da disciplina de **Programação em Python** (Engenharia de Computação — CEFET-MG, Campus V).

---

## 1. Visão Geral e Funcionalidades (Requisitos Funcionais)

O sistema integra o planejamento de materiais (MRP), capacidade produtiva (CRP), controle de estoques e custeio industrial em uma interface gráfica desktop construída com `Tkinter` / `ttk` e visualizações analíticas via `Matplotlib`.

| ID | Requisito Funcional | Módulo Responsável |
| :--- | :--- | :--- |
| **RF01** | Interface principal organizada por abas de navegação | `menu.py`, `main.py` |
| **RF02** | Cadastro, listagem e alteração de itens (`PA`, `SA`, `MP`) | `itens.py` |
| **RF03** | Estrutura de produto (`BOM`) em até 3 níveis com explosão recursiva | `estrutura.py` |
| **RF04** | Movimentações de estoque (`ENTRADA`, `SAIDA`, `AJUSTE`) | `estoque.py` |
| **RF05** | Consulta de saldo e histórico Kardex com alerta de estoque de segurança | `estoque.py` |
| **RF06** | Cadastro de centros de trabalho e roteiros de operação única | `capacidade.py` |
| **RF07** | Plano Mestre de Produção (`MPS`) em horizonte de 8 semanas | `mps.py` |
| **RF08** | Cálculo completo do `MRP` multinível (`PA` $\rightarrow$ `SA` $\rightarrow$ `MP`) | `mrp.py` |
| **RF09** | Geração automática de Ordens de Produção (`OP`) e Compra (`OC`) | `mrp.py` |
| **RF10** | Controle de ciclo de vida das ordens (`PLANEJADA`, `FIRME`, `LIBERADA`, `ENCERRADA`) | `ordens.py` |
| **RF11** | Apontamento de produção com validação de saldo e baixa de componentes | `ordens.py` |
| **RF12** | Planejamento de Carga $\times$ Capacidade (`CRP`) com detecção de sobrecarga | `capacidade.py` |
| **RF13** | Cálculo recursivo de Custo Padrão (materiais + mão de obra direta) | `custos.py` |
| **RF14** | Exportação de posição de estoque e ordens em formato `CSV` | `relatorios.py` |
| **RF15** | Persistência automática em JSON e CSV na pasta `data/` | `persistencia.py` |
| **RF16** | Geração de 4 gráficos gerenciais exibidos em tela e salvos em `PNG` | `graficos.py` |

---

## 2. Arquitetura do Projeto

```text
MRP2_PedalForte/
├── main.py             # Ponto de entrada da aplicação
├── menu.py             # Interface gráfica (Tkinter / ttk)
├── itens.py            # CRUD de itens (PA, SA, MP)
├── estrutura.py        # BOM e explosão recursiva em 3 níveis
├── estoque.py          # Movimentações, saldo e Kardex imutável
├── mps.py              # Plano Mestre de Produção (8 semanas)
├── mrp.py              # Motor de cálculo MRP
├── ordens.py           # Gestão de OPs/OCs e apontamento de produção
├── capacidade.py       # Centros de trabalho, roteiros e cálculo CRP
├── custos.py           # Cálculo recursivo do custo padrão
├── relatorios.py       # Exportação CSV via pandas
├── graficos.py         # Gráficos gerenciais via matplotlib
├── persistencia.py     # Leitura e gravação em JSON e CSV
├── utils.py            # Validações de regras de negócio e formatação
├── data/               # Base de dados persistente (JSON/CSV)
├── docs/               # Relatórios exportados, gráficos PNG, reflexão e GitHub Pages
└── README.md           # Documentação do projeto
```

---

## 3. Decisões de Projeto

- **Separação entre Lógica de Negócio e Interface:** toda a regra matemática do MRP, CRP, custeio e controle de estoque foi implementada em Python puro, sem dependências externas de ERP (RNF08), mantendo a interface gráfica isolada em `menu.py`.
- **Recursividade na BOM e no Custeio:** tanto a explosão indentada da estrutura de produto (`estrutura.py`) quanto a apuração do custo padrão acumulado (`custos.py`) utilizam funções recursivas, respeitando a hierarquia estrita de 3 níveis (`PA` $\rightarrow$ `SA` $\rightarrow$ `MP`), o que também impede ciclos na estrutura (RN03).
- **Persistência Híbrida (JSON + CSV):** entidades estruturadas (itens, BOM, roteiros, MPS e ordens) são armazenadas em arquivos JSON legíveis, enquanto o histórico de movimentações de estoque (Kardex) utiliza `movimentos.csv` em modo *append* para garantir a imutabilidade dos registros (RN10).
- **Interface Gráfica Nativa (Tkinter/ttk):** optou-se pelo `ttk` estilizado visando leveza, estabilidade em ambiente Linux e execução sem necessidade de dependências pesadas de interface.

---

## 4. Como Executar (Ambiente Linux)

### Pré-requisitos

- Python 3.10 ou superior
- Bibliotecas `pandas`, `matplotlib`, `numpy` e `python3-tk`

No Debian/Ubuntu/Linux Mint, instale as dependências caso necessário:

```bash
sudo apt update && sudo apt install -y python3-tk
pip install pandas matplotlib numpy
```

### Execução

Clone o repositório, acesse o diretório do projeto e execute o `main.py`:

```bash
git clone <URL_DO_REPOSITORIO>
cd MRP2_PedalForte
python3 main.py
```

O sistema já acompanha uma base de demonstração pré-populada na pasta `data/`, contendo 2 Produtos Acabados (`PA-001`, `PA-002`), 2 Semiacabados (`SA-010`, `SA-020`), 10 Matérias-Primas (`MP-100` a `MP-304`) e 3 Centros de Trabalho (`CT-01` a `CT-03`), conforme RNF09.