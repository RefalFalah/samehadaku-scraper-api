from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.anime import router
from app.routes.movie import router as movie_router

app = FastAPI(title="Samehadaku Unofficial API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix=settings.api_prefix)
app.include_router(movie_router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    return {
        "status": "Ok",
        "message": "Samehadaku Unofficial API",
        "version": "2.0.0",
"endpoints": {
            "home": f"{settings.api_prefix}/home",
            "top_anime": f"{settings.api_prefix}/top",
            "recent_anime": f"{settings.api_prefix}/recent/{{page?}}",
            "search": f"{settings.api_prefix}/search/{{keyword}}",
            "anime_detail": f"{settings.api_prefix}/anime/{{slug}}",
            "anime_episodes": f"{settings.api_prefix}/anime/{{slug}}/episodes",
            "episode_by_slug": f"{settings.api_prefix}/episode/{{slug}}",
            "anime_batch": f"{settings.api_prefix}/anime/{{slug}}/batch",
            "batch_by_slug": f"{settings.api_prefix}/batch/{{slug}}",
            "genres": f"{settings.api_prefix}/genres",
            "anime_by_genre": f"{settings.api_prefix}/genres/{{slug}}/{{page?}}",
            "schedule": f"{settings.api_prefix}/schedule",
            "movie_list": f"{settings.api_prefix}/movies/{{page?}}",
            "movie_detail": f"{settings.api_prefix}/movie/{{slug}}",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=True)