import type { CultureItem } from '../../types/culture';
import './CultureCard.css';

interface Props {
  item: CultureItem;
}

export const CultureCard = ({ item }: Props) => {
  return (
    <div className="culture-card">
      <div className="card-image">
        <img src={item.imageUrl} alt={item.title} />
        <span className={`category-tag ${item.category}`}>{item.category}</span>
      </div>
      <div className="card-content">
        <h3 title={item.title}>{item.title}</h3>
        <p className="location">📍 {item.location}</p>
        <p className="date">📅 {item.startDate} ~ {item.endDate}</p>
        <div className="card-footer">
          <span className="cost-info">{item.costInfo}</span>
          <span className="source-info">{item.source}</span>
        </div>
      </div>
    </div>
  );
};
