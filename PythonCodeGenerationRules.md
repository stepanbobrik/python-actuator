# Python Code Generation Rules [v1.1]

## Usage Guide

- Rules have severity: [C]ritical, [H]igh, [M]edium, [L]ow
- When rules conflict: Higher severity wins → Existing code patterns take precedence
- Process rules by severity (Critical first)

## Architecture & Structure [A]

- **[A1-C]** The existing code structure must not be changed without a strong reason.
- **[A2-C]** Every bug must be reproduced by a unit test before being fixed.
- **[A3-C]** Every new feature must be covered by a unit test before it is implemented.
- **[A4-H]** Formatting, linters, static analysis, and tests must pass after changes.
- **[A5-H]** Preserve the modular monolith; do not split the service into microservices without a separate architecture decision.
- **[A6-H]** The DDD paradigm must be respected.
- **[A7-M]** Minor inconsistencies and typos in the existing code may be fixed.

## Code Style & Patterns [S]

- **[S1-C]** Code must be formatted with the project's formatter and pass ruff checks.
- **[S2-H]** Identifiers must be written in English and follow Python naming conventions.
- **[S3-H]** Module, function, class, and DTO names must describe the concept, not an implementation detail.
- **[S4-H]** Functions and methods must be short, cohesive, and responsible for one behavior.
- **[S5-M]** Blank lines inside functions are allowed only to separate clearly distinct logical steps.
- **[S6-M]** Comments inside functions are allowed only to explain non-obvious intent; do not comment obvious code.
- **[S7-H]** Dead code, commented-out code, temporary debugging fragments, and IDE artifacts are prohibited.
- **[S8-M]** Error and log messages should be a single phrase and should not end with a period.
- **[S9-H]** Prefer fail fast: invalid state should be detected and interrupted as early as possible.
- **[S10-H]** Global mutable state is prohibited; pass configuration explicitly or through a settings object.
- **[S11-H]** Classes must avoid using public static literals, `@classmethod`, and `@staticmethod`; prefer module-level constants, module-level functions, or injected settings.

## Typing & Data [Y]

- **[Y1-C]** All functions, methods, data classes, and DTOs must have explicit type hints.
- **[Y2-H]** `Any`, `object`, `cast()`, and mypy suppressions are allowed only at integration boundaries and must have local justification.
- **[Y3-C]** Do not return or pass `None` implicitly; absence of a value must be expressed explicitly as `T | None`.
- **[Y4-H]** Do not use arbitrary `dict` or `list` values for structured data when a Pydantic model, dataclass or `TypedDict` is available.
- **[Y5-H]** DTOs for HTTP requests and responses must be Pydantic v2 models with explicit field types.
- **[Y6-H]** Do not use mutable default values; use `default_factory` or create the value inside the function.
- **[Y7-M]** Use `pathlib.Path`, `collections.abc`, `enum`, `uuid`, timezone-aware `datetime`, and standard Python types instead of string surrogates.

## Classes & Objects [C]

- **[C1-H]** A class should exist only when it has state, an invariant or a contract.
- **[C2-C]** Utility classes are strictly prohibited.
- **[C3-H]** Prefer composition over implementation inheritance.
- **[C4-H]** Describe contracts with `typing.Protocol` or ABCs only where real polymorphism exists.
- **[C5-H]** State changes must be explicit behavior or creation of a new object.
- **[C6-H]** Class attributes must not be used as hidden global state.
- **[C7-M]** Keep the number of class attributes small; if an object grows, extract value objects or separate responsibilities.
- **[C8-H]** Setters must be avoided, as they make objects mutable.
- **[C9-H]** Immutable objects must be favored over mutable ones.
- **[C10-C]** Static methods in classes are strictly prohibited.
- **[C11-C]** All classes must be declared final, using `typing.final` or `@final` so the rule is enforced by static analysis.
- **[C12-C]** Every public or non-trivial class must have a class docstring.
- **[C13-H]** Every class must encapsulate at least one attribute, unless a function, protocol, or exception class is a clearer fit.

## Functions & Methods [M]

- **[M1-H]** Public functions and methods must have a clear contract: types, name, exceptions, and side effects.
- **[M2-H]** Separate commands and queries: a method should either change state/perform an action or return data.
- **[M3-C]** Functions must not return `None` unless it is declared in the type and is part of an explicit contract.
- **[M4-C]** `None` arguments are prohibited unless the parameter type allows `None`.
- **[M5-H]** Exceptions must be specific; do not swallow exceptions with empty `except` blocks or `except Exception` without re-raising.
- **[M6-H]** When translating exceptions, use `raise ... from error` to preserve the causal chain.
- **[M7-H]** Exception messages must include safe context sufficient for diagnostics without exposing secrets or tokens.
- **[M8-C]** `eval`, unsafe deserialization, and shell execution from user input are prohibited.
- **[M9-H]** Resources must be managed with context managers, async context managers, or explicitly closeable dependencies.
- **[M10-H]** Methods must be declared in `Protocol` or ABC contracts and then implemented in classes when this helps support a flexible system.
- **[M11-H]** Public methods that do not implement a `Protocol` or ABC contract should be avoided when interface-based design helps support a flexible system.
- **[M12-M]** Methods should avoid checking incoming arguments for validity; perform aggressive validation at endpoints, while domain logic should fail fast instead of sanitizing all trash.
- **[M13-C]** Type introspection and type casting are strictly prohibited outside framework and integration boundaries.
- **[M14-C]** Reflection on object internals is strictly prohibited outside controlled integration boundaries.

