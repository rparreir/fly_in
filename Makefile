MAP = map_file.txt

run:
	python3 main.py $(MAP)

vis:
	SDL_AUDIODRIVER=dummy python3 main.py $(MAP) --vis

select_map:
	@bash -c 'select d in maps/*/; do select f in "$$d"*.txt; do python3 main.py "$$f"; break; done; break; done'

select_map_vis:
	@bash -c 'select d in maps/*/; do select f in "$$d"*.txt; do python3 main.py "$$f" --vis; break; done; break; done'

lint:
	flake8 .
	mypy .

clean:
	rm -rf __pycache__ .mypy_cache

.PHONY: run lint clean
