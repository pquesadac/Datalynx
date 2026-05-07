from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
import io

from cv_processor import process_all_candidates, score_candidate, anonymize_cv

app = FastAPI(
    title="Datalynx API",
    description="API REST para la plataforma de selección de personal con IA",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


_ofertas_db: dict = {}
_candidatos_db: dict = {}



class OfertaCreate(BaseModel):
    titulo: str
    descripcion: str
    habilidades_requeridas: List[str]


class CVTexto(BaseModel):
    nombre: str
    texto_cv: str
    oferta_id: str


class CandidatoRespuesta(BaseModel):
    candidato_id: str
    puntuacion: float
    anos_experiencia: int
    habilidades_coincidentes: List[str]
    habilidades_faltantes: List[str]
    score_habilidades: float
    score_semantico: float
    score_experiencia: float



@app.get("/")
def root():
    return {"status": "ok", "servicio": "Datalynx API", "version": "1.0.0"}



@app.post("/ofertas", summary="Crear nueva oferta de empleo")
def crear_oferta(oferta: OfertaCreate):
    
    oferta_id = str(uuid.uuid4())[:8]
    _ofertas_db[oferta_id] = {
        "id": oferta_id,
        "titulo": oferta.titulo,
        "descripcion": oferta.descripcion,
        "habilidades_requeridas": oferta.habilidades_requeridas,
        "candidatos": [],
    }
    return {"oferta_id": oferta_id, "mensaje": "Oferta creada correctamente"}


@app.get("/ofertas", summary="Listar todas las ofertas activas")
def listar_ofertas():
    """Devuelve todas las ofertas de empleo registradas."""
    return list(_ofertas_db.values())


@app.get("/ofertas/{oferta_id}", summary="Detalle de una oferta")
def detalle_oferta(oferta_id: str):
    if oferta_id not in _ofertas_db:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    return _ofertas_db[oferta_id]



@app.post("/candidatos/texto", summary="Enviar CV como texto")
def enviar_cv_texto(cv: CVTexto):
    
    if cv.oferta_id not in _ofertas_db:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")

    oferta = _ofertas_db[cv.oferta_id]
    candidato_num = len(_candidatos_db) + 1

    scores = score_candidate(
        cv.texto_cv,
        oferta["descripcion"],
        oferta["habilidades_requeridas"],
    )
    anon = anonymize_cv(cv.texto_cv, candidato_num)

    candidato_id = anon["candidato_id"]
    _candidatos_db[candidato_id] = {
        "candidato_id": candidato_id,
        "nombre_real": cv.nombre,  # solo para administradores
        "oferta_id": cv.oferta_id,
        "puntuacion": scores["puntuacion_total"],
        "anos_experiencia": scores["anos_experiencia"],
        "habilidades_coincidentes": scores["habilidades_coincidentes"],
        "habilidades_faltantes": scores["habilidades_faltantes"],
        "score_habilidades": scores["desglose"]["habilidades_pct"],
        "score_semantico": scores["desglose"]["similitud_semantica_pct"],
        "score_experiencia": scores["desglose"]["experiencia_pct"],
        "texto_anonimizado": anon["texto_anonimizado"],
    }

    _ofertas_db[cv.oferta_id]["candidatos"].append(candidato_id)

    return {
        "candidato_id": candidato_id,
        "puntuacion": scores["puntuacion_total"],
        "mensaje": "CV procesado y anonimizado correctamente",
    }



@app.get(
    "/ofertas/{oferta_id}/ranking",
    summary="Ranking de candidatos para una oferta",
    response_model=List[CandidatoRespuesta],
)
def ranking_candidatos(oferta_id: str, top: Optional[int] = None):
    
    if oferta_id not in _ofertas_db:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")

    candidato_ids = _ofertas_db[oferta_id]["candidatos"]
    candidatos = [_candidatos_db[cid] for cid in candidato_ids if cid in _candidatos_db]
    candidatos_ordenados = sorted(candidatos, key=lambda c: c["puntuacion"], reverse=True)

    if top:
        candidatos_ordenados = candidatos_ordenados[:top]

    return candidatos_ordenados


@app.get("/estadisticas", summary="Estadísticas globales del sistema")
def estadisticas_globales():
    return {
        "total_ofertas": len(_ofertas_db),
        "total_candidatos": len(_candidatos_db),
        "candidatos_por_oferta": {
            oferta_id: len(datos["candidatos"])
            for oferta_id, datos in _ofertas_db.items()
        },
    }