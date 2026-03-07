import { CultureDomain } from '../../types/culture';

export const exhibitionCategory: CultureDomain = {
  id: 'exhibition',
  name: '전시',
  icon: '🖼️',
  trunks: [
    {
      id: 'e-trunk-1',
      name: '기획/특별/팝업',
      level: 2,
      children: [
        { id: 'e-branch-1-1', name: '국제 교류/대형 기획전', level: 3 },
        { id: 'e-branch-1-2', name: '기증/기부 특별전', level: 3 },
        { id: 'e-branch-1-3', name: '브랜드 팝업/이벤트 전시', level: 3 },
        { id: 'e-branch-1-4', name: '기업 문화재단 기획전', level: 3 },
        { id: 'e-branch-1-5', name: '사전등록/이벤트 입장 전시', level: 3 },
        { id: 'e-branch-1-6', name: '축제/이벤트 연계 특별전시', level: 3 },
      ]
    },
    {
      id: 'e-trunk-2',
      name: '공공/대학/문화원',
      level: 2,
      children: [
        { id: 'e-branch-2-1', name: '국공립 미술관', level: 3 },
        { id: 'e-branch-2-2', name: '국립/시립 박물관', level: 3 },
        { id: 'e-branch-2-3', name: '자치구 구립/문화재단 갤러리', level: 3 },
        { id: 'e-branch-2-4', name: '외국문화원/지역문화원', level: 3 },
        { id: 'e-branch-2-5', name: '대학 박물관/미술관', level: 3 },
        { id: 'e-branch-2-6', name: '소장품 상설전시', level: 3 },
      ]
    },
    {
      id: 'e-trunk-3',
      name: '로컬 갤러리/아트 투어',
      level: 2,
      children: [
        { id: 'e-branch-3-1', name: '상업 갤러리 기획전', level: 3 },
        { id: 'e-branch-3-2', name: '오픈 스튜디오/아트 투어', level: 3 },
        { id: 'e-branch-3-3', name: '작가 스튜디오/오픈전', level: 3 },
        { id: 'e-branch-3-4', name: '독립/대안공간 전시', level: 3 },
      ]
    },
    {
      id: 'e-trunk-4',
      name: '공공미술/야외/스트릿',
      level: 2,
      children: [
        { id: 'e-branch-4-1', name: '공원/광장 공공미술', level: 3 },
        { id: 'e-branch-4-2', name: '미디어 파사드/라이트 아트', level: 3 },
        { id: 'e-branch-4-3', name: '지하철 역사/공공시설 갤러리', level: 3 },
        { id: 'e-branch-4-4', name: '벽화마을/아트로드/야외 조각', level: 3 },
        { id: 'e-branch-4-5', name: '윈도우/쇼윈도 갤러리', level: 3 },
      ]
    },
    {
      id: 'e-trunk-5',
      name: '어린이/가족/관람',
      level: 2,
      children: [
        { id: 'e-branch-5-1', name: '어린이 전용 미술관/갤러리', level: 3 },
        { id: 'e-branch-5-2', name: '그림책/동화 원화 전시', level: 3 },
        { id: 'e-branch-5-3', name: '가족 특화 전시/공간', level: 3 },
      ]
    }
  ]
};
