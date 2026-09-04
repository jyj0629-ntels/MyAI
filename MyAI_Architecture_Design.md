# MyAI Personal Assistant - High-Level Architecture Design

## 1. 설계 목표 요약

이 설계는 사용자의 개인 데이터, 일정, 메일, 메모, 관심사, 성향, 과거 질문 이력 등을 기반으로 "나만의 AI 비서"를 만드는 것입니다.

핵심 목표는 다음과 같습니다.

- 개인별 성향과 취향을 반영한 프롬프트 구성
- 공개 AI(GPT, Gemini, Copilot 등)에 질의할 때 개인화된 문장으로 변환
- 다수의 AI 응답을 비교하고, 동일하거나 유사한 결론을 합치기
- 로컬 LLM과 메모리를 활용해 개인화된 판단과 요약 수행
- 일정, 메일, 메모, 질문 이력을 기반으로 자동 워크플로우 실행
- 데스크톱 Ubuntu 환경에서 저사양 PC에서도 동작 가능한 단순하고 확장 가능한 아키텍처 구성
- 유지보수와 디버깅이 쉬운 구조, 빠른 복구 가능 구조

---

## 2. 설계 원칙

1. 단순성 우선
   - 최신 기술보다 유지보수성과 디버깅 편의성을 우선
   - 복잡한 마이크로서비스 구조를 채택하지 않고 최소 CNF 구조로 구성

2. 개인 데이터 중심
   - 이메일, 캘린더, 메모, 질문 기록, 메모리, 관심사, 일정, 일기 등을 핵심 입력으로 사용

3. 로컬 중심 + 외부 AI 보조
   - 민감한 개인 정보는 로컬에서 관리
   - 공개 AI는 질문 변환 후 결론 보조용으로 사용

4. 워크플로우 기반 처리
   - 단순 프롬프트 전달이 아니라 단계별 데이터 가공, 검증, 요약, 저장, 선택을 수행

5. 확장성
   - AI 제공자 추가가 쉬운 Provider registry 구조 유지
   - 데이터 소스 추가가 쉬운 Adapter 구조 유지
   - 스케줄러와 workflow engine 분리

---

## 3. 최종 설계 방향

### 3.1 전체 구조

MyAI는 아래 7개 핵심 영역으로 구성합니다.

- 사용자 프로필 및 성향 엔진
- 캘린더/메일/메모 수집기
- 로컬 메모리 저장소
- AI Provider Orchestrator
- Workflow Engine
- Local LLM Judge / Summarizer
- UI + Desktop App Shell

### 3.2 기본 실행 구조

- Ubuntu Desktop OS
- Docker Compose 기반 경량 CNF 운영
- FastAPI 백엔드 서비스 1개
- PostgreSQL 1개
- Ollama 1개
- Redis(선택) 1개
- Nginx(선택) 1개
- Data sync worker 1개
- Scheduler 1개

---

## 4. 최소 CNF 기반 아키텍처

### 4.1 아키텍처 개요

```text
[User / Desktop UI]
        |
        v
[MyAI Desktop App / Web UI]
        |
        v
[API Gateway / FastAPI]
   |------------------------------------|
   |                                    |
   v                                    v
[Workflow Engine]                 [Personalization Engine]
   |                                    |
   v                                    v
[Scheduler + Triggers]           [Memory + Profile Store]
   |                                    |
   v                                    v
[Data Adapters]                 [Local LLM Judge]
   |  - Google Calendar                |
   |  - Gmail / Mail Server            |
   |  - Local Notes / Diary            |
   |  - User Preferences               |
   v                                    v
[Normalized Data Layer]         [Public AI Orchestrator]
   |                                    |
   +------------> [PostgreSQL] <--------+
      |
      +--> [Ollama Local Model]
      +--> [Redis Cache]
      +--> [File Storage / Markdown / Wiki]
```

### 4.2 CNF 설계 방안

다음은 저사양 데스크톱용으로 맞춘 "최소 CNF" 구성입니다.

- 하나의 메인 API 컨테이너로 서비스 운영
- DB와 로컬 AI는 별도 컨테이너로 분리
- 워크플로우와 스케줄러를 별도 프로세스로 분리
- 데이터 처리는 이벤트 기반이 아니라 배치/시퀀스 워크플로우 중심
- 모든 핵심 기능을 Docker Compose로 단일 환경에서 쉽게 재시작 및 복구

