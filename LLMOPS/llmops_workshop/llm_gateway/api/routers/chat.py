from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException
from core.models import ChatCompletionRequest, ChatCompletionResponse, Provider
from config import settings
from services import service_factory  
from api.dependencies import get_cache  

router = APIRouter()

@router.post("/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    background_tasks: BackgroundTasks,
    request: ChatCompletionRequest = Body(...),
    cache = Depends(get_cache)
):
    
    provider_name = request.provider or Provider(settings.DEFAULT_PROVIDER.lower())
    
    
    service = service_factory.get_service(provider_name)
    
    if not service:
        raise HTTPException(
            status_code=400,
            detail=f"Provider '{provider_name}' not available. Available providers: {service_factory.get_available_providers()}"
        )
    
    
        cache_key = f"chat:{provider_name}:{hash(str(request.dict()))}"
        cached_response = await cache.get(cache_key)
        if cached_response:
            return cached_response
    
    response = await service.get_chat_completion(request)
   
    if settings.ENABLE_CACHE and cache and not request.stream:
        background_tasks.add_task(
            cache.set, cache_key, response, expiry=settings.CACHE_EXPIRATION
        )
    
    return response
