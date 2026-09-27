import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.services.text_preprocessor import clean_text

class TFIDFMatcher:
    """
    Computes keyword-level relevance using Term Frequency - Inverse Document Frequency (TF-IDF)
    and Cosine Similarity.
    
    Formula:
    - TF(t, d) = (count of term t in document d) / (total words in document d)
    - IDF(t, D) = log( (1 + |D|) / (1 + df(t)) ) + 1
    - TF-IDF = TF * IDF
    - Cosine Similarity = (A . B) / (||A|| * ||B||)
    """

    def __init__(self, max_features: int = 5000):
        self.max_features = max_features

    def compute_similarity(self, job_text: str, resume_text: str) -> float:
        """
        Calculates cosine similarity between preprocessed job text and resume text.
        Returns float in range [0.0, 1.0].
        """
        if not job_text or not resume_text:
            return 0.0

        clean_job = clean_text(job_text, remove_stopwords=False)
        clean_resume = clean_text(resume_text, remove_stopwords=False)

        if not clean_job.strip() or not clean_resume.strip():
            return 0.0

        # Build TF-IDF representations
        vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=self.max_features,
            ngram_range=(1, 2)  # Unigrams and bigrams for phrases like 'machine learning', 'rest api'
        )

        try:
            tfidf_matrix = vectorizer.fit_transform([clean_job, clean_resume])
            # tfidf_matrix shape is (2, features)
            cos_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Ensure within [0.0, 1.0] bounds
            score = float(np.clip(cos_sim, 0.0, 1.0))
            return round(score, 4)
        except Exception:
            return 0.0
