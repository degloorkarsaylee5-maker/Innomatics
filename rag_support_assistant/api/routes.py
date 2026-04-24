from fastapi import APIRouter, Depends

from api.schemas import QueryRequest, QueryResponse, SourceItem
from graph.workflow import SupportWorkflow
from vector_store.chroma_client import ChromaClient
from vector_store.retriever import Retriever
from utils.logger import GetLogger


router = APIRouter()
_logger = GetLogger("APIRoutes")

# Initialize shared components (singleton-style at module load)
_chroma_client = ChromaClient(collection_name="support_collection")
_retriever = Retriever(_chroma_client)
_workflow = SupportWorkflow(_retriever).Build()


def GetWorkflow():
    return _workflow


@router.post("/query", response_model=QueryResponse)
async def QueryEndpoint(
    request: QueryRequest,
    workflow=Depends(GetWorkflow)
) -> QueryResponse:

    try:
        # Initialize graph state as a plain dict (LangGraph requirement)
        initial_state = {"query": request.query}

        # Execute LangGraph workflow
        result = workflow.invoke(initial_state)

        sources = [
            SourceItem(
                chunk_id=s.get("chunk_id", ""),
                score=s.get("score", 0.0),
                page_number=s.get("page_number")
            )
            for s in result.get("sources", [])
        ]

        response = QueryResponse(
            answer=result.get("answer", ""),
            confidence=result.get("confidence_score", 0.0),
            sources=sources,
            escalated=result.get("escalation_flag", False)
        )

        _logger.info(
            "Query processed",
            extra={
                "confidence": response.confidence,
                "escalated": response.escalated
            }
        )

        return response

    except Exception as ex:
        _logger.error("Query processing failed", exc_info=True)
        raise