# Backend Genérico de Gestão

Backend em FastAPI para gestão operacional, telemetria IoT, rastreabilidade e finanças, pronto para ser configurado para qualquer empresa.

## Requisitos

- Python 3.11+
- MongoDB local ou remoto

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Execução

```bash
uvicorn src.main:app --reload
```

## Variáveis de ambiente

Copie `.env.example` para `.env` e ajuste os valores. Isso permite que a mesma base possa ser reutilizada por diferentes clientes, empresas ou marcas.

Exemplo:

```env
APP_NAME=Sistema XYZ
COMPANY_NAME=Empresa ABC
MONGO_DB=sistema_xyz_db
```