---

## 5. 플랫폼 구성과 역할

| 플랫폼 | 구성 요소 | 역할 | 설치 우선순위 | 메모리 권장 | 비고 |
|---|---|---|---:|---:|---|
| Desktop OS | Ubuntu 22.04 LTS | 기본 실행 환경 | 필수 | - | 가장 이식성이 높음 |
| Runtime | Docker + Docker Compose | 컨테이너 운영 | 필수 | 2~4GB | 유지보수 용이 |
| API | FastAPI | REST 엔드포인트, AI 요청 처리 | 필수 | 1~2GB | 기존 프로젝트와 가장 맞음 |
| DB | PostgreSQL | 사용자, 메모리, 일정, AI 이력 저장 | 필수 | 1~2GB | 안정적이고 복구 용이 |
| Local AI | Ollama | 개인 로컬 추론, 요약, 판단 | 필수 | 4~8GB | 가장 중요 |
| Cache | Redis | 워크플로우 상태, 세션, 빠른 캐시 | 선택 | 512MB~1GB | 경량 옵션 |
| Scheduler | APScheduler / cron | 정기 작업 | 필수 | 256MB~512MB | 단순하고 안정적 |
| Wiki | Markdown + local search | 핵심 요약 저장 | 필수 | 256MB~512MB | 빠르고 이식성 좋음 |
| UI | Streamlit / Gradio / FastAPI HTML | 데스크톱 연동용 기본 UI | 선택 | 512MB~1GB | 빠른 개발 |
| Monitoring | Prometheus + Grafana | 선택적 운영 모니터링 | 선택 | 1GB 이상 | 나중 확장 |

---

## 6. 기존 프로젝트와의 매칭 설계

현재 프로젝트는 다음 구조를 이미 갖추고 있습니다.

- FastAPI 기반 API
- SQLAlchemy 기반 DB 모델
- Provider registry 기반 Public AI 연동
- Personalization layer 기반 사용자 context 구성
- Multi-provider orchestration 구조

이 구조를 유지하면서 아래 보완이 필요합니다.

### 보완 대상

1. 사용자 성향 분석 엔진
2. 일정/메일/일기 ingestion pipeline
3. 워크플로우 엔진
4. 메모리 동기화 / 학습 저장 구조
5. AI 응답 비교 및 결론 선택 엔진
6. Wiki 요약 기능
7. 사용자별 질문 패턴 분석기
8. 데이터 보존 및 재시작 복구 기능

---

## 7. 핵심 모듈 설계

### 7.1 사용자 프로필 및 개인화 엔진

기본 동작:

- 사용자의 관심사, 질문 패턴, 일정 패턴, 메일 응답 패턴, 일기 내용을 분석
- 연령, 직업, 선호, 가치관, 일상 리듬, 행동 습관을 저장
- 매 질문 전에 개인 특화 프롬프트 생성

필수 데이터:

- user_profile
- user_interest
- user_personality_vector
- user_question_pattern
- user_schedule_pattern
- user_memory_summary

기능:

- 최근 30일 관심사 추정
- 테마별 성향 점수 계산
- 질문 유형별 추천 AI 우선순위 계산
- 공개 AI 질의 전에 사용자 맥락 주입

---

### 7.2 캘린더 및 메일 연동 계층

대상:

- Google Calendar
- Microsoft Calendar
- Naver Calendar
- Gmail
- Naver Mail
- 기타 IMAP 기반 메일 서버

처리 방식:

- OAuth 또는 App Password 기반 인증
- 정기 동기화
- 이벤트를 정규화하여 DB 저장
- 제목, 본문, 시간, 태그, 의미 단위로 가공

필수 저장 테이블:

- calendar_events
- mail_messages
- mail_threads
- user_task_trigger
- extracted_tasks

---

### 7.3 워크플로우 엔진

기본 개념:

- 사용자가 "일정에 맞춘 작업 실행"을 등록하면 해당 트리거가 발생
- 워크플로우는 Step by Step으로 동작
- 각 단계마다 입력 데이터, 조건, 출력 데이터를 검증

예시:

