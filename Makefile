activate:
	source .venv/bin/activate

init:
	echo "Initializing project..."
	touch .env

run:
	echo "Running application..."
	python main.py
