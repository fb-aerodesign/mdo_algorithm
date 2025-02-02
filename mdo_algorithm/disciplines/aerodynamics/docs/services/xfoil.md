# Serviço de Interação com XFOIL

Este documento descreve o funcionamento do módulo `xfoil`, que permite a automação do software XFOIL para análises aerodinâmicas.

## 1. Introdução

O XFOIL é um software amplamente utilizado para análise de aerofólios, permitindo a obtenção de coeficientes aerodinâmicos como coeficiente de sustentação (Cl), coeficiente de arrasto (Cd) e coeficiente de momento (Cm). O módulo `xfoil` fornece uma interface automatizada para comunicação com o XFOIL via subprocessos.

## 2. Estrutura do Módulo

O módulo define a classe `XfoilService`, que contém métodos para execução do XFOIL e obtenção de coeficientes aerodinâmicos.

### 2.1 Classe `XfoilService`

A classe `XfoilService` é responsável por executar comandos no XFOIL e processar os resultados.

```python
class XfoilService:
    """
    Serviço para interação com o XFOIL.
    """
```

#### 2.1.1 Método `run_xfoil`

Executa o XFOIL utilizando um conjunto de comandos passados como entrada.

```python
def run_xfoil(self, commands: list[str]) -> None:
    with subprocess.Popen(
        [os.path.join(XFOIL_PATH, "xfoil.exe")],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as xfoil_process:
        xfoil_process.communicate("\n".join(commands))
```

#### 2.1.2 Método `get_coefficients`

Obtém os coeficientes aerodinâmicos para um aerofólio específico em diferentes ângulos de ataque.

```python
def get_coefficients(
    self,
    airfoil: Airfoil,
    alpha: list[float] | tuple[float, float, float],
    reynolds: float | None,
    iterations: int | None,
) -> DataFrame[Coefficients]:
```

**Parâmetros:**
- `airfoil`: Aerofólio a ser analisado.
- `alpha`: Lista de ângulos de ataque ou um intervalo no formato `(início, fim, incremento)`.
- `reynolds`: Número de Reynolds para análise.
- `iterations`: Número de iterações para convergência no XFOIL.

**Retorno:**
- Um `DataFrame` contendo os coeficientes aerodinâmicos.

O método gera comandos para carregar o aerofólio, definir condições de voo e calcular os coeficientes:

```python
commands = [f"LOAD {airfoil_path}", "PANE", "OPER"]
if reynolds is not None:
    commands.append(f"VISC {reynolds}")
    if iterations is not None:
        commands.append(f"ITER {iterations}")
commands.append("PACC")
commands.append(result_file_path)
commands.append("")
```

Os resultados são processados em um `DataFrame` Pandas:

```python
df = DataFrame[Coefficients](
    pd.read_fwf(
        result_file_path,
        colspecs=[(2, 8), (10, 17), (19, 27), (29, 37), (39, 46)],
        names=["alpha", "Cl", "Cd", "Cd_pressure", "Cm"],
        dtype={"alpha": float, "Cl": float, "Cd": float, "Cd_pressure": float, "Cm": float},
        skiprows=12,
    )
)
```

#### 2.1.3 Método `plot_coefficients`

Este método gera gráficos dos coeficientes aerodinâmicos obtidos:

```python
def plot_coefficients(self, coefficients_array: list[DataFrame[Coefficients]]) -> None:
```

Ele cria gráficos para Cl, Cd, Cm e Cl/Cd em função do ângulo de ataque:

```python
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
fig.suptitle("Coefficients")
for coefficients in coefficients_array:
    ax1.plot(coefficients["alpha"], coefficients["Cl"], label=label)
    ax2.plot(coefficients["alpha"], coefficients["Cd"], label=label)
    ax3.plot(coefficients["alpha"], coefficients["Cm"], label=label)
    ax4.plot(coefficients["alpha"], coefficients["Cl"] / coefficients["Cd"], label=label)
```

## 3. Conclusão

O módulo `xfoil` permite a automação da análise de aerofólios no XFOIL, facilitando a obtenção de coeficientes aerodinâmicos de forma programática. Isso é útil para projetos de aeronaves, otimização de perfis e estudos aerodinâmicos.
