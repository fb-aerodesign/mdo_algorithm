# Módulo `avl`

Este documento descreve o funcionamento do módulo `avl`, que define as estruturas de dados necessárias para a configuração de modelos aerodinâmicos no software AVL (Athena Vortex Lattice). O AVL é uma ferramenta amplamente utilizada para análises aerodinâmicas de asas e superfícies sustentadoras utilizando o método de vórtices em rede (VLM - Vortex Lattice Method).

## 1. Introdução

O módulo `avl` fornece classes que representam os principais parâmetros de entrada do AVL, permitindo a geração automática de arquivos de entrada para o software. O objetivo é facilitar a definição de configurações aerodinâmicas e garantir compatibilidade com os requisitos do AVL.

## 2. Estrutura do Módulo

O módulo contém classes para modelar:
- Configurações de simetria (classe `Symmetry`)
- Definição de superfícies de controle (classe `Deflection`)
- Configurações gerais do arquivo de entrada (classe `Header`)
- Superfícies aerodinâmicas (classe `Surface`)
- Seções de superfícies (classe `Section`)
- Controles de superfícies (classe `Control`)
- Corpos não sustentadores (classe `Body`)

## 3. Descrição das Classes

### 3.1 Classe `Header`
A classe `Header` define os parâmetros gerais do arquivo de entrada do AVL, incluindo:
- **Mach Number:** Número de Mach do escoamento livre
- **Simetria:** Define simetria no eixo Y (`iYsym`) e no eixo Z (`iZsym`)
- **Referência Geométrica:** Área de referência (Sref), corda de referência (Cref) e envergadura de referência (Bref)
- **Centro de Referência:** Coordenadas X, Y e Z do ponto de referência para momentos aerodinâmicos
- **Coeficiente de Arrasto de Perfil:** (Opcional) Valor padrão do arrasto de perfil

### 3.2 Classe `Surface`
Representa uma superfície aerodinâmica sustentadora, como uma asa ou um estabilizador:
- **Nome da superfície**
- **Quantidade de vórtices no sentido da corda e espaçamento**
- **Quantidade de vórtices no sentido da envergadura e espaçamento**
- **Parâmetros opcionais:** Reflexão por simetria, deslocamentos e rotações, controle de esteira e contribuição na força total
- **Lista de seções da superfície**

### 3.3 Classe `Section`
Representa uma seção de uma superfície aerodinâmica:
- **Localização da borda de ataque**
- **Corda e ângulo de torção local**
- **Definição do aerofólio**
- **Configuração de vórtices na envergadura**
- **Superfícies de controle associadas**
- **Fatores de ajuste para coeficientes aerodinâmicos**

### 3.4 Classe `Control`
Define uma superfície de controle no AVL:
- **Nome do controle**
- **Ganho (relação entre deflexão e comando)**
- **Posição da dobradiça**
- **Eixo de rotação**
- **Direção da deflexão**

### 3.5 Classe `Body`
Modela corpos não sustentadores, como fuselagens:
- **Nome do corpo**
- **Distribuição de vértices ao longo do comprimento**
- **Opções de espelhamento e deslocamento**

## 4. Geração do Arquivo de Entrada para AVL
Cada classe possui um método `to_input_file()` que retorna a representação formatada do elemento no arquivo de entrada do AVL. O método `to_input_file()` da classe `Input` compila todos os elementos e gera o arquivo final.

## 5. Exemplo de Uso
Abaixo um exemplo de como utilizar o módulo para criar um arquivo de entrada para AVL:

```python
wing = Wing(
    section_array=[
        WingSection(
            location=Xyz(0, 0, 0), chord=0.6, incremental_angle=0, airfoil=Airfoil("s1223")
        ),
        WingSection(
            location=Xyz(0.15, 1.15, 0), chord=0.3, incremental_angle=0, airfoil=Airfoil("s1223")
        ),
    ]
)

avl_input = avl.Input(
    header=avl.Header(
        title="Plane",
        default_mach_number=0,
        y_symmetry=avl.Symmetry.IGNORE,
        z_symmetry=avl.Symmetry.IGNORE,
        xy_plane_location=0,
        reference_area=round(wing.planform_area(), 3),
        reference_chord=round(wing.mean_aerodynamic_chord(), 3),
        reference_span=wing.span(),
        default_location=Xyz(0, 0, 0),
        default_profile_drag_coefficient=None,
    ),
    surface_array=[
        avl.Surface(
            name="Wing",
            chordwise_vortice_count=12,
            chordwise_vortex_spacing=1,
            spanwise_vortice_count=20,
            spanwise_vortex_spacing=-1.5,
            mirror_surface=True,
            xz_plane_location=0,
            scale=None,
            translate=None,
            incremental_angle=None,
            ignore_wake=False,
            ignore_freestream_effect=False,
            ignore_load_contribution=False,
            profile_drag_settings=None,
            section_array=[
                avl.Section(
                    location=wing_section.location,
                    chord=wing_section.chord,
                    incremental_angle=wing_section.incremental_angle,
                    spanwise_vortice_count=None,
                    spanwise_vortex_spacing=None,
                    airfoil=wing_section.airfoil,
                    control_array=[],
                    cl_alpha_slope_scaling=None,
                    profile_drag_settings=None,
                )
                for wing_section in wing.section_array
            ],
        )
    ],
    body_array=[],
)

with open("aeronave.avl", "w") as file:
    file.write(avl_input.to_input_file())
```

## 6. Conclusão
O módulo `avl` permite uma definição estruturada de modelos aerodinâmicos para AVL, garantindo compatibilidade e facilitação na criação de configurações aerodinâmicas. Ele é útil para automatizar a geração de arquivos de entrada e facilitar simulações aerodinâmicas tridimensionais.

