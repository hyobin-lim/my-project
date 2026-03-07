import { CultureDomain } from '../../types/culture';

export const cinemaCategory: CultureDomain = {
  id: 'cinema',
  name: '영화',
  icon: '🎬',
  trunks: [
    {
      id: 'c-trunk-1',
      name: '시사회/기업혜택',
      level: 2,
      children: [
        { id: 'c-branch-1-1', name: '시사회/초대 응모', level: 3 },
        { id: 'c-branch-1-2', name: '통신사/카드사 우대', level: 3 },
        { id: 'c-branch-1-3', name: '0원 딜/선착순 할인권', level: 3 },
      ]
    },
    {
      id: 'c-trunk-2',
      name: '공공/도서관 상영',
      level: 2,
      children: [
        { id: 'c-branch-2-1', name: '전국 공공도서관', level: 3 },
        { id: 'c-branch-2-2', name: '구청/시민강당 상영', level: 3 },
        { id: 'c-branch-2-3', name: '미디어센터 상영', level: 3 },
        { id: 'c-branch-2-4', name: '박물관/미술관 상영', level: 3 },
        { id: 'c-branch-2-5', name: '자치회관 주말극장', level: 3 },
      ]
    },
    {
      id: 'c-trunk-3',
      name: '야외/이색 상영',
      level: 2,
      children: [
        { id: 'c-branch-3-1', name: '자동차 극장', level: 3 },
        { id: 'c-branch-3-2', name: '상설 야외상영/시민극장', level: 3 },
        { id: 'c-branch-3-3', name: '카페/옥상/이색 상영공간', level: 3 },
        { id: 'c-branch-3-4', name: '축제/이벤트 연계 특별상영', level: 3 },
      ]
    },
    {
      id: 'c-trunk-4',
      name: '독립/예술/시네마테크',
      level: 2,
      children: [
        { id: 'c-branch-4-1', name: '독립/예술영화 상영', level: 3 },
        { id: 'c-branch-4-2', name: '시네마테크 기획전', level: 3 },
        { id: 'c-branch-4-3', name: '고전/아카이브 기획전', level: 3 },
        { id: 'c-branch-4-4', name: '예술영화 전용관', level: 3 },
      ]
    },
    {
      id: 'c-trunk-5',
      name: '실버/추억/전용관',
      level: 2,
      children: [
        { id: 'c-branch-5-1', name: '실버/추억 전용상영관', level: 3 },
        { id: 'c-branch-5-2', name: '고전 명작 상설상영', level: 3 },
        { id: 'c-branch-5-3', name: '추억의 영화 기획전', level: 3 },
      ]
    },
    {
      id: 'c-trunk-6',
      name: '어린이/가족/애니',
      level: 2,
      children: [
        { id: 'c-branch-6-1', name: '어린이/가족 상설상영', level: 3 },
        { id: 'c-branch-6-2', name: '애니메이션 전용상영관', level: 3 },
        { id: 'c-branch-6-3', name: '만화박물관 기획상영', level: 3 },
      ]
    },
    {
      id: 'c-trunk-7',
      name: '감독/배우 GV/교육',
      level: 2,
      children: [
        { id: 'c-branch-7-1', name: '감독/배우 GV', level: 3 },
        { id: 'c-branch-7-2', name: '영화 해설/강연', level: 3 },
        { id: 'c-branch-7-3', name: '영화 제작 체험', level: 3 },
        { id: 'c-branch-7-4', name: '청소년 영화 교육', level: 3 },
      ]
    }
  ]
};
