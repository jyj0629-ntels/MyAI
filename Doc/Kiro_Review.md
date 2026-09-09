# MyAI Source Review (Kiro Review)

- Branch reviewed: `demo_renewal`
- Review basis: 7-step Call Flow + 2 core requirements
- Files inspected:
  - `app/core/config.py`
  - `app/api/ai.py`
  - `app/services/local_brain_llm_service.py`
  - `app/services/memory_query_service.py`
  - `app/services/preference_extraction_service.py`
  - `app/ai/services/multi_provider_orchestrator.py`
  - `app/ai/services/response_summary_service.py`
  - `app/ai/services/local_consensus_service.py`
  - `app/ai/providers/ollama_provider.py`
  - `app/services/chat_orchestrator_service.py`

---

## 0. Summary Verdict

이번 `demo_renewal` 브랜치는 이전 대비 크게 개선되었습니다. Local LLM provider 교체 구조, 테마/선호도 키워드의 Config 이전, 선호도 빈도 임계값 Config 도입, 요약의 think=true 유지가 반영되었습니다.

다만 아래 3가지가 요구사항을 위반하거나 회귀했으므로 반드시 수정해야 합니다.
1. `build_combined_summary()`에 통신사(SKT/LG U+/KT) 하드코딩 결론 문장이 다시 들어갔습니다. (하드코딩 금지 위반)
2. `ollama_provider.py`의 `num_predict`가 다시 320으로 고정되었습니다. (회귀)
3. Consensus 점수가 여전히 문자열 유사도(SequenceMatcher)로 계산됩니다. (하드코딩 금지 위반)

| Step | 상태 | 한 줄 요약 |
|---|---|---|
| 1. GUI 질문 입력 | 충족 | `ai.py::chat()`에서 질문 수신·검증 |
| 2. 로컬 LLM 선호도/테마 검토 | 부분 | 키워드 Config화·빈도 임계값 도입, 단 분류가 키워드 매칭·빈도 로직 미연결 |
| 3. Public AI별 Prompt 생성 | 부분 | provider별 분기 구조 있음, 런타임엔 단일 프롬프트 재사용 |
| 4. 각 Public AI로 Request 전송 | 충족 | 병렬 팬아웃, ollama 제외 |
| 5. 로컬 LLM Think 요약 | 충족 | think=true 유지, provider 교체 지원 |
| 6. 요약 취합 + Consensus % | 위반 | 통신사 하드코딩 부활, consensus %는 문자열 유사도 |
| 7. DB 저장 + 이력 관리 | 충족 | chat_history 등 저장 |

---

## 1. Copilot 수정 지시 (Action Items)

아래 항목을 위에서부터 순서대로 수정하세요. 각 항목은 "무엇을 / 어디서 / 어떻게"를 포함합니다.

### [필수 1] Step 6 통신사 하드코딩 문장 제거 (최우선)
- 파일: `app/ai/services/multi_provider_orchestrator.py`
- 함수: `build_combined_summary()`
- 문제: 아래처럼 특정 도메인(통신사)에 고정된 결론 문장이 하드코딩되어 있습니다.
  - "SKT는 네트워크 안정성과 품질 강점이 가장 두드러진다."
  - "LG U+는 요금제 혜택이 가장 강한 경쟁 요소다."
  - "KT는 유선/브로드밴드 강점이 보완 요소로 작용한다."
- 사용자 질문은 어떤 주제가 올지 알 수 없으므로, 위와 같이 특정 단어(SKT, 요금제, 네트워크 등)를 문자열 비교해서 미리 정해둔 문장을 삽입하면 안 됩니다.
- 수정 방법:
  - `build_combined_summary()`의 키워드 기반 문장 생성 로직을 전부 제거하세요.
  - 최종 취합 요약은 `LocalConsensusService`가 로컬 LLM(think=true)으로 생성한 `judge_result["final_answer"]`를 사용하세요.
  - LLM 취합 결과가 없을 때의 fallback은 "각 provider 요약을 문자열로 이어붙이기"만 허용하고, 특정 단어를 판별해 문장을 만들어내지 마세요.

### [필수 2] Step 6 Consensus 점수를 LLM 판정값으로 변경
- 파일: `app/ai/services/multi_provider_orchestrator.py`
- 함수: `semantic_similarity()`, `compare_responses()`
- 문제: consensus_score를 Jaccard 토큰 겹침 + `difflib.SequenceMatcher`(문자열 유사도)로 계산합니다. 이는 문맥이 아니라 글자 유사도만 봅니다.
- 수정 방법:
  - consensus_score는 `LocalConsensusService`가 로컬 LLM으로 산출한 `judge_result["consensus_score"]`를 정식 값으로 사용하세요.
  - 문자열 유사도 계산은 삭제하거나, 참고용 보조 지표로만 남기고 최종 판단에는 쓰지 마세요.

### [필수 3] Ollama num_predict 회귀 복구
- 파일: `app/ai/providers/ollama_provider.py`
- 문제: 요청 옵션에 `"num_predict": 320` 으로 값이 하드코딩되어 있습니다. 긴 요약/취합 시 응답이 중간에 잘립니다.
- 수정 방법:
  - `config.py`에 `OLLAMA_NUM_PREDICT`(예: 기본 1024) 설정을 추가하세요.
  - `ollama_provider.py`에서 `num_predict`를 `request.max_tokens`(있으면 우선) 또는 `settings.OLLAMA_NUM_PREDICT`로 사용하도록 변경하세요.

