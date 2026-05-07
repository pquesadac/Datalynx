import re
import unicodedata
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Se intenta cargar el modelo en español; si no está instalado,
# se usa el inglés como fallback para la demo.
try:
    import spacy
    try:
        nlp = spacy.load("es_core_news_sm")
        _SPACY_AVAILABLE = True
    except OSError:
        try:
            nlp = spacy.load("en_core_web_sm")
            _SPACY_AVAILABLE = True
        except OSError:
            nlp = None
            _SPACY_AVAILABLE = False
except ImportError:
    nlp = None
    _SPACY_AVAILABLE = False



SKILLS_DATABASE: Dict[str, List[str]] = {
    "lenguajes": [
        "python", "java", "javascript", "typescript", "r", "scala", "c++", "c#", "go", "rust", "php"
    ],
    "machine_learning": [
        "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn",
        "keras", "xgboost", "mlflow", "mlops"
    ],
    "nlp": [
        "nlp", "spacy", "nltk", "transformers", "bert", "gpt",
        "procesamiento de lenguaje natural", "hugging face"
    ],
    "data_analysis": [
        "pandas", "numpy", "estadística", "scipy", "matplotlib",
        "seaborn", "plotly", "analisis de datos"
    ],
    "visualizacion": [
        "power bi", "tableau", "streamlit", "dash", "looker", "metabase"
    ],
    "bases_de_datos": [
        "sql", "mysql", "postgresql", "mongodb", "redis",
        "elasticsearch", "oracle", "sqlite", "cassandra"
    ],
    "cloud_devops": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
        "terraform", "ansible", "jenkins", "ci/cd", "git"
    ],
    "big_data": [
        "spark", "hadoop", "kafka", "airflow", "databricks",
        "hive", "flink", "dbt"
    ],
    "web_backend": [
        "fastapi", "django", "flask", "rest api", "graphql",
        "rabbitmq", "celery", "nginx"
    ],
    "soft_skills": [
        "liderazgo", "trabajo en equipo", "comunicacion",
        "gestion de proyectos", "agile", "scrum", "kanban"
    ],
}

ALL_SKILLS: List[str] = [
    skill for category in SKILLS_DATABASE.values() for skill in category
]



def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text



def extract_skills(cv_text: str) -> List[str]:
    """
    Extrae las habilidades técnicas presentes en el texto del CV
    comparando contra el catálogo SKILLS_DATABASE mediante búsqueda
    de subcadenas normalizadas.

    Retorna: lista de habilidades detectadas (sin duplicados).
    """
    normalized_cv = normalize_text(cv_text)
    found: List[str] = []

    for skill in ALL_SKILLS:
        skill_norm = normalize_text(skill)
        pattern = r"\b" + re.escape(skill_norm) + r"\b"
        if re.search(pattern, normalized_cv):
            found.append(skill)

    return list(dict.fromkeys(found))  



def extract_years_experience(cv_text: str) -> int:
    """
    Se estima los años de experiencia del candidato usando dos estrategias:
    1. Búsqueda de menciones explícitas: '5 años de experiencia'
    2. Suma de rangos temporales: '2019 - 2023' → 4 años

    Retorna: número de años (máximo 20 para normalizar outliers).
    """
    text_lower = cv_text.lower()

    # Estrategia 1: menciones explícitas
    explicit_patterns = [
        r"(\d+)\s*a[ñn]os?\s*de\s*experiencia",
        r"experiencia\s*de\s*(\d+)\s*a[ñn]os?",
        r"(\d+)\s*a[ñn]os?\s*de\s*trayectoria",
    ]
    for pattern in explicit_patterns:
        matches = re.findall(pattern, text_lower)
        if matches:
            return min(max(int(m) for m in matches), 20)

    # Estrategia 2: rangos de fechas (ej: "2019 - 2023" o "2021 - actualidad")
    date_range_pattern = r"(\d{4})\s*[-–—]\s*(\d{4}|actualidad|presente|hoy|actual)"
    ranges = re.findall(date_range_pattern, text_lower)
    total = 0
    for start, end in ranges:
        start_year = int(start)
        end_year = 2024 if end in {"actualidad", "presente", "hoy", "actual"} else int(end)
        total += max(0, end_year - start_year)

    return min(total, 20)



