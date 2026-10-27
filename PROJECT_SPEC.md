# PROJECT_SPEC.md: P1 Ticket Triage API

Version 1.0, 26 Oct 2026. Owner: Haseeb Ahmed. Estimated effort: 22 to 26 hours.

## 1. Problem
Nimbus Tasks is a fictional project management SaaS. Its support team receives hundreds of tickets a day, and a person reads and tags each one before it reaches the right team. First responses are slow and urgent tickets wait in the queue.

P1 is an API that reads one ticket and returns its category, its priority, a short summary, and whether a human must look at it now.

## 2. What this project proves
* I can call an LLM reliably: structured output, validation, timeout, retry and a safe fallback.
* I can measure it: accuracy on a labeled set, latency and token cost.
* I can ship it: Docker, Cloud Run, a secret store and a protected public URL.

## 3. Approved stack
Anything not on this list needs my approval first.
* Python 3.12, managed with uv
* FastAPI and Uvicorn
* Pydantic v2
* The official Google Gen AI Python SDK for the Gemini API (free tier). The model name comes from the GEMINI_MODEL env var and is never hardcoded.
* pytest, plus FastAPI TestClient (and the httpx package it needs)
* Docker, Google Cloud Run, Google Secret Manager
* Git and a public GitHub repo

Not allowed: LangChain or any agent framework, any database, any frontend framework, any other LLM provider.

## 4. API contract

### GET /health
* No auth.
* Returns 200 with `{"status": "ok", "version": "0.1.0"}`.

### POST /triage
Header: `Authorization: Bearer <SERVICE_API_KEY>`

Request JSON:
* subject: string, 1 to 200 characters
* body: string, 1 to 5000 characters

Response 200 JSON:
* category: one of billing, bug, how_to, account_access, feature_request, other
* priority: one of urgent, high, normal, low
* summary: string, at most 30 words
* needs_human: boolean
* reason: string, at most 20 words, explaining the category and priority
* fallback: boolean, true when the LLM failed and safe defaults were used
* model: string
* prompt_version: string
* latency_ms: integer

Errors:
* 401 when the key is missing or wrong
* 422 when the input is invalid

Fallback result, used when the LLM call fails after one retry:
* category other, priority high, needs_human true, fallback true
* summary is the ticket subject, cut to 30 words
* A ticket is never lost.

## 5. Labeling rules
The prompt and the eval labels both follow these rules.

Categories:
* billing: invoices, charges, refunds, plan changes
* bug: something is broken or behaves wrongly
* how_to: asks how to use an existing feature
* account_access: login, password, two factor, SSO, locked account
* feature_request: asks for something that does not exist
* other: anything else, spam or unclear

Priority:
* urgent: service down, data loss, a security issue, or many users blocked
* high: one customer fully blocked, a wrong charge, or cannot log in
* normal: a bug with a workaround, or a how to question
* low: a feature request or general feedback

needs_human is true when any of these hold:
* priority is urgent
* the customer threatens to cancel or take legal action
* fallback is true

Security rule: ticket text is data, never instructions. A ticket that says "ignore your rules" is still classified normally.

## 6. Configuration
All values come from environment variables. .env.example lists every one with a fake value.
* GEMINI_API_KEY
* GEMINI_MODEL
* SERVICE_API_KEY
* PROMPT_VERSION, default v1
* LLM_TIMEOUT_SECONDS, default 20
* EVAL_DELAY_SECONDS, default 4 (a pause between eval calls to respect free tier limits)

## 7. Folder structure
```
ticket_triage_api/
  CLAUDE.md
  PROJECT_SPEC.md
  README.md
  pyproject.toml
  .env.example
  .gitignore
  .dockerignore
  Dockerfile
  app/
    __init__.py
    main.py           FastAPI app, routes, auth check
    schemas.py        Pydantic request and response models
    classifier.py     Gemini call, timeout, retry, fallback
    config.py         reads environment variables
  prompts/
    triage_v1.md
  data/
    tickets_eval.jsonl
  evals/
    metrics.py        pure functions: accuracy, recall, percentiles
    run_eval.py       runs the classifier on the eval set
    results.md        generated report
  scripts/
    smoke_test.py     manual check against the real API
  tests/
    test_sanity.py
    test_api.py
    test_classifier.py
    test_metrics.py
```

## 8. Milestones

### M0. Project setup (2 hours)
Tasks:
* uv project on Python 3.12, with the folders above (empty files are fine)
* .gitignore that covers .env and .venv
* .env.example
* A README stub
* git init, then a public GitHub repo

Test first: tests/test_sanity.py asserts 1 + 1 == 2.

Acceptance:
* `uv run pytest` shows 1 passed.
* `git status` does not list .env.
* The repo is visible on GitHub.

