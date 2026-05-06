import logging

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.scraper.movie import get_movies, get_movie_info

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/movies")
@router.get("/movies/{page}")
async def movie_list(
    page: int = 1,
    order: str = Query("update", enum=["update", "latest", "popular", "title", "titlereverse"]),
):
    try:
        result = await get_movies(page, order)
    except Exception as e:
        logger.exception("Failed to fetch movie list")
        return JSONResponse(status_code=500, content={"status": "Error", "message": str(e)})

    if not result.get("pagination"):
        return {"status": "Ok", "data": result.get("data", []), "pagination": None}

    return {
        "status": "Ok",
        "data": result["data"],
        "pagination": result["pagination"],
    }


@router.get("/movie/{slug}")
async def movie_detail(slug: str):
    try:
        data = await get_movie_info(slug)
    except Exception as e:
        logger.exception("Failed to fetch movie detail")
        return JSONResponse(status_code=500, content={"status": "Error", "message": str(e)})

    if not data:
        return JSONResponse(status_code=404, content={"status": "Error", "message": "Movie not found"})
    return {"status": "Ok", "data": data}