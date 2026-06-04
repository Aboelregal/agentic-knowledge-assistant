"""
qa_agent.py
-----------
The QA Agent is responsible for:
1. Receiving retrieved context from the Retrieval Agent
2. Constructing a well-structured prompt
3. Calling the Groq LLM (Llama 3) via LangChain
4. Returning a clear, grounded answer

This agent acts as the "reasoning" layer — it knows how to
think and answer but relies on the Retrieval Agent for facts.
"""

import logging
import os
from dataclasses import dataclass, field
from typing import List, Optional

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from agents.retrieval_agent import RetrievalResult

load_dotenv()
logger = logging.getLogger(__name__)

# System prompt that instructs the LLM to stay grounded in retrieved context
SYSTEM_PROMPT = """You are an expert AI Knowledge Assistant. Your role is to answer questions accurately based ONLY on the provided context from the knowledge base.

Guidelines:
- Answer based strictly on the provided context
- If the context doesn't contain enough information, clearly state that
- Be concise but thorough
- Cite which source documents you used in your answer
- Do not make up information or use knowledge outside the provided context
- Use a professional, helpful tone"""


@dataclass
class QAResult:
    """Structured output from the QA Agent."""

    question: str
    answer: str
    sources: List[str] = field(default_factory=list)
    chunks_used: int = 0
    model_used: str = ""
    status: str = "success"
    error: Optional[str] = None


class QAAgent:
    """
    Agent that generates answers using retrieved context and an LLM.

    Workflow:
    1. Receive a RetrievalResult with context and chunks
    2. Build a structured prompt (system + context + question)
    3. Call Groq's Llama 3 model via LangChain
    4. Return a QAResult with the answer and metadata
    """

    def __init__(
        self,
        model_name: str = "llama-3.1-8b-instant",
        temperature: float = 0.1,  # Low temp for factual, consistent answers
        max_tokens: int = 1024,
    ):
        """
        Args:
            model_name: Groq model identifier
            temperature: LLM temperature (0=deterministic, 1=creative)
            max_tokens: Maximum tokens in the response
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Please set it in your .env file."
            )

        self.model_name = model_name
        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        logger.info(f"QAAgent initialized with model: {model_name}")

    def _build_prompt(self, question: str, context: str) -> List:
        """
        Build the message list for the LLM call.

        Args:
            question: User's question
            context: Formatted context string from Retrieval Agent

        Returns:
            List of LangChain message objects
        """
        user_message = (
            f"Context from Knowledge Base:\n"
            f"{'=' * 50}\n"
            f"{context}\n"
            f"{'=' * 50}\n\n"
            f"Question: {question}\n\n"
            f"Please provide a clear, accurate answer based on the context above."
        )

        return [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

    def run(self, question: str, retrieval_result: RetrievalResult) -> QAResult:
        """
        Generate an answer based on retrieved context.

        Args:
            question: The user's question
            retrieval_result: Output from RetrievalAgent.run()

        Returns:
            QAResult with answer and metadata
        """
        logger.info(f"[QAAgent] Generating answer for: '{question}'")

        # Handle case where retrieval found nothing
        if retrieval_result.status == "no_results":
            return QAResult(
                question=question,
                answer=(
                    "I couldn't find relevant information in the knowledge base "
                    "to answer your question. Please make sure you've uploaded "
                    "documents related to your query."
                ),
                sources=[],
                chunks_used=0,
                model_used=self.model_name,
                status="no_context",
            )

        # Handle retrieval errors
        if retrieval_result.status == "error":
            return QAResult(
                question=question,
                answer="An error occurred while retrieving information. Please try again.",
                sources=[],
                chunks_used=0,
                model_used=self.model_name,
                status="error",
                error=retrieval_result.error,
            )

        try:
            # Build prompt with context
            messages = self._build_prompt(question, retrieval_result.context)

            # Call the LLM
            logger.info(f"[QAAgent] Calling {self.model_name} via Groq...")
            response = self.llm.invoke(messages)
            answer = response.content

            logger.info("[QAAgent] Answer generated successfully.")

            return QAResult(
                question=question,
                answer=answer,
                sources=retrieval_result.sources,
                chunks_used=retrieval_result.chunk_count,
                model_used=self.model_name,
                status="success",
            )

        except Exception as e:
            logger.error(f"[QAAgent] Error calling LLM: {e}", exc_info=True)
            return QAResult(
                question=question,
                answer="An error occurred while generating the answer. Please check your API key and try again.",
                sources=[],
                chunks_used=0,
                model_used=self.model_name,
                status="error",
                error=str(e),
            )
