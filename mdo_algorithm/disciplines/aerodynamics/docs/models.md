# Modelos Aerodinâmicos

Este documento descreve os cálculos presentes no módulo `models`, que contém classes para modelagem de aerofólios e asas.

## 1. Introdução

O módulo `models` fornece classes para representar aerofólios, seções de asa e asas completas, além de métodos para calcular parâmetros geométricos essenciais no projeto aeronáutico.

## 2. Representação de Aerofólios

A classe `Airfoil` é uma estrutura simples que armazena o nome do aerofólio. Essa informação é utilizada para acessar arquivos de perfis aerodinâmicos.

```python
@dataclass
class Airfoil:
    name: str
```

## 3. Seção da Asa

A classe `WingSection` representa uma seção da asa, contendo:

- `x, y, z`: Posição tridimensional da seção
- `chord`: Corda aerodinâmica
- `twist`: Ângulo de torção
- `airfoil`: Instância da classe `Airfoil`

Uma asa retangular ou trapezoidal pode ser representada por uma lista de duas seções, onde a primeira seção é a raiz e a última é a ponta.

```python
@dataclass
class WingSection:
    x: float
    y: float
    z: float
    chord: float
    twist: float
    airfoil: Airfoil
```

## 4. Cálculos Geométricos da Asa

A classe `Wing` representa a asa completa e inclui métodos para calcular diversos parâmetros.

### 4.1 Envergadura

A envergadura é o dobro da posição mais distante da seção da asa em relação ao centro:

```python
def span(self) -> float:
    return 2 * max(s.y for s in self.sections)
```

### 4.2 Área da Planta da Asa

A área da planta da asa é obtida somando a área de trapézios formados entre seções consecutivas:

```python
def planform_area(self) -> float:
    sections = sorted(self.sections, key=lambda x: x.y)
    sections = [(sections[i], sections[i + 1]) for i in range(len(sections) - 1)]
    return 2 * np.sum(
        [
            0.5 * (s1.chord + s2.chord) * np.sqrt((s2.y - s1.y) ** 2 + (s2.x - s1.x) ** 2)
            for s1, s2 in sections
        ]
    )
```

### 4.3 Corda Média Geométrica (MGC)

A corda média geométrica é obtida por integração numérica da seguinte equação:

$$
MGC = \frac{2}{S} \int_{y_{min}}^{y_{max}} C(y)^2 \sqrt{1 + \left(\frac{dx}{dy}\right)^2} dy
$$

A implementação é feita usando `scipy.integrate.quad`:

```python
def mean_geometric_chord(self) -> float:
    s = self.planform_area()

    def integrand(y):
        return self.chord_distribution(y) ** 2 * np.sqrt(1 + self.chord_slope(y) ** 2)

    y_min, y_max = min(s.y for s in self.sections), max(s.y for s in self.sections)
    result = 0
    if y_max != y_min:
        cmg_numerator, _ = quad(integrand, y_min, y_max)
        result = (2 / s) * cmg_numerator if s > 0 else 0
    return result
```

## 5. Exportação para AVL

O método `to_avl` gera um arquivo de entrada para o software AVL, que realiza análises aerodinâmicas em asas tridimensionais:

```python
def to_avl(self, plane_name="Plane", wing_name="Wing", mach=0, iysym=1, izsym=0, zsym=0, profile_drag_coefficient=0) -> str:
    if len(self.sections) < 2:
        raise RuntimeError("The wing must have at least 2 sections")
    sections = sorted(self.sections, key=lambda x: x.y)
    lines = [
        plane_name,
        str(round(mach, 5)),
        f"{iysym} {izsym} {zsym}",
        " ".join(
            [
                str(round(self.planform_area(), 3)),
                str(round(self.mean_geometric_chord(), 3)),
                str(round(self.span(), 3)),
            ]
        ),
        " ".join(
            [
                str(round(self.mean_geometric_chord() / 4, 3)),
                "0",
                "0",
            ]
        ),
        str(round(profile_drag_coefficient, 5)),
        "SURFACE",
        wing_name,
    ]
    for section in sections:
        airfoil_path = os.path.join(AIRFOILS_PATH, f"{section.airfoil.name}.dat")
        lines.extend(
            [
                "SECTION",
                " ".join([
                    str(section.x),
                    str(section.y),
                    str(section.z),
                    str(section.chord),
                    str(section.twist),
                ]),
                f"AFILE {airfoil_path}",
            ]
        )
    return "\n".join(lines)
```

## 6. Conclusão

O módulo `models` fornece ferramentas essenciais para modelagem geométrica de asas e aerofólios, possibilitando cálculos precisos para uso em simulações aerodinâmicas.
