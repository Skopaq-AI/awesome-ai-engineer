from pydantic_settings import BaseSettings
from typing import Dict, List, Optional

class GatewaySettings(BaseSettings):
    app_name: str = "Enterprise AI Gateway"
    env: str = "production"
    port: int = 8000
    host: str = "0.0.0.0"
    
    # Routing thresholds (in tokens or complexity scores)
    fast_model: str = "gpt-4o-mini"
    strong_model: str = "gpt-4o"
    reasoning_model: str = "deepseek-r1"
    
    # Rate Limiter defaults
    default_rate_limit_rpm: int = 600
    default_token_limit_tpm: int = 100000
    
    # Cache settings
    enable_cache: bool = True
    cache_ttl_seconds: int = 3600
    
    # Cost per 1M tokens (USD)
    model_pricing: Dict[str, Dict[str, float]] = {
        "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
        "gpt-4o": {"prompt": 2.50, "completion": 10.00},
        "claude-3-5-sonnet": {"prompt": 3.00, "completion": 15.00},
        "deepseek-r1": {"prompt": 0.55, "completion": 2.19},
        "gemma-2-9b": {"prompt": 0.10, "completion": 0.10}
    }
    
    # Mock upstream API keys for testing/local run
    openai_api_key: Optional[str] = "mock-key"
    anthropic_api_key: Optional[str] = "mock-key"

settings = GatewaySettings()
