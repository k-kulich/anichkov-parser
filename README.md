# Anichkov Parser — Content Aggregation & Management System

A full‑stack application for aggregating posts, announcements, and attached files from multiple sources (VK communities and a Bitrix24‑based portal) into a unified local database, with a desktop GUI for browsing, filtering, and downloading content. Built with Python, SQLAlchemy, PyQt5, and asynchronous HTTP.

## Overview

The Anichkov Parser solves the problem of scattered information across multiple platforms used by an educational institution. It automatically collects posts from:

- __VK communities__ – using the official VK API.
- __Bitrix24 portal__ – scraping the web interface with `aiohttp` and `BeautifulSoup`.

All collected data (author, date, text, attachments) is stored in a local SQLite database via SQLAlchemy. A desktop GUI (PyQt5) lets users view posts in a table, filter by author or date, read full post text, and download attached files directly from the interface.

The project demonstrates a complete pipeline: __data acquisition → parsing → persistence → UI presentation__, with asynchronous I/O and modular architecture.

## Key Features

### Data Acquisition
- __VK API integration__ – fetches the latest posts from a configurable list of groups, handles pagination, and extracts text and attachments (photos, documents, links).
- __Bitrix24 scraping__ – asynchronously downloads and parses the portal’s HTML, extracts post metadata (author, date, text) and file attachments.
- __Robust date parsing__ – converts non‑standard Russian date strings (e.g., “Вчера”, “13 февраля 16:01”) into standard `datetime` objects.
- __Environment‑based credentials__ – reads `VK_TOKEN`, `BX_LOGIN`, and `BX_PASSWORD` from environment variables.

### Persistence
- __SQLAlchemy ORM__ – defines three relational models: `Author`, `Post`, and `Attachment`.
- __Duplicate prevention__ – checks for existing posts before insertion.
- __Attachment management__ – stores file links and filenames for later download.

### Desktop GUI (PyQt5)
- __Interactive table__ – displays all posts with columns for ID, text preview, date, and author.
- __Filtering__ – filter posts by author and/or date via dropdown menus.
- __Post viewer__ – shows the full text of the selected post and its attachments.
- __File download__ – select any attachment and save it locally with a native file dialog.
- __Session management__ – automatically closes the database session on exit.

### Performance & Engineering
- __Asynchronous HTTP__ – uses `aiohttp` for non‑blocking requests to the Bitrix portal, significantly faster than synchronous `requests` for multiple fetches.
- __Benchmark script__ – includes `comparing.py`, which measures and compares the execution time of `requests` vs `aiohttp` over multiple trials, demonstrating the benefits of async I/O.
- __Custom exceptions__ – clear error handling for missing tokens, author lookup failures, and date parsing issues.
- __Modular design__ – separation of concerns: `async_http.py` (network), `vk_parser.py` (VK), `db_worker.py` (database), `gui.py` (UI), `correct_date.py` (utilities).

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| __Language__ | Python 3 |
| __Web / API__ | `aiohttp`, `requests`, `BeautifulSoup4`, `vk_api` |
| __Database__ | SQLite, SQLAlchemy ORM |
| __GUI__ | PyQt5 |
| __Async__ | `asyncio` |
| __Utilities__ | `datetime`, `os`, custom exceptions |

## Architecture

```
anichkov-parser/
├── main.py                 # Entry point: async parsing + GUI launch
├── async_http.py           # Async HTTP client, Bitrix parsing
├── vk_parser.py            # VK API wrapper and post extraction
├── correct_date.py         # Date string normalization
├── db_worker.py            # Database manager (CRUD operations)
├── gui.py                  # PyQt5 GUI logic
├── my_gui.py               # Generated UI layout
├── my_tracebacks.py        # Custom exception classes
├── comparing.py            # Async vs sync HTTP benchmark
├── data/                   # SQLAlchemy models
│   ├── author.py
│   ├── post.py
│   ├── attachment.py
│   └── db_session.py
└── db/                     # SQLite database file
```

The application starts by asynchronously fetching Bitrix posts, storing them in the database, then launching the GUI. VK parsing is triggered from the GUI (requires a user token) and also persists data.

## How to Run

### Prerequisites
- Python 3.8+
- Install dependencies:
  ```bash
  pip install aiohttp requests beautifulsoup4 vk_api sqlalchemy pyqt5 lxml
  ```

### Environment Variables
Set the following variables (e.g., in a `.env` file or your shell):
- `VK_TOKEN` – VK user access token (for VK parsing)
- `BX_LOGIN` – Bitrix24 portal login
- `BX_PASSWORD` – Bitrix24 portal password

### Launch
```bash
python main.py
```
Alternatively, run the compiled `parser.exe` (Windows) with the `db` folder alongside it.

On first launch, if `VK_TOKEN` is missing, the GUI will prompt you to enter it.

### Benchmark (optional)
```bash
python comparing.py
```
Runs 10 trials of 10 HTTP requests using `requests` and `aiohttp`, printing average times.

## What This Project Demonstrates

- __Full‑stack development__ – from data scraping and API integration to database design and desktop UI.
- __Asynchronous programming__ – practical use of `asyncio` and `aiohttp` for concurrent I/O.
- __Database modeling__ – relational schema with foreign keys, ORM usage, and session management.
- __GUI development__ – building a functional PyQt5 interface with filtering, table views, and file dialogs.
- __Robust parsing__ – handling heterogeneous data sources, non‑standard date formats, and attachment extraction.
- __Clean code organization__ – modular files, custom exceptions, environment‑based configuration.
- __Performance awareness__ – benchmarking and demonstrating the advantages of async I/O.

## Future Improvements

- Add support for more sources (e.g., Telegram, email).
- Implement scheduled background parsing.
- Add export to CSV/JSON.
- Package as a standalone executable with PyInstaller.
- Add unit tests for parsers and database operations.
