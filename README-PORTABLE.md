# PathFinder AI Portable For Windows x64

This package runs without installing Java, Python, Node.js, MySQL, Maven, npm, or Docker. All required application runtimes are inside the folder.

Open `docs\STUDENT_MINI_PROJECT_GUIDE.html` in a browser for the complete installation, user, architecture, AI, testing, troubleshooting, sharing, report, demonstration, and viva handbook.

## Requirements

- Windows 10 or Windows 11, 64-bit
- Approximately 1 GB of free disk space
- A modern browser
- Permission to run local applications and listen on loopback ports `8765`, `8766`, and `8767`

No administrator rights are normally required. Windows Firewall should not need a public-network rule because every service binds only to `127.0.0.1`.

## Verify The Download

When the ZIP and its `.sha256` sidecar are supplied together, run the following command in the download folder and compare its hash with the first value in `PathFinder-AI-Portable-Windows-x64.zip.sha256`:

```powershell
Get-FileHash .\PathFinder-AI-Portable-Windows-x64.zip -Algorithm SHA256
```

## Start

1. Extract the ZIP completely. Do not run it from inside the ZIP preview.
2. Open the extracted `PathFinder AI Portable` folder.
3. Double-click `START-PATHFINDER-AI.bat`.
4. Keep the launcher window open while using the application.
5. The browser opens at `http://localhost:8767` after all services are healthy.

First startup can take up to two minutes while the bundled AI models initialize.

Demo sign-in accounts:

- Student: `student@pathfinder.ai` / `Student@123`
- Administrator: `admin@pathfinder.ai` / `Admin@123`

The same credentials are written to `data\LOGIN-CREDENTIALS.txt` on first run.

## Stop

Press `Ctrl+C` in the launcher window, or double-click `STOP-PATHFINDER-AI.bat`.

## Move Or Copy

Stop PathFinder AI first. You can then move the complete folder to another writable directory, external drive, or compatible Windows x64 computer. Always move the whole folder.

User records, uploaded resumes, model data, and generated secrets are stored under `data`. Logs are stored under `logs`.

## Reset Local Data

Stop the application, then rename the `data` folder to keep a backup. The next start creates a fresh database, fresh internal secrets, and the demo accounts.

## Troubleshooting

- If startup reports a port conflict, close the application using ports `8765`, `8766`, or `8767`, or run `STOP-PATHFINDER-AI.bat` if a previous session did not close cleanly.
- Read `logs\ai-model.log`, `logs\backend.log`, and `logs\frontend.log` when startup fails.
- If Windows SmartScreen appears, inspect the extracted files and choose **More info > Run anyway** only when the package came from a trusted source and its checksum matches.
- Keep the folder writable. Running directly from `Program Files`, a read-only disc, or a ZIP preview prevents the local database from being created.

## Scope

This is a local demonstration and evaluation build. It uses a file-backed H2 database instead of the production MySQL deployment. For shared, multi-user, or internet-facing operation, use the Docker/MySQL deployment documented in the source project.