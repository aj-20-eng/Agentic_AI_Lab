"""Azure model factory — one place to control which model each agent uses."""
import os
from functools import lru_cache

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv()

# Keyless auth: `az login` locally, managed identity in Foundry.
_token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default",
)

# Phase 1: one cheap model everywhere. In Phase 3 you split by setting the
# DEPLOY_* env vars (mini for triage/calendar, stronger for response).
_DEFAULT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4-mini")
_ROLE_DEPLOYMENTS = {
    "triage": os.getenv("DEPLOY_TRIAGE", _DEFAULT),
    "supervisor": os.getenv("DEPLOY_SUPERVISOR", _DEFAULT),
    "response": os.getenv("DEPLOY_RESPONSE", _DEFAULT),
    "calendar": os.getenv("DEPLOY_CALENDAR", _DEFAULT),
}


@lru_cache(maxsize=None)
def get_model(role: str = "response") -> AzureChatOpenAI:
    """Return a chat model for the given agent role.

    Note: gpt-5.x reasoning models reject `temperature`, so we don't set it.
    """
    return AzureChatOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_deployment=_ROLE_DEPLOYMENTS.get(role, _DEFAULT),
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        azure_ad_token_provider=_token_provider,
    )