# MyAI Detailed Design v1.0

## 1. Goal

This document defines the implementation details for the personal AI secretary while preserving the current project structure.

## 2. Design scope

The project must support:

- user input question processing
- memory retrieval by user and topic
- personalized prompt generation
- multiple public AI provider calls
- response comparison and local consensus
- workflow-based execution
- personal knowledge summary and search

## 3. Functional architecture

### 3.1 Input layer

- UI or API receives a plain text question
- user_id is associated with the request
- question is classified by topic and workflow type

### 3.2 Context preparation layer

- load user profile
- load recent memory entries
- load goals, preferences, and projects
- create a structured context package

### 3.3 Prompt adaptation layer

- personalize the prompt for each provider
- keep the local context separate from the raw user question
- preserve concise, structured instruction style

### 3.4 AI orchestration layer

- choose public AI candidates
- execute in parallel where possible
- collect outputs
- evaluate similarity and confidence
- call local LLM only for summary and consensus

### 3.5 Persistence layer

- save accepted memories
- save AI response logs
- save workflow states and execution traces
- save summary wiki entries

## 4. Implementation modules

### 4.1 Existing modules to preserve

- app/main.py
- app/api/ai.py
- app/core/config.py
- app/db/database.py
- app/personalization/services/prompt_builder.py
- app/personalization/services/personalization_service.py
- app/ai/services/multi_provider_orchestrator.py
- app/models/*

### 4.2 New modules to add

- app/services/question_classifier_service.py
- app/services/provider_selector_service.py
- app/services/response_similarity_service.py
- app/services/workflow_engine_service.py
- app/services/scheduler_service.py
- app/services/calendar_sync_service.py
- app/services/mail_sync_service.py
- app/services/personal_profile_service.py
- app/services/wiki_summary_service.py
- app/services/trigger_manager_service.py

## 5. Data design

### 5.1 Core tables

#### users
- id
- email
- display_name
- created_at

#### user_profile
- id
- user_id
- personality_summary
- preference_score
- interest_tags
- calendar_pattern
- updated_at

#### memory_items
- id
- user_id
- memory_type
- memory_key
- memory_value
- confidence
- source
- status
- created_at

#### ai_response_log
- id
- user_id
- provider
- model
- request_summary
- response_summary
- similarity_score
- accepted
- created_at

#### workflow_definition
- id
- user_id
- name
- trigger_type
- trigger_config
- workflow_json
- enabled
- created_at

#### workflow_execution
- id
- user_id
- workflow_id
- status
- started_at
- finished_at
- result_summary

#### workflow_step_result
- id
- execution_id
- step_name
- input_summary
- output_summary
- success
- created_at

#### calendar_events
- id
- user_id
- external_id
- title
- description
- event_start
- event_end
- event_type
- tags
- created_at

#### mail_messages
- id
- user_id
- thread_id
- sender
- subject
- body
- received_at
- tags
- created_at

## 6. Workflow engine design

### 6.1 Workflow structure

```json
{
  "workflow_name": "calendar_task_summary",
  "trigger": "calendar_event",
  "steps": [
    {"name": "parse_event", "type": "extract"},
    {"name": "match_task", "type": "router"},
    {"name": "collect_context", "type": "data"},
    {"name": "call_public_ai", "type": "ai"},
    {"name": "summarize_result", "type": "llm"},
    {"name": "save_memory", "type": "persist"}
  ]
}
```

### 6.2 Execution model

- workflow_definition stores the template
- workflow_execution stores the current run
- workflow_step_result stores each step output
- step inputs are passed in a normalized data object
- each step must return a success flag and summary

## 7. Provider strategy

### 7.1 Default provider order

- Gemini
- OpenAI / GPT
- Copilot-compatible API path
- Grok or optional providers

### 7.2 Decision logic

- analyzer decides question type
- preference engine chooses the stronger provider for that topic
- user-related questions prioritize memory + personal context
- low confidence outputs are not accepted automatically

## 8. Memory policy

### 8.1 storage structure

- memory_item stores raw fact-based memory
- summary_memory stores compressed personal knowledge
- confidence is calculated from evidence and repetition

### 8.2 status values

- DRAFT
- CONFIRMED
- ARCHIVED
- REJECTED

### 8.3 acceptance rule

A memory should auto-save only when:

- at least two providers agree or are strongly similar
- the local judge score is above threshold
- the fact matches the user's known behavioral pattern

## 9. Implementation order

### Stage 1

- preserve and stabilize base app
- validate database and memory retrieval
- verify provider orchestration behavior

### Stage 2

- add structured user profile and memory model
- add prompt personalization with theme segmentation
- add question classification

### Stage 3

- add multi-provider comparison and local judge
- add summary and acceptance logic

### Stage 4

- add workflow engine and scheduler
- add calendar and mail integrations

### Stage 5

- add wiki and report summaries
- add dashboard and logs

### Stage 6

- test recovery, backup, and rebuild flow

## 10. Implementation priority in this repo

Highest priority files:

- app/core/config.py
- app/api/ai.py
- app/personalization/services/prompt_builder.py
- app/personalization/services/personalization_service.py
- app/ai/services/multi_provider_orchestrator.py
- app/models/*
- app/repositories/*

## 11. Coding principles

- keep the current base code intact
- do not replace working components with a full rewrite
- add functions in a clear service layer
- prefer explicit logs and structured return values
- keep each stage testable in isolation

## 12. Summary

This detailed design keeps the current project stable while adding the capabilities needed for a personal AI secretary:

- personal memory
- multi-AI orchestration
- workflow automation
- schedule and mail understanding
- summary and wiki generation
- low-complexity but extensible architecture
