# RULES
 - should implemets https://docs.spring.io/spring-boot/docs/2.1.8.RELEASE/actuator-api/html/#health API
 - Code Should be stay simple as possible
 - Advanced usage typing, type hints, modern linting like ruff mypy ty wps etc.
 - PythonCodeGenerationRules.md should be respect

# project
 - It s healthchecks module
 - HealthIndicator protocol should return HealthResult
 - we can have mupltiple indicators/components in one app.

# structure
 python_actuator/ main module dir
 python_actuator/protocols.py
 python_actuator/indicators.py
 python_actuator/models.py