1. Google Calendar에서 제목이 "AI할일"인 이벤트 감지
2. 이벤트 내용 파싱
3. 제품/가격/배송 조건 추출
4. 웹/쇼핑/가격 비교 모듈 호출
5. 최저가, 쿠폰, 배송비 포함 최종가 계산
6. Local LLM으로 요약
7. 사용자에게 알림 또는 메모 저장

필수 구성:

- trigger_manager
- workflow_definition
- workflow_execution
- workflow_step_result
- workflow_data_store

---

### 7.4 Public AI Orchestrator

기본 구조:

- 각 AI는 provider로 등록
- 질문 종류에 따라 적합한 AI 선택
- 여러 AI에게 동시에 질의 가능
- 로컬 LLM이 결과를 비교하고 정합성 검증

설계 원칙:

- 질문마다 AI별 특성 반영
- 동일한 결론이 2개 이상 나오면 해당 답변을 선택
- 유사도가 낮으면 사용자에게 확인 또는 저장 여부 선택

예시 기준:

- 항목 비교/합리적 의사결정 → GPT 또는 Gemini
- 빠른 요약 → Copilot 또는 Gemini
- 실시간 추천/검색 → GPT 또는 Grok
- 제안형 대화 → Copilot

---

### 7.5 Local LLM Judge / Consensus Engine

이 모듈은 개인용 AI 비서의 핵심 엔진입니다.

기능:

- 여러 공개 AI 응답을 비교
- 핵심문장 추출
- 사실점 검증
- 사용자 취향 적합도 계산
- 80% 이상 유사 응답 통합
- 로컬 DB에 메모리로 저장

정합성 규칙:

- 2개 이상 응답이 유사하면 저장 후보로 인정
- 유사도가 낮으면 사용자 확인 필요
- 저장 여부는 사용자 선택 또는 자동 저장 정책으로 통제

---

### 7.6 메모리와 Wiki 시스템

기본 특성:

- 모든 핵심 데이터를 요약형으로 관리
- 긴 설명 대신 1페이지 핵심 요약 방식 사용
- 필요한 경우 상세 페이지 확장
- 검색을 빠르게 하기 위해 markdown 기반 일관성 유지

저장 방식:

- personal_memory
- memory_summary
- wiki_entries
- memory_tags
- preference_history

Wiki는 다음 구조로 설계합니다.

- Topic 단위 문서
- Summary: 5~8줄 요약
- Key points: 핵심 포인트 3~5개
- Evidence: 근거 데이터 링크
- Action: 추천 행동

---

## 8. 데이터 모델 설계 개요

### 8.1 핵심 테이블

| 테이블 | 용도 | 비고 |
|---|---|---|
| users | 사용자 기본 정보 | 1명 중심 설계 |
| user_profile | 성향, 관심사, 관심 분야 | 개인화 데이터 |
| calendar_events | 일정 이벤트 | 구글/마이크로소프트/네이버 캘린더 |
| mail_messages | 메일 메시지 | Gmail/IMAP 기반 |
| user_tasks | 사용자가 등록한 작업 | 자동 실행 대상 |
| memory_items | 개인 메모리 | 사용자 맞춤 기억 |
| memory_summary | 요약 메모리 | 빠른 반복 조회 |
| ai_provider_config | AI 연결 설정 | 공개 AI 키/모델 정보 |
| ai_response_log | AI 답변 로그 | 비교/학습용 |
| workflow_definition | 워크플로우 정의 | 재사용 가능 |
| workflow_execution | 실행 이력 | 디버깅/학습 |
| workflow_step_result | 단계별 결과 | 검증 및 데이터 흐름 |
| wiki_entries | 축약 문서 | 키워드 기반 검색 |
| preference_history | 성향 변화 추적 | 월간/주간 그래프 생성 |

---

