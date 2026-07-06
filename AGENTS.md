# RULES
 - should implemets https://docs.spring.io/spring-boot/docs/2.1.8.RELEASE/actuator-api/html/#health API
 - Code Should be stay simple as possible
 - Advanced usage typing, type hints, modern linting like ruff mypy ty wps etc.
 - PythonCodeGenerationRules.md should be respect
 - Commit messages should follow Conventional Commits

# project
 - It s healthchecks module
 - HealthIndicator protocol should return HealthResult
 - we can have mupltiple indicators/components in one app.

# structure
 src/python_actuator/ main module dir
 src/python_actuator/protocols.py
 src/python_actuator/indicators.py
 src/python_actuator/models.py
