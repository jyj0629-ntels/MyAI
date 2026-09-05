# MyAI Architecture Design v1.1

## 1. 변경 요약

이 문서는 현재 프로젝트 코드 기준으로 재정리한 설계 문서이다.

기존 설계에서 추상적인 구조를 설명했다면, 이번 v1.1은 실제 구현 상태를 반영한다.

핵심 변경 사항은 다음과 같다.

- 사용자 질문을 단순 전송하지 않고 DB/메모리 기반 컨텍스트를 구성하여 개인화된 prompt를 생성
- Public AI별로 전송되는 prompt를 로그로 기록하고, 각 단계별 소요 시간을 표시
- 사용자가 특정 provider만 선택해서 해당 질문에 적용할 수 있는 체크박스 기반 흐름
- 여러 provider의 응답을 합치고, 사용자 선호도와 응답 format에 맞춰 최종 출력 포맷을 정리
- 응답 format을 DB에서 CRUD로 관리할 수 있도록 API와 Swagger 노출
- 채팅 이력과 conversation memory의 저장/복구 구조를 정교화
- provider별 quota/status 확인 로직을 안전한 fallback 형태로 제공

---

## 2. 현재 구현된 아키텍처

```text
[User Web UI / Demo UI]
        |
        v
[FastAPI Backend]
        |
        +--> /ai/chat
        +--> /conversations/*
        +--> /memory-items/*
        +--> /response-formats/*
        +--> /ai/providers/status
        |
        v
[Personalization Layer]
  - User profile lookup
  - Memory retrieval and filtering
  - Preference extraction
  - Prompt generation per provider
  - Timing log per stage

[Orchestration Layer]
  - selected_providers filtering
  - multi-provider fan-out
  - response comparison and merging
  - format final answer according to user preference

[Persistence Layer]
  - PostgreSQL / SQLAlchemy models
  - conversations
  - chat_history
  - memory_items
  - response_templates
  - user profiles

[External AI Providers]
  - Gemini
  - Groq
  - OpenAI
  - Local LLM / Ollama judge / prompt generator

[Operational Components]
  - quota status service
  - provider availability checks
  - final answer log / debug logs
  - request/response tracing
```

---

## 3. 실제 요청 흐름

현재 구현된 흐름은 다음과 같이 동작한다.

1. 사용자가 질문 입력
2. request payload에서 user_id, question, provider 선택, response format, conversation_id 확인
3. 관련 memory를 DB에서 조회
4. user profile과 project context, past conversation context를 조합
5. Local LLM이 사용자 의도와 맥락을 바탕으로 provider별 personalized prompt 생성
6. 선택된 provider만 호출하거나, 전체 provider 중 체크박스 선택에 따라 필터링
7. 각 provider 응답 수집
8. 비교 및 병합 단계 수행
9. 사용자가 지정한 응답 format 또는 DB에서 저장된 format 기준으로 최종 답변을 재구성
10. chat_history 저장
11. conversation memory 업데이트
12. memory extraction 및 preference storage 수행
13. 최종 결과를 UI에 전달

---

## 4. 사용자 개인화 설계

### 4.1 핵심 원칙

현재 설계의 핵심은 단순히 사용자가 질문한 내용을 공개 AI에 그대로 넘기는 것이 아니라, 다음 정보를 함께 전달하는 것이다.

- 과거 질문 이력
- DB에 저장된 메모리
- 사용자 관심사 / 선호도
- 프로젝트 컨텍스트
- 이전 대화 흐름
- provider별 prompt 특화 전략

### 4.2 구성 요소

#### Memory Query
- 사용자가 자주 묻는 주제와 연결된 정보 추출
- 구매/개발/일반 관심사 등 타입 기반 필터링
- 중복 제거와 domain 간 오염 방지

#### User Profile
- 사용자별 선호 스타일
- 인터페이스 응답 스타일
- 질문 패턴
- 관심 관심사

#### Local Brain Prompt Builder
- 사용자 질문을 Local LLM이 해석
- Public AI에 보낼 prompt를 자동 생성
- provider별로 약간씩 다른 prompt style을 적용

---

## 5. Provider 전략

### 5.1 현재 구현 상태

현재 구조는 다중 provider 병렬 호출을 지원하며, 사용자 질문에서 선택한 provider만 호출하도록 필터링한다.

- Gemini
- Groq
- OpenAI
- Local LLM 기반 추가 판단

### 5.2 Provider selection

다음 조건을 기반으로 선택한다.

- 사용자가 checkbox로 별도 선택
- 질문의 성격
- 기존 memory와 context
- provider별 품질/가용성
- quota 또는 status 정보