### 8.2 기본 DB 스키마 예시

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    display_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_profile (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    personality_summary TEXT,
    preference_score JSONB,
    interest_tags JSONB,
    calendar_pattern JSONB,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE memory_items (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    memory_type VARCHAR(50),
    memory_key VARCHAR(255),
    memory_value TEXT,
    confidence FLOAT,
    source VARCHAR(100),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE calendar_events (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    external_id VARCHAR(255),
    title TEXT,
    description TEXT,
    event_start TIMESTAMP,
    event_end TIMESTAMP,
    event_type VARCHAR(100),
    tags JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE workflow_definition (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    name VARCHAR(255),
    trigger_type VARCHAR(100),
    trigger_config JSONB,
    workflow_json JSONB,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 9. 데이터 흐름 설계

### 9.1 질문 처리 흐름

1. 사용자가 텍스트 질문 입력
2. 로컬 시스템이 질문 유형 분석
3. 사용자 프로필 + 메모리 + 일정 + 관심사를 결합
4. 질문 유형에 따라 공개 AI 선택
5. 선택된 AI들에 사용자 맞춤 질의문 생성
6. 각 AI 응답 수집
7. 로컬 LLM이 응답 요약 및 유사성 비교
8. 유사 응답이 기준치 이상이면 합치기
9. 결과를 DB와 메모리에 저장
10. 사용자에게 최종 요약 전달

### 9.2 일정 트리거 흐름

1. Google Calendar 이벤트 감지
2. 제목과 내용을 파싱
3. 이벤트 유형 분류
4. 관련 워크플로우 탐색
5. 필요 시 웹 검색, 가격조회, 메일 분석, 일정 정리 수행
6. 결과를 메모리/알림으로 저장
7. 사용자에게 요약 보고서 전달

### 9.3 성향 분석 흐름

1. 일정 분석
2. 메일 스타일 분석
3. 질문 이력 분석
4. 일기/메모 분석
5. 관심사 주기적 계산
6. 벡터 또는 JSON 형태로 점수화
7. 주간/월간 변화 그래프 생성
8. 사용자에게 표시

---

## 10. AI 선택 전략

### 10.1 기본 원칙

- AI는 "질문 내용의 성격"에 따라 선택
- 사용자는 고정 3개 AI를 기본 등록
- 필요 시 특정 AI만 선택 가능
- 로컬 AI는 비교 및 요약을 담당

### 10.2 추천 기준

| 질문 유형 | 추천 AI | 이유 |
|---|---|---|
| 비교/분석 | Gemini, GPT | 구조적 비교에 강함 |
| 빠른 요약 | Copilot, Gemini | 간결한 요약에 유리 |
| 아이디어 생성 | GPT, Copilot | 창의적 제안에 강함 |
| 실무적 업무 계획 | GPT, Copilot | 실용적 구체화 |
| 특정 문맥 기반 추론 | Gemini | 문맥 적합성 |
| 가격/선택 최적화 | GPT, Gemini | 비교와 판단력이 좋음 |
| 일상 일정 기반 판단 | Local LLM + Gemini | 개인 맥락과 결합 시 우수 |

---

## 11. Open Source 도구 설치 단계 설계

### Stage 1 - 기본 운영 환경

필수 설치:

- Ubuntu 22.04 LTS
- Docker
- Docker Compose
- Git
- curl
- jq
- Python 3.12
- PostgreSQL Client

목적:

- 개발/실행 환경 표준화
- 재배포 가능 구조 확보

---

### Stage 2 - 로컬 AI 서버

설치 도구:

- Ollama
- Qwen3 또는 Llama 기반 모델
- lightweight 모델 우선 활용

목적:

- 로컬 요약
- 로컬 판단
- 개인 정보 보호

권장 구성:

- qwen3:14b 또는 유사 용량 모델 우선
- GPU가 없으면 CPU 기반 실행
- 추론 속도와 메모리를 고려해 8B급 모델 우선

---

### Stage 3 - DB와 서비스 구성

설치 도구:

- PostgreSQL
- Redis(선택)
- FastAPI
- SQLAlchemy
- Alembic

목적:

- 개인 데이터 보관
- 메모리/이력/워크플로우 저장
- AI 요청 관찰

---

### Stage 4 - 데이터 연동

설치 도구:

- Google Calendar API
- Gmail API
- Microsoft Graph API
- IMAP/SMTP 연동
- 파일 시스템 기반 메모/마크다운 로더

목적:

- 일정/메일/기록을 자동 수집
- 개인 특성 분석

---

### Stage 5 - Workflow & Scheduler

설치 도구:

- APScheduler
- cron
- custom workflow engine

목적:

- 트리거 실행
- 주기적 검토
- 이벤트 기반 자동화

---

### Stage 6 - UI 및 관리 도구

설치 도구:

- Streamlit
- Gradio
- FastAPI Admin or custom dashboard

목적:

- 간단한 운영 확인
- AI 결과 히스토리 확인
- 메모리 상태 확인

---

## 12. 아키텍처 설계 표

| 구분 | 구성 요소 | 기능 | 구현 언어 | 비고 |
|---|---|---|---|---|
| Frontend | Desktop shell + dashboard | 사용자 입력, 결과 확인 | Python / Streamlit / Next.js 가능 | 단순하고 빠름 |
| API | FastAPI | 사용자 요청, 공용 AI 호출, 상태 관리 | Python | 기존 구조와 가장 일치 |
| Workflow | Scheduler + Engine | Trigger 시퀀스, 이벤트 처리 | Python | 가장 유지보수 적합 |
| Personalization | Profile Analyzer | 성향/관심사 분석 | Python | 사용자 중심 핵심 |
| Memory | PostgreSQL + summary tables | 메모리 저장/조회 | SQL / Python | 핵심 DB |
| Local AI | Ollama | 요약, 판단, 보조 추론 | Go / 모델 | 로컬 개인 데이터 보호 |
| Public AI | Gemini, GPT, Copilot | 외부 질문/비교 | REST API | 외부 연동 |
| Sync | Calendar + Mail fetchers | 일정/메일 연동 | Python | OAuth 사용 |
| Search/Wiki | markdown + SQLite FTS or PostgreSQL full-text | 요약 검색 | Python / SQL | 매우 중요 |
| Debug/QA | Logging, tests, health checks | 문제 확인, 재현 | Python / pytest | 필수 |

---

## 13. 단계별 설계와 AI 활용 전략

| 단계 | 내용 | 핵심 목적 | 추천 AI | 비고 |
|---|---|---|---|---|
| 1 | 상위 설계 | 전체 구조 정의 | ChatGPT, Gemini | 전반적 설계 및 문맥 이해 |
| 2 | DB Schema 설계 | 저장 구조 설계 | Gemini, Copilot | 정규화와 데이터 명확화 |
| 3 | Platform 설계 | Ubuntu/Docker/Ollama 구성 | Copilot, Gemini | 실무적 구축 경험 |
| 4 | API 설계 | FastAPI 구조 | ChatGPT, Copilot | 구현 적합성 |
| 5 | Workflow 설계 | step-by-step 처리 | ChatGPT, Gemini | 루틴 설계를 위해 적합 |
| 6 | 프로그래밍 | 코드 작성 | Copilot | 구현 속도 우위 |
| 7 | Debugging | 문제 해결 | ChatGPT, Gemini | 원인 파악에 유리 |
| 8 | 시험 | 기능 검증 | Copilot, Gemini | 문서화, 체크리스트 |
| 9 | QA | 검수 및 회귀 | ChatGPT | 검토와 기준 설정 |
| 10 | 운영 개선 | 유지보수/복구 | Gemini | 안정성 강화 |

---

## 14. AI별 효율성 가이드

### ChatGPT

- 상위 설계, 요구문서 검토, 구조 정리, 전체 관점 설계에 적합
- 복잡한 요구를 정리하고 문맥을 정돈하는 데 강함
- 구현 전 설계 문서 수립 시 최고 효율

### Gemini

- 개인 데이터, 일정, 메모, 패턴 분석, 성향 정리 등에 적합
- 문맥 연결 및 요약에 강함
- 메모리와 성향 분석 설계에 매우 유용

### Copilot

- 코드 작성, 구현, 디버깅, 구조화된 코드 생성에 강함
- 빠른 구현 속도와 실시간 편집에 매우 효율적
- 코드 생성과 테스트 보완에 적합

---

## 15. 추천 개발 순서

1. 데이터 모델 초안 작성
2. FastAPI 기본 구조 정리
3. PostgreSQL 연동
4. 사용자 프로필 및 메모리 저장 구조 구현
5. Calendar/Mail ingestion 구현
6. 질문 입력 → personalized prompt 생성
7. Multi AI provider orchestration 구현
8. Local LLM judge 구현
9. 워크플로우 엔진 구현
10. Wiki/요약 검색 구현
11. 자동 트리거 및 일간/주간 리포트 구현
12. 테스트/QA/복구 검증

---

## 16. 최종 권장 아키텍처

### 가장 적합한 최종 구성

- Ubuntu Desktop + Docker Compose
- FastAPI 메인 서비스
- PostgreSQL + Ollama + Redis
- Calendar/Mail adapters
- Personalization + Memory engine
- Workflow engine + Scheduler
- Multi-provider AI orchestrator
- Local LLM judge / consensus engine
- Markdown wiki + summary dashboard

### 왜 이 구조가 최적인가

- 구현이 단순하고 디버깅이 쉽다
- 로컬 환경에서 운영이 가능하다
- 복구와 재설치가 쉽다
- 외부 AI 연동은 가능하지만 개인 데이터는 로컬을 유지한다
- 확장성이 좋고 새 AI provider를 추가하기 쉽다
- 저사양 데스크톑에서도 시작 가능하다

---

## 17. 보완 필요 로직 반영 설계

다음 로직은 현재 프로젝트에 반드시 추가해야 합니다.

### 17.1 사용자 질문 처리 로직

- 사용자 질문 입력
- 질문 유형 인식
- 개인 메모리 기반 컨텍스트 확장
- 질문별 AI 적합성 계산
- AI별 맞춤 문장 생성
- 다중 AI 동시 호출
- 결과 비교 및 유사성 분석
- 기준치 이상이면 저장/학습
- 기준치 미만이면 사용자 확인

### 17.2 메모리 학습 로직

- 사용자의 질문/답변/일정/메일 기반 데이터 저장
- confidence 점수 부여
- status 값 관리: DRAFT / CONFIRMED / ARCHIVED
- 재시작 시 DB에서 메모리 복원
- 로컬 LLM 재시작 후 즉시 메모리 재적재

### 17.3 자동 트리거 로직

- 일정 제목 기반 감지
- 사전 정의된 workflow 매칭
- 적절한 AI 또는 tool chain 호출
- 결과 저장 및 알림

---

## 18. 추천 기술 스택 최종안

| 범주 | 추천 기술 |
|---|---|
| 언어 | Python 3.12 |
| API | FastAPI |
| DB | PostgreSQL |
| ORM | SQLAlchemy + Alembic |
| Local AI | Ollama |
| Workflow | APScheduler + custom workflow engine |
| Cache | Redis |
| UI | Streamlit or FastAPI templates |
| AI provider | Gemini, OpenAI, Groq, Copilot API |
| 검색 | PostgreSQL full-text + Markdown wiki |
| 테스트 | pytest |
| 배포 | Docker Compose |

---

## 19. 중요 설계 결론

이 프로젝트는 "고급 기술을 많이 쓰는 시스템"이 아니라, "개인 맞춤형 판단을 안정적으로 관리하는 시스템"을 만드는 것이 핵심입니다.

그래서 가장 중요하게 고려해야 할 것은 다음입니다.

- 개인 성향과 패턴을 정확히 수집하는 구조
- 로컬 AI와 공개 AI를 조합하는 가장 단순한 오케스트레이션
- 데이터가 누적되고 다시 재사용되도록 만드는 메모리 설계
- 워크플로우를 디버깅하기 쉽도록 만드는 Step-based 구조
- 복구 시간과 재설치 시간을 줄이는 운영 디자인

이 설계를 기준으로 다음 단계부터는 상세 설계와 실제 코드 개발을 진행하면 됩니다.

---

## 20. 권장 문서 구성

다음 문서를 순서대로 작성하는 것을 권장합니다.

1. 사용자 요구사항 정의서
2. 데이터 흐름도
3. ERD
4. Workflow 정의서
5. API 명세서
6. AI provider 설정서
7. 운영/복구 절차서
8. 테스트 체크리스트

---

## 21. 최종 요약

이 설계는 "개인 맞춤형 AI 비서"를 가장 실용적이고 안정적으로 구현하는 데 적합한 최소 CNF 구조입니다.

- 데스크톱 Ubuntu 환경
- Docker Compose 기반 빠른 설치
- FastAPI + PostgreSQL + Ollama 중심
- AI provider orchestration
- 워크플로우 엔진
- 개인 메모리와 성향 분석
- 요약형 wiki와 자동 보고서
- 디버깅 및 복구가 쉬운 구조

이 구조를 기반으로 단계별 개발을 진행하면, 사용자의 요구사항을 가장 안정적으로 만족시키며 향후 모바일 확장까지 자연스럽게 이어갈 수 있습니다.
