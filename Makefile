COMPOSE_PROJECT_NAME_DEV=aichat-dev
COMPOSE_PROJECT_NAME_PROD = aichat-prod

COMPOSE_FILE_DEV = docker/docker-compose.dev.yaml
COMPOSE_FILE_PROD = docker/docker-compose.prod.yaml
ENV_FILE = .env

DC_DEV=docker compose -f $(COMPOSE_FILE_DEV) -p $(COMPOSE_PROJECT_NAME_DEV) --env-file $(ENV_FILE)
DC_PROD = docker compose -f $(COMPOSE_FILE_PROD) -p $(COMPOSE_PROJECT_NAME_PROD) --env-file $(ENV_FILE)

MANAGE_DEV = $(DC_DEV) exec backend python manage.py
MANAGE_PROD = $(DC_PROD) exec backend python manage.py

.PHONY: dev-build dev-up dev-down dev-stop dev-restart dev-logs dev-shell \
        dev-startapp dev-makemigrations dev-migrate dev-superuser dev-static

# ================= DEV =================

dev-build:
	$(DC_DEV) build

dev-up:
	$(DC_DEV) up -d

dev-down:
	$(DC_DEV) down $(args)

dev-stop:
	$(DC_DEV) stop

dev-restart:
	$(DC_DEV) restart $(s)

dev-logs:
	$(DC_DEV) logs -f $(s)

dev-shell:
	$(DC_DEV) exec $(s) sh

dev-startapp:
	$(MANAGE_DEV) startapp $(args)

dev-makemigrations:
	$(MANAGE_DEV) makemigrations $(args)

dev-migrate:
	$(MANAGE_DEV) migrate

dev-webhook:
	$(MANAGE_DEV) set_webhook

dev-superuser:
	$(MANAGE_DEV) createsuperuser

dev-static:
	$(MANAGE_DEV) collectstatic --noinput

# ================= PROD =================

prod-up:
	$(DC_PROD) up -d --build

prod-down:
	$(DC_PROD) down

prod-build-front:
	@echo "Собираем frontend..."
	$(DC_PROD) --profile tools up --build frontend-builder
	@echo "Frontend успешно собран и помещен в volume!"

prod-migrate:
	$(MANAGE_PROD) migrate

prod-static:
	$(MANAGE_PROD) collectstatic --noinput

prod-superuser:
	$(MANAGE_PROD) createsuperuser

# ================= SSL =================

SSL_DIR = $(shell pwd)/ssl

prod-test-ssl:
	@echo "Тестируем получение сертификата для $(DOMAIN)..."
	-docker stop aichat-nginx
	docker run --rm --name certbot \
		-p 80:80 \
		-v $(SSL_DIR):/etc/letsencrypt \
		certbot/certbot certonly --standalone \
		-d $(DOMAIN) \
		--non-interactive --agree-tos --register-unsafely-without-email --dry-run
	@echo "Если ошибок нет (Success) — можно выполнять prod-get-ssl!"

prod-get-ssl:
	@echo "Получаем БОЕВОЙ сертификат для $(DOMAIN)..."
	-docker stop aichat-nginx
	docker run --rm --name certbot \
		-p 80:80 \
		-v $(SSL_DIR):/etc/letsencrypt \
		certbot/certbot certonly --standalone \
		-d $(DOMAIN) \
		--non-interactive --agree-tos --register-unsafely-without-email
	@echo "Сертификат получен и сохранен в папку ./ssl!"

prod-renew-ssl:
	@echo "Обновляем сертификат..."
	-docker stop aichat-nginx
	docker run --rm --name certbot \
		-p 80:80 \
		-v $(SSL_DIR):/etc/letsencrypt \
		certbot/certbot renew --standalone
	docker start aichat-nginx
	@echo "Готово!"
