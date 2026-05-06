from pydantic import BaseModel


class Genre(BaseModel):
    name: str
    slug: str
    url: str


class RecentAnime(BaseModel):
    title: str
    slug: str
    poster: str
    episode: str
    date: str | None = None
    url: str


class TopAnime(BaseModel):
    rank: int
    title: str
    slug: str
    poster: str
    posterHD: str | None = None
    score: str | None = None
    episodeCount: str | None = None
    status: str | None = None
    synopsis: str | None = None
    url: str


class SearchAnime(BaseModel):
    title: str
    slug: str
    poster: str
    type: str | None = None
    score: str | None = None
    status: str | None = None
    synopsis: str | None = None
    genres: list[Genre] = []
    url: str


class EpisodeItem(BaseModel):
    number: str
    title: str
    slug: str
    date: str | None = None
    url: str


class BatchLink(BaseModel):
    title: str
    slug: str
    url: str


class AnimeDetail(BaseModel):
    title: str
    japaneseName: str | None = None
    englishName: str | None = None
    synonyms: str | None = None
    poster: str
    posterHD: str | None = None
    score: str | None = None
    ratingCount: str | None = None
    type: str | None = None
    status: str | None = None
    source: str | None = None
    duration: str | None = None
    episodeCount: str | None = None
    season: Genre | None = None
    studio: Genre | None = None
    producers: list[Genre] = []
    released: str | None = None
    genres: list[Genre] = []
    synopsis: str
    episodeLists: list[EpisodeItem]
    batchLinks: list[BatchLink] = []


class AnimeRef(BaseModel):
    title: str
    slug: str
    url: str


class DownloadLink(BaseModel):
    provider: str
    url: str


class DownloadGroup(BaseModel):
    resolution: str
    urls: list[DownloadLink]


class StreamMirror(BaseModel):
    quality: str
    url: str


class EpisodeDetail(BaseModel):
    title: str
    anime: AnimeRef
    streamUrl: str | None = None
    streamMirrors: list[StreamMirror] = []
    downloadUrls: list[DownloadGroup] = []
    hasNextEpisode: bool = False
    nextEpisode: AnimeRef | None = None
    hasPreviousEpisode: bool = False
    previousEpisode: AnimeRef | None = None


class BatchDownloadGroup(BaseModel):
    resolution: str
    fileSize: str | None = None
    urls: list[DownloadLink]


class BatchDetail(BaseModel):
    title: str
    downloadUrls: list[BatchDownloadGroup]


class Pagination(BaseModel):
    currentPage: int
    lastVisiblePage: int
    hasNextPage: bool
    nextPage: int | None
    hasPreviousPage: bool
    previousPage: int | None


class ScheduleAnime(BaseModel):
    title: str
    slug: str
    poster: str
    url: str


class ScheduleDay(BaseModel):
    day: str
    animeList: list[ScheduleAnime]


class AnimeByGenre(BaseModel):
    title: str
    slug: str
    poster: str
    type: str | None = None
    score: str | None = None
    status: str | None = None
    genres: list[Genre] = []
    synopsis: str | None = None
    url: str


class MovieListItem(BaseModel):
    title: str
    slug: str
    poster: str
    type: str | None = None
    score: str | None = None
    status: str | None = None
    genres: list[Genre] = []
    synopsis: str | None = None
    url: str


class MovieDetail(BaseModel):
    title: str
    japaneseName: str | None = None
    englishName: str | None = None
    synonyms: str | None = None
    poster: str
    posterHD: str | None = None
    score: str | None = None
    ratingCount: str | None = None
    status: str | None = None
    source: str | None = None
    duration: str | None = None
    released: str | None = None
    studio: Genre | None = None
    producers: list[Genre] = []
    genres: list[Genre] = []
    synopsis: str
    episodeLists: list[EpisodeItem]
    downloadUrls: list[DownloadGroup] = []


class OngoingAnime(BaseModel):
    title: str
    slug: str
    poster: str
    currentEpisode: str
    releaseDay: str
    newestReleaseDate: str
    url: str