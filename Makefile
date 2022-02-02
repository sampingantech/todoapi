all:
	uvicorn todoapi.main:app --reload

check:
	mypy --strict --html-report ./report .

test:
	pytest