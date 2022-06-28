[Especificação do projeto](https://github.com/PicPay/picpay-desafio-backend#materiais-%C3%BAteis)

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

## Proposta
### Comunicação com o banco
Numa versão onde não houvesse a restrição imposta pelo professor, toda a comunicação seria feita através de um ORM, puramente por questão de organização

### Arquitetura
As funcionalidades seriam basicamente as mesmas, mas implementadas de forma diferente de modo a tornar a solução mais robusta, o que solucionaria também os problemas do projeto atual

- No envio do SMS, haverá um número de retries com LoopBackOff. Caso o número máximo de retries for excedido, a mensagem será enviada para uma fila (atualmente penso em usar rabbitmq) onde haverá um processo responsável só por consumí-la e tentar enviar as mensagens novamente. Caso consiga, um acknowledge é enviado pra fila e a mensagem é removida dela, caso contrário, um nack (not acknowledged) é enviado e a mensagem continua na fila para tentativas posteriores.
- Na transferência existirá uma HashTable de mutex, onde cada usuário que tenta fazer uma transação deve passar pelo mutex do seu id, ou criá-lo e passar por ele. A própria criação do mutex é protegida por um outro mutex, global, que também é usado para de tempos em tempos limpar os mutexes não utilizados da tabela. Essa abordagem permite transferências simultâneas de usuários diferentes e protege o sistema de inconsistências, mas não escala para um cenário em que usemos múltiplos servidores, o que é um problema. Para uma versão que permita programação distribuída, uma ideia é utilizarmos filas efêmeras, onde as requisições de transações vão para uma fila de gerência que as encaminha para filas com id igual ao id do pagador, mas eu ainda não tenho como certeza de como deletar as filas que não estão em uso para não afogar os recursos.
- Ao deletar um usuário, ele e suas transferências são movidos para uma tabela de histórico, de modo que a qualquer momento a (tabela do sistema U histórico) = todos os registros já feitos no sistema
- Um sistema de autenticação/autorização para que só o usuário x possa mover recursos da conta do usuário x, além de proteger outras operações como deleção e consulta

# Considerações gerais
O programa atual é bem simples, com algumas falhas óbvias, como a condição de corrida entre transações do mesmo usuário, mas que foram ignoradas por não ser o foco da disciplina tratar esse tipo de questão. Em contra partida, o código fornecido teve um foco em desacoplamento e, apesar de algumas gambiarras, legibilidade para permitir que eu possa implementar as propostas de melhoria sem dores de cabeça no futuro, caso eu queira.