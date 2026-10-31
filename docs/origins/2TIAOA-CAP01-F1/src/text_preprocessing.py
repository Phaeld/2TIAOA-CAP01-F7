# initialize nltk resources (only need to run once)
import nltk

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

# init of model preprocessing script
import os
import re
import string

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

RAW_TEXT_DIR = "data/raw/texts"
PROC_TEXT_DIR = "data/processed/texts"

EN_STOPWORDS = set(stopwords.words("english"))


def basic_clean(text: str) -> str:
    """
    Basic cleaning:
    - removes all lowercase letters
    - removes multiple spaces
    - removes extraneous characters 
    """

    text = text.lower()

    
    text = re.sub(r"[\r\t\f\v]", " ", text)

    
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def remove_references_section(text: str) -> str:
    """
    Remove seção de referências, se existir.
    Procura por 'references' ou 'bibliography' no final do artigo.
    Isso é opcional, mas costuma deixar o texto mais limpo.
    """
    pattern = r"(references|bibliography)\s*[:\n].*"
    return re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)


def tokenize_and_filter(text: str) -> str:
    """
    - tokenize
    - remove punctuation
    - remove stopwords
    - remove very short tokens
    """
    
    tokens = word_tokenize(text)

    
    table = str.maketrans("", "", string.punctuation)

    cleaned_tokens = []
    for token in tokens:
        
        token = token.translate(table)

        if not token:
            continue

        if token.isdigit():
            continue

        if token in EN_STOPWORDS:
            continue

        if len(token) <= 2:
            continue

        cleaned_tokens.append(token)

    return " ".join(cleaned_tokens)


def clean_text_pipeline(text: str) -> str:
    """
    Complete Text Cleaning Pipeline:
    1. Basic Cleaning
    2. Removal of References Section
    3. Tokenization + Stopword/Punctuation Removal
    """
    text = basic_clean(text)
    text = remove_references_section(text)
    text = tokenize_and_filter(text)
    return text


def process_all_texts(
    raw_dir: str = RAW_TEXT_DIR,
    out_dir: str = PROC_TEXT_DIR,
) -> None:
    """
    Reads all .txt files in raw_dir, applies the cleanup
    and saves the result in out_dir with the same filename.
    """
    os.makedirs(out_dir, exist_ok=True)

    files = [f for f in os.listdir(raw_dir) if f.lower().endswith(".txt")]

    if not files:
        print(f"Nenhum .txt encontrado em {raw_dir}")
        return

    for filename in files:
        in_path = os.path.join(raw_dir, filename)
        out_path = os.path.join(
            out_dir,
            filename.replace("_raw", "").replace("_bruto", "").replace(".txt", "_clean.txt"),
        )

        print(f"Processando: {in_path} -> {out_path}")

        with open(in_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()

        cleaned_text = clean_text_pipeline(raw_text)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

    print("Processamento concluído!")


if __name__ == "__main__":
    process_all_texts()