### [필수 4] Step 2 선호도 빈도 임계값을 실제 흐름에 연결
- 파일: `app/services/preference_extraction_service.py`
- 문제: `PREFERENCE_MIN_FREQUENCY`(config)와 `should_register_preference()`가 정의만 되어 있고, `persist_from_question()`에서 호출되지 않습니다. 그래서 "자주 질문한 경우에만 선호도 등록"이 실제로 동작하지 않습니다.
- 수정 방법:
  - 같은 사용자·같은 선호도 key가 몇 번 관측됐는지 카운트하는 로직을 추가하세요(DB에 카운트 컬럼 또는 관측 이력 테이블).
  - `persist_from_question()`에서 관측 횟수를 증가시키고, `should_register_preference(frequency, threshold=settings.PREFERENCE_MIN_FREQUENCY)`가 True일 때만 PREFERENCE를 ACTIVE로 등록하세요.
  - 임계값 미만이면 등록하지 말고 관측 횟수만 누적하세요.
- 추가 정리: `should_register_preference()`가 클래스 안에 2번 중복 정의되어 있습니다. 하나만 남기세요.

### [필수 5] Step 2 테마 분류를 로컬 LLM 기반으로 승격
- 파일: `app/services/memory_query_service.py`
- 함수: `detect_question_theme()`
- 문제: 테마를 `settings.PURCHASE_THEME_KEYWORDS` 등 키워드가 질문에 들어있는지(`keyword in text`)로 판별합니다. 키워드를 Config로 뺀 것은 개선이지만, 여전히 "문자열 포함 여부"로 분류하는 방식입니다.
- 수정 방법:
  - 질문의 테마(개발/뉴스/쇼핑/일반 등)는 로컬 LLM(`LOCAL_LLM_PROVIDER`)에게 판단을 맡기세요.
  - 로컬 LLM 호출이 실패할 때만 Config 키워드 매칭을 fallback으로 사용하세요.

### [권장 6] 하드코딩된 숫자를 Config 참조로 통일
- 파일: `app/api/ai.py`, `app/ai/services/multi_provider_orchestrator.py`, `app/services/chat_orchestrator_service.py`
- 문제: 아래 값들이 코드에 직접 박혀 있습니다.
  - `ai.py`: `requires_confirmation = ... < 80` → `settings.CONSENSUS_THRESHOLD` 사용
  - `ask_all()`: `>= 2` → `settings.MIN_CONSENSUS_RESPONSES` 사용
  - `chat_orchestrator_service.py`: 선호도 write-back의 `0.75` → `settings.PREFERENCE_MIN_CONFIDENCE` 사용
- 수정 방법: 위 리터럴들을 모두 대응되는 settings 값으로 교체하세요.

### [권장 7] 사용하지 않는 코드 정리
- 파일: `app/ai/services/consensus_engine.py`, `claim_extractor.py`, `claim_matcher.py`
- 문제: import는 되어 있으나 실제 호출 흐름에 연결되지 않았습니다(dead code로 보임).
- 수정 방법: 실제로 쓸 것이면 흐름에 연결하고, 아니면 제거하세요.

### [권장 8] Step 5 fallback 요약의 하드코딩 문구 최소화
- 파일: `app/ai/services/response_summary_service.py`
- 함수: `_fallback_summary()`
- 문제: `generic_prefixes`, `generic_fragments`에 "안녕하세요", "잡담" 같은 고정 문구 목록이 있습니다. LLM 실패 시에만 동작하지만, 요구사항(하드코딩 문자열 비교 금지) 취지와 부분적으로 어긋납니다.
- 수정 방법: 가능하면 fallback도 문구 목록 대신 길이/구조 기반 필터만 사용하세요. 문구 목록을 유지해야 한다면 Config로 빼세요.

### [로드맵 9] Step 3 provider별 프롬프트 차등 생성
- 파일: `app/api/ai.py`, `app/services/local_brain_llm_service.py`
- 현재: `build_provider_prompt()`에 provider별 스타일 dict가 있어 확장 구조는 있으나, 실제로는 프롬프트를 한 번만 만들어 모든 provider에 동일하게 보냅니다.
- 수정 방법(향후): 팬아웃 직전에 provider마다 `build_provider_prompt(provider_name=...)`를 각각 호출해 서로 다른 프롬프트를 전달하세요.

---

## 2. 이번 브랜치에서 잘 반영된 부분 (유지할 것)

- Local LLM provider 교체 구조 도입: `local_brain_llm_service.get_local_provider_instance()`,
  `response_summary_service._local_provider_instance()`가 `LOCAL_LLM_PROVIDER`로 동적 로딩. (요구 1 충족)
- 테마/선호도/fast-path 키워드를 Config로 이전:
  `PURCHASE_THEME_KEYWORDS`, `DEVELOPMENT_THEME_KEYWORDS`, `LOCAL_LLM_FAST_PATH_HINTS`.
- 선호도 빈도 임계값 Config 신설: `PREFERENCE_MIN_FREQUENCY`, `PREFERENCE_MIN_CONFIDENCE`.
- 선호도 추출을 고정 문장 매칭 → 토큰 스코어링(`_score_preferences`) 기반으로 재작성.
- Step 5 요약에서 `think=True` 유지(이전 브랜치의 think=False 회귀 해소).

---

## 3. 참고: 요구사항 원문 대비 체크

- 요구 1(로컬 LLM 교체 + 모델명 Config): 충족.
  `LOCAL_LLM_PROVIDER`, `LOCAL_LLM_MODEL`로 provider·모델명 모두 교체 가능.
- 요구 2(하드코딩 문자열 비교/요약 금지): 부분 충족.
  분류/선호도/힌트 하드코딩은 해소했으나, Step 6 취합·비교에 하드코딩이 남아 있음 → [필수 1], [필수 2]에서 해결 필요.
