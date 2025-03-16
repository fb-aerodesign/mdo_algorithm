# MDO Algorithm

Este projeto implementa um algoritmo de Otimização de Design Multidisciplinar (MDO) em Python.

## Descrição

O algoritmo MDO é utilizado para otimizar problemas complexos que envolvem múltiplas disciplinas. Ele é amplamente aplicado em engenharia, especialmente em design aeroespacial e automotivo.

## Documentação

A documentação geral do módulo `mdo_algorithm` pode ser encontrada em [mdo_algorithm/docs/mdo_algorithm.md](mdo_algorithm/docs/mdo_algorithm.md).

## Instalação de Bibliotecas

Para instalar as bibliotecas necessárias, execute o seguinte comando:

```bash
pip install -r requirements.txt
```

## Instalação de Softwares

Este projeto utiliza alguns softwares de análises. Como esses softwares não são de nossa autoria, eles não são distribuídos diretamente neste repositório.

### Como baixar os executáveis:

- XFOIL: Baixe diretamente do site oficial [https://web.mit.edu/drela/Public/web/xfoil/](https://web.mit.edu/drela/Public/web/xfoil/)
- AVL: Baixe diretamente do site oficial [https://web.mit.edu/drela/Public/web/avl/](https://web.mit.edu/drela/Public/web/avl/)
- QPROP: Baixe diretamente do site oficial [https://web.mit.edu/drela/Public/web/qprop/](https://web.mit.edu/drela/Public/web/qprop/)

### Como configurar:

O algoritmo espera que os arquivos executáveis (.exe) estejam localizados na pasta `mdo_algorithm/softwares/`

### Licenciamento:

Os softwares XFOIL, AVL e QPROP foram desenvolvidos pelo MIT e possuem seus próprios termos de uso. Certifique-se de ler as licenças oficiais antes de utilizá-los.
