# Cálculo do Número de Reynolds

## Introdução

O número de Reynolds (Re) é um parâmetro adimensional que indica o regime de escoamento de um fluido sobre um corpo. No contexto da aerodinâmica, é um fator crucial para determinar a separação de camada limite e o comportamento do fluxo sobre um aerofólio.

A equação geral para o número de Reynolds é:

$$
Re = \frac{\rho v L}{\mu}
$$

Onde:

- \(\rho\) = densidade do ar (kg/m³),
- \(v\) = velocidade do ar sobre o aerofólio (m/s),
- \(L\) = comprimento característico (corda do aerofólio, em metros),
- \(\mu\) = viscosidade dinâmica do ar (Pa.s ou kg/(m·s)).

## Cálculo da Densidade do Ar

A densidade do ar varia conforme a altitude e pode ser estimada pela equação da Atmosfera Padrão Internacional (ISA):

$$
\rho = \frac{P}{R T}
$$

Onde:

- \(P\) = pressão atmosférica (Pa),
- \(R\) = constante do gás para o ar seco (287.05 J/(kg·K)),
- \(T\) = temperatura do ar (K).

A pressão atmosférica é calculada por:

$$
P = P_0 \left(1 - \frac{L h}{T_0}\right)^{\frac{g}{RL}}
$$

Onde:

- \(P_0 = 101325\) Pa (pressão ao nível do mar),
- \(L = 0.0065\) K/m (gradiente térmico),
- \(h\) = altitude (m),
- \(T_0 = 288.15\) K (temperatura ao nível do mar),
- \(g = 9.80665\) m/s² (aceleração gravitacional).

## Cálculo da Viscosidade do Ar

A viscosidade dinâmica do ar é calculada pela fórmula de Sutherland:

$$
\mu = \frac{C_1 T^{3/2}}{T + S}
$$

Onde:

- \(C_1 = 1.458 \times 10^{-6}\) kg/(m·s·K^0.5) (constante de Sutherland),
- \(S = 110.4\) K (constante de temperatura).
