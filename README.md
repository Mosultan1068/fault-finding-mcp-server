\# Fault Finding MCP Server

By: 	Mohamed Sultan

Date: 	Aug 2026



A proof-of-concept \*\*Model Context Protocol (MCP) server\*\* that exposes breakdown/callout fault data as a tool an AI assistant (e.g. Claude Desktop) can query directly — plus a full \*\*CI/CD pipeline\*\* that automatically tests and containerises the project on every push.



Built as a hands-on learning project to understand, end to end, how MCP servers work and how a real CI/CD pipeline is structured — not just in theory, but by building, breaking, and fixing a working example.



\---



\## What it does



The server exposes \*\*one tool\*\*: `get\_average\_resolution\_time`.



Given a fault category (e.g. `"Battery"`, `"Engine"`, `"Tyre Puncture"`), it returns the average resolution time in minutes, calculated from a mock dataset of 100 breakdown callouts.



\*\*Example, asked directly in Claude Desktop once connected:\*\*

> "What's the average resolution time for battery faults?"

>

> \*"The average resolution time for a battery fault is about 90 minutes (89.9 minutes, based on 15 callouts)."\*



\---



\## Why this scope



This is deliberately a \*\*proof of concept, not a production system\*\*. The goal was to prove the full mechanism works — MCP tool exposed → called by an LLM client → real data returned — and to build genuine, hands-on CI/CD experience, without the scope creep of trying to build something "impressive." One tool, one CSV, one pipeline, fully working, beats a half-finished ambitious version.



\*\*Natural next steps, if extended:\*\*

\- Replace the CSV with a real database (e.g. PostgreSQL/Supabase or MySQL)

\- Add more tools (e.g. count by vehicle type, percentage resolved onsite, busiest month)

\- Move from local `stdio` transport to a remote HTTP/SSE-based MCP server, so it isn't tied to a single machine

\- Push the built image to a container registry as part of the pipeline



\---



\## Tech stack



\- \*\*Python 3.11\*\*

\- \*\*MCP Python SDK\*\* (`FastMCP`) — exposes the tool over the Model Context Protocol

\- \*\*pandas\*\* — data filtering and aggregation

\- \*\*Docker\*\* — containerisation

\- \*\*GitHub Actions\*\* — CI/CD pipeline



\---



\## Project structure



```

fault\_finding/

├── .github/

│   └── workflows/

│       └── ci.yml          # CI/CD pipeline definition

├── data/

│   └── callouts.csv        # mock dataset, 100 breakdown callouts

├── Dockerfile               # container build instructions

├── requirements.txt

├── server.py                # the MCP server and its one tool

└── README.md

```



\---



\## Running it locally



```bash

python -m venv venv

venv\\Scripts\\activate          # Windows

pip install -r requirements.txt

python server.py

```



The server communicates over `stdio`, so it won't print anything when running correctly — it sits waiting for a client to connect. This is expected behaviour, not a hang.



\*\*To connect it to Claude Desktop\*\*, add an entry to Claude Desktop's local MCP server config (Settings → Developer → Edit Config):



```json

{

&#x20; "mcpServers": {

&#x20;   "fault-finding-server": {

&#x20;     "command": "C:\\\\fault\_finding\\\\venv\\\\Scripts\\\\python.exe",

&#x20;     "args": \["C:\\\\fault\_finding\\\\server.py"]

&#x20;   }

&#x20; }

}

```



\---



\## Running it in Docker



```bash

docker build -t fault-finding-server .

docker run fault-finding-server

```



`docker build` packages the project into an \*\*image\*\*. `docker run` starts a \*\*container\*\* — a running instance of that image. As with running it directly, it will sit silently, waiting for a client; this confirms it started correctly.



\---



\## CI/CD pipeline



Every push to `main` automatically triggers a GitHub Actions workflow (`.github/workflows/ci.yml`) that:



1\. Checks out the code

2\. Installs dependencies

3\. Runs a smoke test — loads the CSV, confirms Battery-category data exists, confirms the calculated average is a sensible positive number

4\. \*\*Only if the test passes\*\*, builds the Docker image



This can be watched live on the repo's \*\*Actions\*\* tab. If the smoke test fails, the pipeline stops immediately and the Docker build step never runs — I deliberately broke the test once (pointed it at a non-existent fault category) to confirm this behaviour, watched it fail with `exit code 1`, then reverted it and watched the pipeline pass again. That failure/fix history is visible in the Actions tab.



\---



\## What I learned building this



\- How the MCP protocol actually works in practice — a server exposing a defined tool, and a client (Claude Desktop) discovering and calling it with structured arguments

\- The difference between a Docker \*\*image\*\* (built blueprint) and a \*\*container\*\* (running instance), and why `build` and `run` are separate steps

\- How a CI/CD pipeline is triggered (a `push` event matching a condition in a workflow file), and how it gates later steps (like a Docker build) behind earlier ones (like a test) passing

\- A real debugging story: Claude Desktop (installed via the Microsoft Store) reads its MCP config from a sandboxed `AppData\\Local\\Packages\\...` path, not the standard `%APPDATA%\\Claude` location — cost some time to track down, but a good example of methodical troubleshooting using logs rather than guesswork

\- A second real bug: the server initially used a relative file path (`"data/callouts.csv"`) to load its dataset, which failed once launched by Claude Desktop from a different working directory. Fixed by resolving the path relative to the script's own location (`Path(\_\_file\_\_).resolve().parent`) instead of assuming a specific working directory

