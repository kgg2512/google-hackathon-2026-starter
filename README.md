# Generic hackathon infrastructure starter

This repository contains only a health endpoint, an honest readiness screen,
container configuration and a deployment helper. It implements no competition
feature and performs no model inference. It is a reusable starter, not a finished
hackathon submission. Follow the organizer's kickoff instructions before adding
competition demo code. Do not copy pre-event product demos into the submission.

Use Python 3.11. Create a virtual environment and install `requirements.lock.txt`,
then run `python app.py`. Open `http://127.0.0.1:8080`. The `/health` endpoint
verifies this server only; it does not verify a model or a cloud deployment.

Preview without cloud calls using `deploy.ps1 -ProjectId PROJECT_ID -PlanOnly`.
After receiving and authenticating the event account, use
`deploy.ps1 -ProjectId PROJECT_ID -Account ID@gcplab.me`.
The helper checks the active account, project access, required APIs, deployment
and the deployed HTTPS health endpoint. It stops on failures, does not change
your default gcloud project, and does not override Cloud Run's reserved `PORT`.

Model IDs, permissions and limits must be checked on the supplied event account.
No personal subscription or billing change is assumed.
Deployment reference: https://docs.cloud.google.com/run/docs/deploying-source-code

The repository itself is only infrastructure preparation. A working model-backed
demo, live deployment, English description, demo video and final submission are
event-time deliverables. Back up the actual source and video before the temporary
event account and project are deleted. Never commit API keys or `.env` files.
