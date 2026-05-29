.PHONY: test validate generate all

test:
	python -m pytest tests/ -v

validate:
	python scripts/config_validation/validate_config.py --config-dir config

generate:
	python scripts/scenario_generator/generate_scenarios.py

all: validate test
