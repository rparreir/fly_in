MAP = map_file.txt
MAIN = main.py
VISUALIZER = --vis

install:
	pip install pygame
	pip install flake8
	pip install mypy

run:
	python3 $(MAIN) $(MAP)

debug:
	python3 -m pdb $(MAIN) $(MAP)

vis:
	SDL_AUDIODRIVER=dummy python3 $(MAIN) $(MAP) $(VISUALIZER)

select_map:
	@bash -c 'select d in maps/*/; do select f in "$$d"*.txt; do python3 $(MAIN) "$$f"; break; done; break; done'

select_map_vis:
	@bash -c 'select d in maps/*/; do select f in "$$d"*.txt; do python3 $(MAIN) "$$f" $(VISUALIZER); break; done; break; done'

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 . 
	mypy . --strict

clean:
	rm -rf __pycache__ .mypy_cache

.PHONY: install run debug vis select_map select_map_vis lint lint-strict clean
