from enum import Enum
from typing import Any, Dict, List, Optional, Union
import time
from pydantic import BaseModel, Field

# Define the supported LLM providers
class Provider(str, Enum):
    openai = "openai"
    anthropic = "anthropic"
    groq = "groq"
    ollama = "ollama"

# Represents a message in a chat conversation
class Message(BaseModel):
    role: str = Field(..., description="Role of the message sender (e.g., system, user, assistant)")
    content: str = Field(..., description="Content of the message")

# Standard format for chat completion requests
class ChatCompletionRequest(BaseModel):
    model: str = Field(..., description="Model identifier (e.g., 'gpt-3.5-turbo')")
    messages: List[Message] = Field(..., description="List of messages forming the conversation")
    temperature: Optional[float] = Field(0.7, description="Sampling temperature for response randomness")
    max_tokens: Optional[int] = Field(100, description="Maximum tokens for the generated completion")
    provider: Optional[Provider] = Field(None, description="Optional LLM provider to use")
    stream: Optional[bool] = Field(False, description="Flag to indicate if streaming responses are expected")

# A helper model to encapsulate individual message generation choice in a response
class Choice(BaseModel):
    index: int = Field(..., description="Index of this choice in the response")
    message: Message = Field(..., description="Message generated for this choice")
    finish_reason: Optional[str] = Field(None, description="Reason for completion termination (e.g., 'stop')")

# A helper model to represent token usage for the chat completion
class Usage(BaseModel):
    prompt_tokens: Optional[int] = Field(0, description="Number of tokens used in the prompt")
    completion_tokens: Optional[int] = Field(0, description="Number of tokens generated in the completion")
    total_tokens: Optional[int] = Field(0, description="Total tokens for the entire request")

# Standard format for chat completion responses
class ChatCompletionResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the chat completion")
    object: str = Field("chat.completion", description="Type of returned object")
    created: int = Field(default_factory=lambda: int(time.time()), description="Timestamp for when the response was created")
    model: str = Field(..., description="Model identifier used for generating the response")
    choices: List[Choice] = Field(..., description="List of generated choices")
    usage: Optional[Usage] = Field(None, description="Token usage information")
    provider: Optional[Provider] = Field(None, description="LLM provider that generated the response")

# Standard format for text embedding requests
class TextEmbeddingRequest(BaseModel):
    model: str = Field(..., description="Model identifier for generating text embeddings")
    input: str = Field(..., description="Text input to be embedded")
    provider: Optional[Provider] = Field(None, description="Optional LLM provider to use for embeddings")

# Standard format for text embedding responses
class TextEmbeddingResponse(BaseModel):
    model: str = Field(..., description="Model identifier used for generating the embeddings")
    embedding: List[float] = Field(..., description="Embedding vector representing the input text")
    provider: Optional[Provider] = Field(None, description="LLM provider used for generating the embeddings")

# Model information structure for available LLM models
class ModelInfo(BaseModel):
    id: str = Field(..., description="Unique identifier for the model")
    name: Optional[str] = Field(None, description="Human-readable name of the model")
    description: Optional[str] = Field(None, description="Detailed description of the model")
    capabilities: List[str] = Field(default_factory=list, description="Capabilities of the model (e.g., chat, embeddings)")
