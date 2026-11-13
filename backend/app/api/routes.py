"""Routes de l'API Cahier PCT."""

from __future__ import annotations

import json

from flask import Blueprint, current_app, jsonify, request
from pydantic import BaseModel, ValidationError

from ..errors import ApiError
from ..schemas import ExercicesRequest, FicheRequest, QuestionRequest
from ..services import generators
from . import deps


def parse_body(model: type[BaseModel]) -> BaseModel:
    payload = request.get_json(silent=True)
    if payload is None:
        raise ApiError(
            400,
            "Un corps JSON est attendu.",
            code="invalid_body",
        )
    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        raise ApiError(
            422,
            "Les données envoyées sont invalides.",
            code="validation_error",
            details=json.loads(exc.json()),
        ) from exc


def register_routes(bp: Blueprint) -> None:
    # --- Santé et métadonnées ---------------------------------------------

    @bp.get("/health")
    def health():
        return jsonify(
            {
                "status": "ok",
                "service": current_app.config["APP_NAME"],
                "version": current_app.config["APP_VERSION"],
            }
        )

    @bp.get("/meta")
    def meta():
        service = deps.llm()
        return jsonify(
            {
                "name": current_app.config["APP_NAME"],
                "version": current_app.config["APP_VERSION"],
                "llm": {
                    "mode": service.mode,
                    "model": service.model,
                    "live": service.is_live,
                },
                "corpus": deps.corpus().stats(),
            }
        )

    # --- Corpus ------------------------------------------------------------

    @bp.get("/corpus")
    def list_corpus():
        active = deps.corpus()
        type_filter = request.args.get("type")
        status_filter = request.args.get("status")
        return jsonify(
            {
                "corpus": active.stats(),
                "extracts": active.list_extracts(
                    type_=type_filter, status=status_filter
                ),
            }
        )

    @bp.get("/corpus/<path:extract_id>")
    def get_extract(extract_id: str):
        extract = deps.corpus().get(extract_id)
        if extract is None:
            raise ApiError(
                404,
                "Extrait introuvable.",
                code="extract_not_found",
                details={"id": extract_id},
            )
        return jsonify({"extract": extract.to_dict()})

    # --- Modes -------------------------------------------------------------

    @bp.post("/question")
    def question():
        body: QuestionRequest = parse_body(QuestionRequest)
        result = generators.generate_question(
            deps.corpus(),
            deps.llm(),
            question=body.question,
            level=body.level,
            top_k=body.top_k,
        )
        return jsonify(result.to_dict())

    @bp.post("/fiche")
    def fiche():
        body: FicheRequest = parse_body(FicheRequest)
        result = generators.generate_fiche(
            deps.corpus(),
            deps.llm(),
            competence=body.competence,
            level=body.level,
            duration=body.duration,
            class_size=body.class_size,
            context=body.context,
        )
        return jsonify(result.to_dict())

    @bp.post("/exercices")
    def exercices():
        body: ExercicesRequest = parse_body(ExercicesRequest)
        result = generators.generate_exercices(
            deps.corpus(),
            deps.llm(),
            competence=body.competence,
            level=body.level,
            count=body.count,
            with_correction=body.with_correction,
            difficulty=body.difficulty,
            context=body.context,
        )
        return jsonify(result.to_dict())
