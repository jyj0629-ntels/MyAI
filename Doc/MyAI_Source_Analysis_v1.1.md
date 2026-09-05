# MyAI Source Analysis v1.1

## 1. 분석 목적

이 문서는 현재 코드베이스의 핵심 모듈과 책임을 정리해, 어떤 기능이 이미 구현되었고, 어떤 흐름이 현재 동작 중인지 확인하기 위한 문서이다.

---

## 2. 핵심 구성

### app/main.py

역할:
- FastAPI 애플리케이션 부트스트랩
- 라우터 등록
- 정적 UI 경로 연결
- health endpoint 제공
- provider status endpoint 제공

핵심 의미:
- 전체 시스템의 진입점이며, AI API와 UI가 연결되는 중심 지점이다.
- /ui, /demo, /ai/providers/status 등의 경로는 현재 UI 동작에 직접 연결된다.

---

### app/api/ai.py

역할:
- /ai/chat 엔드포인트 처리
- 사용자 질문을 받아 context와 memory를 조합
- provider별 personalized prompt 생성
- selected_providers를 기준으로 provider filter 적용
- 최종 최종 응답 포맷 정리
- 저장 로직 호출

핵심 의미:
- 실제 질문 처리 로직의 중심이다.
- 여기에서 memory lookup, prompt generation, multi-provider orchestration, formatting, DB 저장이 연결된다.

---

### app/ai/models/request.py

역할:
- AI request schema 정의
- selected_providers normalization
- payload compatibility 처리

핵심 의미:
- Swagger와 실제 백엔드 파라미터가 서로 어긋나지 않도록 정합성을 맞추는 역할을 한다.
- 사용자 질문과 provider 선택을 안정적으로 받기 위해 중요하다.

---

### app/ai/services/multi_provider_orchestrator.py

역할:
- 여러 provider 응답을 수집
- 사용자 선택에 따라 provider를 필터링
- 응답 비교 및 합치기
- 최종 읽기 쉬운 답변 형식으로 변환

핵심 의미:
- 단순 provider 호출이 아니라, 병렬 응답 비교와 최종 정제 로직을 담당한다.
- “다중 AI 답변을 합쳐서 사용자에게 정리된 답변으로 보여주는” 핵심 기능이다.

---

### app/services/provider_quota_service.py

역할:
- provider별 status, quota, availability를 안전하게 조회
- 실제 API가 없거나 비정상일 때 graceful fallback 처리

핵심 의미:
- UI에서 provider별 남은 토큰/상태를 확인하고 싶을 때 필요한 비즈니스 로직이다.
- provider가 표준 API를 제공하지 않아도 앱이 죽지 않도록 설계되었다.

---

### app/static/index.html

역할:
- 데모 UI 렌더링
- provider checkbox 표시
- conversation history 로딩
- provider status 가져오기
- memory context 및 결과 표시

핵심 의미:
- 백엔드 API와 실제 사용자 인터랙션을 연결하는 프런트엔드 장치이다.
- 브라우저 캐시나 서버 재시작 전/후 상태를 확인해야 하는 UI 지점이다.

---

### app/api/conversations.py

역할:
- conversation 생성/조회/목록 관리
- 질문-답변 기록 복구
- 대화 이력 관리

핵심 의미:
- 사용자가 이전 대화를 이어가거나 회기적으로 볼 수 있도록 한다.
- history restore 기능과 불일치가 생기면 UX 문제가 발생한다.

---

### app/repositories/chat_repository.py

역할:
- chat_history 저장 및 조회 처리

핵심 의미:
- 최종 답변을 DB에 저장하는 책임이 있다.
- 초기 구현에서는 저장 누락이 있었고, 최종 응답 저장 경로를 보강해야 했다.

---

### app/services/chat_orchestrator_service.py

역할:
- 질문/답변 저장
- summary memory 갱신
- memory extraction 또는 학습 누적 흐름 연결

핵심 의미:
- 단일 prompt를 보내는 것만 아니라, 사용자 행동을 장기적으로 기억하게 만드는 중심 로직이다.

---

### app/services/memory_query_service.py

역할:
- 관련 memory retrieval
- 중복/노이즈 제거
- 사용자 주제별 필터링

핵심 의미:
- “비슷한 질문의 메모리를 학습”하는 핵심 기능이다.
- purchase 관련 메모리와 개발 관련 메모리를 섞지 않도록 필터를 둔다.

