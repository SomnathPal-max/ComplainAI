import os
import sys
import uvicorn

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))

    print("=" * 70)
    print("⚡ Starting ComplainAI — Civic & Enterprise Grievance Intelligence")
    print(f"   Server listening at: http://{host}:{port}")
    print(f"   Local browser URL:  http://localhost:{port}")
    print(f"   Integrated LLM:     Ollama (http://127.0.0.1:11434) with Autonomous Local Engine")
    print("=" * 70)

    uvicorn.run("backend.main:app", host=host, port=port, reload=False)
