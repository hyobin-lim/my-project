import { CultureDomain } from '../../types/culture';

export const broadcastCategory: CultureDomain = {
  id: 'broadcast',
  name: '방송',
  icon: '📺',
  trunks: [
    {
      id: 'b-trunk-1',
      name: '음악/오디션/쇼',
      level: 2,
      children: [
        { id: 'b-branch-1-1', name: '음악 방송/아이돌', level: 3 },
        { id: 'b-branch-1-2', name: '오디션 프로그램/경연', level: 3 },
        { id: 'b-branch-1-3', name: '연말 시상식', level: 3 },
      ]
    },
    {
      id: 'b-trunk-2',
      name: '토크쇼/예능/코미디',
      level: 2,
      children: [
        { id: 'b-branch-2-1', name: '토크쇼/버라이어티', level: 3 },
        { id: 'b-branch-2-2', name: '공개 코미디/개그', level: 3 },
      ]
    },
    {
      id: 'b-trunk-3',
      name: '교양/다큐/시사',
      level: 2,
      children: [
        { id: 'b-branch-3-1', name: '강연/교양/다큐', level: 3 },
        { id: 'b-branch-3-2', name: '시사/토론', level: 3 },
      ]
    },
    {
      id: 'b-trunk-4',
      name: '라디오/기타',
      level: 2,
      children: [
        { id: 'b-branch-4-1', name: '라디오 공개방송', level: 3 },
      ]
    }
  ]
};
