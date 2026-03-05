import { CultureDomain } from '../../types/culture';

export const festivalCategory: CultureDomain = {
  id: 'festival',
  name: '축제',
  icon: '🎪',
  trunks: [
    {
      id: 'f-trunk-1',
      name: '문화/예술 축제',
      level: 2,
      children: [
        { id: 'f-branch-1-1', name: '영화제/연극/무대 페스티벌', level: 3 },
        { id: 'f-branch-1-2', name: '공연/음악제/페스티벌', level: 3 },
        { id: 'f-branch-1-3', name: '미술/비엔날레/아트페어', level: 3 },
        { id: 'f-branch-1-4', name: '문학/도서/출판/북페어', level: 3 },
      ]
    },
    {
      id: 'f-trunk-2',
      name: '자연/생태/꽃',
      level: 2,
      children: [
        { id: 'f-branch-2-1', name: '꽃/벚꽃/단풍/눈꽃/식물원', level: 3 },
        { id: 'f-branch-2-2', name: '축제/공원/수목원', level: 3 },
        { id: 'f-branch-2-3', name: '바다/해수욕장/계곡', level: 3 },
      ]
    },
    {
      id: 'f-trunk-3',
      name: '지역특산/전통/역사',
      level: 2,
      children: [
        { id: 'f-branch-3-1', name: '고궁/궁궐/문화재/왕릉', level: 3 },
        { id: 'f-branch-3-2', name: '전통/민속/역사', level: 3 },
        { id: 'f-branch-3-3', name: '지역특산/먹거리', level: 3 },
        { id: 'f-branch-3-4', name: '종교/사찰/사원', level: 3 },
      ]
    },
    {
      id: 'f-trunk-4',
      name: '마을/거리/야간',
      level: 2,
      children: [
        { id: 'f-branch-4-1', name: '마을/골목/벽화마을', level: 3 },
        { id: 'f-branch-4-2', name: '거리/플리마켓', level: 3 },
        { id: 'f-branch-4-3', name: '야간/빛축제/불꽃', level: 3 },
        { id: 'f-branch-4-4', name: '야시장/푸드트럭', level: 3 },
      ]
    }
  ]
};
