# UI Traps Helper

A two-pass AI analysis tool that identifies UI Tenets & Traps in interface screenshots.

## First-time setup

### 1. Clone and configure environment

```bash
git clone https://github.com/mmedlock1970/UITraps_Platform.git
cd UITraps_Platform
```

Copy the environment template and fill in your values:

```bash
cp backend/.env.example backend/.env
```

Open `backend/.env` and set at minimum:

| Variable | What to put |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key from [console.anthropic.com](https://console.anthropic.com) |
| `BOOK_SOURCE_PATH` | Full path to your local copy of the book source file |
| `DEV_MODE` | Leave as `true` for local development |

### 2. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Install frontend dependencies

```bash
cd frontend
npm install
```

## Running the app

Two terminals are needed:

**Terminal 1 — Backend (port 8000)**
```bash
cd backend
python app.py
```

**Terminal 2 — Frontend (port 5173)**
```bash
cd frontend
npm run dev
```

Then open [http://localhost:5173](http://localhost:5173).

## Pulling updates

```bash
git pull
```

Check `backend/.env.example` after pulling — if new environment variables have been added, they'll appear there and you'll need to add them to your `backend/.env`.
