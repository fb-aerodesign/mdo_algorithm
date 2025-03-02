# Módulo `mdo_algorithm`

# 1. `disciplines`

Disciplinas de projeto de aeronaves, cada uma responsável por modelar e simular um aspecto específico do projeto. As disciplinas disponíveis são:

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

Para isso, recebe o argumento `coefficients`, um DataFrame com os coeficientes de sustentação e ângulos de ataque em graus.

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

##### 1.1.4.1.2. `Header`

Classe para representar o cabeçalho de um arquivo de entrada de geometria do [AVL](https://web.mit.edu/drela/Public/web/avl/). Descreve os valores padrão para coordenadas, simetria e dimensões de referência.

Possui o método `to_avl` para converter os valores em uma string formatada para o [AVL](https://web.mit.edu/drela/Public/web/avl/).

##### 1.1.4.1.3. `ProfileDragSettings`

Classe para representar as configurações de arrasto parasita de um perfil aerodinâmico.

O [AVL](https://web.mit.edu/drela/Public/web/avl/) não considera os efeitos viscosos, essas configurações permitem alimentá-lo com dados obtidos por métodos que consideram a viscosidade, como o [XFOIL](https://web.mit.edu/drela/Public/web/xfoil/), para obter um arrasto mais preciso no [AVL](https://web.mit.edu/drela/Public/web/avl/).

Essa configuração corresponde ao parâmetro CDCL do [AVL](https://web.mit.edu/drela/Public/web/avl/), no qual são definidos valores de coeficiente de arrasto em função do coeficiente de sustentação, sendo:

- CL1 CD1: para baixo CL.
- CL2 CD2: região principal da polar.
- CL3 CD3: para alto CL.

O método `from_xfoil_coefficients` permite criar uma instância a partir de coeficientes obtidos no [XFOIL](https://web.mit.edu/drela/Public/web/xfoil/) de forma automática. Para isso, é necessário fornecer um DataFrame com os coeficientes de sustentação e arrasto em um intervalo apropriado de ângulo de ataque, recomendado em torno de 0° a 20° com incremento de 0,5°.

##### 1.1.4.1.4. `Control`

Classe para representar uma superfície de controle no [AVL](https://web.mit.edu/drela/Public/web/avl/).

Possui o método `to_avl` para converter os valores em uma string formatada para o [AVL](https://web.mit.edu/drela/Public/web/avl/).

##### 1.1.4.1.5. `Section`

Classe para representar uma seção de superfície sustentadora no [AVL](https://web.mit.edu/drela/Public/web/avl/).

Possui o método `to_avl` para converter os valores em uma string formatada para o [AVL](https://web.mit.edu/drela/Public/web/avl/).

##### 1.1.4.1.6. `Body`

Classe para representar uma fuselagem ou um corpo não sustentador no [AVL](https://web.mit.edu/drela/Public/web/avl/).

Possui o método `to_avl` para converter os valores em uma string formatada para o [AVL](https://web.mit.edu/drela/Public/web/avl/).

##### 1.1.4.1.7. `Surface`

Classe para representar uma superfície sustentadora no [AVL](https://web.mit.edu/drela/Public/web/avl/).

Possui o método `to_avl` para converter os valores em uma string formatada para o [AVL](https://web.mit.edu/drela/Public/web/avl/).

##### 1.1.4.1.8. `GeometryInput`

Classe para representar um arquivo de entrada de geometria do [AVL](https://web.mit.edu/drela/Public/web/avl/).

Possui o método `from_wing` para criar uma instância automaticamente a partir de um objeto [`Wing`](#11433-wing).

Possui o método `to_avl` para converter os valores em uma string formatada para o [AVL](https://web.mit.edu/drela/Public/web/avl/).

##### 1.1.4.1.9. `MassInput`

Classe para representar um arquivo de entrada de massa do [AVL](https://web.mit.edu/drela/Public/web/avl/).

Possui o método `from_wing` para criar uma instância automaticamente a partir de um objeto [`Wing`](#11433-wing).

Possui o método `to_mass` para converter os valores em uma string formatada para o [AVL](https://web.mit.edu/drela/Public/web/avl/).

#### 1.1.4.2. `dataframe`

[mdo_algorithm.disciplines.aerodynamics.models.dataframe](../disciplines/aerodynamics/models/dataframe/main.py)

Modelos de dados para análises aerodinâmicas com DataFrames.

##### 1.1.4.2.1. `Coefficients`

DataFrame para armazenar coeficientes de sustentação e arrasto em função do ângulo de ataque.

| Coluna | Tipo | Descrição |
| --- | --- | --- |
| `alpha` | `float` | Ângulo de ataque em graus. |
| `lift_coefficient` | `float` | Coeficiente de sustentação. |
| `drag_coefficient` | `float` | Coeficiente de arrasto. |
| `moment_coefficient` | `float` | Coeficiente de momento. |

##### 1.1.4.2.2. `LiftCoefficientDistribution`

DataFrame para armazenar distribuição do coeficiente de sustentação ao longo da envergadura.

| Coluna | Tipo | Descrição |
| --- | --- | --- |
| `spanwise_location` | `float` | Localização ao longo da envergadura. |
| `lift_coefficient` | `float` | Coeficiente de sustentação. |

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

Possui o método `span` para obter a envergadura da asa em $ \text{m} $. Para isso, é obtido o dobro da localização da seção mais externa da asa.

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

Possui o método `planform_area` para obter a área da forma em planta da asa em $ \text{m}^{2} $. A área é obtida calculando o dobro da integral da corda ao longo da meia envergadura, utilizando a equação:

$$
S = 2 \int_{0}^{y_{\text{máx}}} c(y) \ dy
$$

O cálculo da integral é feito utilizando a função `quad` do módulo `scipy.integrate`.

```python
def planform_area(self) -> float:
    return 2 * quad(self.chord_distribution, 0, self.span() / 2)[0]
```

Possui o método `mean_aerodynamic_chord` para obter a corda aerodinâmica média $ C_{MAC} $ da asa em $ \text{m} $. A corda é obtida calculando uma integral descrita na equação:

$$
C_{MAC} = \frac{2}{S} \int_{0}^{y_{\text{máx}}} c(y)^{2} \, dy
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

temperatura ao nível do mar em $ \text{K} $ = $ 288.15 \text{K} $

#### 1.2.1.2. `SEA_LEVEL_PRESSURE`

pressão ao nível do mar em $ \text{Pa} $ = $ 101325 \text{Pa} $

#### 1.2.1.3. `TEMPERATURE_LAPSE_RATE`

taxa de variação da temperatura com a altitude em $ \frac{\text{K}}{\text{m}} $ = $ 0.0065 \frac{\text{K}}{\text{m}} $

#### 1.2.1.4. `MOLAR_GAS_CONSTANT`

constante universal dos gases em $ \frac{\text{J}}{\text{mol} \cdot \text{K}} $ = $ 8.3145 \frac{\text{J}}{\text{mol} \cdot \text{K}} $

#### 1.2.1.5. `MOLAR_MASS_FOR_DRY_AIR`

massa molar do ar seco em $ \frac{\text{kg}}{\text{mol}} $ = $ 0.028966 \frac{\text{kg}}{\text{mol}} $

#### 1.2.1.6. `GRAVITATIONAL_ACCELERATION`

aceleração gravitacional em $ \frac{\text{m}}{\text{s}^{2}} $ = $ 9.80665 \frac{\text{m}}{\text{s}^{2}} $

#### 1.2.1.7. `SEA_LEVEL_AIR_DYNAMIC_VISCOSITY`

viscosidade dinâmica do ar ao nível do mar em $ \text{Pa} \cdot \text{s} $ = $ 1.716 \cdot 10^{-5} \text{Pa} \cdot \text{s} $

#### 1.2.1.8. `SUTHERLAND_CONSTANT`

constante de Sutherland em $ \text{K} $ = $ 110.4 \text{K} $

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

- $ \rho $ é a densidade do ar em $ \frac{\text{kg}}{\text{m}^{3}} $
- $ P $ é a pressão atmosférica local em $ \text{Pa} $
- $ R_{\text{ar}} $ é a constante específica do ar seco em $ \frac{\text{J}}{\text{mol} \cdot \text{K}} $
- $ T $ é a temperatura em $ \text{K} $

A constante específica do ar seco é calculada utilizando a equação:

$$
R_{\text{ar}} = \frac{R}{M_{\text{ar}}}
$$

Onde:

- $ R $ é a [constante universal dos gases](#1214-molar_gas_constant) em $ \frac{\text{J}}{\text{mol} \cdot \text{K}} $
- $ M_{\text{ar}} $ é a [massa molar do ar seco](#1215-molar_mass_for_dry_air) em $ \frac{\text{kg}}{\text{mol}} $

A temperatura é estimada utilizando a equação:

$$
T = T_{0} - L \cdot h
$$

Onde:

- $ T_{0} $ é a [temperatura ao nível do mar](#1211-sea_level_temperature) em $ \text{K} $
- $ L $ é a [taxa de variação da temperatura com a altitude](#1213-temperature_lapse_rate) em $ \frac{\text{K}}{\text{m}} $
- $ h $ é a altitude em $ \text{m} $

A pressão atmosférica local é estimada utilizando a equação barométrica para altitudes até 11 km:

$$
P = P_{0} \left(1 - \frac{L \cdot h}{T_{0}}\right)^{\frac{g}{R_{\text{ar}} \cdot L}}
$$

Onde:

- $ P_{0} $ é a [pressão ao nível do mar](#1212-sea_level_pressure) em $ \text{Pa} $
- $ g $ é a [aceleração gravitacional](#1216-gravitational_acceleration) em $ \frac{\text{m}}{\text{s}^{2}} $

#### 1.2.2.2. `air_viscosity`

Calcula a viscosidade dinâmica do ar em função da temperatura.

Para isso, utiliza a equação de Sutherland, que considera a variação da viscosidade com a temperatura.

$$
\mu = \mu_{0} \left(\frac{T}{T_{0}}\right)^{\frac{3}{2}} \left(\frac{T_{0} + S}{T + S}\right)
$$

Onde:

- $ \mu $ é a viscosidade dinâmica do ar em $ \text{Pa} \cdot \text{s} $
- $ \mu_{0} $ é a [viscosidade dinâmica do ar ao nível do mar](#1217-sea_level_air_dynamic_viscosity) em $ \text{Pa} \cdot \text{s} $
- $ T $ é a temperatura em $ \text{K} $
- $ T_{0} $ é a [temperatura ao nível do mar](#1211-sea_level_temperature) em $ \text{K} $
- $ S $ é a [constante de Sutherland](#1218-sutherland_constant) em $ \text{K} $

#### 1.2.2.3. `reynolds_number`

Calcula o número de Reynolds em função da velocidade, corda e viscosidade dinâmica.

Para isso, utiliza a equação:

$$
\text{Re} = \frac{\rho \cdot V \cdot l}{\mu}
$$

Onde:

- $ \text{Re} $ é o número de Reynolds
- $ \rho $ é a densidade do ar em $ \frac{\text{kg}}{\text{m}^{3}} $
- $ V $ é a velocidade em $ \frac{\text{m}}{\text{s}} $
- $ l $ é o comprimento de referência em $ \text{m} $
- $ \mu $ é a viscosidade dinâmica do ar em $ \text{Pa} \cdot \text{s} $

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
