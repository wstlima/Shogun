# Shogun Microsoft Teams Bridge

This service is the Microsoft-facing edge for Katana. It uses the Microsoft 365
Agents SDK, validates Bot/Teams traffic through that SDK, normalizes activities,
and calls Shogun's internal command API. It contains no agent execution logic.

Requires Node.js 22+. Configure the standard Microsoft Agents SDK identity
environment variables plus `SHOGUN_INTERNAL_API_URL` and an injected
`SHOGUN_INTERNAL_API_KEY`. Run `npm install`, `npm run build`, then `npm start`.
The Teams messaging endpoint is `/api/messages` on port 3978. Liveness is exposed
on the same service at `/api/teams/health`. Authenticated proactive delivery uses
`POST /api/teams/proactive`; a conversation must first have contacted the bot.

The included in-memory conversation store is for development. Enterprise
deployments should substitute the Agents SDK Azure Blob or Cosmos storage
provider so proactive references survive restarts and scale-out.
