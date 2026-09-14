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
        dev-startapp dev-makemigrations dev-migrate dev-webhook-set dev-webhook-delete \
		dev-superuser dev-static dev-test-backend dev-test-frontend dev-test-all

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

dev-webhook-set:
	$(MANAGE_DEV) set_webhook

dev-webhook-delete:
	$(MANAGE_DEV) set_webhook --delete

dev-superuser:
	$(MANAGE_DEV) createsuperuser

dev-static:
	$(MANAGE_DEV) collectstatic --noinput

dev-test-backend:
	$(DC_DEV) exec backend pytest apps/core/tests/

dev-test-frontend:
	$(DC_DEV) exec frontend npm run test -- --run

dev-test-all: dev-test-backend dev-test-frontend

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

prod-webhook-set:
	$(MANAGE_PROD) set_webhook

prod-webhook-delete:
	$(MANAGE_PROD) set_webhook --delete

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

# ================= TG-SDK =================

SDK_URL = https://telegram.org/js/telegram-web-app.js
SDK_PATH = frontend/public/telegram-web-app.js
EMPTY_HASH = e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

check-tg-sdk:
	@REMOTE_HASH=$$(curl -sSf --connect-timeout 3 --max-time 7 $(SDK_URL) | shasum -a 256 | awk '{ print $$1 }'); \
	if [ -z "$$REMOTE_HASH" ] || [ "$$REMOTE_HASH" = "$(EMPTY_HASH)" ]; then \
		echo ">>> [ERROR] Connection to Telegram failed (Blocked or Timeout)."; \
		exit 1; \
	fi; \
	LOCAL_HASH=$$(shasum -a 256 -b $(SDK_PATH) 2>/dev/null | awk '{ print $$1 }'); \
	if [ "$$REMOTE_HASH" = "$$LOCAL_HASH" ]; then \
		echo ">>> [OK] Telegram SDK is up to date."; \
	else \
		echo ">>> [WARNING] Telegram SDK has changed on the server!"; \
		echo ">>> Remote: $$REMOTE_HASH"; \
		echo ">>> Local:  $$LOCAL_HASH"; \
		echo ">>> Run 'make update-tg-sdk' to sync."; \
		exit 1; \
	fi

update-tg-sdk:
	@mkdir -p frontend/public
	@curl -sSf --connect-timeout 5 --max-time 15 -o $(SDK_PATH) $(SDK_URL) || (echo ">>> [ERROR] Download failed."; exit 1)
	@echo ">>> [SUCCESS] Telegram SDK updated at $(SDK_PATH)"
