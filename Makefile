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

clear_logs:
	@echo "Clearing logs"
	@rm -rf logs
