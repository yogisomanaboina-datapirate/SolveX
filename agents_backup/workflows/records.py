from core.logging import logger
from agents.records.report_agent import medical_report_agent
from agents.records.schemas import ReportAnalyzerRequest, ReportAnalyzerResponse


def run_report_analyzer_workflow(request: ReportAnalyzerRequest) -> ReportAnalyzerResponse:
    """
    Execute Medical Report Analyzer Workflow.
    Parses supplied report text, extracts lab/clinical parameters, and invokes Featherless AI for structured insights.
    """
    logger.info("Executing Medical Report Analyzer Workflow...")
    response = medical_report_agent.analyze_report(request)
    logger.info(f"Report Analyzer Workflow Completed -> Type: {response.report_type}, Findings Count: {len(response.key_findings)}")
    return response
