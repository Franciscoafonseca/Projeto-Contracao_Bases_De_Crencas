# Projeto de Contração de Bases de Crenças

## Descrição

Este projeto implementa um sistema de contração de bases de crenças em Python, baseado em lógica proposicional e em conceitos de revisão de crenças.

A aplicação permite representar fórmulas proposicionais, gerir bases de crenças e aplicar operadores clássicos de contração, nomeadamente:

- Partial Meet Contraction
- Kernel Contraction

O projeto inclui uma interface gráfica moderna, funcionalidades de exploração de possibilidades, registo da execução e exportação de relatórios em PDF.

Também é disponibilizada uma versão executável para Windows, permitindo testar a aplicação sem instalar Python.

---

## Estrutura do projeto

```text
Projeto-Contracao_Bases_De_Crencas/
│
├── export/                  # Exportação de relatórios em PDF
├── gui/                     # Interface gráfica da aplicação
├── logica/                  # Implementação da lógica proposicional e operadores
├── storage/                 # Apoio ao armazenamento/gestão de dados
│
├── dist/
│   └── ProjetoCrencas.exe   # Executável final da aplicação
│
├── favicon.ico              # Ícone da aplicação
├── main_gui.py              # Ponto de entrada da interface gráfica
├── ProjetoCrencas.spec      # Configuração do PyInstaller
├── README.md                # Documentação do projeto
└── .gitignore               # Ficheiros e pastas ignorados pelo Git
```

---

## Funcionalidades

- Interface gráfica para utilização dos operadores de contração.
- Gestão de bases de crenças.
- Adição, remoção e limpeza de fórmulas.
- Parsing de fórmulas proposicionais.
- Verificação de consequência lógica.
- Teste de tautologias.
- Cálculo de remainders para Partial Meet.
- Cálculo de kernels para Kernel Contraction.
- Exploração de diferentes possibilidades de contração.
- Registo detalhado da execução.
- Exportação de relatórios em PDF.
- Versão executável para Windows.

---

## Sintaxe das fórmulas

A aplicação trabalha com fórmulas proposicionais escritas em texto.

Exemplos:

```text
p
neg p
(p e q)
(p ou q)
(p imp q)
(p eq q)
```

Operadores disponíveis:

| Operador | Significado  |
| -------- | ------------ |
| `neg`    | negação      |
| `e`      | conjunção    |
| `ou`     | disjunção    |
| `imp`    | implicação   |
| `eq`     | equivalência |

---

## Como executar

### Opção 1 — Executar a versão compilada

A forma mais simples de testar o projeto é executar o ficheiro:

```text
dist/ProjetoCrencas.exe
```

No Windows, basta abrir a pasta `dist` e clicar duas vezes em:

```text
ProjetoCrencas.exe
```

---

### Opção 2 — Executar com Python

Na pasta principal do projeto, executar:

```bash
python main_gui.py
```

ou:

```bash
py main_gui.py
```

---

## Dependências

Para executar a versão em Python, podem ser necessárias as seguintes bibliotecas:

```bash
pip install customtkinter reportlab pillow
```

Para gerar novamente o executável:

```bash
pip install pyinstaller
```

---

## Gerar o executável

O executável foi gerado com PyInstaller em modo `onefile`, para que o projeto tenha apenas um ficheiro final em `dist`.

Comando usado:

```bash
py -m PyInstaller --noconfirm --clean --onefile --windowed --name ProjetoCrencas --icon favicon.ico --collect-all customtkinter main_gui.py
```

O ficheiro final gerado é:

```text
dist/ProjetoCrencas.exe
```

As pastas e ficheiros temporários criados durante a compilação, como `build/`, `__pycache__/`, ficheiros `.toc`, `.pkg`, `.pyz` e outros ficheiros internos do PyInstaller, não fazem parte do projeto final e são ignorados pelo Git.

---

## Operadores implementados

### Partial Meet Contraction

A contração Partial Meet baseia-se na identificação dos subconjuntos máximos da base de crenças que deixam de implicar a fórmula a contrair. A partir desses subconjuntos, é aplicada uma função de seleção para obter a nova base.

### Kernel Contraction

A contração Kernel identifica subconjuntos mínimos da base que implicam a fórmula a contrair. Em seguida, uma função de incisão escolhe fórmulas a remover, garantindo que a base resultante deixa de implicar essa fórmula.

---

## Exemplo de utilização

Base de crenças:

```text
p
p imp q
q imp r
```

Fórmula a contrair:

```text
r
```

O sistema analisa a base, identifica os subconjuntos relevantes e devolve uma nova base que deixa de implicar `r`, de acordo com o operador escolhido.

---

## Tecnologias utilizadas

- Python
- CustomTkinter
- ReportLab
- Pillow
- PyInstaller
- Lógica proposicional
- Algoritmos de contração de crenças

---

## Objetivo

O objetivo do projeto é aplicar, de forma prática e visual, conceitos de:

- lógica proposicional;
- representação de conhecimento;
- revisão e contração de crenças;
- bases de crenças;
- algoritmos de decisão;
- operadores Partial Meet e Kernel.

---

## Conclusão

Este projeto demonstra a implementação prática de operadores de contração de bases de crenças, permitindo manipular fórmulas proposicionais, verificar consequências lógicas e aplicar métodos clássicos da área de revisão de crenças através de uma interface gráfica simples e funcional.
