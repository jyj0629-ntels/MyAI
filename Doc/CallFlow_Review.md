# MyAI 기능별 Call Flow Review

이 문서는 현재 소스 기준으로, 사용자 입력부터 AI 응답 생성, 저장, 조회, 화면 표시까지의 흐름을 Text 기반 Call Flow로 정리한 문서입니다.

목적:
- 기능 누락 여부를 빠르게 점검하기 위해서
- 대항목/중항목/소항목 단위로 흐름을 검토하기 위해서
- 다른 AI가 함께 리뷰할 수 있도록 정리하기 위해서

---

## 0. 전체 개요

사용자 입력 → 브라우저 UI → REST API → 로컬 컨텍스트 분석 → 멀티 프로바이더 호출 → 응답 비교/선정 → DB 저장 → 대화 기록/메모리 추출 → UI 재렌더링

핵심 구조:
- Frontend: `app/static/index.html`
- API Endpoint: `app/api/ai.py`, `app/api/conversations.py`
- Service Layer: `app/services/*`
- Repository/DB Layer: `app/repositories/*`, `app/models/*`

---

## Step 1. 앱 초기화 및 대화 세션 준비

### 1-1. 브라우저 로딩 시 초기 상태 설정

- 페이지 로드 시 `window.addEventListener('load', async () => { ... })` 실행
- `loadProviderStatus()` 호출
  - `/ai/providers/status` 호출
  - Provider 상태를 가져와 `state.providers` 초기화
- `ensureConversation()` 호출
  - 가장 최근 대화 조회 시도
  - 없으면 `/conversations/` 로 새 대화 생성
- `loadHistory()` 호출
  - 현재 conversation_id 기준으로 `/conversations/{id}/history` 조회
  - 기존 메시지 목록을 UI에 렌더링
- `loadPreferences()` 호출
  - `/memory-items/user/{user_id}` 조회
  - 사용자 선호도/프로필 요약 반영

### 1-2. 대화 생성/조회 로직

- `ensureConversation()` 기능
  - 기존 대화가 있으면 가장 최근 대화의 id를 선택
  - 없으면 새 conversation을 생성
- conversation 생성 API
  - POST `/conversations/`
  - request body: `{ title: "Demo conversation" }`
- 서버는 `ConversationService.create()`로 conversation 생성

### 1-3. 히스토리 로드 로직

- `loadHistory()`
  - `GET /conversations/{conversation_id}/history`
  - DB에서 해당 conversation_id의 ChatHistory row들을 시간 순으로 가져옴
- 각 item마다
  - `addMessage('user', item.question)`
  - provider_response_path가 있으면
    - `GET /conversations/{conversation_id}/history/{chat_id}/provider-responses`
    - 상세 provider 응답을 조회해서 modal에 연결
  - `addMessage('ai', item.answer)` 로 화면 출력

### 1-4. 리뷰 포인트

- 초기 로딩 시 대화 이력이 없을 경우에도 빈 상태 메시지를 보여줌
- 사용자 프로필/메모리/대화 기록의 로드 순서가 분리되어 있어, UI 의존성이 존재함
- 로딩 실패 시 예외 처리는 있지만, 일부 실패 시 partial rendering이 발생할 수 있음

---

## Step 2. 사용자 질문 전송

### 2-1. 입력 검증

- `sendQuestion()` 호출
- `questionInput.value.trim()` 확인
- 비어 있으면 `질문을 입력해 주세요` 반환
- `state.sendInFlight` 체크
  - 이미 전송 중이면 추가 요청을 막음

### 2-2. 질문 전송 전 UI 반응

- `questionInput.value = ''`
- 화면에 사용자 메시지를 즉시 추가
  - `addMessage('user', text)`
- 전송 버튼과 입력창 잠금
  - `setSendControlsLocked(true)`

### 2-3. 대화 세션 보증

- `ensureConversation()` 호출
- 현재 state.conversationId가 없으면 생성
- conversation_id를 payload에 포함

### 2-4. 요청 payload 구성

요청 payload 예시:
- `user_id`
- `question`
- `conversation_id`
- `provider`
- `selected_providers`
- `response_format_text`

### 2-5. AI 채팅 API 호출

