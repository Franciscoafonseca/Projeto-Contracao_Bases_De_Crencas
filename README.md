# Projeto de Revisão de Crenças

## Descrição
Este projeto implementa um sistema de revisão de crenças em Python baseado em lógica proposicional. Permite representar fórmulas, avaliar consequência lógica, testar tautologias e aplicar operadores de contração de crenças.

Inclui também interface gráfica, testes e uma versão executável.

## Estrutura do projeto
- logica/__init__.py - facilita imports dos módulos
- logica/belief_base.py - estrutura da base de crenças
- logica/contraction.py - operadores de contração (partial meet e kernel)
- logica/cp_logic.py - parser, fórmulas, tautologia e consequência lógica
- main.py - execução em modo texto
- main_gui.py - interface gráfica
- main_partial_meet_test.py - testes
- dist/ProjetoCrencas.exe - executável
- ProjetoCrencas.spec - configuração do PyInstaller

## Funcionalidades
- parsing de fórmulas proposicionais
- verificação de fórmulas válidas
- cálculo de consequência lógica
- teste de tautologias (truth-table e SAT)
- gestão de base de crenças
- operadores de contração:
  - partial meet contraction
  - kernel contraction

## Sintaxe das fórmulas
Exemplos:
- p
- neg p
- (p e q)
- (p ou q)
- (p imp q)
- (p eq q)

Operadores:
- neg - negação
- e - conjunção
- ou - disjunção
- imp - implicação
- eq - equivalência

## Tecnologias
- Python
- dataclasses
- typing
- itertools
- re
- PyInstaller

## Como executar

### Executar com Python
Na pasta do projeto:
python main.py

Interface gráfica:
python main_gui.py

Testes:
python main_partial_meet_test.py

### Executar versão compilada
Ir à pasta dist e executar:
ProjetoCrencas.exe

## Dependências
O projeto usa essencialmente bibliotecas standard do Python.

Se necessário:
pip install -r requirements.txt

## Funcionamento

### Base de crenças
Armazena fórmulas como strings:
- p
- p imp q
- neg q

Permite:
- adicionar fórmulas
- remover fórmulas
- listar conteúdo

### Consequência lógica
Verifica se premissas implicam uma conclusão.

Exemplo:
premissas: p imp q, p  
conclusão: q  

### Tautologia
Verifica se uma fórmula é sempre verdadeira.

Exemplo:
(p imp q) eq (neg q imp neg p)

### Contração de crenças
Remove fórmulas da base para deixar de implicar uma dada fórmula.

Métodos:
- partial meet contraction
- kernel contraction

## Exemplo
Base:
- p
- p imp q
- q imp r

Contração por r:
- sistema remove subconjuntos mínimos
- devolve nova base que não implica r

## Objetivo
Aplicar conceitos de:
- lógica proposicional
- representação de conhecimento
- revisão de crenças
- algoritmos de decisão

## Conclusão
O projeto demonstra a implementação prática de revisão de crenças, permitindo manipular fórmulas, verificar implicações e aplicar operadores clássicos sobre bases de conhecimento.****
