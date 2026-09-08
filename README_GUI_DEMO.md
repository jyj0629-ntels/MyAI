# MyAI GUI POC Demo

## Overview
This branch adds a browser-based GUI demo for the MyAI assistant with a polished "AI personal assistant" look and feel.

It is designed to show a realistic service UI instead of Swagger-only interaction, and it visually resembles modern AI assistant products using a multi-provider design.

## Run
From the project root:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Then open:

- http://localhost:8000/demo
- http://localhost:8000/ui

## Demo flow
- The page shows a modern AI assistant layout.
- The left panel simulates connected public AI providers such as ChatGPT, Gemini, Groq, and Meta AI.
- The center area looks like a production chat assistant interface.
- The UI concept demonstrates buy/recommendation context and development context learning in a service-like format.

## Notes
This is a POC/GUI prototype and is intended for demonstration and validation, not full production frontend architecture.
