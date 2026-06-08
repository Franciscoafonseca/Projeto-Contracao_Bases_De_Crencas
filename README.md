# Projeto de RevisÃ£o de CrenÃ§as

## DescriÃ§Ã£o
Este projeto implementa um sistema de revisÃ£o de crenÃ§as em Python baseado em lÃ³gica proposicional. Permite representar fÃ³rmulas, avaliar consequÃªncia lÃ³gica, testar tautologias e aplicar operadores de contraÃ§Ã£o de crenÃ§as.

Inclui tambÃ©m interface grÃ¡fica, testes e uma versÃ£o executÃ¡vel.

## Estrutura do projeto
- logica/__init__.py - facilita imports dos mÃ³dulos
- logica/belief_base.py - estrutura da base de crenÃ§as
- logica/contraction.py - operadores de contraÃ§Ã£o (partial meet e kernel)
- logica/cp_logic.py - parser, fÃ³rmulas, tautologia e consequÃªncia lÃ³gica
- main.py - execuÃ§Ã£o em modo texto
- main_gui.py - interface grÃ¡fica
- main_partial_meet_test.py - testes
- dist/ProjetoCrencas/ProjetoCrencas.exe - executÃ¡vel
- ProjetoCrencas.spec - configuraÃ§Ã£o do PyInstaller

## Funcionalidades
- parsing de fÃ³rmulas proposicionais
- verificaÃ§Ã£o de fÃ³rmulas vÃ¡lidas
- cÃ¡lculo de consequÃªncia lÃ³gica
- teste de tautologias (truth-table e SAT)
- gestÃ£o de base de crenÃ§as
- operadores de contraÃ§Ã£o:
  - partial meet contraction
  - kernel contraction

## Sintaxe das fÃ³rmulas
Exemplos:
- p
- neg p
- (p e q)
- (p ou q)
- (p imp q)
- (p eq q)

Operadores:
- neg - negaÃ§Ã£o
- e - conjunÃ§Ã£o
- ou - disjunÃ§Ã£o
- imp - implicaÃ§Ã£o
- eq - equivalÃªncia

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

Interface grÃ¡fica:
python main_gui.py

Testes:
python main_partial_meet_test.py

### Executar versÃ£o compilada
Ir Ã  pasta dist e executar:
ProjetoCrencas.exe

## DependÃªncias
O projeto usa essencialmente bibliotecas standard do Python.

Se necessÃ¡rio:
pip install -r requirements.txt

## Funcionamento

### Base de crenÃ§as
Armazena fÃ³rmulas como strings:
- p
- p imp q
- neg q

Permite:
- adicionar fÃ³rmulas
- remover fÃ³rmulas
- listar conteÃºdo

### ConsequÃªncia lÃ³gica
Verifica se premissas implicam uma conclusÃ£o.

Exemplo:
premissas: p imp q, p  
conclusÃ£o: q  

### Tautologia
Verifica se uma fÃ³rmula Ã© sempre verdadeira.

Exemplo:
(p imp q) eq (neg q imp neg p)

### ContraÃ§Ã£o de crenÃ§as
Remove fÃ³rmulas da base para deixar de implicar uma dada fÃ³rmula.

MÃ©todos:
- partial meet contraction
- kernel contraction

## Exemplo
Base:
- p
- p imp q
- q imp r

ContraÃ§Ã£o por r:
- sistema remove subconjuntos mÃ­nimos
- devolve nova base que nÃ£o implica r

## Objetivo
Aplicar conceitos de:
- lÃ³gica proposicional
- representaÃ§Ã£o de conhecimento
- revisÃ£o de crenÃ§as
- algoritmos de decisÃ£o

## ConclusÃ£o
O projeto demonstra a implementaÃ§Ã£o prÃ¡tica de revisÃ£o de crenÃ§as, permitindo manipular fÃ³rmulas, verificar implicaÃ§Ãµes e aplicar operadores clÃ¡ssicos sobre bases de conhecimento.****
