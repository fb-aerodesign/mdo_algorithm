# Módulo `mdo_algorithm`

# Íncide

1. [`disciplines`](#1-disciplines)
   1. [`aerodynamics`](#11-aerodynamics)
      1. [`airfoils`](#111-airfoils)
      2. [`constants`](#112-constants)
      3. [`functions`](#113-functions)
         1. [`lift_coefficient_slope`](#1131-lift_coefficient_slope)
         2. [`plot_coefficients`](#1132-plot_coefficients)
         3. [`plot_drag_polar`](#1133-plot_drag_polar)
         4. [`plot_lift_distribution`](#1134-plot_lift_distribution)
      4. [`models`](#114-models)
         1. [`avl`](#1141-avl)
            1. [`Symmetry`](#11411-symmetry)
            2. [`Deflection`](#11412-deflection)
            3. [`Header`](#11413-header)
            4. [`ProfileDragSettings`](#11414-profiledragsettings)
            5. [`Control`](#11415-control)
            6. [`Section`](#11416-section)
            7. [`Body`](#11417-body)
            8. [`Surface`](#11418-surface)
            9. [`GeometryInput`](#11419-geometryinput)
            10. [`MassInput`](#114110-massinput)
         2. [`dataframe`](#1142-dataframe)
            1. [`Coefficients`](#11421-coefficients)
            2. [`LiftCoefficientDistribution`](#11422-liftcoefficientdistribution)
         3. [`geometries`](#1143-geometries)
            1. [`Airfoil`](#11431-airfoil)
            2. [`SurfaceSection`](#11432-surfacesection)
            3. [`Wing`](#11433-wing)
      5. [`services`](#115-services)
         1. [`avl`](#1151-avl)
            1. [`AvlService`](#11511-avlservice)
         2. [`xfoil`](#1152-xfoil)
            1. [`XfoilService`](#11521-xfoilservice)
   2. [`common`](#12-common)
      1. [`constants`](#121-constants)
         1. [`SEA_LEVEL_TEMPERATURE`](#1211-sea_level_temperature)
         2. [`SEA_LEVEL_PRESSURE`](#1212-sea_level_pressure)
         3. [`TEMPERATURE_LAPSE_RATE`](#1213-temperature_lapse_rate)
         4. [`MOLAR_GAS_CONSTANT`](#1214-molar_gas_constant)
         5. [`MOLAR_MASS_FOR_DRY_AIR`](#1215-molar_mass_for_dry_air)
         6. [`GRAVITATIONAL_ACCELERATION`](#1216-gravitational_acceleration)
         7. [`SEA_LEVEL_AIR_DYNAMIC_VISCOSITY`](#1217-sea_level_air_dynamic_viscosity)
         8. [`SUTHERLAND_CONSTANT`](#1218-sutherland_constant)
      2. [`functions`](#122-functions)
         1. [`air_density`](#1221-air_density)
         2. [`air_viscosity`](#1222-air_viscosity)
         3. [`reynolds_number`](#1223-reynolds_number)
      3. [`models`](#123-models)
         1. [`geometries`](#1231-geometries)
            1. [`Point`](#1231-point)
            2. [`ProductsOfInertia`](#1232-productsofinertia)
            3. [`MassProperties`](#1233-massproperties)
2. [`softwares`](#2-softwares)
   1. [`avl`](#21-avl)
   2. [`xfoil`](#22-xfoil)

# 1. `disciplines`

Disciplinas de projeto de aeronaves, cada uma responsável por modelar e simular um aspecto específico do projeto.

## 1.1. `aerodynamics`

Ferramentas para modelar e simular o comportamento aerodinâmico de uma aeronave.

### 1.1.1. `airfoils`

Arquivos com coordenadas de diversos perfis aerodinâmicos, utilizados para modelar as seções de asas e estabilizadores. Os arquivos estão no formato `.dat` e seguem a convenção de coordenadas `(x, y)`.

### 1.1.2. `constants`

[mdo_algorithm.disciplines.aerodynamics.constants](../disciplines/aerodynamics/constants/main.py)

Valores constantes utilizados nas simulações aerodinâmicas. Esses valores são:

- `XFOIL_PATH`: caminho para o executável do [XFOIL](https://web.mit.edu/drela/Public/web/xfoil/), utilizado para análises de perfis aerodinâmicos.
- `AVL_PATH`: caminho para o executável do [AVL](https://web.mit.edu/drela/Public/web/avl/), utilizado para análises de superfícies aerodinâmicas.
- `AIRFOILS_PATH`: caminho para a pasta com os arquivos de perfis aerodinâmicos.

### 1.1.3. `functions`

[mdo_algorithm.disciplines.aerodynamics.functions](../disciplines/aerodynamics/functions/main.py)

Funções utilitárias para cálculos aerodinâmicos.

#### 1.1.3.1. `lift_coefficient_slope`

Calcula a inclinação em $\text{rad}^{-1}$ da curva de coeficiente de sustentação em relação ao ângulo de ataque.

Para isso, recebe o argumento `coefficients`, um [DataFrame](#11421-coefficients) com os coeficientes de sustentação e ângulos de ataque em graus.

```python
def lift_coefficient_slope(coefficients: DataFrame[Coefficients]) -> float: ...
```

O DataFrame é filtrado para considerar a região linear da curva, considerando um intervalo de ângulo de ataque de 0° a 5°.

O ângulo de ataque é convertido para radianos, utilizando a equação:

$$
\alpha_{\text{radianos}} = \alpha_{\text{graus}} \cdot \frac{\pi}{180}
$$

Para $\pi$, utiliza-se a constante `pi` do módulo `numpy`.

```python
mask = (coefficients["alpha"] > 0) & (coefficients["alpha"] < 5)
alpha = coefficients.loc[mask, "alpha"] * np.pi / 180
cl = coefficients.loc[mask, "lift_coefficient"]
```

O resultado é calculado através de uma regressão linear, utilizando a equação:

$$
\text{inclinação} = \frac{\Delta C_{L}}{\Delta \alpha}
$$

Utiliza-se a função `linregress` do módulo `scipy.stats`.

```python
return linregress(alpha, cl).slope
```

#### 1.1.3.2 `plot_coefficients`

Plota os coeficientes de sustentação e arrasto em função do ângulo de ataque.

#### 1.1.3.3 `plot_drag_polar`

Plota o coeficiente de arrasto em função do coeficiente de sustentação.

#### 1.1.3.4 `plot_lift_distribution`

Plota o coeficiente de sustentação ao longo da envergadura.

### 1.1.4. `models`

Classes para modelagem de dados de aerodinâmica.

#### 1.1.4.1. `avl`

[mdo_algorithm.disciplines.aerodynamics.models.avl](../disciplines/aerodynamics/models/avl/main.py)

Modelos de dados para análises aerodinâmicas com o [AVL](https://web.mit.edu/drela/Public/web/avl/).

##### 1.1.4.1.1. `Symmetry`

Classe Enum que define uma condição de simetria. Corresponde aos parâmetros iYsym e iZsym do [AVL](https://web.mit.edu/drela/Public/web/avl/).

- `SYMMETRIC`: simétrico com relação ao plano de referência (1 no [AVL](https://web.mit.edu/drela/Public/web/avl/)).
- `ANTISYMMETRIC`: anti-simétrico com relação ao plano de referência (-1 no [AVL](https://web.mit.edu/drela/Public/web/avl/)).
- `IGNORE`: ignorar a simetria (0 no [AVL](https://web.mit.edu/drela/Public/web/avl/)).

##### 1.1.4.1.2. `Deflection`

Classe Enum que define um tipo de deflexão para superfícies espelhadas. Corresponde ao parâmetro SgnDup do [AVL](https://web.mit.edu/drela/Public/web/avl/).

- `NORMAL`: deflexão normal (1 no [AVL](https://web.mit.edu/drela/Public/web/avl/)).
- `INVERSE`: deflexão invertida (-1 no [AVL](https://web.mit.edu/drela/Public/web/avl/)).

##### 1.1.4.1.3. `Header`

Classe para representar o cabeçalho de um arquivo de entrada de geometria do [AVL](https://web.mit.edu/drela/Public/web/avl/). Descreve os valores padrão para coordenadas, simetria e dimensões de referência.

Possui o método `to_avl` para converter os valores em uma string formatada para o [AVL](https://web.mit.edu/drela/Public/web/avl/).

##### 1.1.4.1.4. `ProfileDragSettings`

Classe para representar as configurações de arrasto parasita de um perfil aerodinâmico.

O [AVL](https://web.mit.edu/drela/Public/web/avl/) não considera os efeitos viscosos, essas configurações permitem alimentá-lo com dados obtidos por métodos que consideram a viscosidade, como o [XFOIL](https://web.mit.edu/drela/Public/web/xfoil/), para obter um arrasto mais preciso no [AVL](https://web.mit.edu/drela/Public/web/avl/).

Essa configuração corresponde ao parâmetro CDCL do [AVL](https://web.mit.edu/drela/Public/web/avl/), no qual são definidos valores de coeficiente de arrasto em função do coeficiente de sustentação, sendo:

- CL1 CD1: para baixo CL.
- CL2 CD2: região principal da polar.
- CL3 CD3: para alto CL.

O método `from_xfoil_coefficients` permite criar uma instância a partir de coeficientes obtidos no [XFOIL](https://web.mit.edu/drela/Public/web/xfoil/) de forma automática. Para isso, é necessário fornecer um [DataFrame](#11421-coefficients) com os coeficientes de sustentação e arrasto em um intervalo apropriado de ângulo de ataque, recomendado em torno de 0° a 20° com incremento de 0,5°.

##### 1.1.4.1.5. `Control`

Classe para representar uma superfície de controle no [AVL](https://web.mit.edu/drela/Public/web/avl/).

Possui o método `to_avl` para converter os valores em uma string formatada para o [AVL](https://web.mit.edu/drela/Public/web/avl/).

##### 1.1.4.1.6. `Section`

Classe para representar uma seção de superfície sustentadora no [AVL](https://web.mit.edu/drela/Public/web/avl/).

Possui o método `to_avl` para converter os valores em uma string formatada para o [AVL](https://web.mit.edu/drela/Public/web/avl/).

##### 1.1.4.1.7. `Body`

Classe para representar uma fuselagem ou um corpo não sustentador no [AVL](https://web.mit.edu/drela/Public/web/avl/).

Possui o método `to_avl` para converter os valores em uma string formatada para o [AVL](https://web.mit.edu/drela/Public/web/avl/).

##### 1.1.4.1.8. `Surface`

Classe para representar uma superfície sustentadora no [AVL](https://web.mit.edu/drela/Public/web/avl/).

Possui o método `to_avl` para converter os valores em uma string formatada para o [AVL](https://web.mit.edu/drela/Public/web/avl/).

##### 1.1.4.1.9. `GeometryInput`

Classe para representar um arquivo de entrada de geometria do [AVL](https://web.mit.edu/drela/Public/web/avl/).

Possui o método `from_wing` para criar uma instância automaticamente a partir de um objeto [`Wing`](#11433-wing).

Possui o método `to_avl` para converter os valores em uma string formatada para o [AVL](https://web.mit.edu/drela/Public/web/avl/).

##### 1.1.4.1.10. `MassInput`

Classe para representar um arquivo de entrada de massa do [AVL](https://web.mit.edu/drela/Public/web/avl/).

Possui o método `from_wing` para criar uma instância automaticamente a partir de um objeto [`Wing`](#11433-wing).

Possui o método `to_mass` para converter os valores em uma string formatada para o [AVL](https://web.mit.edu/drela/Public/web/avl/).

#### 1.1.4.2. `dataframe`

[mdo_algorithm.disciplines.aerodynamics.models.dataframe](../disciplines/aerodynamics/models/dataframe/main.py)

Modelos de dados para análises aerodinâmicas com DataFrames.

##### 1.1.4.2.1. `Coefficients`

DataFrame para armazenar coeficientes de sustentação e arrasto em função do ângulo de ataque.

| Coluna               | Tipo    | Descrição                   |
| -------------------- | ------- | --------------------------- |
| `alpha`              | `float` | Ângulo de ataque em graus.  |
| `lift_coefficient`   | `float` | Coeficiente de sustentação. |
| `drag_coefficient`   | `float` | Coeficiente de arrasto.     |
| `moment_coefficient` | `float` | Coeficiente de momento.     |

##### 1.1.4.2.2. `LiftCoefficientDistribution`

DataFrame para armazenar distribuição do coeficiente de sustentação ao longo da envergadura.

| Coluna              | Tipo    | Descrição                            |
| ------------------- | ------- | ------------------------------------ |
| `spanwise_location` | `float` | Localização ao longo da envergadura. |
| `lift_coefficient`  | `float` | Coeficiente de sustentação.          |

#### 1.1.4.3. `geometries`

[mdo_algorithm.disciplines.aerodynamics.models.geometries](../disciplines/aerodynamics/models/geometries/main.py)

Modelos de dados para geometrias de aerodinâmica.

##### 1.1.4.3.1. `Airfoil`

Classe para representar um perfil aerodinâmico.

Possui o método `relative_path` para obter o caminho relativo do arquivo do perfil.

##### 1.1.4.3.2. `SurfaceSection`

Classe para representar uma seção de superfície sustentadora.

##### 1.1.4.3.3. `Wing`

Classe para representar uma asa.

Possui o método `span` para obter a envergadura da asa em metros. Para isso, é obtido o dobro da localização da seção mais externa da asa.

```python
def span(self) -> float:
    return 2 * max(s.location.y for s in self.section_array)
```

Possui o método `chord_distribution` para obter o valor de corda em determinado ponto da envergadura da asa. A distribuição é obtida através de interpolação linear entre as cordas das seções utilizando a função `interp` do módulo `numpy`.

```python
def chord_distribution(self, y: float) -> float:
    sections = sorted(self.section_array, key=lambda x: x.location.y)
    return np.interp(
        y, np.array([s.location.y for s in sections]), np.array([s.chord for s in sections])
    )
```

Possui o método `planform_area` para obter a área da forma em planta da asa em m². A área é obtida calculando o dobro da integral da corda ao longo da meia envergadura, utilizando a equação:

$$
S = 2 \int_{0}^{y_{\text{máx}}} c(y) \ dy
$$

O cálculo da integral é feito utilizando a função `quad` do módulo `scipy.integrate`.

```python
def planform_area(self) -> float:
    return 2 * quad(self.chord_distribution, 0, self.span() / 2)[0]
```

Possui o método `mean_aerodynamic_chord` para obter a corda aerodinâmica média da asa em metros. A corda é obtida calculando uma integral descrita na equação:

$$
C_{MAC} = \frac{2}{S} \int_{0}^{y_{\text{máx}}} c(y)^{2} \ dy
$$

```python
def mean_aerodynamic_chord(self) -> float:
    area = self.planform_area()
    result = 0
    if area != 0:
        result = (
            2 / area * quad(lambda x: self.chord_distribution(x) ** 2, 0, self.span() / 2)[0]
        )
    return result
```

### 1.1.5. `services`

Classes para interagir com softwares de simulação e análise aerodinâmica.

#### 1.1.5.1. `avl`

[mdo_algorithm.disciplines.aerodynamics.services.avl](../disciplines/aerodynamics/services/avl/main.py)

##### 1.1.5.1.1. `AvlService`

Classe para interagir com o [AVL](https://web.mit.edu/drela/Public/web/avl/).

Possui o método `run_avl` para executar o [AVL](https://web.mit.edu/drela/Public/web/avl/) com comandos predeterminados.

Possui o método `get_wing_coefficients` para executar uma série de comandos no [AVL](https://web.mit.edu/drela/Public/web/avl/) e obter os coeficientes aerodinâmicos a partir de um objeto [`Wing`](#11433-wing).

Possui o método `get_wing_lift_coefficient_distribution` para executar uma série de comandos no [AVL](https://web.mit.edu/drela/Public/web/avl/) e obter a distribuição do coeficiente de sustentação a partir de um objeto [`Wing`](#11433-wing).

#### 1.1.5.2. `xfoil`

[mdo_algorithm.disciplines.aerodynamics.services.xfoil](../disciplines/aerodynamics/services/xfoil/main.py)

##### 1.1.5.2.1. `XfoilService`

Classe para interagir com o [XFOIL](https://web.mit.edu/drela/Public/web/xfoil/).

Possui o método `run_xfoil` para executar o [XFOIL](https://web.mit.edu/drela/Public/web/xfoil/) com comandos predeterminados.

Possui o método `get_coefficients` para executar uma série de comandos no [XFOIL](https://web.mit.edu/drela/Public/web/xfoil/) e obter os coeficientes aerodinâmicos a partir de um objeto [`Airfoil`](#11431-airfoil).

## 1.2. `common`

Classes e funções comuns a diversas disciplinas.

### 1.2.1. `constants`

[mdo_algorithm.disciplines.common.constants](../disciplines/common/constants/main.py)

Valores constantes utilizados nas disciplinas. Esses valores são:

#### 1.2.1.1. `SEA_LEVEL_TEMPERATURE`

Temperatura ao nível do mar.

$$
288.15 \ \text{K}
$$

#### 1.2.1.2. `SEA_LEVEL_PRESSURE`

Pressão ao nível do mar.

$$
101325 \ \text{Pa}
$$

#### 1.2.1.3. `TEMPERATURE_LAPSE_RATE`

Taxa de variação da temperatura com a altitude.

$$
0.0065 \ \frac{\text{K}}{\text{m}}
$$

#### 1.2.1.4. `MOLAR_GAS_CONSTANT`

Constante universal dos gases.

$$
8.3145 \ \frac{\text{J}}{\text{mol} \cdot \text{K}}
$$

#### 1.2.1.5. `MOLAR_MASS_FOR_DRY_AIR`

Massa molar do ar seco.

$$
0.028966 \ \frac{\text{kg}}{\text{mol}}
$$

#### 1.2.1.6. `GRAVITATIONAL_ACCELERATION`

Aceleração gravitacional.

$$
9.80665 \ \frac{\text{m}}{\text{s}^{2}}
$$

#### 1.2.1.7. `SEA_LEVEL_AIR_DYNAMIC_VISCOSITY`

Viscosidade dinâmica do ar ao nível do mar.

$$
1.716 \cdot 10^{-5} \ \text{Pa} \cdot \text{s}
$$

#### 1.2.1.8. `SUTHERLAND_CONSTANT`

Constante de Sutherland.

$$
110.4 \ \text{K}
$$

### 1.2.2. `functions`

[mdo_algorithm.disciplines.common.functions](../disciplines/common/functions/main.py)

Funções utilitárias comuns a diversas disciplinas.

#### 1.2.2.1. `air_density`

Calcula a densidade do ar em função da altitude.

Para isso, utiliza a equação do modelo atmosférico ISA (International Standard Atmosphere), que considera a variação da temperatura com a altitude.

$$
\rho = \frac{P}{R_{\text{ar}} \cdot T}
$$

Onde:

$$
\rho \text{ é a densidade do ar em } \frac{\text{kg}}{\text{m}^{3}}
$$

$$
P \text{ é a pressão atmosférica local em } \text{Pa}
$$

$$
R_{\text{ar}} \text{ é a constante específica do ar seco em } \frac{\text{J}}{\text{mol} \cdot \text{K}}
$$

$$
T \text{ é a temperatura em } \text{K}
$$

A constante específica do ar seco é calculada utilizando a equação:

$$
R_{\text{ar}} = \frac{R}{M_{\text{ar}}}
$$

Onde:

$$
R \text{ é a constante universal dos gases em } \frac{\text{J}}{\text{mol} \cdot \text{K}}
$$

$$
M_{\text{ar}} \text{ é a massa molar do ar seco em } \frac{\text{kg}}{\text{mol}}
$$

A temperatura é estimada utilizando a equação:

$$
T = T_{0} - L \cdot h
$$

Onde:

$$
T_{0} \text{ é a temperatura ao nível do mar em } \text{K}
$$

$$
L \text{ é a taxa de variação da temperatura com a altitude em } \frac{\text{K}}{\text{m}}
$$

$$
h \text{ é a altitude em } \text{m}
$$

A pressão atmosférica local é estimada utilizando a equação barométrica para altitudes até 11 km:

$$
P = P_{0} \left(1 - \frac{L \cdot h}{T_{0}}\right)^{\frac{g}{R_{\text{ar}} \cdot L}}
$$

Onde:

$$
P_{0} \text{ é a pressão ao nível do mar em } \text{Pa}
$$

$$
g \text{ é a aceleração gravitacional em } \frac{\text{m}}{\text{s}^{2}}
$$

#### 1.2.2.2. `air_viscosity`

Calcula a viscosidade dinâmica do ar em função da temperatura.

Para isso, utiliza a equação de Sutherland, que considera a variação da viscosidade com a temperatura.

$$
\mu = \mu_{0} \left(\frac{T}{T_{0}}\right)^{\frac{3}{2}} \left(\frac{T_{0} + S}{T + S}\right)
$$

Onde:

$$
\mu \text{ é a viscosidade dinâmica do ar em } \text{Pa} \cdot \text{s}
$$

$$
\mu_{0} \text{ é a viscosidade dinâmica do ar ao nível do mar em } \text{Pa} \cdot \text{s}
$$

$$
T \text{ é a temperatura em } \text{K}
$$

$$
T_{0} \text{ é a temperatura ao nível do mar em } \text{K}
$$

$$
S \text{ é a constante de Sutherland em } \text{K}
$$

#### 1.2.2.3. `reynolds_number`

Calcula o número de Reynolds em função da velocidade, corda e viscosidade dinâmica.

Para isso, utiliza a equação:

$$
\text{Re} = \frac{\rho \cdot V \cdot l}{\mu}
$$

Onde:

$$
\text{Re} \text{ é o número de Reynolds}
$$

$$
\rho \text{ é a densidade do ar em } \frac{\text{kg}}{\text{m}^{3}}
$$

$$
V \text{ é a velocidade em } \frac{\text{m}}{\text{s}}
$$

$$
l \text{ é o comprimento de referência em } \text{m}
$$

$$
\mu \text{ é a viscosidade dinâmica do ar em } \text{Pa} \cdot \text{s}
$$

### 1.2.3. `models`

Classes para modelagem de dados comuns a diversas disciplinas.

#### 1.2.3.1. `geometries`

[mdo_algorithm.disciplines.common.models.geometries](../disciplines/common/models/geometries/main.py)

Modelos de dados para geometrias comuns a diversas disciplinas.

##### 1.2.3.1.1. `Point`

Classe para representar um ponto no espaço.

##### 1.2.3.1.2. `ProductsOfInertia`

Classe para representar os produtos de inércia de um corpo.

##### 1.2.3.1.3. `MassProperties`

Classe para representar as propriedades de massa de um corpo.

# 2. `softwares`

Softwares de simulação e análise.

## 2.1. `avl`

Software de análise aerodinâmica [AVL](https://web.mit.edu/drela/Public/web/avl/).

## 2.2. `xfoil`

Software de análise de perfis aerodinâmicos [XFOIL](https://web.mit.edu/drela/Public/web/xfoil/).