### 5.3 Quota / Status 처리

provider별 토큰 사용량, 남은 quota, 접근 상태는 best-effort 방식으로 확인한다.

- provider가 공식 quota API를 제공하면 반영
- 제공하지 않으면 unknown 또는 unavailable로 안전하게 처리
- UI는 상태만 표시하고, 전체 흐름은 멈추지 않도록 설계

---

## 6. 응답 포맷 설계

### 6.1 요구 사항

사용자는 단순 자연어 응답만 고집하지 않고, 더 구조화된 출력이 필요할 수 있다.

예시:

- 표 형식
- bullet list
- Priority / Summary / Recommendation 구조
- 사용자 지정 문체
- 메모/리포트형 답변

### 6.2 구현 방식

응답 format은 DB에 저장하고 API로 CRUD를 수행한다.

- 생성
- 조회
- 수정
- 삭제
- 특정 사용자 또는 기본 format 적용

이 구조를 통해 UI 또는 API에서 format을 동적으로 교체할 수 있다.

---

## 7. Multi-provider 응답 병합 로직

여러 provider의 응답을 단순 나열하지 않고, 아래 흐름으로 가공한다.

1. 각 provider 응답 수집
2. 유사한 핵심 정보 병합
3. 중복 문장/결론 제거
4. 사용자 응답 format에 맞게 재구성
5. 핵심 요약 + 상세 항목 + 추천 사항 구조로 렌더링

이 단계는 단순한 합산이 아니라, 사용자에게 읽기 좋은 최종 답변을 생성하는 핵심 로직이다.

---

## 8. Logging 및 성능 추적

현재 구현은 각 단계마다 로그와 시간을 기록하도록 설계되어 있다.

예시 로그 항목:

- question_received
- memory_lookup
- context_build
- local_prompt_generation
- provider_filtering
- provider_call
- response_merge
- final_formatting
- db_save_history

기본적인 목적은 디버깅과 성능 분석을 쉽게 만드는 것이다.

특히 다음이 중요하다.

- 어떤 단계에서 시간이 많이 걸리는지 추적 가능
- provider별 응답 지연 비교 가능
- prompt generation 문제를 빠르게 재현 가능
- UI에서 사용자에게 stage 단위 상태를 보여줄 수 있음

---

## 9. 데이터 모델 구성

현재 구조는 다음 테이블 중심으로 동작한다.

- users
- conversations
- chat_history
- conversation_memory
- memory_items
- ai_prompt_runs
- response_templates

이 구조는 단순 저장소를 넘어서, 사용자 개인화와 질문 패턴 누적을 가능하게 한다.

---

## 10. 운영 환경 및 검증 방향

현재 개발은 로컬 Windows 환경과 추가로 Docker / CentOS 기반 Linux 환경 검증을 염두에 둔다.

운영 목표:

- FastAPI 서비스 안정화
- Docker compose 기반 실행
- DB migration 및 replay 가능성 확보
- provider status check 정상화
- 사용자 대화 이력 복구 검증
- multi-provider UI 선택 플로우 검증

---

## 11. 현재 상태와 핵심 포인트

현재 구현 상태는 단순 “질문을 보내고 답변을 받는 앱”이 아니라, 다음 기능을 갖춘 개인 AI 비서 구조로 진화했다.

- 메모리 기반 개인화
- provider별 자동 prompt 생성
- 사용자 선택 기반 provider 병렬 호출
- final answer formatting
- DB 기반 응답 format 관리
- 대화 이력 보존
- provider status / quota visibility
- 단계별 시간 로그

이 구조는 MyAI의 본질인 “개인화된, 비교 기반, 누적 학습형 AI 비서”를 구현하는 방향과 일치한다.

---

## 12. 다음 단계

다음 단계는 아래 항목 중심으로 확장한다.

1. 일정/메일/메모 연동
2. workflow automation lifecycle
3. 사용자 memory confidence 정책 강화
4. provider별 추천 순위 및 비용 최적화
5. 대화/기억/프로필 관리 UX 개선
6. 실제 CentOS/Docker 환경에서 end-to-end 검증

---

## 13. 결론

v1.1은 이전의 “기본 AI 응답기” 구조에서 사용자 맞춤형 개인 AI 비서 구조로 전환된 시점이다.

특히 다음 세 가지가 가장 중요하다.

- 개인화된 prompt 생성
- 다중 provider 응답 병합
- 사용자 지정 format + DB 기반 관리

이 세 요소가 조합될 때 MyAI는 단순 챗봇이 아니라, 사용자 고유의 기억과 선호도를 아는 실제 비서형 서비스에 가까워진다.
