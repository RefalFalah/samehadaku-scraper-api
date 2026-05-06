# Samehadaku API Unofficial

REST API tidak resmi untuk mengambil data anime dari Samehadaku dengan format JSON yang lebih rapi dan mudah dipakai.

## Fitur

- Endpoint terstruktur dengan prefix `/api/v1`
- Home page (anime terbaru + top 10 minggu ini)
- Top 10 anime minggu ini
- Anime terbaru (paginated)
- Pencarian anime berdasarkan keyword
- Detail anime lengkap (info, episode list, batch links, genre, score, dll)
- Detail episode (stream URL + link download MP4/MKV)
- Detail batch download
- Daftar genre + anime berdasarkan genre
- Jadwal rilis anime per hari
- Auto bypass Cloudflare via Scrapling StealthyFetcher
- Swagger docs otomatis di `/docs`

## Tech Stack

- Python 3.12+
- FastAPI + Uvicorn
- Scrapling (fetcher + parser + anti-bot bypass)

## Menjalankan Project

1. Install Python 3.10+, lalu:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   # source .venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   scrapling install
   ```

2. Copy env:
   ```bash
   cp .env.example .env
   ```

3. Jalankan:
   ```bash
   uvicorn app.main:app --reload --port 3000
   ```

Default server berjalan di:
- `http://localhost:3000`
- Base API: `http://localhost:3000/api/v1`
- Swagger docs: `http://localhost:3000/docs`

## Konfigurasi Environment

Gunakan file `.env`:
```env
BASE_URL=https://v2.samehadaku.how
PORT=3000
```

## Format Response

Contoh response sukses:
```json
{
  "status": "Ok",
  "data": {}
}
```

Contoh response dengan paginasi:
```json
{
  "status": "Ok",
  "data": [],
  "pagination": {
    "currentPage": 1,
    "lastVisiblePage": 10,
    "hasNextPage": true,
    "nextPage": 2,
    "hasPreviousPage": false,
    "previousPage": null
  }
}
```

Contoh response error:
```json
{
  "status": "Error",
  "message": "Anime not found"
}
```

## Daftar Endpoint

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/v1/home` | Home page (recent anime + top 10) |
| GET | `/api/v1/top` | Top 10 anime minggu ini |
| GET | `/api/v1/recent/:page?` | Anime terbaru (default page 1) |
| GET | `/api/v1/search/:keyword` | Cari anime berdasarkan keyword |
| GET | `/api/v1/anime/:slug` | Detail lengkap anime |
| GET | `/api/v1/anime/:slug/episodes` | Daftar episode anime |
| GET | `/api/v1/episode/:slug` | Detail episode berdasarkan slug |
| GET | `/api/v1/anime/:slug/batch` | Batch download berdasarkan anime slug |
| GET | `/api/v1/batch/:slug` | Batch download berdasarkan slug |
| GET | `/api/v1/genres` | Daftar semua genre |
| GET | `/api/v1/genres/:slug/:page?` | Anime per genre |
| GET | `/api/v1/schedule` | Jadwal rilis anime per hari |

## Contoh Pemakaian

```bash
# Home page
curl http://localhost:3000/api/v1/home

# Top 10 anime
curl http://localhost:3000/api/v1/top

# Anime terbaru halaman 2
curl http://localhost:3000/api/v1/recent/2

# Cari anime
curl http://localhost:3000/api/v1/search/one%20piece

# Detail anime
curl http://localhost:3000/api/v1/anime/one-piece

# Daftar episode
curl http://localhost:3000/api/v1/anime/one-piece/episodes

# Detail episode
curl http://localhost:3000/api/episode/one-piece-episode-1160

# Jadwal rilis
curl http://localhost:3000/api/v1/schedule

# Genre
curl http://localhost:3000/api/v1/genres
```

## Contoh Response: Home

```json
{
  "status": "Ok",
  "data": {
    "recentAnime": [
      {
        "title": "One Piece",
        "slug": "one-piece",
        "poster": "https://...",
        "episode": "1160",
        "date": "8 hours ago",
        "url": "https://v2.samehadaku.how/anime/one-piece/"
      }
    ],
    "topAnime": [
      {
        "rank": 1,
        "title": "One Piece",
        "slug": "one-piece",
        "poster": "https://...",
        "score": "8.73",
        "url": "https://v2.samehadaku.how/anime/one-piece/"
      }
    ]
  }
}
```

## Contoh Response: Anime Detail

```json
{
  "status": "Ok",
  "data": {
    "title": "One Piece Sub Indo",
    "japaneseName": "ONE PIECE",
    "englishName": "One Piece",
    "poster": "https://...",
    "score": "8.73",
    "type": "TV",
    "status": "Ongoing",
    "episodeCount": "Unknown",
    "duration": "24 min.",
    "season": {"name": "Fall 1999", "slug": "fall-1999", "url": "..."},
    "studio": {"name": "Toei Animation", "slug": "toei-animation", "url": "..."},
    "genres": [...],
    "synopsis": "...",
    "episodeLists": [...],
    "batchLinks": [...]
  }
}
```

## Catatan

- API ini tidak resmi dan tidak berafiliasi dengan Samehadaku.
- Struktur HTML sumber dapat berubah sewaktu-waktu dan bisa mempengaruhi hasil scraping.
- StealthyFetcher otomatis bypass Cloudflare, tapi jika situs down hasil bisa error.
- Gunakan dengan bijak dan patuhi kebijakan situs sumber.

## Deploy ke Server (EC2 dll)

```bash
git clone <repo>
cd api-anime
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
scrapling install
uvicorn app.main:app --host 0.0.0.0 --port 3000
```

Untuk production, gunakan systemd/supervisor + nginx reverse proxy.