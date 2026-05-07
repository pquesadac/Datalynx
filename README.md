# 🔍 Datalynx — Plataforma de Selección con IA

Plataforma SaaS para la optimización de procesos de selección de personal mediante
Inteligencia Artificial y Procesamiento de Lenguaje Natural.

**Autor:** Pablo Quesada Castellano  
**Curso:** Especialización en Inteligencia Artificial y Big Data

---

## 🏗️ Estructura del proyecto

```
datalynx/
├── app.py              # Interfaz web (Streamlit) — punto de entrada principal
├── api.py              # API REST (FastAPI) — backend de integración
├── cv_processor.py     # Motor de IA (spaCy + Scikit-Learn) — núcleo del sistema
├── sample_data.py      # CVs y ofertas de demo para la demostración
├── requirements.txt    # Dependencias Python
└── README.md
```

---
## ⚙️ Instalación

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. (Opcional) Modelo de lenguaje español de spaCy
Solo compatible con Python 3.11 / 3.12. El sistema funciona sin él.
```bash
pip install spacy
python -m spacy download es_core_news_sm
```

---

## 🚀 Ejecución

### Opción A — Interfaz web (recomendado para demo)
```bash
streamlit run app.py
```
Se abre automáticamente en http://localhost:8501

### Opción B — API REST + interfaz (arquitectura completa)

Terminal 1:
```bash
uvicorn api:app --reload --port 8000
```

Terminal 2:
```bash
streamlit run app.py
```

Documentación interactiva de la API: http://localhost:8000/docs

---

## 🤖 Cómo funciona 

### 1. Extracción de información
- Detección de habilidades técnicas por comparación contra `SKILLS_DATABASE` (10 categorías, +80 skills)
- Estimación de años de experiencia mediante expresiones regulares y rangos de fechas
- Detección de entidades nombradas (NER) con spaCy cuando está disponible

### 2. Puntuación de candidatos

La puntuación final (escala 0–10) combina tres criterios ponderados:

| Criterio | Peso | Descripción |
|---|---|---|
| Coincidencia de habilidades | 45 % | Skills requeridas presentes en el CV |
| Similitud semántica (TF-IDF) | 30 % | Similitud coseno entre el CV y la oferta |
| Años de experiencia | 25 % | Normalizado sobre un máximo de 8 años |

### 3. Anonimización (RGPD)

Antes de mostrar resultados al reclutador, el sistema elimina:

- Nombres propios (NER con spaCy o regex como fallback)
- Direcciones de email
- Números de teléfono (formato español)
- Menciones de edad explícitas

---

## 📡 Endpoints de la API

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Health check |
| POST | `/ofertas` | Crear nueva oferta de empleo |
| GET | `/ofertas` | Listar todas las ofertas |
| GET | `/ofertas/{id}` | Detalle de una oferta |
| POST | `/candidatos/texto` | Enviar CV y obtener puntuación |
| GET | `/ofertas/{id}/ranking` | Ranking de candidatos |
| GET | `/estadisticas` | Métricas globales |

---

## 🛠️ Stack tecnológico

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.11+ |
| NLP | spaCy `es_core_news_sm` (opcional) + regex |
| ML | Scikit-Learn (TF-IDF, cosine similarity) |
| Interfaz | Streamlit |
| API REST | FastAPI + Uvicorn |
| Datos | Pandas + NumPy |
| Visualización | Plotly |
| Cloud (producción) | AWS EC2 + S3 + RDS |

---

## ⚠️ Nota sobre spaCy y Python 3.13

spaCy no es compatible con Python 3.13 en el momento de escritura. El sistema detecta
automáticamente si está instalado y usa regex como fallback para la anonimización.
Para NLP completo, usa Python 3.11 o 3.12.
