MAP = map_file.txt

run:
	python3 main.py $(MAP)

lint:
	flake8 .
	mypy .

clean:
	rm -rf __pycache__ .mypy_cache

.PHONY: run lint clean
