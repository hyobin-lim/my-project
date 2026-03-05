import { CultureDomain } from '../../types/culture';
import { performanceCategory } from './performance';
import { cinemaCategory } from './cinema';
import { exhibitionCategory } from './exhibition';
import { broadcastCategory } from './broadcast';
import { festivalCategory } from './festival';
import { educationCategory } from './education';

export const ALL_CATEGORIES: CultureDomain[] = [
  performanceCategory,
  cinemaCategory,
  exhibitionCategory,
  broadcastCategory,
  festivalCategory,
  educationCategory,
];

export {
  performanceCategory,
  cinemaCategory,
  exhibitionCategory,
  broadcastCategory,
  festivalCategory,
  educationCategory,
};
