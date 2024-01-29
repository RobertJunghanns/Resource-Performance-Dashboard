.PHONY: shell
shell:
	@echo "Enter pipenv shell..."
	@pipenv shell

.PHONY: exit-shell
exit-shell:
	@echo "Exit pipenv shell..."
	@exit

.PHONY: run-dashboard
run-dashboard: install-requirements
	@echo "Starting Dashboard..."
	@python src/index.py

.PHONY: run-tests
run-tests:
	@echo "Running tests..."
	@python -m unittest discover -s tests

.PHONY: run-coverage-tests
run-coverage-tests:
	@echo "Running statement and branch coverage test..."
	@coverage run --branch --source=src/framework -m unittest discover -s tests
	@coverage html
	@open htmlcov/index.html

.PHONY: install-requirements
install-requirements:
	@echo "Installing requirements..."
	@pip install -r requirements.txt

.PHONY: show-requirements
show-requirements:
	@echo "Show requirements..."
	@pip freeze

.PHONY: update-requirements
update-requirements:
	@echo "Update requirements.txt..."
	@pip freeze > requirements.txt