---

### app/services/preference_extraction_service.py

역할:
- 사용자 질문에서 관심사/선호/의도 추출
- memory 저장 대상 생성

핵심 의미:
- 사용자의 취향을 누적하는 엔진이다.
- user_id 누락 문제나 FK 문제로 rollback이 발생하던 부분을 검토하여 안정화했다.

---

## 3. 구현된 핵심 기능

### 3.1 개인화된 prompt 생성

기존에는 사용자가 직접 질문을 공개 AI에 넘기기만 했지만, 지금은 아래 정보가 모두 반영된다.

- 과거 메모리
- 사용자 프로필
- 프로젝트/업무 컨텍스트
- 질문의 목적
- 과거 대화 이력
- provider별 prompt adaptation

즉, “질문 그대로 전달” 보다는 “사용자 맞춤형 prompt 생성”이 핵심이었다.

---

### 3.2 선택형 provider 호출

사용자는 질문당 어떤 provider를 사용할지 선택할 수 있어야 한다.

- provider checkbox 기반 UI
- selected_providers 검증
- 실제 호출 시 필터링

이 기능은 현재 MyAI의 사용자 제어성과 실용성을 크게 높인다.

---

### 3.3 응답 통합 및 포맷화

여러 AI답변을 단순 붙여서 보여주지 않고, 아래 방식으로 가공한다.

- 중복 제거
- 핵심 요약 병합
- 사용자 선호 format 적용
- 읽기 쉬운 구조로 변환

결과적으로 사용자는 여러 AI 답변을 비교하면서도 쉽게 이해할 수 있다.

---

### 3.4 DB 기반 응답 format 관리

응답 포맷을 하드코딩하지 않고 DB에서 관리한다.

- 사용자 지정 문체 유지
- 구조화된 답변 템플릿 관리
- API로 CRUD 제공
- Swagger 등록

이는 사용자 맞춤형 “답변 스타일 설정”을 실현하는 중요한 기능이다.

---

## 4. 문제 해결 포인트

### 4.1 Swagger / request mismatch

초기에는 request schema와 실제 라우트 파라미터가 서로 달라서, API 문서와 구현이 어긋나는 문제가 있었다.

해결 방향:
- FastAPI request model 통일
- 선택 필드 normalization
- Swagger 기반 파라미터 정합성 보장

---

### 4.2 chat history 저장 누락

초기에는 최종 답변이 DB에 저장되지 않아 대화 이력이 가끔 비어 보였다.

해결 방향:
- 최종 AI 응답을 저장 경로로 직접 전달
- 저장 후 memory update 로직 연동

---

### 4.3 memory contamination / dedupe 문제

개발 메모리와 구매/개인 관심사 메모리가 섞이면서, 관련 없는 context가 prompt에 포함되는 문제가 있었다.

해결 방향:
- topic/theme 기반 필터링
- 중복 제거
- domain boundary enforcement

---

### 4.4 stale UI / unpushed code 문제

브라우저가 예전 UI를 계속 표시하는 문제는 단순 cache 문제라기보다, 서버가 최신 코드로 재실행되지 않은 상태 때문이었다.

해결 방향:
- git push 후 서버 pull / rebuild
- container 재기동
- 브라우저 새로고침 및 clean reload 확인

---

## 5. 현재 코드의 의의

이 프로젝트는 다음 단계의 개인화 AI 구조로 진화했다.

- raw prompt relay에서 personalized assistant로 전환
- memory-centric context building
- multi-provider response selection and merge
- DB-backed response formatting
- user choice control through provider filter
- visible per-stage timing log

즉, 현재 코드는 단일 질문에 대해 답변을 받는 앱이 아니라,
사용자의 과거 맥락과 선호를 반영해 정리된 답변을 만들어주는 “개인용 지능형 비서”를 목표로 한다.

---

## 6. 결론

소스 분석 관점에서 가장 핵심적인 점은 다음 세 가지이다.

1. app/api/ai.py가 전체 동작의 중심이다.
2. app/services/memory_query_service.py와 preference extraction이 개인화의 핵심이다.
3. app/ai/services/multi_provider_orchestrator.py가 응답 병합과 최종 종합을 담당한다.

이 세 모듈이 함께 동작할 때, MyAI는 단순 챗봇이 아니라 사용자 맞춤형 AI 비서 구조로 완성된다.
