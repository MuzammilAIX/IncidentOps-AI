# Deployment Guide

## Option 1: Railway (5 min, free)

1. Go to https://railway.app -> sign in with GitHub
2. New Project -> Deploy from GitHub repo -> select `IncidentOps-AI`
3. "+ New" -> Database -> Add PostgreSQL
4. "+ New" -> Database -> Add Redis
5. In web service -> Variables, add:
   - SECRET_KEY=<generate fresh: python -c "import secrets; print(secrets.token_urlsafe(50))">
   - DEBUG=False
   - ALLOWED_HOSTS=*.railway.app
   - SECURE_SSL_REDIRECT=True
   - DJANGO_SETTINGS_MODULE=config.settings.production
   - DB_NAME=${{Postgres.PGDATABASE}}
   - DB_USER=${{Postgres.PGUSER}}
   - DB_PASSWORD=${{Postgres.PGPASSWORD}}
   - DB_HOST=${{Postgres.PGHOST}}
   - DB_PORT=${{Postgres.PGPORT}}
   - REDIS_URL=${{Redis.REDIS_URL}}
   - USE_SIMULATOR=1
6. Click Deploy
7. URL: your-app.railway.app
8. Test: https://your-app.railway.app/health/ returns {"status":"healthy"}

## Option 2: Render (10 min, free)

Same steps at https://render.com.

## Option 3: VPS (30 min, $4/mo)

1. Hetzner CX11, Ubuntu 24.04
2. ssh root@your-server-ip
3. curl -fsSL https://get.docker.com | sh
4. git clone https://github.com/MuzammilAIX/IncidentOps-AI.git
5. cd IncidentOps-AI
6. cp .env.production.example .env
7. nano .env (fill in values)
8. docker compose -f docker-compose.prod.yml up -d

## Local Production Test

1. cp .env.production.example .env
2. python -c "import secrets; print(secrets.token_urlsafe(50))" (paste into .env)
3. Set ALLOWED_HOSTS=localhost,127.0.0.1 and SECURE_SSL_REDIRECT=False
4. docker compose -f docker-compose.prod.yml up --build
5. Open http://localhost/login/

## Troubleshooting

| Error | Fix |
|-------|-----|
| 502 Bad Gateway | docker compose logs web |
| DisallowedHost | Update ALLOWED_HOSTS |
| DB connection refused | Check DB_HOST=${{Postgres.PGHOST}} |
| Static files 404 | docker compose exec web python manage.py collectstatic |
