from synthbench.providers.base import (
    Distribution,
    PersonaSpec,
    Provider,
    ProviderError,
    Response,
)

PROVIDERS: dict[str, str] = {
    "raw-anthropic": "synthbench.providers.raw_anthropic:RawAnthropicProvider",
    "raw-openai": "synthbench.providers.raw_openai:RawOpenAIProvider",
    "raw-gemini": "synthbench.providers.raw_gemini:RawGeminiProvider",
    "aana-openrouter": "synthbench.providers.aana_openrouter:AANAOpenRouterProvider",
    "openrouter": "synthbench.providers.openrouter:OpenRouterProvider",
    "ollama": "synthbench.providers.ollama:OllamaProvider",
    "althing": "synthbench.providers.althing:AlthingProvider",
    # Deprecated alias — synthpanel was renamed to althing (2026-07). Kept so
    # existing configs and `--provider synthpanel` invocations keep working;
    # leaderboard-results/ entries recorded under the old id remain valid.
    "synthpanel": "synthbench.providers.althing:AlthingProvider",
    "http": "synthbench.providers.http:HttpProvider",
    "random": "synthbench.providers.random_baseline:RandomBaselineProvider",
    "majority": "synthbench.providers.majority_baseline:MajorityBaselineProvider",
    "population-average": "synthbench.providers.population_baseline:PopulationAverageBaselineProvider",
}


def load_provider(name: str, **kwargs) -> Provider:
    """Load a provider by name. Raises KeyError if not found."""
    if name not in PROVIDERS:
        raise KeyError(f"Unknown provider '{name}'. Available: {list(PROVIDERS)}")
    module_path, class_name = PROVIDERS[name].rsplit(":", 1)
    import importlib

    mod = importlib.import_module(module_path)
    cls = getattr(mod, class_name)
    return cls(**kwargs)


__all__ = [
    "Distribution",
    "PersonaSpec",
    "Provider",
    "ProviderError",
    "Response",
    "PROVIDERS",
    "load_provider",
]
