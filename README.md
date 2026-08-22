# Army AFT Assistant

>A lightweight assistant service used in the Army AFT learning workspace. Provides a simple Python backend, optional frontend, and tooling for running locally or in Docker.

## Features
- Python backend service (API and helper scripts)
- Optional frontend and Docker-based deployment
- Simple vector store / knowledge base integration
- Test suite for backend components

## Repository layout
- `army-aft-assistant/` — project root (this folder)
	- [backend](army-aft-assistant/backend) — Python app, requirements, tests
	- [docker-compose.yml](army-aft-assistant/docker-compose.yml) — local Docker stack

See the files above for implementation details.

## Prerequisites
- Python 3.9+ (3.10 recommended)
- pip
- (Optional) Docker & Docker Compose

## Quickstart — local (venv)
1. Clone the repo and change into the project folder:

```bash
cd army-aft-assistant
```

2. Create and activate a virtual environment:

Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install backend dependencies:

```bash
pip install -r backend/requirements.txt
```

4. Run the backend (development):

```bash
python backend/app.py
```

Open the API at the address printed by the server (commonly `http://127.0.0.1:5000` or `http://127.0.0.1:8000`).

## Quickstart — Docker
Start the whole stack with Docker Compose:

```bash
docker-compose up --build
```

This will build images and run services defined in [docker-compose.yml](army-aft-assistant/docker-compose.yml).

## Tests
Run tests from the project root:

```bash
pip install -r backend/requirements.txt
pytest backend/tests
```

## Configuration
- If the project uses environment variables, put them in a `.env` file in the project root or export them before running.
- Check `backend` for any additional config files or templates.

## Contributing
- Open an issue for proposed features or bugs.
- Send a pull request with a descriptive title and tests when applicable.

## License
No license is provided in the repository. Add a `LICENSE` file to clarify terms.

## Contact
If you want help improving this README or the project, open an issue or ping the maintainer in the repository.

