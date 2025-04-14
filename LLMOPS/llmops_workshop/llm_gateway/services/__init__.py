from typing import Dict, Optional
from core.models import Provider
from services.base import BaseLLMService
from config import settings


from services.ollama_service import OllamaService
class LLMServiceFactory:
    def __init__(self) -> None:
        self._services: Dict[Provider, BaseLLMService] = {}
        self._initialize_services()
        
    def _initialize_services(self) -> None:
        """
        Initialize the available LLM service implementations.
        Each provider-specific service instance is created and stored in the _services dict.
        """
        try:
            self._services[Provider.ollama] = OllamaService()
        except Exception as e:
            print(f"Error initializing OllamaService: {e}")
    def get_service(self, provider: Provider) -> Optional[BaseLLMService]:
        """
        Retrieve a service instance for the specified provider.
        """
        return self._services.get(provider)
    
    def get_default_service(self) -> Optional[BaseLLMService]:
        """
        Retrieve the default service instance based on application settings.
        """
        default_provider = Provider(settings.DEFAULT_PROVIDER.lower())
        return self.get_service(default_provider)
    
    def get_fallback_service(self, primary_provider: Provider) -> Optional[BaseLLMService]:
        """
        Select an alternative service for fallback.
        This example returns the first available provider that is not the primary.
        More complex logic (e.g., cost-based selection) can be implemented here.
        """
        for provider, service in self._services.items():
            if provider != primary_provider:
                return service
        return None
    
