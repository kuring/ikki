## ADDED Requirements

### Requirement: YAML configuration is supported

The system SHALL load configuration from a YAML file such as `~/.ikki/config.yaml` using a safe YAML loading mode.

#### Scenario: Valid YAML config loads

- **WHEN** the user provides a valid YAML configuration file with `app` and `models` sections
- **THEN** the system returns an internal configuration object containing app settings and model profiles

#### Scenario: Missing config file is handled

- **WHEN** the user provides a config path that does not exist
- **THEN** the system reports a clear Chinese configuration error

### Requirement: Runtime paths are resolved consistently

The system SHALL use `~/.ikki/` as the default Agent work directory and `~/.ikki/config.yaml` as the default config file path.

#### Scenario: Default config path is used

- **WHEN** the user does not provide `--config` or `IKKI_CONFIG`
- **THEN** the system looks for configuration at `~/.ikki/config.yaml` and falls back to built-in defaults when that file is absent

#### Scenario: Config path can be overridden

- **WHEN** the user provides `--config` or `IKKI_CONFIG`
- **THEN** the explicit config path is used, with `--config` taking precedence over `IKKI_CONFIG`

#### Scenario: Work directory can be overridden

- **WHEN** `IKKI_HOME` is present
- **THEN** the default config path is resolved as `config.yaml` inside that directory

### Requirement: Configuration schema is validated by Pydantic

The system SHALL use Pydantic models as the internal configuration schema and validate configuration fields before runtime model selection, including provider names, required model fields, timeout values, temperature values, extra fields, and default model references.

#### Scenario: Unknown provider is rejected

- **WHEN** a model profile uses an unsupported provider value
- **THEN** configuration loading fails with a clear error naming the invalid provider

#### Scenario: Default model must exist

- **WHEN** `app.default_model` points to a missing model profile
- **THEN** configuration loading fails with a clear error naming the missing profile

#### Scenario: Numeric model parameters are bounded

- **WHEN** a model profile contains an invalid timeout or temperature value
- **THEN** configuration loading fails before any model backend is invoked

#### Scenario: Extra config field is rejected

- **WHEN** the YAML file contains an unsupported field in a known configuration section
- **THEN** Pydantic validation fails with a clear configuration error naming the unsupported field

### Requirement: Configuration precedence is deterministic

The system SHALL apply configuration precedence in this order: command line arguments override environment variables, environment variables override YAML file values, YAML file values override defaults.

#### Scenario: CLI model overrides default

- **WHEN** the YAML file sets `app.default_model: default` and the user passes `--model local_test`
- **THEN** the selected model profile is `local_test`

#### Scenario: Environment log level overrides file value

- **WHEN** the YAML file sets `app.log_level: WARNING` and `IKKI_LOG_LEVEL=DEBUG` is present without a CLI log level
- **THEN** the effective log level is `DEBUG`

### Requirement: Secrets are referenced by environment variable name

The system SHALL read API keys only from environment variables named by model profile fields and SHALL NOT require or encourage storing raw API keys in project configuration.

#### Scenario: API key env var resolves

- **WHEN** a real model profile sets `api_key_env: OPENAI_API_KEY` and that environment variable is present
- **THEN** the model backend receives the resolved API key value at runtime

#### Scenario: API key value is absent

- **WHEN** a real model profile sets `api_key_env` but the environment variable is absent
- **THEN** model selection fails with a clear missing-secret error before sending any HTTP request
