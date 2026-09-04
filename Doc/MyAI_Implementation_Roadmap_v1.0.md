# MyAI Implementation Roadmap v1.0

## Phase 1: foundation

### Goal

Establish the stable base for the personal AI assistant.

### Tasks

- confirm and preserve current FastAPI structure
- stabilize environment configuration
- verify DB connection and models
- confirm provider registry and orchestration works
- define user and memory tables clearly

### Deliverables

- working health checks
- database schema ready
- provider orchestration working with at least one provider

## Phase 2: personalization

### Goal

Turn raw user data into personalized context.

### Tasks

- build user profile data model
- store memory with confidence and status
- create prompt builder that merges memory and profile into context
- create question classification and theme detection
- initialize interest and preference tracking

### Deliverables

- personalized prompt generation
- memory retrieval by question and theme
- user profile scores

## Phase 3: multi-AI comparison pipeline

### Goal

Generate better answers by comparing multiple public AI outputs.

### Tasks

- create provider selection strategy
- support multi-provider requests
- collect responses
- compare similarity and confidence
- reject low-confidence or conflicting results
- save accepted summaries to memory

### Deliverables

- multi-provider ask flow
- response aggregation and summary
- local judge/consensus layer

## Phase 4: workflow engine

### Goal

Execute scheduled and event-triggered tasks with step-by-step processing.

### Tasks

- define workflow schema
- create trigger manager
- define step execution model
- enable sequential step data passing
- support result validation at each stage

### Deliverables

- event-driven task execution
- workflow logs
- data passing between steps

## Phase 5: calendar and mail integration

### Goal

Analyze personal data to understand habits and needs.

### Tasks

- Google Calendar sync
- Microsoft/Naver calendar import support
- Gmail / IMAP ingestion
- event and mail normalization
- personal pattern extraction

### Deliverables

- calendar event storage
- mail response and thread parsing
- schedule pattern and preference extraction

## Phase 6: memory and wiki summary

### Goal

Support short, searchable, high-value personal knowledge.

### Tasks

- create summary memory tables
- generate short wiki entries from important memories
- support indexed search over summary strings
- create one-page summaries and detail expansion

### Deliverables

- wiki summary store
- memory retrieval with summary-first output
- fast keyword search

## Phase 7: dashboard and monitoring

### Goal

Make system easier to operate and debug.

### Tasks

- dashboard for overall status
- AI response history
- workflow execution logs
- memory confidence trends
- daily and weekly report views

### Deliverables

- monitoring UI
- system health and traceability
- easier debugging and operation

## Phase 8: QA and recovery

### Goal

Make the system reliable and recoverable.

### Tasks

- test API flows
- test workflow step execution
- test multi-provider consistency handling
- test DB recovery and bootstrap
- test Docker startup and local rebuild

### Deliverables

- repeatable QA checklist
- recovery procedures
- backup and restore plan
