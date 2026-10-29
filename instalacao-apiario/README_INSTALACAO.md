# Instalação do Apiário Rocha no Windows

## Requisitos

- Windows 10 ou 11.
- Python 3.11 instalado e disponível pelo comando `py -3.11` ou `python`.
- Conexão com a internet na primeira instalação para baixar as dependências.

## Instalar e iniciar

1. Extraia a pasta `instalacao-apiario` para um local gravável, como Documentos.
2. Execute `instalar.bat` para preparar o sistema ou `iniciar.bat` para preparar e abrir.
3. Na primeira execução, aguarde a criação do ambiente Python e a instalação dos pacotes.
4. O navegador abrirá em `http://127.0.0.1:8001`.
5. Para encerrar, feche a janela do terminal ou pressione `Ctrl+C`.

O instalador cria uma chave JWT aleatória no arquivo local
`apiario-rocha-backend\.env`. Esse arquivo e o banco de dados são gerados no
computador de destino e não acompanham o pacote. O sistema cria seu banco em
`data\apiario.db` ao iniciar.

## Acesso inicial

O projeto disponibiliza as credenciais de demonstração `admin` / `apiario123`.
Altere as credenciais antes de usar o sistema com dados reais.

## Observações

- A pasta `.venv` e os pacotes instalados ficam dentro de `instalacao-apiario`.
- Mantenha a pasta no mesmo local depois da instalação; ambientes virtuais do
  Windows não devem ser movidos depois de criados.
- Cada instalação mantém seu próprio banco SQLite. Para compartilhar dados entre
  computadores, é necessário configurar um banco centralizado.
- Não copie seu arquivo `.env` ou banco de dados pessoal para distribuir o
  pacote.
