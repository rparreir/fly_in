MAP = map_file.txt

run:
	python3 main.py $(MAP)

easy:
	@bash -c 'select f in maps/easy/*.txt; do python3 main.py "$$f"; break; done'

lint:
	flake8 .
	mypy .

clean:
	rm -rf __pycache__ .mypy_cache

.PHONY: run lint clean