- `POST /ai/chat`
- 서버는 `app/api/ai.py`의 `chat()` 함수로 진입
- request validation 수행
- 비어 있는 질문이면 422 에러 반환

### 2-6. 리뷰 포인트

- 입력값 검증은 있지만, 중복 전송 방지 기능은 UI에서 추가됨
- 질문을 입력 중인 상태와 실제 서버 전송 상태를 구분하는 UI 상태 관리가 필요함
- 응답이 늦게 오는 상황에서 사용자에게 현재 상태를 보여주는 UX 보완이 필요한지 점검 필요

---

## Step 3. 서버 요청 수신 및 기본 처리

### 3-1. HTTP 요청 파싱

`app/api/ai.py`의 `chat()` 함수 시작

- request.question 검증
- form-data 또는 multipart 처리 분기
- `AIRequest.from_payload(...)` 로 변환 가능
- `request.question`이 비어 있으면 예외 발생

### 3-2. 사용자 선호도 추출

- `request.user_id`가 있으면
  - `PreferenceExtractionService.persist_from_question(request.user_id, request.question, db)`
- 사용자 질문으로부터 preference 추출 시도
- 실패 시 `db.rollback()` 후 warning 로그

### 3-3. Context 및 Memory Retrieval

- `MemoryItemService`와 `MemoryQueryService` 사용
- `request.user_id`가 있으면 recall 수행
- Retrieved memories는 다음 타입으로 분류됨
  - PREFERENCE
  - PROJECT
  - GOAL

### 3-4. 컨텍스트 패키지 구성

- `ContextPackageService().build(...)`
- 사용자 프로필, 프로젝트 컨텍스트, 목표를 묶어서 구성
- 이후 로컬 브레인 분석에 사용됨

### 3-5. 리뷰 포인트

- 사용자 인터랙션과 메모리 추출이 같은 요청에서 동기적으로 수행됨
- memory retrieval 실패 시 전체 응답이 실패하는지, partial 응답으로 처리하는지 명확히 구분 필요
- preference extraction 실패는 warning으로 흘려보내고 있어, 기능 연속성을 보장하는 구조는 약함

---

## Step 4. Local Brain Prompt 생성

### 4-1. Local Brain 분석

- `LocalBrainService().analyze(...)` 호출
- 입력:
  - question
  - user_profile
  - project_context
- 출력:
  - `brain_result.provider`
  - `brain_result.task_type`
  - `brain_result.prompt`

### 4-2. Provider 선택

- 우선순위:
  - request.provider
  - brain_result.provider
  - fallback settings
- `provider` 값이 없거나 유효하지 않으면 기본 Provider 로 fallback
  - `LOCAL_LLM_PROVIDER`
  - `LOCAL_BRAIN_DEFAULT_PROVIDER`
  - `PRIMARY_PROVIDER`
  - 기본값: `ollama`

### 4-3. 응답 포맷 템플릿 생성

- 사용자/설정 기준으로 `response_format_template` 조회
- `request.response_format_text` 또는 디폴트 템플릿을 사용
- provider prompt 생성
  - `LocalBrainLLMService().build_provider_prompt(...)`

### 4-4. 최종 Prompt 설정

- `request.prompt = provider_prompt`
- `request.system_prompt = provider_prompt`
- `request.user_context = ...`
- `AIPromptRunService.create(...)` 로 prompt run log 기록

### 4-5. 리뷰 포인트

- Local Brain이 provider 선택과 요청 prompt 생성의 핵심 허브 역할을 수행함
- provider 선택 fallback 로직이 복잡하고, 실제로 어떤 provider가 최종 선택됐는지 로그가 충분히 남는지 점검 필요
- 응답 형식 template이 강제 되는 구조는 사용자 요구에 잘 맞지만, 필드가 빠지면 답변 형식이 다른 경우도 발생할 수 있음

---

## Step 5. Multi Provider Fanout 및 비교

### 5-1. 멀티 프로바이더 호출

- `MultiProviderOrchestrator(...).ask_all(request)` 호출
- 여러 provider를 동시에 혹은 순차적으로 호출하도록 구성됨
- 결과는 `multi_result`로 반환

