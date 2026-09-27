import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from backend.services.text_preprocessor import clean_text

logger = logging.getLogger(__name__)

class SemanticMatcher:
    """
    Computes semantic similarity using Sentence Transformers (all-MiniLM-L6-v2).
    Generates 384-dimensional dense embeddings to capture contextual meanings
    (e.g., matching 'predictive modeling' with 'machine learning').
    
    Includes lazy-loading and resilient fallback if heavy dependencies or network models
    are still warming up.
    """

    _model = None
    _model_loaded = False
    _model_load_attempted = False

    @classmethod
    def get_model(cls):
        """Lazy-load the SentenceTransformer model to optimize server startup time."""
        import os
        from flask import current_app

        use_fast = False
        try:
            if current_app and current_app.config.get("USE_FAST_EMBEDDINGS"):
                use_fast = True
        except Exception:
            pass

        if use_fast or os.environ.get("TESTING") == "1" or os.environ.get("USE_FAST_EMBEDDINGS") == "1":
            return None

        if not cls._model_load_attempted:
            cls._model_load_attempted = True
            try:
                from sentence_transformers import SentenceTransformer
                logger.info("Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
                cls._model = SentenceTransformer("all-MiniLM-L6-v2")
                cls._model_loaded = True
                logger.info("SentenceTransformer model successfully loaded.")
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer ('all-MiniLM-L6-v2'): {e}. Using resilient semantic fallback.")
                cls._model = None
                cls._model_loaded = False
        return cls._model

    def compute_similarity(self, job_text: str, resume_text: str) -> float:
        """
        Compute contextual cosine similarity between job description and resume.
        Returns float in range [0.0, 1.0].
        """
        if not job_text or not resume_text:
            return 0.0

        clean_job = clean_text(job_text)
        clean_resume = clean_text(resume_text)

        if not clean_job.strip() or not clean_resume.strip():
            return 0.0

        model = self.get_model()

        if model is not None:
            try:
                # Chunk texts into sections if long to avoid 512 token truncation clipping
                # Sentence transformers work best on paragraph/sentence sized inputs
                job_chunks = [c.strip() for c in clean_job.split("\n") if len(c.strip()) > 15] or [clean_job]
                resume_chunks = [c.strip() for c in clean_resume.split("\n") if len(c.strip()) > 15] or [clean_resume]

                # If single large blocks, chunk by words
                if len(job_chunks) == 1 and len(clean_job.split()) > 150:
                    words = clean_job.split()
                    job_chunks = [" ".join(words[i:i+100]) for i in range(0, min(len(words), 400), 100)]
                
                if len(resume_chunks) == 1 and len(clean_resume.split()) > 150:
                    words = clean_resume.split()
                    resume_chunks = [" ".join(words[i:i+100]) for i in range(0, min(len(words), 400), 100)]

                # Compute mean embeddings
                job_embeddings = model.encode(job_chunks, convert_to_numpy=True, normalize_embeddings=True)
                resume_embeddings = model.encode(resume_chunks, convert_to_numpy=True, normalize_embeddings=True)

                job_vec = np.mean(job_embeddings, axis=0, keepdims=True)
                resume_vec = np.mean(resume_embeddings, axis=0, keepdims=True)

                sim = cosine_similarity(job_vec, resume_vec)[0][0]
                return round(float(np.clip(sim, 0.0, 1.0)), 4)
            except Exception as e:
                logger.error(f"Error during SentenceTransformer inference: {e}. Falling back.")

        # Resilient fallback: character n-gram + word n-gram dense semantic approximation
        return self._fallback_semantic_similarity(clean_job, clean_resume)

    @staticmethod
    def _fallback_semantic_similarity(text1: str, text2: str) -> float:
        """
        Lightweight dense n-gram semantic approximation used as safety fallback.
        Calculates character-level and sub-word cosine similarity to approximate semantic overlap.
        """
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), max_features=10000)
        try:
            mat = vectorizer.fit_transform([text1, text2])
            sim = cosine_similarity(mat[0:1], mat[1:2])[0][0]
            return round(float(np.clip(sim, 0.0, 1.0)), 4)
        except Exception:
            return 0.0
