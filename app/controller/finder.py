from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/search")
def search(query: str):
    # Placeholder implementation for search functionality
    return {"query": query, "results": []}
