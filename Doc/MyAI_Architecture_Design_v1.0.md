# MyAI Architecture Design v1.0

## 1. Purpose

This document defines the architecture for a personal AI secretary for a single user running on a desktop Ubuntu environment.

The system should:

- learn the user’s preferences, behavior, and communication patterns
- use local memory as the primary personal data layer
- combine multiple public AI providers
- compare responses and keep only high-confidence conclusions
- automate recurring tasks through scheduled workflows
- support future mobile or cloud extension without large refactoring

## 2. Design principles

1. Simplicity first
2. Local data protection first
3. Keep the existing codebase structure
4. Prefer a step-by-step workflow over direct ad hoc prompting
5. Make debugging easy with explicit logs and stages
6. Optimize for recoverability and migration

## 3. Core architecture

```text
User
  |
  v
Desktop UI / Web Shell
  |
  v
FastAPI Application
  |-- Personalization Layer
  |-- Workflow Engine
  |-- AI Orchestrator
  |-- Memory Service
  |-- Scheduler / Trigger Manager
  |-- Integrations Layer
  |
  +--> PostgreSQL
  +--> Local LLM (Ollama)
  +--> Public AI Providers
  +--> Calendar / Mail / Notes Adapters
  +--> Markdown Wiki / Summary Store
```

## 4. Component responsibilities

### 4.1 API layer

- request handling
- user sessions
- AI chat interface
- workflow trigger endpoint
- health and operational status

### 4.2 Personalization layer

- user profile analysis
- preference scoring
- memory retrieval and filtering
- personalized prompt generation
- topic interest tracking

### 4.3 Memory layer

- store user facts and observed preferences
- store confidence scores
- maintain history of accepted and rejected memories
- reload data on service restart

### 4.4 AI provider layer

- Gemini
- GPT/OpenAI
- Copilot equivalent API path
- Grok / other providers as optional services
- local Ollama as judge and summary model

### 4.5 Workflow engine

- trigger on calendar events or schedule
- parse task content
- call data gathering steps
- compare results
- save accepted outcomes to memory and summary logs

### 4.6 Integration layer

- Google Calendar
- Microsoft Calendar
- Naver Calendar
- Gmail / IMAP mail fetchers
- local notes and diary imports

## 5. Minimal CNF structure

For a low-spec desktop, the target is a minimal containerized architecture.

| Layer | Component | Purpose | Priority |
|---|---|---|---|
| Runtime | Ubuntu + Docker Compose | install and run services | High |
| API | FastAPI | backend app | High |
| Database | PostgreSQL | persistent metadata and memory | High |
| Local AI | Ollama | local summarization and judgement | High |
| Cache | Redis | optional caching and session state | Medium |
| Scheduler | APScheduler | time-based triggers | High |
| Workflow | custom workflow engine | step execution | High |
| UI | Streamlit or minimal dashboard | monitoring and control | Medium |

## 6. Design choice for this project

The project already contains a workable base:

- FastAPI application layer
- SQLAlchemy data layer
- provider registry and orchestration
- personalization prompt builder
- memory-related models and services

Therefore, the design should preserve this structure and extend it rather than replace it.

## 7. Data model goals

The database should support:

- user identity
- user profile and preferences
- memory entries and confidence
- AI provider configs
- schedule events
- email message data
- workflow definitions and executions
- AI response logs
- summary wiki entries

## 8. Processing flow

### 8.1 Question flow

1. User enters a question
2. System identifies question theme
3. Personalization service adds user profile and memory context
4. AI provider selection engine chooses relevant providers
5. Providers receive personalized prompts
6. Local LLM compares results
7. High-confidence summaries are accepted
8. Accepted facts are saved to memory and history

### 8.2 Calendar trigger flow

1. Google Calendar event is detected
2. Event title and description are parsed
3. Workflow match is checked
4. Needed data from web or local sources is collected
5. Summary is generated
6. Final result is saved under memory or task execution history

## 9. AI selection pattern

The system should begin with 3 providers:

- Gemini
- ChatGPT API
- Copilot-compatible provider

Selection logic:

- analyze question type
- map question to provider strengths
- allow manual override
- adapt provider ranking based on historical success and personal preference

## 10. Memory policy

Use a confidence-based memory model:

- DRAFT: not yet accepted
- CONFIRMED: accepted as useful personal memory
- ARCHIVED: no longer active but retained for history

Accepted memory should be stored in both:

- operational memory table
- summary memory table for fast recall

## 11. Implementation constraints

- keep code understandable for PM-level maintainers
- avoid complex microservice patterns
- keep logs explicit and simple
- keep each workflow stage observable
- use Docker and local file backups for recoverability

## 12. Summary

This architecture is designed for a single-user, desktop-first personal AI secretary that remains:

- simple to build
- simple to debug
- easy to migrate
- easy to back up
- adaptable to future extension
