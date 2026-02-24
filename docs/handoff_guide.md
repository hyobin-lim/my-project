# 🚀 세션 인수인계 가이드 (Handoff Guide)
*최종 업데이트: 2026-02-24 18:00:20*

이 문서는 학원과 집 사이의 작업 전환을 위해 **'지금 즉시 해야 할 일'**만 기록합니다.

---

## 🏫 학원에서 마무리할 일 (지금 바로 실행!)
1. **작업 내용 클라우드 업로드**:
   ```powershell
   git add .
   git commit -m "2026-02-24: 웹 UI 뼈대 구축 완료 및 문서 체계 확립"
   git push origin main
   ```
   *(Git 미사용 시, `web/node_modules` 폴더를 **제외**하고 프로젝트 전체를 압축하여 업로드)*

---

## 🏠 집에 도착해서 할 일
1. **최신 코드 가져오기**: `git pull origin main` (또는 압축 풀기)
2. **웹 패키지 재설치 (최초 1회 필수)**:
   ```powershell
   cd web
   npm install
   ```
3. **웹 실행 및 확인**: `npm run dev`
4. **AI 에이전트 브리핑**: "나 집에 왔어. `docs/` 폴더 읽고 다음 단계 알려줘."

---

## 📍 현재 프로젝트 상태 요약
- **웹**: React + Vite 6 환경 구축 완료. Header, Card 컴포넌트 구조 잡힘. Mock 데이터 렌더링 중.
- **데이터**: `hello_bot.py` 환경 테스트 성공. 실제 수집 로봇(`collector.py`) 개발 대기 중.
- **문서**: 6종의 문서 체계(Vision, Task, Log, Troubleshooting, Structure, Handoff) 구축 완료.
