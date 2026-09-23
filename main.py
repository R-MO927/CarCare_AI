from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path



from rag import (
    hybrid_retrieve,
    generate_with_ollama,
    has_direct_part_evidence,
    PART_NAME_MAP,
)

from cv import detect_vehicle_parts

PROJECT_ROOT = Path(__file__).resolve().parent



app = FastAPI(
    title="CarCare AI",
    description="AI-powered vehicle maintenance assistant",
    version="1.0.0"
)
app.mount(
    "/static",
    StaticFiles(directory=PROJECT_ROOT / "frontend"),
    name="static"
)

class AskRequest(BaseModel):
    question: str
    part: str | None = None


@app.get("/", include_in_schema=False)
def root():
    return FileResponse(
        PROJECT_ROOT / "frontend" / "index.html"
    )


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
@app.post("/detect")
async def detect(image: UploadFile = File(...)):

    image_bytes = await image.read()

    temp_path = PROJECT_ROOT / "data" / "temp_upload.jpg"
    temp_path.write_bytes(image_bytes)

    detected_parts = detect_vehicle_parts(temp_path)

    primary_part = None

    if detected_parts:
        primary_part = max(
            detected_parts,
            key=lambda x: x["confidence"]
        )

    return {
        "filename": image.filename,
        "primary_part": primary_part,
        "detected_parts": detected_parts
    }
@app.post("/ask-with-image")
async def ask_with_image(
    image: UploadFile = File(...),
    question: str = Form("")
):
    image_bytes = await image.read()

    temp_path = PROJECT_ROOT / "data" / "temp_upload.jpg"
    temp_path.write_bytes(image_bytes)

    detected_parts = detect_vehicle_parts(temp_path)

    if not detected_parts:
        return {
            "filename": image.filename,
            "question": question,
            "answer": "No vehicle part was detected in the image.",
            "sources": []
        }

    primary_part = max(
        detected_parts,
        key=lambda x: x["confidence"]
    )

    part = primary_part["part"]

    friendly_part = PART_NAME_MAP.get(
        part,
        part.replace("_", " ")
    )

    search_query = (
        f"Vehicle part: {friendly_part}. "
        f"Maintenance question: {question}. "
        f"Related terms: tyre, tire, wheel, rim, tread, pressure, damage, inspection"
      )

    retrieved_results = hybrid_retrieve(
        search_query,
        top_k=5
    )

    if not has_direct_part_evidence(
        friendly_part,
        retrieved_results
    ):
        return {
            "filename": image.filename,
            "question": question,
            "part": friendly_part,
            "answer": (
                f"The available maintenance document does not provide "
                f"enough specific information about the {friendly_part} "
                f"to answer the question reliably."
            ),
            "sources": []
        }

    answer = generate_with_ollama(
        search_query,
        retrieved_results
    )

    sources = [
        {
            "page": result["page"],
            "score": round(result["final_score"], 4)
        }
        for result in retrieved_results
    ]

    return {
        "filename": image.filename,
        "question": question,
        "part": friendly_part,
        "confidence": primary_part["confidence"],
        "answer": answer,
        "sources": sources
    }

@app.post("/ask")
def ask(request: AskRequest):

    friendly_part = None

    if request.part:
        friendly_part = PART_NAME_MAP.get(
            request.part,
            request.part.replace("_", " ")
        )

    search_query = request.question

    if friendly_part:
        search_query = (
            f"Vehicle part: {friendly_part}. "
            f"Maintenance question: {request.question}"
        )

    retrieved_results = hybrid_retrieve(
        search_query,
        top_k=5
    )

    if friendly_part:
        has_evidence = has_direct_part_evidence(
            friendly_part,
            retrieved_results
        )

        if not has_evidence:
            return {
                "question": request.question,
                "part": friendly_part,
                "answer": (
                    f"The available maintenance document does not provide "
                    f"enough specific information about the {friendly_part} "
                    f"to answer the question reliably."
                ),
                "sources": []
            }

    answer = generate_with_ollama(
        search_query,
        retrieved_results
    )

    sources = [
        {
            "page": result["page"],
            "score": round(result["final_score"], 4)
        }
        for result in retrieved_results
    ]

    return {
        "question": request.question,
        "part": friendly_part,
        "answer": answer,
        "sources": sources
    }