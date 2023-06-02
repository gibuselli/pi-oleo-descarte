# Óleo Descarte

## Projeto Integrador para o 4º semestre da UNIVESP

### Sobre o projeto
O projeto **Óleo Descarte** é uma aplicação web que visa auxiliar na doação e coleta de óleo usado entre membros de uma cidade, bairro, comunidade, etc, que desejam contribuir com a reciclagem e evitar a poluição causada pelo óleo que é descartado incorretamente. Por meio de uma interface simples, os usuários podem se registrar e anunciar o óleo armazenado para pessoas interessadas coletarem e reutilizarem.

### Como foi feito?
A versão atual do **Óleo Descarte** foi desenvolvida com as seguintes tecnologias:
* **HTML e CSS**: para a criação dos templates estáticos que compõem toda a aplicação.
* **Javascript**: para a interação de elementos como modais e popups.
* **Python/Fastapi**: linguagem e framework web para lidar com validações, interação com servidor e gerenciamento de rotas.
* **Jinja**: Mecanismo de templates web para Python.
* **SQLite**: base de dados relacional embutida na aplicação.

### Como utilizar?
Atualmente, a aplicação roda apenas localmente, mas logo será hospedada em domínio para uso geral.
* Clone o repositório
* Crie um ambiente virtual (.venv) e instale as dependências no arquivo *requirements.txt*
* Crie um arquivo *.env* e crie as seguintes variáveis de ambiente
* Abra um terminal no nível do módulo *app*
* Rode o comando `uvicorn main:app --reload --port <porta>` ou `uvicorn main:app --reload` para rodar na porta padrão 8000
* Acesse localhost:8000 (ou a porta que você escolheu)

### Futuras melhorias:
* Migraçao da base de dados para PostgreSQL.
* Hospedagem em domínio para uso em produção.
* Eventuais refatorações para melhores práticas com a stack utilizada.

### Desenvolvedores:
* @gibuselli
* @ncbnayara
* @Mari-sant
* @bobpetrillo
* @Edsogarc
* @vctmor
