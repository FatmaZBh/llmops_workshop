# LAB1 - Building a robust LLM Server Gateway Wrapper with FastAPI

In this lab we will be building a unified API gateway that abstracts away the differences between various Large Language Model providers. Your gateway will serve as a middleware layer that standardizes requests and responses across multiple LLM services including OpenAI, Anthropic (Claude), Groq, and locally hosted models via Ollama like [LiteLLM](https://www.litellm.ai/) 🔥

## Specifications

By the end of this lab, you'll have :
1. A FastAPI application that exposes a unified interface for LLM interactions
2. Support for multiple LLM providers with easy extension capabilities
3. Standardized request/response formats
4. Proper error handling and logging
5. Rate limiting and request validation
6. A comprehensive test suite
7. Documentation for API endpoints

The learning objectives are (your mission if you choose to accept it 🕵️):

- [ ] Create modular service adapters
- [ ] Develop a robust error handling and fallback strategy for tiers parties api 
- [ ] Implement caching and rate limiting for optimization with redis
- [ ] Build practical test driven devlopement
- [ ] Deploy your project using docker 

Let's start by the architecture overview of our gateway project 🤓

## Architecture Overview

Our LLM gateway will follow a simple modular architecture. 


```
┌───────────────┐      ┌─────────────────┐      ┌───────────────────┐
│               │      │                 │      │                   │
│  Client App   ├──────▶  FastAPI Gateway├──────▶  Provider Adapters│
│               │      │                 │      │                   │
└───────────────┘      └─────────────────┘      └─────────┬─────────┘
                                                          │
                                                          ▼
                       ┌───────────────────────────────────────────────┐
                       │                                               │
                       │  ┌─────────┐  ┌────────┐  ┌───────┐  ┌──────┐ │
                       │  │         │  │        │  │       │  │      │ │
                       │  │  OpenAI │  │  Groq  │  │ Claude│  │Ollama│ │
                       │  │         │  │        │  │       │  │      │ │
                       │  └─────────┘  └────────┘  └───────┘  └──────┘ │
                       │                                               │
                       │               LLM Providers                   │
                       │                                               │
                       └───────────────────────────────────────────────┘
```

The architecture above consists of these primary components :

1. **FastAPI Gateway**: The entry point that exposes unified REST endpoints.

2. **Provider Adapters**: A layer of adapters that translate between our standard format and provider-specific formats.

3. **LLM Providers**: Integration with various LLM services (OpenAI, Claude, Groq) and local deployment (Ollama).

4. **Shared Components**:
   - Authentication service
   - Caching mechanism
   - Rate limiter
   - Request validator
   - Response formatter
   - Logging service

That's pretty much it for the overview of the project, now let's dig into the implementation 😅

### Structure

Below the `tree` structure of the lab : 

```
llm_gateway/
├── main.py                  # FastAPI application entry point
├── config.py                # Configuration settings
├── requirements.txt         # Dependencies
├── .env.example             # Example environment variables
│   ├── __init__.py
├── core/
│   ├── models.py            # Pydantic models for requests/responses
│   ├── constants.py         # Constant values
│   ├── errors.py            # Custom exceptions
│   └── utils.py             # Utility functions
├── services/
│   ├── __init__.py
│   ├── base.py              # Base LLM service interface
│   ├── openai_service.py    # OpenAI implementation
│   ├── anthropic_service.py # Anthropic implementation
│   ├── groq_service.py      # Groq implementation
│   └── ollama_service.py    # Ollama implementation
├── api/
│   ├── __init__.py
│   ├── dependencies.py      # FastAPI dependencies
│   ├── errors.py            # Error handlers
│   ├── middleware.py        # Custom middleware
│   └── routers/
│       ├── __init__.py
│       ├── chat.py          # Chat completion endpoints
│       ├── embeddings.py    # Text embedding endpoints
│       └── models.py        # Model info endpoints
├── tests/ # see the test section at the end of the doc
└─
```

> This is a classical API structure if you are not familiar with this kind of things please read the official [documentation](https://fastapi.tiangolo.com/fr/#en-resume) and/or the excellent article [How to Structure Your FastAPI Projects](https://medium.com/@amirm.lavasani/how-to-structure-your-fastapi-projects-0219a6600a8f) from Amir Lavasani. 

## Features

Our project is **divided into 6 majors components called `core components`**

### Core Components

1. **FastAPI Application**: The entry point and API layer for client interactions.
2. **Provider Service Adapters**: Adapters that translate between our unified API format and provider-specific formats.
3. **Core Models**: Standardized data models for requests and responses.
4. **Middleware**: Components for authentication, rate limiting, and request/response logging.
5. **Cache**: Response caching to improve performance and reduce API costs.
6. **Error Handling**: Comprehensive error handling and automatic fallback mechanisms.

Below the explicits 8 features for our fastapi app 🧙‍♂️

### 1. Unified API for Multiple Providers

The gateway provides standardized endpoints for :
- [ ] Chat completions
- [ ] Text embeddings
- [ ] Model information and selection

All providers are accessed through the same interface, allowing easy switching between providers without changing client code.

### 2. Provider Adapters

Each LLM provider has a dedicated adapter that:
- [ ] Converts our standardized request format to the provider's format
- [ ] Handles authentication with the provider
- [ ] Converts the provider's response to our standardized format
- [ ] Provides provider-specific utility functions (like token counting)

### 3. Automatic Fallbacks

The gateway includes a robust fallback mechanism that :
- [ ] Detects when a provider is unavailable
- [ ] Automatically routes the request to a fallback provider
- [ ] Maintains equivalent model selection across providers

### 4. Caching

Response caching improves performance and reduces costs by :
- [ ] Storing responses for identical requests
- [ ] Supporting both in-memory and Redis-based caching
- [ ] Configurable cache expiration policies

### 5. Rate Limiting

To protect API keys and manage costs, the gateway includes :
- [ ] Configurable rate limiting by API key or client IP
- [ ] Graceful handling of rate limit exceeded scenarios
- [ ] Per-provider rate limit tracking

### 6. Model Mapping and Selection

The gateway simplifies model selection with :
- [ ] Standardized model information across providers
- [ ] Model capability filtering (chat, embeddings, etc.)
- [ ] Cross-provider model mappings for equivalent models

### 7. Comprehensive Error Handling

Robust error handling ensures reliability :
- [ ] Standardized error responses
- [ ] Detailed error logging
- [ ] Automatic retries with exponential backoff
- [ ] Provider-specific error translation

### 8. Monitoring and Logging

Built-in monitoring provides insights into :
- [ ] Request/response timing
- [ ] Token usage and estimated costs
- [ ] Provider availability and errors
- [ ] Request volume and patterns

--- 

## Implementation Walkthrough

Now let's dive into the implempentation of our project 👀

### 1. Core Data Models

First thing first, let's take a look to the core data model : the basic objects involves in our game 🛠️ 

When constructing an API, starting with the core data models is essential because they **define what information flows through your system and how it's structured**. This upfront modeling helps prevent inconsistencies and makes it easier to implement features while maintaining a coherent system design.RetryClaude can make mistakes. Please double-check responses.

> The core models define the standardized data structures for requests and responses. These use [Pydantic](https://docs.pydantic.dev/latest/) for validation and serialization.

Key models include:
- [ ]  `Provider` enum: Defines supported LLM providers
- [ ] `Message`: Represents a message in a chat conversation
- [ ] `ChatCompletionRequest`: Standard format for chat completion requests
- [ ] `ChatCompletionResponse`: Standard format for chat completion responses
- [ ] `TextEmbeddingRequest`: Standard format for text embedding requests
- [ ] `TextEmbeddingResponse`: Standard format for text embedding responses
- [ ] `ModelInfo`: Information about some LLM model

### 2. Service Interface

In this part we will be coding the service interface as a [python abstract class](https://docs.python.org/3/library/abc.html) 💡

In a nutshell, abstract methods define a "model" that all concrete implementations must adhere to, ensuring consistency across providers. We define a `BaseLLMService` abstract class with methods that all provider implementations must follow. 

> The abstract class defines what operations are supported without specifying how they are implemented 🤓

For example every provider must have a `get_chat_completion` method but we will implement this method for each specific provider in a other "child" class, for example the openai `get_chat_completion` method will be implemented inside `openai_service.py`. 

```python

class BaseLLMService(ABC):
    """
    Abstract base class for LLM service implementations.
    All provider-specific services must implement these methods.
    """
    
    provider: Provider
    # Get chat completion 
    @abstractmethod
    async def get_chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        pass
    
    # Get embeddings 
    @abstractmethod
    async def get_embeddings(self, request: TextEmbeddingRequest) -> TextEmbeddingResponse:
        pass

    # List models 
    @abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        pass

    # Get model infos from provider 
    @abstractmethod
    async def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        pass

    # Check if the service is running right 
    @abstractmethod
    async def health_check(self) -> bool:
        pass
    
    # Convert a standardized request to the provider-specific format
    @abstractmethod
    def convert_request(self, request: Union[ChatCompletionRequest, TextEmbeddingRequest]) -> Dict[str, Any]:
        pass
    
    # Convert a standardized response request to the provider-specific format
    @abstractmethod
    def convert_response(self, response: Any, request_type: str) -> Union[ChatCompletionResponse, TextEmbeddingResponse]:
        pass

    # Count token 
    @abstractmethod
    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        pass
```

> The abstract class provides a clear structure for implementing new provider adapters, reducing development time and errors.

### 3. Provider Implementations

As we said earlier, **each provider has a dedicated service implementation**. For example, the OpenAI service handles all interactions with the OpenAI API only, preventing these details from leaking into the rest of the application 🛠️

The provider implementation workflow is :
- [ ] Initialize the provider's client with API keys
- [ ] Implement all methods from the base service interface
- [ ] Handle provider-specific error handling and retries
- [ ] Convert between standardized and provider-specific formats

To keep the same example as before with the `openai_service.py` will follow the above features.

> NOTE : if you not have any openai, anthropic key try groq it's free and do not require any banking card validation 💡

### 4. Service Factory

In order to centralized the providers management and enabling runtime selection and automatic fallback mechanisms we will code a `service factory` using the [Factory pattern](https://en.wikipedia.org/wiki/Factory_method_pattern) 🥸

The main idea here is to decoupled client code from service implementation details, in order to simplifying the maintenance and provider additions

The `LLMServiceFactory` manages all provider services and handles provider selection:

```python
class LLMServiceFactory:
    """
    Factory class for creating and managing LLM service instances.
    This provides a centralized way to access different LLM providers.
    """
    
    def __init__(self):
        self._services: Dict[Provider, BaseLLMService] = {}
        self._initialize_services()
    
    def get_service(self, provider: Provider) -> Optional[BaseLLMService]:
        return self._services.get(provider)
    
    def get_default_service(self) -> Optional[BaseLLMService]:
        default_provider = Provider(settings.DEFAULT_PROVIDER.lower())
        return self.get_service(default_provider)
    
    def get_fallback_service(self, primary_provider: Provider) -> Optional[BaseLLMService]:
        # Implementation for selecting fallback providers
        ...
```

> Our factory here can handle loading configuration for different providers, keeping this complexity away from the rest of the application 🔥


### 5. API Routes

As you may know or read in the intro section, the API routes handle HTTP requests and delegate to the appropriate service. 

You can check the [official doc](https://fastapi.tiangolo.com/tutorial/body/#request-body-path-parameters) if you are not comfortable with the FastAPI routing 💪

Like you saw in the project structure earlier, we will not put everything in a single file. We will follow the [doc guidance](https://fastapi.tiangolo.com/tutorial/bigger-applications/?h=bluep#an-example-file-structure) with the `APIRouter` to organise our app.

![](https://fastapi.tiangolo.com/img/tutorial/bigger-applications/package.svg)

For example, the chat completions endpoint will be like this :

```python
@router.post("/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    background_tasks: BackgroundTasks,
    request: ChatCompletionRequest = Body(...),
    cache = Depends(get_cache)
):
    # Get the requested provider or use the default
    provider_name = request.provider or Provider(settings.DEFAULT_PROVIDER.lower())
    
    # Get the service for the requested provider
    service = service_factory.get_service(provider_name)
    
    if not service:
        raise HTTPException(
            status_code=400,
            detail=f"Provider '{provider_name}' not available. Available providers: {service_factory.get_available_providers()}"
        )
    
    # Check for cached response
    if settings.ENABLE_CACHE and cache and not request.stream:
        cache_key = f"chat:{provider_name}:{hash(str(request.dict()))}"
        cached_response = await cache.get(cache_key)
        if cached_response:
            return cached_response
    
    # Get the chat completion from the provider
    response = await service.get_chat_completion(request)
    
    # Cache the response if applicable
    if settings.ENABLE_CACHE and cache and not request.stream:
        background_tasks.add_task(
            cache.set, cache_key, response, expiry=settings.CACHE_EXPIRATION
        )
    
    return response
```

### 6. Middleware

Middleware provides a clean way to implement functionality that should apply to multiple or all endpoints, reducing code duplication and ensuring consistent behavior. 

You can see the FastAPI documentation [here](https://fastapi.tiangolo.com/tutorial/middleware/) 

> Request/response processing can be modified globally without changing endpoint implementation code, improving separation of concerns 😎

Our middleware will handle cross-cutting concerns like:
- Logging requests and responses
- Rate limiting
- Error handling

For example, the logging middleware should be like :

```python
class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses."""
    
    async def dispatch(self, request: Request, call_next):
        """Process the request and log the details."""
        request_id = request.headers.get("X-Request-ID", "")
        start_time = time.time()
        
        # Log request details
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Process the request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response details
        logger.info(
            f"Response {request_id}: {response.status_code} in {process_time:.4f}s"
        )
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
```

Implementing middleware allows your API to maintain cleaner endpoint handlers focused on business logic while common operations like request validation, error handling, and performance monitoring are handled consistently across all routes.


### 7. Caching 

Caching is the technique of storing copies of frequently accessed data in a fast-access temporary storage layer to reduce response times and computational load when the same data is requested again.

> That's why your amazon bucket is rarely empty your informations are stored by your browser. 

Our caching system will support both in-memory caching (for development) and Redis-based caching (for production). 

Below the template for the redis class : 

```python
class RedisCache:
    """Simple Redis cache for storing responses."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Any, expiry: int = 3600) -> bool:
        """Set a value in the cache with expiry in seconds."""
        await self.redis.setex(key, expiry, json.dumps(value, default=self._json_serializer))
        return True
```

Implementing caching in your API design is a very good practice and allows you to strategically optimize for performance and cost without compromising the clarity of your core service implementation, creating a more scalable and efficient system 😎

### 8. Testing

Testing is an important part of this lab, indeed is not the most funniest part but in today's software development world, testing and Test-Driven Development (TDD) have become crucial practices for engineers. 


Our testing suite will include :
- [ ] Unit tests for each provider implementation
- [ ] Integration tests for API endpoints
- [ ] Mocking for external dependencies

See below in the testing section for more details 🧐


### Exception Handling

The project will implement comprehensive exception handling for various scenarios like :

- [ ] **Provider API Errors**: When a provider's API returns an error
- [ ] **Authentication Errors**: When API keys are invalid or missing
- [ ] **Rate Limit Exceeded**: When a provider or the gateway rate limit is exceeded
- [ ] **Validation Errors**: When a request fails validation
- [ ] **Provider Unavailable**: When a provider is temporarily unavailable
- [ ] **Model Not Found**: When a requested model can't be found
- [ ] **Content Filter Errors**: When content is filtered by a provider

⚠️ All errors must be returned in a standardized format like this ⚠️

```json
{
  "error": true,
  "code": "error_code",
  "message": "Human-friendly error message",
  "details": {
    // Additional error details if available
  }
}
```

### API Endpoints

Here is an overview of all the endpoints of our project 👀

#### Chat Completions

```http
POST /api/v1/chat/completions
```

Request format:

```json
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, how are you?"}
  ],
  "temperature": 0.7,
  "max_tokens": 100,
  "provider": "openai"  // Optional, defaults to configured default provider
}
```

#### Text Embeddings

```http
POST /api/v1/embeddings
```

Request format:

```json
{
  "model": "text-embedding-ada-002",
  "input": "Hello, world!",
  "provider": "openai"  // Optional
}
```

#### List Models

```http
GET /api/v1/models
```

Optional query parameters:

- `provider`: Filter by provider (e.g., "openai", "anthropic")
- `capability`: Filter by capability (e.g., "chat", "embeddings")

#### Get Model Information

```http
GET /api/v1/models/{model_id}
```

Optional query parameters:

- `provider`: Specify the provider to get model information from

#### Health Check

```http
GET /health
```

--- 

## Deployment

The gateway can be deployed using Docker and Docker Compose (use the file below), making it easy to set up in any environment 🐳

The Docker Compose configuration includes:
- The LLM Gateway API
- Redis for the caching managment 
- Ollama for local model support

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
    env_file:
      - .env
    environment:
      - REDIS_URL=redis://redis:6379/0
      - OLLAMA_HOST=http://ollama:11434
    depends_on:
      - redis
    networks:
      - llm_network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - llm_network
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - llm_network
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

> NOTE : if your machine do not have GPU just remove the `deploy` section of the `ollama` service 


## Automation with `makefile`

A [Makefile](https://fr.wikipedia.org/wiki/Make) is a configuration file that defines a set of tasks (commands) to be executed through the make utility, providing developers with standardized shortcuts for common operations like building, testing, and deploying code, which helps streamline development workflows and ensures consistency across the team when working on an API project.

In your makefile you will ensure the following : 

- [ ] **Core Setup and Management**
  - [ ] Set up the development environment using an installation script
  - [ ] Clean up generated files and directories (cache, build artifacts, etc.)
  - [ ] Run the application in standard mode
  - [ ] Run the application in development mode with auto-reload

- [ ] **Docker Management**
  - [ ] Build Docker images for the application
  - [ ] Run the application in Docker containers
  - [ ] Stop Docker containers

- [ ] **Testing**
  - [ ] Run the full test suite
  - [ ] Test chat functionality with configurable models and providers
  - [ ] Run provider-specific tests for Ollama, OpenAI, and Anthropic

- [ ] **Project Structure**
  - [ ] Initialize the project directory structure
  - [ ] Create the project file structure (this is mainly a bash script call)

- [ ] **Code Quality [BONUS]**
  - [ ] Run linters (flake8, mypy) to check code quality 
  - [ ] Format code using standard tools (black, isort)


You will use this makefile template below :

```makefile 
# Environment variables
PYTHON := python
PIP := pip
CONDA := conda
ENV_NAME := llmops
VENV_DIR := venv
PORT := 8000
HOST := 0.0.0.0
APP := main:app

# Directories
SRC_DIR := llm_gateway
TEST_DIR := tests
LOGS_DIR := logs

# Files
REQ_FILE := requirements.txt
DEV_REQ_FILE := requirements-dev.txt
ENV_FILE := .env
ENV_EXAMPLE := .env.example
INSTALL_SCRIPT := install.sh
TEST_SCRIPT := test_chat.sh

# Docker
DOCKER_COMPOSE := docker-compose
DOCKERFILE := Dockerfile

# Colors
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

.PHONY: help install setup clean run run-dev test lint format docker-build docker-run docker-stop init-dir create-structure test-chat test-ollama test-openai test-anthropic

# Default target
help:
	@echo "LLM Gateway Project Makefile"
	@echo "============================"
	@echo "Available commands:"
	@echo ""
	@echo "  make setup         - Set up the environment using install.sh script"
	@echo "  make clean         - Clean up generated files"
	@echo "  make run           - Run the application"
	@echo "  make run-dev       - Run the application in development mode"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run Docker container"
	@echo "  make docker-stop   - Stop Docker container"
	@echo "  make init-dir      - Initialize project directory structure"
	@echo "  make create-structure - Create project file structure"
	@echo ""
	@echo "Testing commands:"
	@echo "  make test-chat MODEL=model_name PROVIDER=provider_name STREAM=true|false"
	@echo "  make test-ollama [MODEL=model_name] - Test with Ollama provider (default: llama3.2)"
	@echo "  make test-openai [MODEL=model_name] - Test with OpenAI provider (default: gpt-3.5-turbo)"
	@echo "  make test-anthropic [MODEL=model_name] - Test with Anthropic provider (default: claude-3-haiku)"
```

--- 

## Test scenarios 

The test structure for the project should follow this structure : 

```bash
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures and configuration
├── fixtures/                      # Test data
│   ├── __init__.py
│   ├── requests.json              # Sample API requests
│   └── responses.json             # Sample API responses
├── test_api.py                    # Tests for API endpoints
├── test_services.py               # Basic service tests (shared functionality)
├── test_openai_service.py         # OpenAI-specific tests
├── test_anthropic_service.py      # Anthropic-specific tests 
├── test_groq_service.py           # Groq-specific tests
├── test_ollama_service.py         # Ollama-specific tests
├── test_models.py                 # Data model validation tests
└── test_middleware.py             # Middleware tests
```

1. First, make sure all tests dependencies are installed:

```bash
pip install pytest pytest-cov httpx
```


## Fixtures

We will be using [fixtures](https://en.wikipedia.org/wiki/Test_fixture#Software) in our test. 

The purpose of a test fixture is to ensure that there is a well known and fixed environment in which tests are run so that results are repeatable. Some people call this the test context. See more [here](https://stackoverflow.com/questions/12071344/what-are-fixtures-in-programming).

In a nutshell with fixtures you can : 
- Test error handling by simulating API errors 
- No spending on API calls when running tests hundreds of times during development 💸
- Focus on testing your code's behavior, not the API's


Common test fixtures should be defined in your `conftest.py`. These can include :

- [ ] `client` - FastAPI test client
- [ ] `test_data_dir` - Temporary directory for test data
- [ ] `api_key_headers` - Headers with mock API key
- [ ] `test_data` - Loaded test data from JSON files
- [ ] `sample_prompt` - Sample prompt for testing
- [ ] `sample_template` - Sample template for testing

--- 

Below here is simple templates for creating your test functions, please focusing on the key patterns rather than complete implementations 🤗


### Service Test Template
```python 
# In test_openai_service.py, test_anthropic_service.py, etc.

import pytest
from unittest.mock import MagicMock, patch

async def test_service_method(mock_client):
    """Test description explaining what this tests."""
    # 1. ARRANGE - Set up test data and expectations
    request_data = {...}  # Test input data
    expected_response = {...}  # Expected output data
    
    # Configure mock behavior
    mock_client.some_method.return_value = MagicMock(...)
    
    # 2. ACT - Call the method being tested
    result = await service.method_being_tested(request_data)
    
    # 3. ASSERT - Verify the results
    assert result.some_property == expected_response["some_property"]
    assert len(result.some_list) == 2
    
    # Verify the client was called correctly
    mock_client.some_method.assert_called_once_with(...)
```

### API Test Template

```python 
# In test_api.py

def test_api_endpoint(client, mock_service_factory):
    """Test description explaining what this tests."""
    # 1. ARRANGE - Set up test data and mocks
    request_data = {...}
    expected_response = {...}
    
    # Configure mock service
    mock_service = mock_service_factory.get_service.return_value
    mock_service.some_method.return_value = expected_response
    
    # 2. ACT - Make the API call
    response = client.post("/api/endpoint", json=request_data)
    
    # 3. ASSERT - Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["key"] == expected_response["key"]

```

### Model Test Template
```python 
# In test_models.py

def test_model_validation():
    """Test description explaining what this tests."""
    # 1. ARRANGE - Set up test data
    valid_data = {...}
    
    # 2. ACT - Create model instance
    model = ModelClass(**valid_data)
    
    # 3. ASSERT - Verify model properties
    assert model.property == valid_data["property"]
    
    # Test invalid data (should raise ValidationError)
    with pytest.raises(ValidationError):
        ModelClass(invalid_field="invalid value")

```


### Error Handling Test Template

```python 
# In any test file
async def test_error_handling():
    """Test description explaining what this tests."""
    # 1. ARRANGE - Set up to trigger an error
    mock_client.some_method.side_effect = Exception("Test error")
    
    # 2. ACT & ASSERT - Verify error is handled correctly
    with pytest.raises(CustomError) as excinfo:
        await service.method_being_tested(...)
    
    # Verify error details
    assert "meaningful error message" in str(excinfo.value)
```

For example, testing the chat completion endpoint:

```python
def test_chat_completion(client: TestClient, mock_service_factory: MagicMock, api_key_header: Dict[str, str], sample_chat_request: Dict[str, Any]):
    """Test the chat completion endpoint returns the expected response."""
    # Set up the openai mock to return a specific chat completion response
    mock_response = MagicMock(spec=ChatCompletionResponse)
    mock_response.dict.return_value = {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677858242,
        "model": "gpt-3.5-turbo",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "I'm doing well, thank you! How can I help you today?"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 25,
            "completion_tokens": 12,
            "total_tokens": 37
        },
        "provider": "openai"
    }
    
    # TODO: Configure the mock service
    
    # TODO : Call the chat completion endpoint
    
    # TODO : Check the response
    
```

### General tips for your tests

- [ ] Follow the [AAA pattern](https://automationpanda.com/2020/07/07/arrange-act-assert-a-pattern-for-writing-good-tests/): Arrange, Act, Assert
- [ ] Give tests descriptive names that explain what they're testing
- [ ] Include tests for both success cases and error handling
- [ ] Keep tests focused on a single behavior or feature
- [ ] Use fixtures for reusable test setup
- [ ] Mock external dependencies to isolate what you're testing

You should generate a coverage report of your tests to see quickly the results 😎


--- 

## Lab Challenges and Extensions | only for the braves 🥷

Once you've implemented the core gateway functionality, try these bonus tasks if you want :

- [ ] **Streaming Support**: Implement streaming responses for chat completions.
- [ ] **User Management**: Add user accounts and API key management.
- [ ] **Cost Tracking**: Implement cost tracking and budgeting per API key.
- [ ] **Intelligent Routing**: Route requests to the most cost-effective provider based on the request type.
- [ ] **Model Fine-tuning API**: Add support for fine-tuning models through a unified API.
- [ ] **Function Calling**: Implement support for function calling across providers.
- [ ] **Advanced Caching**: Implement semantic caching based on embedding similarity.
- [ ] **Monitoring Dashboard**: Create a web dashboard for monitoring gateway metrics.


## Conclusion

This lab has guided you through building a minimal software brick, with good practice.💪

These skills are valuable for building any kind of API gateway or middleware layer in modern cloud-native architectures whatever the language you use ! 

Hope you liked it, happy coding 🤗


