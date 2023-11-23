#!/usr/bin/env bash


# locations
llm_engine_dir="../LLMEngine/"
chat_client_dir="../ChatGPT-Client-Web/"
llm_engine_dependency="${llm_engine_dir}/.venv"

# first check if we already have the virtual environment
if [ -d "$llm_engine_dependency" ]; then
    echo "Dependency installed proceed to run the project."
else
    echo "Dependency not installed. Setup project."

    # Check if Python 3.11 is installed
	if python3.11 --version &> /dev/null
	then
	    echo "Python 3.11 is installed."
	else
	    echo "Python 3.11 is not installed. Installing now..."
	    # Install Python 3.11 using Homebrew
	    brew install python@3.11
	fi

	python3 -m venv ${llm_engine_dependency}
	source "${llm_engine_dependency}/bin/activate"

	# Check if pip is installed
	if pip --version &> /dev/null
	then
	    echo "pip is installed."
	else
	    echo "pip is not installed. Installing now..."
	    # Install pip
	    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
	    python3 get-pip.py
	    rm get-pip.py

	    # Upgrade pip
		echo "Upgrading pip..."
		python3 -m pip install --upgrade pip
	fi
fi

# run the llm engine
source ../LLMEngine/.venv/bin/activate
python ../LLMEngine/main.py


# run chat client
cd chat_client_dir
yarn build
yarn start