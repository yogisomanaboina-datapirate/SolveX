import json
from typing import Any, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel
from openai import OpenAI
from core.config import settings
from core.errors import FeatherlessAPIError
from core.logging import logger

T = TypeVar("T", bound=BaseModel)


class FeatherlessClient:
    """
    OpenAI-compatible wrapper client for Featherless.ai API.
    """
    def __init__(self):
        self.api_key = settings.featherless_api_key
        self.base_url = settings.featherless_base_url
        self.model = settings.featherless_model
        self._client: Optional[OpenAI] = None

        if settings.is_featherless_configured:
            try:
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                logger.info(f"Initialized Featherless AI client with model '{self.model}' at '{self.base_url}'")
            except Exception as e:
                logger.error(f"Failed to initialize Featherless OpenAI client: {e}")
                self._client = None
        else:
            logger.warning("Featherless API key not provided or set to default. Running in mock/unconfigured mode.")

    @property
    def is_available(self) -> bool:
        """Return True if Featherless OpenAI client is initialized with valid credentials or explicitly using mock mode."""
        return self._client is not None or settings.use_mock_llm

    def generate_completion(
        self,
        prompt: str,
        system_prompt: str = "You are LifeLink AI, an expert healthcare coordination agent.",
        temperature: float = 0.2,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate raw text response from Featherless.ai model.
        """
        if settings.use_mock_llm or self._client is None:
            logger.info("Using mock completion response (Featherless not configured or mock mode enabled).")
            return f"[MOCK AI RESPONSE]: Analyzed request for '{prompt[:50]}...'. Recommendation: Proceed with healthcare coordination."

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content
            if not content:
                raise FeatherlessAPIError("Received empty response from Featherless API.")
            return content.strip()
        except Exception as e:
            logger.error(f"Featherless API completion call failed: {e}")
            raise FeatherlessAPIError(str(e))

    def generate_structured_json(
        self,
        prompt: str,
        system_prompt: str,
        response_model: Type[T],
        temperature: float = 0.1
    ) -> T:
        """
        Generate response from Featherless and parse into a target Pydantic schema model.
        Forces JSON format in system prompt.
        """
        if self._client is None:
            raise FeatherlessAPIError("Featherless client not initialized with valid API key. Falling back to domain heuristic engine.")

        json_system_prompt = (
            f"{system_prompt}\n\n"
            "IMPORTANT: You MUST respond ONLY with valid JSON matching the target schema. "
            "Do not include any markdown formatting, backticks, or introductory text."
        )

        raw_output = self.generate_completion(
            prompt=prompt,
            system_prompt=json_system_prompt,
            temperature=temperature
        )

        # Clean JSON fences if present
        clean_json = raw_output.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
        clean_json = clean_json.strip()

        try:
            data = json.loads(clean_json)
            return response_model.model_validate(data)
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to parse Featherless JSON response into {response_model.__name__}. Raw: {raw_output}")
            raise FeatherlessAPIError(
                message=f"Model output failed to parse into valid JSON for schema {response_model.__name__}",
                details={"raw_output": raw_output, "parse_error": str(e)}
            )

    def test_connection(self) -> Dict[str, Any]:
        """
        Development-only connectivity test function for Featherless API.
        Does NOT expose the API key in logs or outputs.
        """
        api_key_detected = settings.is_featherless_configured
        model_detected = bool(settings.featherless_model and settings.featherless_model.strip())

        if not api_key_detected:
            return {
                "success": False,
                "api_key_detected": False,
                "model_detected": model_detected,
                "model_used": settings.featherless_model,
                "error": "FEATHERLESS_API_KEY is not set or is using default placeholder in environment/.env file.",
                "ai_response": None
            }

        if not model_detected:
            return {
                "success": False,
                "api_key_detected": True,
                "model_detected": False,
                "model_used": "",
                "error": "FEATHERLESS_MODEL is empty in configuration.",
                "ai_response": None
            }

        if settings.use_mock_llm:
            return {
                "success": False,
                "api_key_detected": True,
                "model_detected": True,
                "model_used": settings.featherless_model,
                "error": "USE_MOCK_LLM is set to true. Set USE_MOCK_LLM=false to test live Featherless API connectivity.",
                "ai_response": None
            }

        try:
            client = OpenAI(
                api_key=settings.featherless_api_key,
                base_url=settings.featherless_base_url
            )
            logger.info(f"Initiating test Featherless chat completion call with model '{settings.featherless_model}'...")
            response = client.chat.completions.create(
                model=settings.featherless_model,
                messages=[
                    {"role": "system", "content": "You are a test assistant for LifeLink AI."},
                    {"role": "user", "content": "Hello Featherless, reply with 'CONNECTED' and your model status."}
                ],
                max_tokens=60,
                temperature=0.1
            )
            ai_output = response.choices[0].message.content
            if not ai_output:
                raise Exception("Received empty response content from Featherless.")
            
            logger.info("Featherless connection test succeeded!")
            return {
                "success": True,
                "api_key_detected": True,
                "model_detected": True,
                "model_used": settings.featherless_model,
                "ai_response": ai_output.strip(),
                "error": None
            }
        except Exception as e:
            logger.error(f"Featherless connection test failed: {e}")
            return {
                "success": False,
                "api_key_detected": True,
                "model_detected": True,
                "model_used": settings.featherless_model,
                "error": f"Featherless API Error: {str(e)}",
                "ai_response": None
            }


# Singleton Featherless client instance
featherless_client = FeatherlessClient()

