# Roteiro de apresentação — Apiário Rocha 4.0

Este roteiro foi preparado para uma apresentação de aproximadamente **5 a 7 minutos**. Os trechos entre colchetes são instruções para quem apresenta, não precisam ser lidos em voz alta.

## Antes de apresentar

- Inicie a aplicação e confirme que o painel abre em `http://127.0.0.1:8000/`.
- Tenha à mão as credenciais locais definidas no `.env`. **Não mostre nem leia essas credenciais, a chave JWT ou o conteúdo do arquivo `.env`.**
- A interface ainda usa o nome de demonstração **“Empresa Exemplo”**. Se for adequado, atualize o nome no módulo **Empresa** antes da apresentação.
- Use registros fictícios ou previamente preparados. Não exiba dados pessoais ou credenciais reais.
- As telas de colmeias, lotes, telemetria, rastreabilidade e finanças não oferecem todas as operações administrativas completas pelo painel; explique isso se navegar por elas.

## Fala sugerida

### 1. Abertura e objetivo

> Olá. Vou apresentar o Apiário Rocha 4.0, uma aplicação web criada para centralizar informações importantes da gestão de um apiário.
>
> A proposta é reunir em um único sistema os cadastros, o catálogo de produtos, o estoque, as vendas e informações ligadas à produção. A aplicação também conta com recursos de colmeias, telemetria e rastreabilidade de lotes. Assim, o objetivo é facilitar a consulta e a organização das informações da operação.

### 2. Demonstração do painel e das funcionalidades

[Mostre a tela inicial e a navegação. Faça login com as credenciais configuradas localmente, sem as exibir.]

> Este é o painel administrativo. O acesso é protegido e, depois da autenticação, a navegação reúne os principais módulos do sistema.
>
> Há módulos para usuários e administradores, funcionários, clientes e fornecedores. Também é possível trabalhar com vendas, produtos e estoque. O catálogo de produtos e o estoque são separados: o catálogo descreve o item comercial, enquanto o estoque acompanha quantidades disponíveis e níveis mínimos.
>
> Nas áreas de cadastro que têm operações implementadas na interface, podemos incluir, consultar, editar e remover registros. Algumas telas também permitem pesquisar, paginar os resultados e exportar dados para CSV.

[Se houver dados de demonstração adequados, mostre um cadastro simples em Produtos ou Clientes. Evite criar ou remover registros importantes durante a apresentação.]

> O módulo de vendas registra as operações comerciais e aplica a regra financeira prevista pelo sistema: 70% para renda e 30% para o fundo de modernização. Quando uma venda inclui produto e quantidade, o sistema também pode aplicar a regra de baixa de estoque implementada.
>
> Para produção, existem recursos de API para colmeias, leituras de telemetria e lotes. A consulta pública de rastreabilidade permite consultar um lote auditado. Algumas dessas áreas ainda aparecem no painel como telas informativas, então nem toda operação disponível na API tem um formulário completo na interface.

### 3. Tecnologias e arquitetura

> Em relação às tecnologias, a interface é feita com HTML, CSS e JavaScript, sem depender de um framework de interface como React. Ela é servida pelo próprio backend.
>
> O backend é escrito em Python e usa FastAPI para disponibilizar uma API REST. O Pydantic valida os dados recebidos, e o SQLite armazena as informações em um arquivo local. O acesso ao SQLite é feito de forma assíncrona com a biblioteca aiosqlite.
>
> Em resumo, o navegador apresenta as telas e envia requisições HTTP; a API valida e processa essas requisições; e o banco SQLite persiste os dados. A documentação interativa da API pode ser consultada em `/docs`.

### 4. Segurança

> A segurança foi considerada em diferentes partes do sistema. O painel usa credenciais administrativas configuradas no ambiente do servidor, e não uma senha padrão embutida no código. Após o login, a API emite um token JWT com prazo de validade, que é enviado nas chamadas protegidas.
>
> As senhas armazenadas nos cadastros de usuários e administradores são protegidas com hash scrypt e salt aleatório. A API omite o campo de senha nas respostas de listagem e atualização, e senhas antigas em texto simples são migradas para hash na inicialização.
>
> Os segredos, como a chave usada para assinar tokens e a senha administrativa, ficam em configuração local e não devem ser publicados ou enviados ao repositório. Em uma implantação acessível pela rede, também é importante usar HTTPS e proteger o arquivo do banco e os backups.
>
> É importante dizer que segurança não é algo que se possa resumir a “o sistema é totalmente seguro”. Há melhorias ainda necessárias: o token fica no armazenamento local do navegador; não existem permissões por perfil, revogação de tokens ou limitação de tentativas; e as rotas de telemetria são públicas na versão atual. Por isso, antes de usar em produção, essas rotas devem ser protegidas e a implantação deve ser revisada.

### 5. Encerramento

> Como resultado, o Apiário Rocha 4.0 oferece uma base integrada para organizar cadastros e atividades do apiário, com uma interface web, uma API documentada e armazenamento local em SQLite.
>
> Os próximos passos podem incluir completar os fluxos visuais de produção, definir permissões diferentes para cada perfil, reforçar a proteção da telemetria e preparar a aplicação para implantação com HTTPS, backups e monitoramento.
>
> Obrigado. Agora posso demonstrar algum módulo ou responder às perguntas.

## Ordem rápida para a demonstração

1. Apresentar o painel e explicar o login.
2. Mostrar um módulo de cadastro com dados fictícios.
3. Explicar a diferença entre Produtos e Estoque.
4. Mostrar Vendas e resumir a regra financeira de 70/30.
5. Apontar Colmeias, Lotes, Telemetria e Rastreabilidade, esclarecendo quais telas são informativas.
6. Explicar a arquitetura e as linguagens.
7. Encerrar com os controles de segurança e as melhorias pendentes.

## Respostas curtas para perguntas comuns

**O sistema está pronto para acesso público na internet?**

> Ainda precisa de preparação para produção. É necessário proteger as rotas públicas de telemetria, usar HTTPS, manter os segredos fora do repositório, restringir o acesso ao banco e aos backups e avaliar controles contra tentativas abusivas.

**O cadastro de usuários é o mesmo login do painel?**

> Não nesta versão. Os registros de usuários e administradores são cadastros do sistema; o login administrativo usa as credenciais configuradas no servidor.

**O sistema depende de um servidor de banco separado?**

> Não para a configuração atual. Ele usa SQLite, que armazena os dados em um arquivo. Para uma instalação maior, a escolha de banco deve considerar o volume e a forma de operação.

**Todas as funções da API já estão disponíveis em telas?**

> Não. Existem endpoints para mais áreas do que os fluxos visuais completos do painel. Em especial, algumas telas de produção e telemetria ainda são informativas.
