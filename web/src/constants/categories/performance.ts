import { CultureDomain } from '../../types/culture';

export const performanceCategory: CultureDomain = {
  id: 'performance',
  name: '공연',
  icon: '🎭',
  trunks: [
    {
      id: 'p-trunk-1',
      name: '연극/뮤지컬 [FIX]',
      level: 2,
      children: [
        { 
          id: 'p-branch-1-1', 
          name: '프리미엄/대형/스페셜', 
          level: 3,
          children: [
            { id: 'p-twig-1-1-1', name: '라이선스 대작', level: 4 },
            { id: 'p-twig-1-1-2', name: '오리지널 내한', level: 4 },
            { id: 'p-twig-1-1-3', name: '스타 캐스팅', level: 4 },
          ]
        },
        { 
          id: 'p-branch-1-2', 
          name: '대학로/상설/창작', 
          level: 3,
          children: [
            { id: 'p-twig-1-2-1', name: '로맨틱 코미디', level: 4 },
            { id: 'p-twig-1-2-2', name: '공포/스릴러', level: 4 },
            { id: 'p-twig-1-2-3', name: '창작 뮤지컬', level: 4 },
            { id: 'p-twig-1-2-4', name: '오픈런 연극', level: 4 },
          ]
        },
        { id: 'p-branch-1-3', name: '학생/시민/아마추어', level: 3 },
      ]
    },
    {
      id: 'p-trunk-2',
      name: '클래식/오페라/무용',
      level: 2,
      children: [
        { id: 'p-branch-2-1', name: '독주/협주곡', level: 3 },
        { id: 'p-branch-2-2', name: '교향악/필하모닉', level: 3 },
        { id: 'p-branch-2-3', name: '합창/성악', level: 3 },
        { id: 'p-branch-2-4', name: '오페라', level: 3 },
        { id: 'p-branch-2-5', name: '발레/무용', level: 3 },
        { id: 'p-branch-2-6', name: '현대무용/한국무용', level: 3 },
      ]
    },
    {
      id: 'p-trunk-3',
      name: '국악/전통예술',
      level: 2,
      children: [
        { id: 'p-branch-3-1', name: '판소리/민요', level: 3 },
        { id: 'p-branch-3-2', name: '사물놀이/풍물', level: 3 },
        { id: 'p-branch-3-3', name: '민속/마당놀이', level: 3 },
        { id: 'p-branch-3-4', name: '전통 무용/제례', level: 3 },
      ]
    },
    {
      id: 'p-trunk-4',
      name: '대중음악',
      level: 2,
      children: [
        { id: 'p-branch-4-1', name: '인디/록/재즈', level: 3 },
        { id: 'p-branch-4-2', name: 'K-POP/아이돌', level: 3 },
        { id: 'p-branch-4-3', name: '팝/콘서트/쇼케이스', level: 3 },
        { id: 'p-branch-4-4', name: '포크/발라드/트로트', level: 3 },
      ]
    },
    {
      id: 'p-trunk-5',
      name: '어린이/가족 [FIX]',
      level: 2,
      children: [
        { id: 'p-branch-5-1', name: '캐릭터 뮤지컬/연극', level: 3 },
        { id: 'p-branch-5-2', name: '인형극/오브제극', level: 3 },
        { id: 'p-branch-5-3', name: '가족 음악회/국악 동화', level: 3 },
        { id: 'p-branch-5-4', name: '이색/참여형 퍼포먼스', level: 3 },
      ]
    },
    {
      id: 'p-trunk-6',
      name: '기획/복합/이벤트',
      level: 2,
      children: [
        { id: 'p-branch-6-1', name: '뮤지컬/오페라 갈라쇼', level: 3 },
        { id: 'p-branch-6-2', name: '북콘서트/토크콘서트', level: 3 },
        { id: 'p-branch-6-3', name: '융복합예술 퍼포먼스', level: 3 },
        { id: 'p-branch-6-4', name: '거리공연(버스킹)', level: 3 },
        { id: 'p-branch-6-5', name: '축제/행사 연계 특별공연', level: 3 },
      ]
    }
  ]
};
