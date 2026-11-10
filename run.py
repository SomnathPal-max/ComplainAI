import uvicorn
import sys
import os

if __name__ == "__main__":
    print("=" * 70)
    print("⚡ Starting ComplainAI Ecosystem...")
    print("   Autonomous Multimodal Grievance Intelligence & Zero-Touch Resolution")
    print("   Default Port: http://127.0.0.1:8000")
    print("   Integrated LLM: Ollama (http://127.0.0.1:11434) with Autonomous Mode")
    print("=" * 70)
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)
