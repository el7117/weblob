# Railway deployment

1. Create a Railway service from this repository and generate a public domain.
2. Add a persistent Volume mounted at `/data`.
3. Add these Variables:
   - `WEB_GAME_DB_PATH=/data/WEB_GAME.db`
   - `CLIENT_ID=<Discord application client id>`
   - `CLIENT_SECRET=<Discord application client secret>`
   - `REDIRECT_URI=https://<your-railway-domain>/auth/discord/callback`
4. Use `python server.py` as the Start Command (also configured in `railway.toml`).
5. Add the exact same HTTPS callback URL to Discord Developer Portal → OAuth2 → Redirects.

Railway supplies `PORT`; the application binds to `0.0.0.0` and uses port 8080 only when `PORT` is absent. Keep the service at one replica: the live lobby and login sessions are process-local, while the SQLite database is stored on the mounted Volume.

On the first start of an empty Volume, the current `WEB_GAME.seed.db` is copied to the configured `WEB_GAME_DB_PATH`. Later restarts and deploys reuse the existing Volume database and never overwrite it. Local launches still use the working `WEB_GAME.db` by default.

If `/data/WEB_GAME.db` was already created from the old `GAME.db`, delete that one file from the Volume once (or recreate the Volume) before the next start. This initialization rule only applies to an empty database path.
