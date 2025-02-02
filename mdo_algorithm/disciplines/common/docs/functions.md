# Módulo `functions`

Este documento descreve o funcionamento do módulo `functions`, que contém funções auxiliares para cálculos aerodinâmicos.

## 1. Introdução

O módulo `functions` fornece funções fundamentais para a análise aerodinâmica, incluindo o cálculo da densidade do ar, viscosidade dinâmica e número de Reynolds.

## 2. Estrutura do Módulo

O módulo contém três funções principais:

- `air_density(altitude: float) -> float`
- `air_viscosity(temperature: float) -> float`
- `reynolds_number(velocity: float, reference_length: float, altitude: float, temperature: float) -> float`

### 2.1 Cálculo da Densidade do Ar

A densidade do ar é calculada com base na Atmosfera Padrão Internacional (ISA):

$$
\rho = \frac{P}{R T}
$$

Onde:
- \( P \) = pressão atmosférica (Pa)
- \( R \) = constante do gás para o ar seco (J/(kg·K))
- \( T \) = temperatura do ar (K)

A pressão atmosférica é obtida por:

$$
P = P_0 \left(1 - \frac{L h}{T_0}\right)^{\frac{g}{RL}}
$$

A implementação em Python é a seguinte:

```python
def air_density(altitude: float) -> float:
    h = altitude
    t0 = SEA_LEVEL_TEMPERATURE
    p0 = SEA_LEVEL_PRESSURE
    r0 = MOLAR_GAS_CONSTANT
    m0 = MOLAR_MASS_FOR_DRY_AIR
    l = TEMPERATURE_LAPSE_RATE
    g = GRAVITATIONAL_ACCELERATION

    r = r0 / m0
    t = t0 - l * h
    p = p0 * (1 - l * h / t0) ** (g / (r * l))
    rho = p / (r * t)
    return rho
```

### 2.2 Cálculo da Viscosidade do Ar

A viscosidade dinâmica do ar é calculada pela equação de Sutherland:

$$
\mu = \frac{C_1 T^{3/2}}{T + S}
$$

Onde:
- \( C_1 \) = constante de Sutherland
- \( S \) = constante de temperatura

A implementação é:

```python
def air_viscosity(temperature: float) -> float:
    t = temperature + 273.15
    c1 = SUTHERLAND_CONSTANT
    s = SUTHERLAND_TEMPERATURE_CONSTANT

    mu = c1 * t**1.5 / (t + s)
    return mu
```

### 2.3 Cálculo do Número de Reynolds

O número de Reynolds é definido como:

$$
Re = \frac{\rho v L}{\mu}
$$

Onde:
- \( \rho \) = densidade do ar (kg/m³)
- \( v \) = velocidade do ar sobre o aerofólio (m/s)
- \( L \) = comprimento característico (corda do aerofólio, em metros)
- \( \mu \) = viscosidade dinâmica do ar (Pa.s)

A implementação em Python:

```python
def reynolds_number(
    velocity: float, reference_length: float, altitude: float, temperature: float
) -> float:
    rho = air_density(altitude)
    mu = air_viscosity(temperature)

    re = (rho * velocity * reference_length) / mu
    return re
```

## 3. Conclusão

O módulo `functions` fornece funções essenciais para cálculos aerodinâmicos, facilitando a análise de escoamentos e condições atmosféricas para aplicações aeronáuticas.
