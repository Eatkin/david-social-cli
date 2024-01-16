all:
	make pyenv
	make install

pyenv:
	@echo "Setting up pyenv virtual environment"
	@echo "If you have not installed pyenv, please install it first: https://github.com/pyenv/pyenv"
	pyenv virtualenv david
	pyenv local david
	@echo "Virtual environment $$(cat .python-version) created"

install:
	@echo "Installing dependencies"
	pip install --upgrade pip
	pip install -r requirements.txt

build_exe:
	@echo "Building executable with pyinstaller"
	pyinstaller david.py

clear_logs:
	@echo "Clearing logs"
	@rm -rf logs

clear_pycache:
	@echo "Clearing pycache"
	@rm -rf scripts/__pycache__

clear_all:
	@echo "Clearing all"
	@make clear_logs
	@make clear_pycache
	@make clear_executables

clear_executables:
	@echo "Clearing executables"
	@rm -rf base_library
	@rm -rf *.spec
	@rm -rf build
	@rm -rf dist
