"""Phase-two TF-IDF classifier and phase-one corpus retrieval."""
import csv
import re
import unicodedata

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics.pairwise import cosine_similarity

from ..config import ASSETS, DISCLAIMER


def normalize(text):
    return "".join(c for c in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(c) != "Mn")


class TextService:
    def __init__(self):
        with (ASSETS / "dados_risco.csv").open(encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        # The phase-two notebook did not export a model; recreate its logistic
        # regression pipeline from the committed 50 examples, not from mock rules.
        self.model = make_pipeline(TfidfVectorizer(strip_accents="unicode"), LogisticRegression(random_state=42))
        self.model.fit([r["frase"] for r in rows], [r["situacao"] for r in rows])
        with (ASSETS / "mapa_doencas.csv").open(encoding="utf-8-sig") as f:
            self.map = list(csv.DictReader(f))
        self.corpus = []
        for path in sorted((ASSETS / "knowledge").glob("*.txt")):
            words = path.read_text().split()
            for i in range(0, len(words), 120):
                self.corpus.append({"source": path.name, "excerpt": " ".join(words[i:i+160])})
        self.retriever = TfidfVectorizer(strip_accents="unicode")
        self.matrix = self.retriever.fit_transform([p["excerpt"] for p in self.corpus])

    def analyze(self, message):
        probabilities = self.model.predict_proba([message])[0]
        words = set(re.findall(r"\w+", normalize(message)))
        matches = []
        for row in self.map:
            for key in ("Sintoma1", "Sintoma2"):
                phrase = row[key]
                if set(normalize(phrase).split()) <= words:
                    matches.append(phrase)
        return {
            "label": str(self.model.predict([message])[0]),
            "scores": {str(k): round(float(v), 4) for k, v in zip(self.model.classes_, probabilities)},
            "matched_symptoms": sorted(set(matches)),
            "source": "phase2_tfidf_logistic_regression", "training_examples": 50,
            "limitations": "Base didática pequena; sem validação clínica. Negação e contexto podem ser interpretados incorretamente.",
            "disclaimer": DISCLAIMER,
        }

    def retrieve(self, message):
        scores = cosine_similarity(self.retriever.transform([message]), self.matrix)[0]
        indices = scores.argsort()[::-1][:2]
        return [{**self.corpus[int(i)], "similarity": round(float(scores[i]), 4)} for i in indices if scores[i] > 0.05]
