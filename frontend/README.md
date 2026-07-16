# Aegis frontend

React + TypeScript + Vite dashboard for the Aegis guardrail layer. See the
[repo root README](../README.md) for the full project, API docs, and setup.

```bash
npm install
npm run dev      # -> http://127.0.0.1:5173
npm run build
npm run lint
```

`VITE_API_URL` controls which backend it talks to (see `.env.example`);
defaults to `http://127.0.0.1:8000`.
