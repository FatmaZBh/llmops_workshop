from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from core.models import (
    Provider,
    ChatCompletionRequest,
    ChatCompletionResponse,
    TextEmbeddingRequest,
    TextEmbeddingResponse,
    ModelInfo
)

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

    # Get model information from provider 
    @abstractmethod
    async def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        pass

    # Check if the service is running properly 
    @abstractmethod
    async def health_check(self) -> bool:
        pass
    
    # Convert a standardized request to the provider-specific format
    @abstractmethod
    def convert_request(self, request: Union[ChatCompletionRequest, TextEmbeddingRequest]) -> Dict[str, Any]:
        pass
    
    # Convert a provider-specific response into the standardized format
    @abstractmethod
    def convert_response(self, response: Any, request_type: str) -> Union[ChatCompletionResponse, TextEmbeddingResponse]:
        pass

    # Count tokens in a given text (optionally for a specific model)
    @abstractmethod
    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        pass