포함된 항목:
- `responses`
- `comparison`
- `judge_request`
- `selected`

### 5-2. 응답 비교

- `comparison` 값 사용
- 여러 provider 응답을 비교 분석
- `judge_request` 생성
- 하나의 최종 답변을 선정

### 5-3. 최종 응답 결정

- 최종 선정된 답변은 `selected` 객체로 추출
- 보통 최종 answer를 사용자에게 전달
- provider별 응답 목록을 함께 보관 가능

### 5-4. 리뷰 포인트

- 멀티 provider 구조는 사용자에게 “비교”를 제공하는 장점이 있지만, 응답 순서 및 일관성 확보가 중요함
- 특정 provider 응답이 실패해도 전체 흐름이 유지되는지 확인 필요
- `selected` 값과 `provider_responses` 값이 항상 일치하는지 점검할 필요 있음

---

## Step 6. 최종 응답 반환

### 6-1. 응답 직렬화

- API는 `AIResponse` 모델로 변환하여 응답 반환
- 주요 필드:
  - `answer`
  - `summary`
  - `provider_responses`
  - `success`
  - 기타 metadata

### 6-2. 브라우저 응답 처리

- `const data = await res.json()`
- `answer = data.answer || data.summary || '응답이 비어 있습니다.'`
- `providerResponses = Array.isArray(data.provider_responses) ? data.provider_responses : []`
- `addMessage('ai', answer, { providerResponses })`

### 6-3. 사용자 화면 표시

- AI 응답 버블 생성
- provider response가 있으면 클릭 시 modal로 상세 비교 결과 표시
- `openProviderResponsesModal(...)` 실행

### 6-4. 리뷰 포인트

- 응답의 일부 값이 비어 있을 경우 fallback 처리 있음
- AI 응답이 화면에 들어가기 전에 여러 비동기 이벤트가 겹칠 수 있어 UI 스레드/순서 안정성이 중요함
- 응답 JSON 구조와 화면 렌더 로직이 직접 연결되어 있으므로 schema 변경 시 UI도 함께 점검 필요

---

## Step 7. 대화 기록 저장

### 7-1. ChatOrchestratorService.post_process()

- response 처리 후 DB에 저장
- 핵심 입력값:
  - conversation_id
  - provider
  - model
  - question
  - answer
  - input_tokens
  - output_tokens
  - success

### 7-2. provider response 파일 저장

- `provider_responses`가 있으면
  - `ProviderResponseStorageService.write_markdown(...)` 호출
- markdown 파일 생성
  - 파일 경로를 `provider_response_path`로 저장

### 7-3. ChatHistory insert

- `ChatRepository.save(...)` 호출
- `ChatHistory` row 생성
- `conversation_id`, `provider`, `model`, `question`, `answer`, `provider_response_path` 저장

### 7-4. DB 저장 결과

저장되는 데이터 예시:
- conversation_id
- provider
- model
- question
- answer
- input_tokens
- output_tokens
- success
- provider_response_path

### 7-5. 리뷰 포인트

- 저장 로직 자체는 단일 row insert 구조라서 “질문-답변 매칭” 측면에서 비교적 단순함
- 다만 UI에서 메시지 순서가 엇갈릴 수 있는 구조가 있어, 실제 화면 인식 문제와 DB 문제를 혼동하기 쉬움
- provider response 파일 저장 경로를 DB에 함께 저장하는 방식은 분산 추적에 유리하지만, 파일 정합성 관리를 별도로 보완할 필요가 있음

---

## Step 8. 대화 요약 및 메모리 갱신

### 8-1. Conversation summary build

- 최근 대화 이력을 조회
- `get_recent_by_conversation(conversation_id, limit=20)`
- `Q: ...` / `A: ...` 형식으로 message 리스트 구성
- `ConversationMemoryUpdateService.update_summary(...)` 호출

### 8-2. 메모리 추출 단계

- 요약이 비어 있으면 메모리 추출 건너뛰기
- 요약이 있으면
  - `LLMMemoryExtractionService(GeminiMemoryExtractionProvider())`
  - `MemoryExtractionOrchestrator.process(...)`
