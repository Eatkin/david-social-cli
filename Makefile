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
	@rm -rf logs | true

clear_pycache:
	@echo "Clearing pycache"
	@rm -rf scripts/__pycache__ | true

clear_all:
	@echo "Clearing all"
	@make clear_logs
	@make clear_pycache
	@make clear_executables
	@make clear_credentials

clear_executables:
	@echo "Clearing executables"
	@rm -rf base_library | true
	@rm -rf *.spec | true
	@rm -rf build | true
	@rm -rf dist | true

clear_credentials:
	@echo "Clearing credentials"
	@rm .david.cred | true
	@rm .david.key | true
	@rm secrets.yaml | true
