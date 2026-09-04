from core.logging import logger
from agents.chat.chatbot_agent import chatbot_agent
from agents.chat.schemas import ChatbotRequest, ChatbotResponse


def run_chatbot_workflow(request: ChatbotRequest) -> ChatbotResponse:
    """
    Execute LifeLink AI Chatbot Workflow.
    Parses user query, integrates optional patient profile context, and invokes HuggingFace/Featherless AI for response.
    """
    logger.info("Executing LifeLink AI Chatbot Workflow...")
    response = chatbot_agent.chat(request)
    logger.info(f"Chatbot Workflow Completed -> Intent: {response.intent}, Response Length: {len(response.message)}")
    return response
