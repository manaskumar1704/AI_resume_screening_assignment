import logging
import json
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

from app.config import settings

logger = logging.getLogger(__name__)


class ScorecardSchema(BaseModel):
    score: int = Field(..., ge=0, le=100)
    verdict: Literal["strong_match", "moderate_match", "weak_match"]
    missing_requirements: list[str]
    justification: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    match_percentages: dict[str, float]
    extracted_skills: list[str]


def load_prompt() -> str:
    prompt_path = (
        Path(__file__).parent.parent.parent / "prompts" / "resume_screening.md"
    )
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def get_llm():
    provider = settings.LLM_PROVIDER or "openai"
    model = settings.LLM_MODEL or "gpt-4o-mini"

    api_key = None
    if provider == "openai":
        api_key = settings.OPENAI_API_KEY
    elif provider == "anthropic":
        api_key = settings.ANTHROPIC_API_KEY
    elif provider == "groq":
        api_key = settings.GROQ_API_KEY

    return init_chat_model(
        model=model,
        model_provider=provider,
        api_key=api_key,
        temperature=0.1,
    )


def parse_json_fallback(response_text: str) -> ScorecardSchema:
    json_match = re.search(r"\{[\s\S]*\}", response_text)
    if json_match:
        data = json.loads(json_match.group())
        return ScorecardSchema(**data)
    raise ValueError("Could not parse JSON from response")


async def screen(resume_text: str, jd_text: str) -> ScorecardSchema:
    system_prompt = load_prompt()
    system_prompt_escaped = system_prompt.replace("{", "{{").replace("}", "}}")

    llm = get_llm()

    logger.info(
        f"Invoking LLM with provider={settings.LLM_PROVIDER}, model={settings.LLM_MODEL}"
    )

    try:
        prompt = ChatPromptTemplate.from_template(
            f"{system_prompt_escaped}\n\nResume:\n{{resume}}\n\nJob Description:\n{{jd}}"
        )

        formatted_prompt = await prompt.ainvoke({"resume": resume_text, "jd": jd_text})

        structured_llm = llm.with_structured_output(ScorecardSchema)
        response = await structured_llm.ainvoke(formatted_prompt)

        logger.info(
            f"LLM response (structured): score={response.score}, verdict={response.verdict}"
        )

        return response

    except Exception as e:
        logger.warning(f"Structured output failed: {e}, attempting fallback")

        try:
            prompt = ChatPromptTemplate.from_template(
                f"{system_prompt_escaped}\n\nResume:\n{{resume}}\n\nJob Description:\n{{jd}}"
            )

            formatted_prompt = await prompt.ainvoke(
                {"resume": resume_text, "jd": jd_text}
            )

            response_text = await llm.ainvoke(formatted_prompt)
            response_str = (
                response_text.content
                if hasattr(response_text, "content")
                else str(response_text)
            )

            logger.info(f"Fallback response text: {response_str[:200]}...")

            result = parse_json_fallback(response_str)
            logger.info(
                f"Fallback succeeded: score={result.score}, verdict={result.verdict}"
            )
            return result

        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {fallback_error}")
            raise ValueError(
                f"Both structured and fallback parsing failed: {fallback_error}"
            ) from fallback_error
