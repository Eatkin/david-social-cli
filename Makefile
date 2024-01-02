all:
	make setup
	make install
	make env

setup:
	curl https://pyenv.run | bash | true
	# Python version 3.11 required for tomllib
	pyenv virtualenv 3.11.0 david | true
	pyenv local david
	echo "Virtual environment $$(cat .python-version) created"

install:
	pip install --upgrade pip
	pip install -r requirements.txt
