import { CultureDomain } from '../../types/culture';

export const educationCategory: CultureDomain = {
  id: 'education',
  name: '교육',
  icon: '🎓',
  trunks: [
    {
      id: 'ed-trunk-1',
      name: '인문학/교양/강연',
      level: 2,
      children: [
        { id: 'ed-branch-1-1', name: '도서관/북토크/저자만남', level: 3 },
        { id: 'ed-branch-1-2', name: '미술/예술/클래식 강연', level: 3 },
        { id: 'ed-branch-1-3', name: '역사/전통/박물관 교육', level: 3 },
        { id: 'ed-branch-1-4', name: '과학/IT/테크 강연', level: 3 },
      ]
    },
    {
      id: 'ed-trunk-2',
      name: '창작/메이커/취미',
      level: 2,
      children: [
        { id: 'ed-branch-2-1', name: '공예/만들기/체험', level: 3 },
        { id: 'ed-branch-2-2', name: '글쓰기/글짓기/시창작', level: 3 },
        { id: 'ed-branch-2-2', name: '미술/드로잉/사진', level: 3 },
        { id: 'ed-branch-2-2', name: '음악/악기/노래', level: 3 },
      ]
    },
    {
      id: 'ed-trunk-3',
      name: '어린이/청소년/가족',
      level: 2,
      children: [
        { id: 'ed-branch-3-1', name: '어린이/청소년 교육', level: 3 },
        { id: 'ed-branch-3-2', name: '가족 참여 프로그램', level: 3 },
        { id: 'ed-branch-3-3', name: '진로/직업 체험', level: 3 },
        { id: 'ed-branch-3-4', name: '캠프/방학 프로그램', level: 3 },
      ]
    },
    {
      id: 'ed-trunk-4',
      name: '디지털/IT/미디어',
      level: 2,
      children: [
        { id: 'ed-branch-4-1', name: '코딩/프로그래밍', level: 3 },
        { id: 'ed-branch-4-2', name: '영상제작/미디어/유튜브', level: 3 },
        { id: 'ed-branch-4-3', name: 'AI/인공지능/데이터', level: 3 },
        { id: 'ed-branch-4-4', name: '스마트폰/스마트기기', level: 3 },
      ]
    },
    {
      id: 'ed-trunk-5',
      name: '전문가/취업/미디어',
      level: 2,
      children: [
        { id: 'ed-branch-5-1', name: '전문직무 교육', level: 3 },
        { id: 'ed-branch-5-2', name: '자격증/취업 특강', level: 3 },
        { id: 'ed-branch-5-3', name: '스타트업/창업 교육', level: 3 },
      ]
    }
  ]
};
