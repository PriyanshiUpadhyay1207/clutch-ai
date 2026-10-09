# Clutch.ai 🎮
**Track: Personal AI | Nebius x NVIDIA Global AI Hackathon**

Clutch.ai is a gamified, strictly-sandboxed personal AI agent that runs in the background for competitive gamers. It tracks local PC telemetry and post-match stats to act as a ruthless performance coach, without requiring dangerous root-level OS access.

## How We Use the Stack
* **Nebius Token Factory:** Powers our LLM routing. We use `https://api.tokenfactory.nebius.com/v1/` as our OpenAI-compatible base URL.
* **Nemotron 3 Nano/Super:** Used for high-speed, sub-second routing of voice commands (e.g., "clip that").
* **Nemotron 3 Ultra:** Used asynchronously via Nebius Serverless Jobs at the end of a match to generate the deep, gamified "Chess.com style" breakdown of the player performance.
* **NVIDIA NemoClaw & OpenShell:** Enforces strict sandbox constraints. The AI can only read temperatures (via `pynvml`) and trigger OBS clips; it cannot read arbitrary local user files.

## Repository Structure
* `/local_daemon/`: Builder 1 Python scripts for `psutil`/`pynvml` hardware telemetry and OpenShell tool definitions.
* `/nebius_backend/`: Builder 2 LangChain routing, Serverless Jobs setup, and Nemotron Ultra prompt orchestration.
* `/.ralph/`: The state files for our autonomous Wiggum/Ralph development loop.

## Setup Instructions
1. Clone the repository and navigate to the root directory.
2. Copy `.env.example` to `.env` and add your `NEBIUS_API_KEY`.
3. Install dependencies: `pip install openai psutil pynvml langchain`
4. Run the local daemon: `python local_daemon/monitor.py`
