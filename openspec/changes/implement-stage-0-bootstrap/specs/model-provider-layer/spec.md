## ADDED Requirements

### Requirement: Unified model request and response interface is provided

The system SHALL expose a model provider interface based on `ModelRequest` and `ModelResponse`, allowing the Agent to request a text completion without depending on a concrete model vendor implementation.

#### Scenario: Agent uses interface only

- **WHEN** the Agent runs a normalized user task
- **THEN** it converts the task into a `ModelRequest` and calls the configured model provider through the unified interface rather than importing a vendor-specific client

#### Scenario: Model response carries assistant text

- **WHEN** a provider call succeeds
- **THEN** it returns a `ModelResponse` containing the assistant text instead of returning a raw string

### Requirement: ModelRequest supports message-based input

The system SHALL represent model input as messages so later phases can add system prompts, multi-turn conversation history, and tool messages without replacing the model interface.

#### Scenario: Single task becomes user message

- **WHEN** the CLI receives a single task string in stage 0
- **THEN** the Agent creates a `ModelRequest` containing one user message with that task text

#### Scenario: Provider receives messages

- **WHEN** a remote provider sends a request to its backend
- **THEN** it maps `ModelRequest.messages` into the provider-specific request format

### Requirement: Echo provider supports offline execution

The system SHALL provide an `echo` provider that returns a deterministic local response without network access or API keys.

#### Scenario: Echo provider returns task text

- **WHEN** the selected model profile uses provider `echo` and the task is `hello`
- **THEN** the model response includes `Ikki 已接收任务：hello`

### Requirement: OpenAI-compatible provider supports chat completion

The system SHALL provide an `openai-compatible` provider that sends a non-streaming Chat Completions style request to a configured `base_url`.

#### Scenario: OpenAI-compatible request succeeds

- **WHEN** the selected profile has provider `openai-compatible`, model, base URL, API key environment variable, timeout, and temperature
- **THEN** the provider maps `ModelRequest.messages` to the configured Chat Completions endpoint and returns the assistant text in `ModelResponse.text`

#### Scenario: OpenAI-compatible response is invalid

- **WHEN** the provider receives a response without usable assistant text
- **THEN** it raises a model error with a clear Chinese explanation

### Requirement: Anthropic provider supports Messages API

The system SHALL provide an `anthropic` provider that sends a non-streaming Anthropic Messages API request to a configured `base_url`.

#### Scenario: Anthropic request succeeds

- **WHEN** the selected profile has provider `anthropic`, model, base URL, API key environment variable, timeout, and temperature
- **THEN** the provider maps `ModelRequest.messages` to the configured Messages API endpoint and returns the assistant text in `ModelResponse.text`

#### Scenario: Anthropic response is invalid

- **WHEN** the provider receives a response without usable text content
- **THEN** it raises a model error with a clear Chinese explanation

### Requirement: Model selection uses configured profile

The system SHALL construct the model provider from the effective model profile selected by CLI argument or default configuration.

#### Scenario: Config default provider is used

- **WHEN** the YAML file sets `app.default_model: local_test` and the user does not pass `--model`
- **THEN** the system constructs the `local_test` provider from configuration

#### Scenario: CLI selected provider wins

- **WHEN** the default model is a remote provider and the CLI passes `--model local_test`
- **THEN** the system constructs the echo provider and does not attempt to read remote API credentials

#### Scenario: Unknown profile is rejected

- **WHEN** the user selects a model profile that is not defined
- **THEN** the system fails with a clear Chinese error naming the missing profile
