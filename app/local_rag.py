import os
from pathlib import Path
import requests
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
INDEX_DIR = DATA_DIR / "index"
MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")

class LocalRAG:
    def __init__(self):
        self.encoder = None
        self.index = None
        self.chunks = []
        self._load_index()

    def _encoder(self):
        if self.encoder is None:
            self.encoder = SentenceTransformer(MODEL_NAME, device="cpu")
        return self.encoder

    def _load_index(self):
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        meta, idx = INDEX_DIR / "chunks.json", INDEX_DIR / "vectors.faiss"
        if meta.exists() and idx.exists():
            import json
            self.chunks = json.loads(meta.read_text(encoding="utf-8"))
            self.index = faiss.read_index(str(idx))

    def _save(self):
        import json
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        (INDEX_DIR / "chunks.json").write_text(json.dumps(self.chunks, ensure_ascii=False, indent=2), encoding="utf-8")
        if self.index is not None:
            faiss.write_index(self.index, str(INDEX_DIR / "vectors.faiss"))

    def add_text(self, text: str, source: str):
        text = text.strip()
        if not text:
            raise ValueError("Document text is empty")
        pieces = [text[i:i+900] for i in range(0, len(text), 750)]
        vectors = np.asarray(self._encoder().encode(pieces, normalize_embeddings=True), dtype="float32")
        if self.index is None:
            self.index = faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)
        self.chunks.extend([{"text": p, "source": source} for p in pieces])
        self._save()
        return len(pieces)

    def add_pdf(self, path: str):
        reader = PdfReader(path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return self.add_text(text, Path(path).name)

    def retrieve(self, question: str, k: int = 4):
        if self.index is None or not self.chunks:
            return []
        vector = np.asarray(self._encoder().encode([question], normalize_embeddings=True), dtype="float32")
        scores, ids = self.index.search(vector, min(k, len(self.chunks)))
        return [{"score": float(score), **self.chunks[int(i)]} for score, i in zip(scores[0], ids[0]) if i >= 0]

    def answer(self, question: str, k: int = 4):
        hits = self.retrieve(question, k)
        if not hits:
            return {"answer": "No local evidence found. Add documents first.", "sources": [], "mode": "local-rag"}
        context = "\n\n".join(f"[{i+1}] Source: {h['source']}\n{h['text']}" for i, h in enumerate(hits))
        prompt = ("Answer using only the evidence below. If insufficient, say so. Cite claims as [1], [2]. "
                  "Do not invent sources.\n\nEvidence:\n" + context + "\n\nQuestion: " + question + "\nAnswer:")
        response = requests.post(
            OLLAMA_URL.rstrip("/") + "/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.1, "num_ctx": 3072}},
            timeout=180,
        )
        response.raise_for_status()
        return {"answer": response.json().get("response", ""), "sources": hits, "mode": "local-rag", "model": OLLAMA_MODEL}
