# Instalação local no Windows

## Opção recomendada para uso individual

1. Copie a pasta inteira do projeto para o computador que vai usar o sistema.
2. Mantenha a pasta junto com a venv local `apiario-rocha-backend-py311`.
3. Clique duas vezes em `start_apiario_rocha.bat`.
4. O navegador abrirá em `http://localhost:8001`.
5. Faça login com as credenciais padrão:
   - Usuário: `admin`
   - Senha: `apiario123`

## Arquivos importantes

- `start_apiario_rocha.bat`: inicia o backend e abre a tela no navegador.
- `src/main.py`: aplicação FastAPI.
- `docs/data/apiario.db`: banco SQLite local do sistema.

## Observação sobre vários computadores

Este projeto usa SQLite local. Isso significa que cada máquina mantém seu próprio banco de dados e dados independentes.

Se você quiser que vários computadores compartilhem o mesmo banco, será necessário migrar para um banco centralizado, como PostgreSQL/MySQL com servidor compartilhado.

## Criar atalho na área de trabalho

1. Clique com o botão direito em `start_apiario_rocha.bat`.
2. Selecione "Enviar para" > "Área de trabalho (criar atalho)".
3. Use esse atalho para abrir o sistema no futuro.

## Encerrar o sistema

Feche a janela do terminal que abriu com o servidor, ou pressione `Ctrl + C` dentro do terminal.
