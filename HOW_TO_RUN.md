# How to open the app (every time)

You already cloned the repo and installed dependencies once. After that,
starting it up again is just 2 windows, 2 commands.

## 1. Start the backend

Open PowerShell:

```powershell
cd C:\Users\umasu\BioOil-Automation\backend
venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

Leave this window open. Wait for `Uvicorn running on http://127.0.0.1:8000`.

## 2. Start the frontend

Open a **second** PowerShell window:

```powershell
cd C:\Users\umasu\BioOil-Automation\frontend
npm run dev
```

Leave this window open too. Wait for `Local: http://localhost:5173/`.

## 3. Open the app

In your browser, go to:

```
http://localhost:5173
```

## To stop

Click into each PowerShell window and press `Ctrl+C`.

## Notes

- Both windows must stay open while you use the app — closing either one
  breaks the connection.
- You do **not** need to reinstall anything or retrain models each time —
  `pip install` / `npm install` / training are one-time setup steps.
- If `http://localhost:5173` doesn't load, check the backend window first —
  most failures show up there.
