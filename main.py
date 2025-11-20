import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from database import db, create_document, get_documents
from schemas import (
    User,
    Client,
    Document,
    Project,
    Task,
    CEEApplication,
    MARApplication,
    Audit,
)

app = FastAPI(title="ERFMS Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "ERFMS Backend running", "version": app.version}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the ERFMS backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response: Dict[str, Any] = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = getattr(db, "name", "✅ Connected")
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:  # pragma: no cover - safety
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# --- Schema discovery for admin tooling ---
class SchemaField(BaseModel):
    name: str
    type: str
    required: bool = False
    description: Optional[str] = None


@app.get("/schema")
def get_schema():
    """Expose available collections (derived from Pydantic models)."""
    models = [User, Client, Document, Project, Task, CEEApplication, MARApplication, Audit]
    payload: Dict[str, Any] = {"collections": []}
    for model in models:
        fields: List[SchemaField] = []
        for name, field in model.model_fields.items():
            fields.append(
                SchemaField(
                    name=name,
                    type=str(field.annotation.__name__) if hasattr(field.annotation, "__name__") else str(field.annotation),
                    required=field.is_required(),
                    description=(field.description or None),
                ).model_dump()
            )
        payload["collections"].append({
            "name": model.__name__.lower(),
            "title": model.__name__,
            "fields": fields,
        })
    return payload


# --- Helper ---
COLLECTIONS = {
    "user": User,
    "client": Client,
    "document": Document,
    "project": Project,
    "task": Task,
    "ceeapplication": CEEApplication,
    "marapplication": MARApplication,
    "audit": Audit,
}


def list_items(collection: str, limit: Optional[int] = 100):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    data = get_documents(collection, {}, limit)
    # Convert ObjectId to string safely
    for d in data:
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
    return data


def create_item(collection: str, model: BaseModel):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    inserted_id = create_document(collection, model)
    return {"id": inserted_id}


# --- Minimal CRUD endpoints for key resources ---
@app.get("/api/projects")
def api_list_projects(limit: int = 100):
    return list_items("project", limit)


@app.post("/api/projects")
def api_create_project(payload: Project):
    return create_item("project", payload)


@app.get("/api/cee")
def api_list_cee(limit: int = 100):
    return list_items("ceeapplication", limit)


@app.post("/api/cee")
def api_create_cee(payload: CEEApplication):
    return create_item("ceeapplication", payload)


@app.get("/api/mar")
def api_list_mar(limit: int = 100):
    return list_items("marapplication", limit)


@app.post("/api/mar")
def api_create_mar(payload: MARApplication):
    return create_item("marapplication", payload)


@app.get("/api/audits")
def api_list_audits(limit: int = 100):
    return list_items("audit", limit)


@app.post("/api/audits")
def api_create_audit(payload: Audit):
    return create_item("audit", payload)


@app.get("/api/documents")
def api_list_documents(limit: int = 100):
    return list_items("document", limit)


@app.post("/api/documents")
def api_create_document(payload: Document):
    return create_item("document", payload)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
