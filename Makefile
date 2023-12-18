all:
	make setup
	make install
	make env

setup:
	curl https://pyenv.run | bash | true
	pyenv virtualenv 3.11.0 david | true
	pyenv local david
	echo "Virtual environment $$(cat .python-version) created"

install:
	pip install --upgrade pip
	pip install -r requirements.txt

env:
	@touch .envrc
	@if [ ! -s .envrc ]; then \
				echo 'export DAVID_GET_PROFILE=""' >> .envrc; \
				echo 'export DAVID_GET_CHECK_ALREADY_LIKED=""' >> .envrc; \
				echo 'export DAVID_GET_CAT_PETS=""' >> .envrc; \
				echo 'export DAVID_GET_USER_POSTS=""' >> .envrc; \
				echo 'export DAVID_GET_REPLIES=""' >> .envrc; \
				echo 'export DAVID_GET_POST_DATA=""' >> .envrc; \
				echo 'export DAVID_GET_USER_LIST=""' >> .envrc; \
				echo 'export DAVID_GET_BOOTLICKER_FEED=""' >> .envrc; \
				echo 'export DAVID_GET_GLOBAL_FEED=""' >> .envrc; \
				echo 'export DAVID_GET_BOOTLICKERS=""' >> .envrc; \
				echo 'export DAVID_GET_FOLLOWERS=""' >> .envrc; \
				echo 'export DAVID_GET_LIKES=""' >> .envrc; \
				echo 'export DAVID_GET_AVI_URL=""' >> .envrc; \
        direnv allow; \
        echo "Created and configured .envrc"; \
				echo "Please fill in the environment variables"; \
    fi
	direnv allow
