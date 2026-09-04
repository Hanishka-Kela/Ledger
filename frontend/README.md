# Ledger frontend

## Run locally

1. Copy `.env.example` to `.env`. The default `/api` value uses Vite's development proxy to reach the backend at `http://localhost:8000`.
2. Run `npm install`.
3. Run `npm run dev`.

Use `npm run build` to create a production build.

For production, set `VITE_API_BASE_URL` to the public API URL at build time. Because the frozen backend does not currently configure CORS, deploy the frontend and API behind a same-origin reverse proxy unless CORS is enabled outside this project.
