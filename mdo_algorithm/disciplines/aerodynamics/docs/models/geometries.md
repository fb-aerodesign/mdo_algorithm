# Modelos Geométricos Aerodinâmicos

Este documento descreve o funcionamento do módulo `geometries`, que contém classes para modelagem geométrica de aerofólios e asas.

## 1. Introdução

O módulo `geometries` fornece classes para representar aerofólios, seções de asas e asas completas. Ele também inclui métodos para calcular parâmetros geométricos essenciais no projeto aeronáutico, como envergadura, área da planta e corda aerodinâmica média.

## 2. Representação de Aerofólios

A classe `Airfoil` é uma estrutura simples que armazena o nome do aerofólio. Essa informação é utilizada para acessar arquivos contendo perfis aerodinâmicos.

```python
@dataclass
class Airfoil:
    name: str

    def relative_path(self):
        return os.path.join(AIRFOILS_PATH, self.name + ".dat")
```

## 3. Seção da Asa

A classe `WingSection` representa uma seção da asa, contendo:

- `location`: Posição tridimensional da seção (ponto de bordo de ataque)
- `chord`: Corda aerodinâmica local
- `incremental_angle`: Ângulo de torção da seção
- `airfoil`: Instância da classe `Airfoil`

```python
@dataclass
class WingSection:
    location: Xyz
    chord: float
    incremental_angle: float
    airfoil: Airfoil
```

## 4. Cálculos Geométricos da Asa

A classe `Wing` representa a asa completa e inclui métodos para calcular diversos parâmetros geométricos.

### 4.1 Envergadura

A envergadura é o dobro da posição mais distante da seção da asa em relação ao centro:

```python
def span(self) -> float:
    return 2 * max(s.location.y for s in self.section_array)
```

### 4.2 Área da Planta da Asa

A área da planta da asa é obtida através da integração numérica:

```python
def planform_area(self) -> float:
    sections = sorted(self.section_array, key=lambda x: x.location.y)
    return 2 * float(
        np.trapezoid(
            np.array([s.chord for s in sections]), np.array([s.location.y for s in sections])
        )
    )
```

### 4.3 Corda Aerodinâmica Média (MAC)

A corda aerodinâmica média é obtida por integração numérica:

$$
MAC = \frac{2}{S} \int_0^{b/2} C(y)^2 dy
$$

A implementação em Python é:

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

## 5. Conclusão

O módulo `geometries` fornece ferramentas essenciais para modelagem geométrica de asas e aerofólios. Ele permite cálculos precisos que auxiliam no projeto e análise aerodinâmica de aeronaves.