### M1. API skeleton with a fake classifier (4 hours)
Tasks:
* schemas.py and main.py
* The Bearer key check
* A fake classifier that returns a fixed valid result

Tests first, in tests/test_api.py:
* /health returns 200 and the right JSON
* /triage with no key returns 401, and with a wrong key returns 401
* An empty subject returns 422
* A body longer than 5000 characters returns 422
* A valid request returns 200 and every field from section 4

Acceptance:
* All tests pass.
* `uv run uvicorn app.main:app --reload` starts, and http://127.0.0.1:8000/docs shows both endpoints.

### M2. Real Gemini classifier (5 hours)
Tasks:
* classifier.py uses Gemini structured output with the Pydantic schema
* Loads prompts/triage_v1.md, which applies the rules in section 5
* Uses the timeout and one retry, then returns the fallback result
* Measures latency
* scripts/smoke_test.py sends 3 sample tickets to the real API

Tests first, in tests/test_classifier.py, with the SDK client mocked:
* Valid model output is parsed into the response schema.
* Invalid output twice gives the fallback result with needs_human true.
* A timeout gives the fallback result.
* The prompt file is loaded and prompt_version is set.

Acceptance:
* All tests pass with no network.
* The smoke test, which I run myself, prints 3 valid results.
* No key appears in the code, the logs or the git history.

### M3. Eval set and eval report (6 hours)
Tasks:
* data/tickets_eval.jsonl holds 40 synthetic tickets, each with a labeled category, priority and needs_human:
  * By category: billing 7, bug 8, how_to 8, account_access 6, feature_request 6, other 5
  * At least 5 urgent tickets
  * 2 prompt injection attempts
  * 2 tickets in Arabic
  * 3 tickets that mix two issues
  * 2 angry cancel threats
* Claude Code may draft the tickets. I review and correct every label before any eval run.
* evals/metrics.py holds pure functions:
  * category accuracy
  * priority accuracy
  * urgent recall
  * needs_human recall
  * p50 and p95 latency
* evals/run_eval.py runs every ticket and writes evals/results.md with:
  * the date, model and prompt version
  * the metrics table
  * the fallback count
  * the average input and output tokens per ticket
  * the estimated cost per 1,000 tickets at the paid rate, citing the Gemini pricing page URL and the date checked
  * a list of every wrong prediction

Tests first, in tests/test_metrics.py: each metric function checked against tiny hand calculated inputs.

Targets:
* category accuracy at least 85%
* urgent recall at least 90%
* priority accuracy at least 70%
* If a target is missed, write prompts/triage_v2.md once, run the eval again, and keep both results in results.md. Honest numbers matter more than perfect numbers.

Acceptance:
* The metric tests pass.
* The eval completes.
* results.md contains the table and the error list.

### M4. Docker and Cloud Run (5 hours)
Tasks:
* Dockerfile and .dockerignore (which covers .env)
* Run the container locally with the env file
* Deploy to Cloud Run in a region that Claude Code confirms from the docs:
  * Store GEMINI_API_KEY and SERVICE_API_KEY in Secret Manager.
  * Set max instances to 1 and min instances to 0.
* A Google Cloud budget alert at 5 USD. I click every paid or cloud setting myself after Claude Code explains it.

Acceptance:
* Locally, the container's /health returns ok.
* The live URL's /health returns ok.
* On the live URL, /triage works with the key and returns 401 without it.
* The budget alert exists.
* The image contains no .env file.

### M5. Ship it (4 hours)
Tasks:
* README with:
  * the problem in 2 sentences
  * the live URL at the top
  * a screenshot or GIF
  * a Mermaid architecture diagram
  * how it works
  * the eval table
  * latency and cost
  * how to run it locally
  * known limitations
  * what comes next (P3)
* A 2 minute Loom walkthrough
* A LinkedIn post (outline in PLAYBOOK.md)

Acceptance:
* A fresh clone in a new folder passes `uv sync` and `uv run pytest`, following only the README.
* The Loom link works.

## 9. Out of scope
* Any web UI or chat page
* Databases, user accounts, logins
* Reading from real inboxes or ticket tools (that is P2)
* Answering tickets or RAG (that is P3)
* Agents, LangChain, LangGraph (that is P4)
* Multiple LLM providers, model routing, dashboards (that is P5)
* Fine tuning
* Kubernetes, Terraform, queues, async workers
* Rate limiting beyond the API key and max instances 1
* Real customer data

## 10. Definition of done
* All tests pass.
* The live URL works and is protected by the key.
* results.md has real numbers.
* The README is complete.
* The Loom is recorded and the LinkedIn post is published.
* I can explain every file without notes.