- 추출된 memory는 타입별로 저장
  - PREFERENCE
  - PROJECT
  - GOAL
  - 기타 memory

### 8-3. Memory 저장

- `memory_service.exists_by_key(...)` 검사
- 이미 존재하면 갱신
- 없으면 새로 저장

### 8-4. 리뷰 포인트

- conversation summary와 memory extraction은 사용자 맞춤화 기능의 핵심
- 이 단계가 실패하면 이후 추천/프로필 갱신이 부정확해질 수 있음
- memory 추출이 비동기적으로 보이므로, 입력-처리-저장의 전체 흐름을 전체적으로 보완해야 함

---

## Step 9. 대화 기록 조회 및 상세 확인

### 9-1. 대화 기록 API

- `GET /conversations/{conversation_id}/history`
- `ChatService.get_conversation_history()`
- DB에서 해당 conversation_id의 모든 history를 `id asc` 순으로 조회

### 9-2. provider response 상세 API

- `GET /conversations/{conversation_id}/history/{chat_id}/provider-responses`
- `ChatHistory.id` 기반으로 해당 row를 찾음
- `provider_response_path`가 있으면 markdown 파일을 읽어 파싱
- `ProviderResponseStorageService.parse_markdown_responses()` 로 다시 구조화

### 9-3. 화면 복원 로직

- `loadHistory()`에서 다시 질문과 응답을 UI로 복원
- 각각의 AI 답변에 providerResponses 정보를 연결해서 modal에 연결

### 9-4. 리뷰 포인트

- 대화 복원은 저장된 DB row를 기반으로 하므로 화면 재현 속성이 좋음
- 단, 질문/답변 표시 순서가 UI 상에서 비동기적으로 섞이지 않도록 보장해야 함
- history 조회 API는 DB 정합성을 확인하기 위한 좋은 디버깅 포인트임

---

## Step 10. 실제 기능 매핑 Summary

### 대항목: 사용자 입력 및 UI 동작
- 질문 입력
- 전송 버튼 클릭
- 중복 전송 방지
- 응답 UI 표시
- 히스토리 렌더링

### 대항목: API 요청 및 검증
- request parse
- form-data 처리
- 질문 공백/유효성 검사
- prompt trace 및 logging

### 대항목: 사용자 맥락 및 메모리
- preference 추출
- memory retrieval
- context package 구성
- user profile 생성

### 대항목: AI provider orchestration
- local brain prompt 생성
- provider 선택
- fanout calls
- comparison and judge
- selected answer pick

### 대항목: 데이터 저장
- ChatHistory 저장
- provider response markdown 저장
- summary update
- memory extraction and persist

### 대항목: 조회/복원
- history 조회
- provider response 상세 조회
- UI 재렌더링

---

## Step 11. 리뷰 체크리스트 (누락/보완 포인트)

다음 항목은 실제 개발 시 반드시 점검할 것을 권장합니다.

- 중복 요청 방지 로직이 충분한가
- 비동기 응답의 순서를 UI에서 보장하는가
- provider 응답 비교 결과와 최종 answer가 일치하는가
- memory retrieval 실패 시 전체 요청이 멈추는가
- 대화 히스토리 조회 시 질문/답변 ordering이 올바른가
- provider response 파일 저장 실패 시 DB는 어떻게 처리되는가
- conversation summary가 너무 오래되거나 비어 있을 때 fallback 처리가 적절한가
- 사용자 메시지와 AI 메시지가 화면에 정확히 짝지어지는가
- 대규모 대화에서 history query가 느려지지 않는가

---

## Step 12. 결론

현재 구조를 보면, 핵심 흐름은 잘 설계되어 있으나, 다음 두 가지 영역이 기능 안정성의 핵심 포인트입니다.

1. 화면 단의 비동기 메시지 순서 관리
- 여러 요청이 겹치면 UI 표시가 엇갈릴 수 있음

2. 메모리/summary 저장의 오류 복구 로직
- 일부 단계를 실패해도 전체 사용자 경험이 유지되는지 검토 필요

이 문서를 기준으로, 누락된 기능이나 보완이 필요한 구간을 다시 정리한 뒤, 필요한 기능을 추가 개발하는 것이 가장 효율적입니다.
