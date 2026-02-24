# 🗺️ 시스템 구조도 (System Structure)
*최종 업데이트: 2026-02-24 18:00:20*

이 문서는 '문화생활 통합 플랫폼' 프로젝트의 전체적인 구조와 관리 체계를 설명합니다.

## 1. 프로젝트 폴더 구조 (Directory Map)

```text
my-project/
├── data/               # 데이터 관련 자산
│   ├── bot/            # 데이터 수집 로봇 (Python 스크립트)
│   └── store/          # 수집된 JSON 데이터 저장소
├── docs/               # 프로젝트 관리 및 기술 문서
│   ├── vision_roadmap.md    # 장기 계획 및 철학
│   ├── task_tracker.md      # 단기 할 일 및 진행 현황
│   ├── development_log.md   # 일자별 상세 수행 기록
│   ├── troubleshooting.md   # 오류 해결 및 교훈 기록
│   ├── handoff_guide.md     # 학원-집 이동 시 즉시 실행 가이드
│   └── system_structure.md  # [현재 문서] 전체 구조 안내
└── web/                # 리액트 기반 웹 프론트엔드
    ├── src/
    │   ├── components/ # 재사용 가능한 UI 부품
    │   ├── types/      # 데이터 형식 정의 (TypeScript)
    │   ├── App.tsx     # 메인 조립 페이지
    │   └── App.css     # 메인 스타일시트
    └── index.html      # 웹 진입점
```

## 2. 문서 체계 상세 가이드 (Documentation System)

| 문서명 | 주요 내용 | 기록 시점 |
| :--- | :--- | :--- |
| **Vision & Roadmap** | 프로젝트 목표, 핵심 가치, 기술 스택 | 큰 방향성이나 기술이 바뀔 때 |
| **Task Tracker** | 현재 진행 중인 To-Do, 완료된 작업 | 새로운 작업을 시작하거나 마칠 때 |
| **Development Log** | 시간대별 작업 내용, 결정 사항 | 매 작업 세션 종료 후 |
| **Troubleshooting** | 에러 로그, 해결 방법, 계획 변경 이유 | 예상치 못한 문제 해결 시 |
| **Handoff Guide** | 환경 전환 시 즉시 실행할 체크리스트 | 매 세션 종료 전 |
| **System Structure** | 폴더 구조, 문서 역할, 시스템 설계 | 구조적인 변화가 생길 때 |

## 3. 핵심 개발 원칙 (Core Principles)
1. **Web First**: 데이터 수집보다 눈에 보이는 웹 UI를 먼저 구축하여 가시성 확보.
2. **Component Based**: 모든 UI는 독립된 부품(Component)으로 만들어 재사용성과 관리 효율을 높임.
3. **Double Check**: 위험한 작업(삭제, 리셋 등) 전에는 반드시 파트너와 상의 후 진행.
4. **Honesty & Limits (Absolute)**: AI는 자신의 한계를 인정하고 모르는 것을 추측하지 않으며, 파트너와 상호 정직하게 소통함. (2026-02-24 확립)
5. **Efficient Role Division**: 대용량 다운로드, 패키지 설치, 상호작용이 필요한 명령어는 파트너가 직접 실행하여 속도와 안정성을 확보함.
6. **Clean Docs**: 모든 작업 결과와 시행착오는 약속된 문서 체계에 정확한 시스템 시간 확인 후 즉시 기록함.