## FastAPI & Integration [F]

- **[F1-H]** FastAPI route handlers must be thin: accept a DTO, call the application/service layer, and return a DTO.
- **[F2-H]** Business logic must not live in route handlers, dependencies, or Pydantic validators.
- **[F3-H]** Pydantic validators may normalize and validate data shape, but must not perform I/O or access infrastructure.
- **[F4-C]** Secrets, tokens, production configuration, and personal data must not be stored in the repository.
- **[F5-C]** Do not log secrets, tokens, full `Authorization` headers, or sensitive parameters.
- **[F6-H]** External HTTP calls must have explicit timeouts, error handling, and a controlled retry strategy.
- **[F7-H]** Configuration must come from environment variables through Pydantic Settings or an equivalent settings object.
- **[F8-M]** Async code must use async libraries and must not block the event loop with synchronous I/O.

## Testing Standards [T]

- **[T1-C]** Every change must be covered by a unit test to guarantee repeatability.
- **[T2-H]** A test must verify one specific behavior.
- **[T3-H]** Every test must include an explicit check: `assert`, `pytest.raises`, or a test client response assertion.
- **[T4-M]** Test cases must be as short as possible.
- **[T5-H]** Tests must not depend on execution order or shared mutable state.
- **[T6-H]** Fixture data must be local to the test or come from an isolated fixture.
- **[T7-H]** Tests must work without Internet access.
- **[T8-H]** Use `tmp_path` or `tempfile` for files, not codebase directories.
- **[T9-H]** Use ephemeral ports for network tests, such as binding to port `0`.
- **[T10-H]** Waiting for events, threads, async tasks, and external responses must always have a timeout.
- **[T11-H]** Do not mock the file system, sockets, or memory managers when real temporary resources can be used.
- **[T12-M]** Do not assert on error or log text unless it is part of the public contract.
- **[T13-M]** Do not assert on logs unless logging is explicit behavior.
- **[T14-H]** Tests must not print messages to stdout or stderr.
- **[T15-H]** Random test data must be deterministic: seed, factory with a controlled source, or property-based test with a reproducible failing case.
- **[T16-M]** Prefer inlining small fixture data; prefer generating large fixture data during the test.
- **[T17-H]** Tests must not use real secrets, production URLs, or production configuration.
- **[T18-M]** Do not test trivial getters, setters, and constructors separately; test observable behavior and invariants.
- **[T19-H]** Functionality added only for tests is prohibited in production code.
- **[T20-H]** Every test case should contain one assertion, or a dedicated assertion helper; integration tests may be exempt when needed.
- **[T21-M]** Each test file must have a one-to-one mapping with the feature file it tests.
- **[T22-H]** Tests may not use setUp() or tearDown() idioms.
- **[T23-H]** Tests may not use static literals or other shared constants.
- **[T24-M]** Tests must not clean up after themselves; instead, they must prepare a clean state at the start.
- **[T25-M]** Tests should be separated into three parts: init, execute, assert.
- **[T26-M]** Tests should use plain pytest `assert`; matcher libraries such as `dirty-equals` or `pytest-unordered` may be used when they improve assertions.
- **[T27-H]** Tests must verify object behavior in multi-threaded, concurrent, or async environments when the code under test uses them.
- **[T28-H]** Tests may retry potentially flaky code blocks only with bounded retries; flakiness should be removed rather than masked.
- **[T29-H]** Tests must not rely on default configurations of the objects they test, providing custom arguments.
- **[T30-M]** Tests may create supplementary fixture objects to avoid code duplication.

## AI Code Generation Process [AI]

- **[AI1-H]** Analyze existing patterns first.
- **[AI2-H]** Write tests before implementation.
- **[AI3-H]** Before adding an abstraction, prove that it reduces complexity or expresses a real contract.
- **[AI4-H]** Implement with immutability, explicit types, and a minimal public surface in mind.
- **[AI5-H]** Do not touch unrelated files or reformat outside the task scope.
- **[AI6-H]** After edits, run the available checks: `uv run ruff format .`, `uv run ruff check --fix .`, `uv run mypy .`, `uv run pytest`.