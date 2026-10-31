
from agents import Agent, handoff
from pipeline_context import PipelineContext

from risk_agent import risk_agent
from protocol_specialist import protocol_specialist
from planner_agent import planner_agent


# Etapa 1: o analista calcula o risco e transfere o controle.
risk_agent.instructions = (
    "You are the CardioIA risk analysis specialist. "
    "Use the analyze_risk tool to obtain the prediction from the "
    "trained machine learning model. Never invent or modify numerical results. "
    "After the tool returns successfully, hand off control to the "
    "Protocol Specialist Agent. Do not finish the workflow yourself."
)

risk_agent.handoffs = [
    handoff(
        agent=protocol_specialist,
        tool_name_override="transfer_to_protocol_specialist",
        tool_description_override=(
            "Transfer control after obtaining the machine learning prediction."
        ),
    )
]


# Etapa 2: o especialista consulta os protocolos e transfere o controle.
protocol_specialist.instructions = (
    "You are the CardioIA simulated protocol specialist. "
    "Use analyze_protocols to retrieve the protocols selected by the "
    "existing rule-based engine. Do not invent additional protocols. "
    "After the tool returns successfully, hand off control to the "
    "Response Planning Agent."
)

protocol_specialist.handoffs = [
    handoff(
        agent=planner_agent,
        tool_name_override="transfer_to_response_planner",
        tool_description_override=(
            "Transfer control after completing the simulated protocol analysis."
        ),
    )
]


# Etapa 3: o orquestrador inicia o fluxo.
orchestrator = Agent[PipelineContext](
    name="CardioIA Orchestrator",
    instructions=(
        "You coordinate the CardioIA multi-agent workflow. "
        "Immediately transfer control to the Risk Analysis Agent. "
        "Do not calculate risk yourself or invent patient data. "
        "The specialist agents must perform their own tasks and handoffs."
    ),
    handoffs=[
        handoff(
            agent=risk_agent,
            tool_name_override="transfer_to_risk_agent",
            tool_description_override=(
                "Start the workflow by sending the case to the risk analysis agent."
            ),
        )
    ],
)
