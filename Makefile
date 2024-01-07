all:
	make setup
	make install

setup:
	curl https://pyenv.run | bash | true
	pyenv virtualenv david | true
	pyenv local david
	echo "Virtual environment $$(cat .python-version) created"

install:
	pip install --upgrade pip
	pip install -r requirements.txt

clear_logs:
	@rm -rf logs