def anonymize_cv(cv_text: str, candidate_id: int) -> Dict:
    """
    Se eliminalos datos personales del CV para garantizar
    un proceso de selección libre de sesgos y conforme al RGPD.

    Usa spaCy para detectar nombres (entidades PER/PERSON) y regex
    para emails, teléfonos y edades.

    Retorna: dict con el ID anónimo y el texto anonimizado.
    """
    anonymized = cv_text
    alias = f"CANDIDATO_{candidate_id:03d}"

    if _SPACY_AVAILABLE and nlp is not None:
        doc = nlp(cv_text[:5000])  
        for ent in sorted(doc.ents, key=lambda e: -e.start_char):
            if ent.label_ in {"PER", "PERSON"}:
                anonymized = anonymized[: ent.start_char] + f"[{alias}]" + anonymized[ent.end_char :]

    anonymized = re.sub(
        r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",
        "[EMAIL_OCULTO]",
        anonymized,
    )

    anonymized = re.sub(
        r"\b(\+34\s?|0034\s?)?[6-9]\d{2}[\s.\-]?\d{3}[\s.\-]?\d{3}\b",
        "[TELÉFONO_OCULTO]",
        anonymized,
    )

    anonymized = re.sub(
        r"\b\d{2}\s*a[ñn]os?\b",
        "[EDAD_OCULTA]",
        anonymized,
        flags=re.IGNORECASE,
    )

    return {
        "candidato_id": alias,
        "texto_anonimizado": anonymized,
    }



def score_candidate(
    cv_text: str,
    job_description: str,
    required_skills: List[str],
) -> Dict:
    """
    Puntúa a un candidato en base a tres criterios ponderados:

    ┌─────────────────────────────────────┬────────┐
    │ Criterio                            │  Peso  │
    ├─────────────────────────────────────┼────────┤
    │ Coincidencia de habilidades         │  45 %  │
    │ Similitud semántica (TF-IDF)        │  30 %  │
    │ Años de experiencia (normalizado)   │  25 %  │
    └─────────────────────────────────────┴────────┘

    Retorna: dict con puntuación total (0-10) y desglose detallado.
    """
    cv_skills = extract_skills(cv_text)
    req_norm = [normalize_text(s) for s in required_skills]
    cv_norm = [normalize_text(s) for s in cv_skills]

    if req_norm:
        matched = [s for s in req_norm if s in cv_norm]
        skill_score = len(matched) / len(req_norm)
        habilidades_coincidentes = [s for s in required_skills if normalize_text(s) in cv_norm]
        habilidades_faltantes = [s for s in required_skills if normalize_text(s) not in cv_norm]
    else:
        skill_score = 0.5
        habilidades_coincidentes = []
        habilidades_faltantes = []

    try:
        vectorizer = TfidfVectorizer(max_features=500, sublinear_tf=True)
        tfidf_matrix = vectorizer.fit_transform([job_description, cv_text])
        semantic_score = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
    except Exception:
        semantic_score = 0.0

    years = extract_years_experience(cv_text)
    exp_score = min(years / 8, 1.0)  # 8 años = puntuación máxima

    raw = (skill_score * 0.45) + (semantic_score * 0.30) + (exp_score * 0.25)
    final_score = round(raw * 10, 2)  # escala 0–10

    return {
        "puntuacion_total": final_score,
        "habilidades_encontradas": cv_skills,
        "habilidades_coincidentes": habilidades_coincidentes,
        "habilidades_faltantes": habilidades_faltantes,
        "anos_experiencia": years,
        "desglose": {
            "habilidades_pct": round(skill_score * 10, 2),
            "similitud_semantica_pct": round(semantic_score * 10, 2),
            "experiencia_pct": round(exp_score * 10, 2),
        },
    }



def process_all_candidates(
    candidates: List[Dict],
    job_description: str,
    required_skills: List[str],
) -> pd.DataFrame:
    """
    Procesa una lista de candidatos y devuelve un DataFrame ordenado
    por puntuación (de mayor a menor) con todos los datos relevantes.
    Esta función es el punto de entrada principal del motor de IA.
    """
    results = []

    for idx, candidate in enumerate(candidates, start=1):
        cv_text = candidate.get("texto_cv", "")

        scores = score_candidate(cv_text, job_description, required_skills)

        anon = anonymize_cv(cv_text, idx)

        results.append({
            "candidato_id": anon["candidato_id"],
            "nombre_real": candidate.get("nombre", f"Candidato {idx}"),  # solo visible en modo admin
            "puntuacion": scores["puntuacion_total"],
            "anos_experiencia": scores["anos_experiencia"],
            "habilidades_encontradas": scores["habilidades_encontradas"],
            "habilidades_coincidentes": scores["habilidades_coincidentes"],
            "habilidades_faltantes": scores["habilidades_faltantes"],
            "score_habilidades": scores["desglose"]["habilidades_pct"],
            "score_semantico": scores["desglose"]["similitud_semantica_pct"],
            "score_experiencia": scores["desglose"]["experiencia_pct"],
            "texto_anonimizado": anon["texto_anonimizado"],
            "texto_original": cv_text,
        })

    df = pd.DataFrame(results)
    df = df.sort_values("puntuacion", ascending=False).reset_index(drop=True)
    df.index += 1  

    return df