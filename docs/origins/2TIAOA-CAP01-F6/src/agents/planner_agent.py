"""
CardioIA - Response Planning Agent
Consolida previsão de risco e protocolos em uma recomendação final.
"""

from agents import Agent, RunContextWrapper, function_tool

from pipeline_context import PipelineContext
from response_schema import FinalRecommendation, ProtocolSuggestion


@function_tool
def get_pipeline_results(ctx: RunContextWrapper[PipelineContext]) -> dict:
    """Retrieve the actual prediction and protocol analysis results."""
    context = ctx.context

    if not context.ml_result:
        raise ValueError("The risk prediction is missing.")

    if not context.protocol_result:
        raise ValueError("The protocol analysis is missing.")

    return {
        "prediction": context.ml_result,
        "protocol_analysis": context.protocol_result,
    }


@function_tool
def build_final_recommendation(
    ctx: RunContextWrapper[PipelineContext],
    summary: str,
) -> dict:
    """
    Build and validate the final structured recommendation.

    Use only values already stored in the shared context. The summary must
    describe the synthetic operational analysis without inventing numbers.
    """
    context = ctx.context

    if not context.ml_result or not context.protocol_result:
        raise ValueError(
            "Prediction and protocol analysis must exist before building "
            "the final recommendation."
        )

    protocols = [
        ProtocolSuggestion(
            protocol_id=item["id"],
            action=item["action"],
        )
        for item in context.protocol_result.get("suggested_protocols", [])
    ]

    recommendation = FinalRecommendation(
        predicted_class=int(context.ml_result["predicted_class"]),
        risk_probability=float(context.ml_result["risk_probability"]),
        risk_level=str(context.ml_result["risk_level"]),
        suggested_protocols=protocols,
        summary=summary.strip(),
    )

    # Guarda a recomendação validada no contexto compartilhado.
    context.final_recommendation = recommendation.model_dump()

    return context.final_recommendation


planner_agent = Agent[PipelineContext](
    name="Response Planning Agent",
    instructions=(
        "You are the response planning specialist for CardioIA, an academic "
        "prototype that analyzes synthetic operational cardiac-risk data. "
        "First, call get_pipeline_results to retrieve the real model prediction "
        "and the protocol engine results. "
        "Then call build_final_recommendation with a concise operational summary "
        "based only on those results. "
        "Copy predicted_class, risk_probability and risk_level from the prediction "
        "without changing their values. "
        "Copy the protocol identifiers and actions from protocol_analysis. "
        "Do not invent probabilities, classifications, protocols or actions. "
        "Write the summary in Portuguese. "
        "After build_final_recommendation succeeds, briefly confirm in "
        "Portuguese that the final recommendation was created. "
        "This is a simulation, not a clinical diagnosis or medical advice."
    ),
    tools=[get_pipeline_results, build_final_recommendation],
)
