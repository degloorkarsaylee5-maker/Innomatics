from typing import List


class PromptTemplates:
    @staticmethod
    def GetSystemPrompt() -> str:
        return (
            "You are a customer support assistant. "
            "Answer ONLY using the provided context. "
            "If the answer is not explicitly in the context, say: "
            "'I do not have enough information to answer that.' "
            "Do NOT hallucinate. Do NOT infer beyond context. "
            "Always be concise and factual."
        )

    @staticmethod
    def BuildRagPrompt(query: str, context_chunks: List[str]) -> str:
        context_block: str = "\n\n".join(context_chunks)

        return (
            f"Context:\n{context_block}\n\n"
            f"Question:\n{query}\n\n"
            "Instructions:\n"
            "- Use ONLY the context above\n"
            "- If unsure, say you don't know\n"
            "- Provide a direct answer\n"
        )