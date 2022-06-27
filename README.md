# setup
## Pré-requisitos

- Garanta que as portas 5432 e 8000 estão livres
- Docker instalado
- Docker compose instalado

## Executando
Simplesmente rode o comando `docker-compose up` na raiz do projeto. A API será inicializada e todas as rotas, junto com a documentação, poderão ser visualizadas [neste endereço](0.0.0.0:8000/docs)

# Estrutura
## Atual
### Comunicação com o banco
Atualmente o projeto é bem simples e cru. Para a criação inicial das tabelas foi utilizado um ORM, só pela capacidade
de modelarmos as tabelas no próprio código, o que deixa as coisas menos propícias a erro do que se mantivéssemos strings
para as queries de criação de tabela. Fora isso, nenhum ORM é utilizado pra nada e a conexão com o banco (postgresql) é feita com o [psycopg2](https://www.psycopg.org/docs/usage.html), tomando cuidado em todas as queries para que não exista vulnerabilidade de sql injection.

### Arquitetura
Podemos criar usuários, deletar usuários e pesquisar as informações de um usuário específico. Além disso, podemos fazer transações para fazer a transferência de saldo de um usuário para o outro. Algumas checagens são feitas antes de uma transação:

- Se o usuário que está enviando dinheiro não é um lojista
- Se o usuário está autorizado a fazer a transação (através da consulta de um serviço externo)
- Se o usuário tem saldo suficiente para a transação

Além disso, após a transação, é simulado o envio de um SMS para o usuário que recebeu a transferência.

### Problemas
- Não há retries no envio do SMS, se o serviço estiver fora do ar a notificação é simplesmente perdida
- Na transferência de dinheiro, apesar dela ser feita atômicamente entre o pagador e o recebedor, não há um controle de concorrência entre múltiplas transações feitas paralelamente pelo mesmo pagador, o que pode gerar um estado inconsistente.
- As transações dos usuários são salvas, mas caso um usuário seja deletada, elas também são, fazendo com que potencialmente percamos o histórico de recebimentos de um usuário ativo