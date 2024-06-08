.PHONY: start
start:
	@printf "[exec] Python Django Start!!!\n"; \
	poetry run python manage.py runserver --settings=config.django.local

.PHONY: test
test:
	@printf "[exec] Python Django Test!!!\n"; \
	poetry run pytest --cov=mung_manager --cov-fail-under=80 tests/

.PHONY: mypy
mypy:
	@printf "[exec] Python Django MyPy!!!\n"; \
	poetry run mypy --config mypy.ini mung_manager/

.PHONY: migrate
migrate:
	@printf "[exec] Python Django Migrate!!!\n"; \
	poetry run python manage.py migrate --settings=config.django.local

.PHONY: makemigrations
makemigrations:
	@printf "[exec] Python Django MakeMigrations!!!\n"; \
	poetry run python manage.py makemigrations --settings=config.django.local

.PHONY: createsuperuser
createsuperuser:
	@printf "[exec] Python Django CreateSuperUser!!!\n"; \
	poetry run python manage.py createsuperuser --settings=config.django.local

.PHONY: shell
shell:
	@printf "[exec] Python Django Shell!!!\n"; \
	poetry run python manage.py shell --settings=config.django.local

.PHONY: collectstatic
collectstatic:
	@printf "[exec] Python Django CollectStatic!!!\n"; \
	poetry run python manage.py collectstatic --settings=config.django.local

.PHONY: createcachetable
createcachetable:
	@printf "[exec] Python Django CreateCacheTable!!!\n"; \
	poetry run python manage.py createcachetable --settings=config.django.local

.PHONY: startapp
startapp:
	@printf "[exec] Python Django StartApp!!!\n"; \
	@printf "[create] 앱 이름: "; \
	read app; \
	poetry run python manage.py startapp $$app --settings=config.django.local
