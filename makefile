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

run_daily:
	PYTHONPATH=. python main.py daily_report

run_dr:
	PYTHONPATH=. python util/dividend_rate/__init__.py