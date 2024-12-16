set shell := ["bash", "-uc"]

init-venv:
	rm -rf .venv 2> /dev/null
	rm -rf requirements.txt 2> /dev/null
	python3 -m venv .venv
	.venv/bin/pip install -q pip-tools

compile-deps:
	.venv/bin/pip-compile -q --resolver=backtracking --strip-extras requirements.in

install-deps:
	.venv/bin/pip-sync -q requirements.txt

compile-and-install-deps: compile-deps install-deps

run:
    .venv/bin/python3 main.py
