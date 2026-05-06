from fastapi import APIRouter

from app.scraper.home import get_home, get_top_anime
from app.scraper.recent import get_recent_anime
from app.scraper.search import search_anime
from app.scraper.anime import get_anime_info, get_anime_episodes
from app.scraper.episode import get_episode_by_slug
from app.scraper.batch import get_batch_by_slug, get_batch_by_anime_slug
from app.scraper.genre import get_genre_lists, get_anime_by_genre
from app.scraper.schedule import get_schedule

router = APIRouter()


@router.get("/home")
async def home():
    data = await get_home()
    return {"status": "Ok", "data": data}


@router.get("/top")
async def top_anime():
    data = await get_top_anime()
    return {"status": "Ok", "data": data}


@router.get("/recent")
@router.get("/recent/{page}")
async def recent_anime(page: int = 1):
    result = await get_recent_anime(page)
    if not result["pagination"]:
        return {"status": "Error", "message": "Page not found"}
    return {
        "status": "Ok",
        "data": result["data"],
        "pagination": result["pagination"],
    }


@router.get("/search/{keyword}")
async def search(keyword: str):
    data = await search_anime(keyword)
    return {"status": "Ok", "data": data}


@router.get("/anime/{slug}")
async def anime_detail(slug: str):
    data = await get_anime_info(slug)
    if not data:
        return {"status": "Error", "message": "Anime not found"}
    return {"status": "Ok", "data": data}


@router.get("/anime/{slug}/episodes")
async def anime_episodes(slug: str):
    data = await get_anime_episodes(slug)
    if not data:
        return {"status": "Error", "message": "Episodes not found"}
    return {"status": "Ok", "data": data}


@router.get("/episode/{slug}")
async def episode_by_slug(slug: str):
    data = await get_episode_by_slug(slug)
    if not data:
        return {"status": "Error", "message": "Episode not found"}
    return {"status": "Ok", "data": data}


@router.get("/anime/{slug}/batch")
async def anime_batch(slug: str):
    data = await get_batch_by_anime_slug(slug)
    if not data:
        return {"status": "Error", "message": "This anime does not have a batch yet"}
    return {"status": "Ok", "data": data}


@router.get("/batch/{slug}")
async def batch_by_slug(slug: str):
    data = await get_batch_by_slug(slug)
    if not data:
        return {"status": "Error", "message": "Batch not found"}
    return {"status": "Ok", "data": data}


@router.get("/genres")
async def genres():
    data = await get_genre_lists()
    return {"status": "Ok", "data": data}


@router.get("/genres/{slug}")
@router.get("/genres/{slug}/{page}")
async def anime_by_genre(slug: str, page: int = 1):
    result = await get_anime_by_genre(slug, page)
    return {
        "status": "Ok",
        "data": result["data"],
        "pagination": result["pagination"],
    }


@router.get("/schedule")
async def schedule():
    data = await get_schedule()
    return {"status": "Ok", "data": data}