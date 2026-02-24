import { CultureItem } from '../types/culture';

interface Props {
  item: CultureItem;
}

export const CultureCard = ({ item }: Props) => {
  return (
    <div className="culture-card">
      <div className="card-image">
        <img src={item.imageUrl} alt={item.title} />
        <span className={`category-tag ${item.category}`}>{item.category}</span>
        {item.isFree && <span className="free-tag">무료</span>}
      </div>
      <div className="card-content">
        <h3 title={item.title}>{item.title}</h3>
        <p className="location">📍 {item.location}</p>
        <p className="date">📅 {item.startDate} ~ {item.endDate}</p>
        <p className="target">👥 {item.target}</p>
      </div>
    </div>
  );
};
