makemigrations:
	mkdir -p ~/.economy_dog
	PYTHONPATH=. alembic revision --autogenerate

migrate:
	mkdir -p ~/.economy_dog
	PYTHONPATH=. alembic upgrade head

clean:
	rm -rf ~/.economy_dog

run:
	PYTHONPATH=. python main.py annual_report