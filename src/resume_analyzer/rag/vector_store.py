from __future__ import annotations

import hashlib
import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr

from ai_agent_system.config import settings
from resume_analyzer.models import JobProfile


class DeterministicEmbeddings(Embeddings):
    """Local fallback embeddings so the app works without external API access."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    @staticmethod
    def _embed(text: str, dims: int = 32) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values = [digest[i % len(digest)] / 255.0 for i in range(dims)]
        return values


def _build_embedding_model() -> Embeddings:
    key = settings.openai_api_key.strip()
    if key and key.lower() not in {"replace-me", "changeme", "your-key-here"}:
        return OpenAIEmbeddings(api_key=SecretStr(key))
    return DeterministicEmbeddings()


class JobVectorStore:
    def __init__(self) -> None:
        self._store: Chroma | None = None
        self._fallback_docs: list[Document] = []
        self._ingested_ids: set[str] = set()
        self._init_store()

    @staticmethod
    def _resolve_persist_directory() -> Path:
        # Vercel serverless file system is read-only except /tmp.
        if os.getenv("VERCEL"):
            return Path("/tmp/chroma").resolve()
        return Path("data/chroma").resolve()

    def _init_store(self) -> None:
        persist_dir = self._resolve_persist_directory()
        try:
            persist_dir.mkdir(parents=True, exist_ok=True)
            self._store = Chroma(
                collection_name="jobs",
                embedding_function=_build_embedding_model(),
                persist_directory=str(persist_dir),
            )
        except Exception:
            # Keep app operational in constrained serverless environments.
            self._store = None

    @staticmethod
    def _job_to_doc(job: JobProfile) -> Document:
        skill_names = [s.get("name", "") for s in job.get("required_skills", [])]
        text = "\n".join(
            [
                job.get("title", ""),
                job.get("company", ""),
                job.get("raw_description", ""),
                "Required skills: " + ", ".join(skill_names),
            ]
        )
        return Document(
            page_content=text,
            metadata={
                "job_id": job.get("id", ""),
                "title": job.get("title", ""),
                "company": job.get("company", ""),
            },
        )

    def ingest_jobs(self, jobs: list[JobProfile]) -> None:
        docs = [self._job_to_doc(job) for job in jobs]
        incoming_ids = [doc.metadata.get("job_id", f"job_{idx}") for idx, doc in enumerate(docs)]

        pending_docs: list[Document] = []
        pending_ids: list[str] = []
        for doc, job_id in zip(docs, incoming_ids):
            if job_id in self._ingested_ids:
                continue
            pending_docs.append(doc)
            pending_ids.append(job_id)

        if not pending_docs:
            return

        if self._store is not None:
            try:
                self._store.add_documents(documents=pending_docs, ids=pending_ids)
                self._ingested_ids.update(pending_ids)
                return
            except Exception:
                # Continue with fallback corpus if vector backend rejects writes.
                self._store = None

        self._fallback_docs.extend(pending_docs)
        self._ingested_ids.update(pending_ids)

    def retrieve(self, query: str, k: int = 5) -> list[dict[str, object]]:
        if self._store is not None:
            docs = self._store.similarity_search(query, k=k)
        else:
            query_tokens = set(query.lower().split())
            ranked = sorted(
                self._fallback_docs,
                key=lambda doc: len(query_tokens.intersection(doc.page_content.lower().split())),
                reverse=True,
            )
            docs = ranked[:k]

        results: list[dict[str, object]] = []
        for idx, doc in enumerate(docs):
            rank_score = max(0.0, 1.0 - (idx / max(1, k)))
            results.append({
                "job_id": doc.metadata.get("job_id", ""),
                "title": doc.metadata.get("title", ""),
                "company": doc.metadata.get("company", ""),
                "relevance": float(rank_score),
                "content": doc.page_content,
            })
        return results


job_vector_store = JobVectorStore()
