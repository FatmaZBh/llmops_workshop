import os
import time
from typing import Any, Dict, List, Optional, Union

import ollama
from tenacity import retry, wait_fixed, stop_after_attempt

from core.models import (
    Provider,
    ChatCompletionRequest,
    ChatCompletionResponse,
    TextEmbeddingRequest,
    TextEmbeddingResponse,
    ModelInfo,
    Message,
    Choice,
    Usage,
)
from services.base import BaseLLMService


class OllamaService(BaseLLMService):
    """
    Ollama service implementation that adheres to the BaseLLMService interface.
    This service handles interactions with the Ollama API for chat completions,
    text embeddings, model listings, and other functionalities.
    """
    provider: Provider = Provider.ollama

    def __init__(self) -> None:
        # Initialize the Ollama client using the host URL.
        # Use the OLLAMA_HOST environment variable, defaulting to "http://localhost:11434".
        host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.client = ollama.Client(host=host)

    @retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
    async def get_chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        # Convert the standardized request into Ollama's expected parameters.
        ollama_request = self.convert_request(request)
        try:
            # Call Ollama's asynchronous chat completion endpoint.
            response = await self.client.chat_completion(**ollama_request)
        except Exception as e:
            raise Exception(f"Ollama chat completion error: {str(e)}")
        # Convert Ollama's response back into our standardized format.
        standardized_response = self.convert_response(response, "chat")
        return standardized_response

    @retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
    async def get_embeddings(self, request: TextEmbeddingRequest) -> TextEmbeddingResponse:
        ollama_request = self.convert_request(request)
        try:
            response = await self.client.embedding(**ollama_request)
        except Exception as e:
            raise Exception(f"Ollama embeddings error: {str(e)}")
        standardized_response = self.convert_response(response, "embeddings")
        return standardized_response

    async def list_models(self) -> List[ModelInfo]:
        try:
            models_response = await self.client.list_models()
        except Exception as e:
            raise Exception(f"Ollama list models error: {str(e)}")
        models = []
        for model in models_response.get("data", []):
            models.append(ModelInfo(
                id=model.get("id"),
                name=model.get("name", model.get("id")),
                description=model.get("description"),
                capabilities=["chat", "embeddings"]
            ))
        return models

    async def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        try:
            model_response = await self.client.get_model_info(model_id)
        except Exception as e:
            # If an error occurs or the model isn't found, return None.
            return None
        if model_response:
            return ModelInfo(
                id=model_response.get("id"),
                name=model_response.get("name", model_response.get("id")),
                description=model_response.get("description"),
                capabilities=["chat", "embeddings"]
            )
        return None

    async def health_check(self) -> bool:
        try:
            # Simple health check by attempting to list models.
            await self.list_models()
            return True
        except Exception:
            return False

    def convert_request(self, request: Union[ChatCompletionRequest, TextEmbeddingRequest]) -> Dict[str, Any]:
        if isinstance(request, ChatCompletionRequest):
            # Map our standardized chat request to Ollama's expected format.
            ollama_messages = [{"role": m.role, "content": m.content} for m in request.messages]
            return {
                "model": request.model,
                "messages": ollama_messages,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
            }
        elif isinstance(request, TextEmbeddingRequest):
            return {
                "model": request.model,
                "input": request.input
            }
        else:
            raise ValueError("Unsupported request type for Ollama conversion")

    def convert_response(self, response: Any, request_type: str) -> Union[ChatCompletionResponse, TextEmbeddingResponse]:
        if request_type == "chat":
            choices = []
            # Process each choice from the Ollama response.
            for choice in response.get("choices", []):
                msg = choice.get("message", {})
                choices.append(Choice(
                    index=choice.get("index"),
                    message=Message(
                        role=msg.get("role", "assistant"),
                        content=msg.get("content", "")
                    ),
                    finish_reason=choice.get("finish_reason")
                ))
            usage = None
            if response.get("usage"):
                usage = Usage(
                    prompt_tokens=response["usage"].get("prompt_tokens", 0),
                    completion_tokens=response["usage"].get("completion_tokens", 0),
                    total_tokens=response["usage"].get("total_tokens", 0)
                )
            return ChatCompletionResponse(
                id=response.get("id"),
                object="chat.completion",
                created=response.get("created", int(time.time())),
                model=response.get("model"),
                choices=choices,
                usage=usage,
                provider=self.provider,
            )
        elif request_type == "embeddings":
            data = response.get("data", [])
            if data and len(data) > 0:
                embedding_data = data[0]
                return TextEmbeddingResponse(
                    model=response.get("model"),
                    embedding=embedding_data.get("embedding"),
                    provider=self.provider
                )
            else:
                raise ValueError("Invalid embeddings response from Ollama")
        else:
            raise ValueError("Unsupported request type for conversion")

    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        # Basic token counting by splitting text on whitespace.
        return len(text.split())
