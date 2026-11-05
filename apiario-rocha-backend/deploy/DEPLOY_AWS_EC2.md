# Deploy na AWS (EC2 Ubuntu + Nginx + FastAPI)

Este guia usa os arquivos de modelo em `deploy/` para publicar o Apiario Rocha.

## 1) Preparar a EC2

- AMI: Ubuntu 22.04 LTS
- Tipo inicial: t3.micro
- Security Group:
  - TCP 22: apenas seu IP
  - TCP 80: 0.0.0.0/0
  - TCP 443: 0.0.0.0/0
- Associar Elastic IP

## 2) Conectar por SSH

No Windows PowerShell:

```powershell
ssh -i C:\caminho\sua-chave.pem ubuntu@SEU_IP_PUBLICO
```

## 3) Instalar pacotes no servidor

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip nginx git
```

## 4) Publicar o código

Opcao A (Git):

```bash
cd /home/ubuntu
git clone URL_DO_REPOSITORIO apiario-rocha-backend
cd apiario-rocha-backend
```

Opcao B (copiar pasta local com scp, via PowerShell no seu PC):

```powershell
scp -i C:\caminho\sua-chave.pem -r "C:\Users\edson33091906\Documents\Apiario Rocha\docs\apiario-rocha-backend" ubuntu@SEU_IP_PUBLICO:/home/ubuntu/apiario-rocha-backend
```

## 5) Criar ambiente Python e instalar dependencias

```bash
cd /home/ubuntu/apiario-rocha-backend
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 6) Configurar variaveis de ambiente

Crie o `.env` com base no exemplo:

```bash
cp .env.example .env
nano .env
```

Minimo obrigatorio no `.env`:

- `SECRET_KEY` com pelo menos 32 caracteres
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`

Observacao de CORS para acesso externo (frontend no mesmo host):

Adicione o dominio/IP publico em `CORS_ORIGINS` no `.env`, por exemplo:

```env
CORS_ORIGINS=["http://SEU_IP_PUBLICO","https://SEU_DOMINIO"]
```

## 7) Teste manual da API

```bash
cd /home/ubuntu/apiario-rocha-backend
source .venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Valide em outro terminal:

```bash
curl http://127.0.0.1:8000/health
```

Se retornar `{"status":"ok"}`, pare com `Ctrl + C`.

## 8) Configurar service systemd

Copie o modelo para o systemd:

```bash
sudo cp deploy/apiario.service /etc/systemd/system/apiario.service
```

Se a pasta final no servidor nao for `/home/ubuntu/apiario-rocha-backend`, ajuste em `/etc/systemd/system/apiario.service` os campos:

- `WorkingDirectory`
- `Environment`
- `EnvironmentFile`
- `ExecStart`

Ativar e iniciar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable apiario
sudo systemctl start apiario
sudo systemctl status apiario --no-pager
```

Logs em tempo real:

```bash
sudo journalctl -u apiario -f
```

## 9) Configurar Nginx

```bash
sudo cp deploy/nginx-apiario.conf /etc/nginx/sites-available/apiario
sudo ln -sf /etc/nginx/sites-available/apiario /etc/nginx/sites-enabled/apiario
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

Teste:

```bash
curl http://127.0.0.1/health
```

## 10) Habilitar HTTPS (se tiver dominio)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
```

Renovacao automatica:

```bash
sudo systemctl status certbot.timer --no-pager
```

## 11) Deploy de atualizacao

Sempre que atualizar codigo:

```bash
cd /home/ubuntu/apiario-rocha-backend
git pull
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart apiario
sudo systemctl status apiario --no-pager
```

## 12) Banco SQLite em producao

Atualmente a aplicacao usa SQLite local (`../data/apiario.db` por padrao).

- Funciona para baixa concorrencia
- Para maior escala/confiabilidade, migrar para PostgreSQL (ex.: Amazon RDS)

Backup rapido:

```bash
cp /home/ubuntu/data/apiario.db /home/ubuntu/data/apiario_$(date +%F).db
```

## 13) Checklist final

- `http://SEU_IP_PUBLICO/health` retorna `ok`
- Login funciona com `ADMIN_USERNAME` e `ADMIN_PASSWORD`
- `sudo systemctl status apiario` sem erros
- `sudo nginx -t` sem erros
- Security Group sem porta 8000 aberta publicamente
