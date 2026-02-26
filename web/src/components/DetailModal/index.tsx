import type { CultureItem } from '../../types/culture';
import './DetailModal.css';

interface Props {
  item: CultureItem | null;
  onClose: () => void;
}

export const DetailModal = ({ item, onClose }: Props) => {
  if (!item) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>&times;</button>
        
        <div className="modal-header-image">
          <img src={item.imageUrl} alt={item.title} />
          <div className="modal-category-badge">{item.category}</div>
        </div>

        <div className="modal-body">
          <div className="benefit-highlight">
            <span className="benefit-label">혜택 안내</span>
            <span className="benefit-value">{item.costInfo}</span>
          </div>

          <h2 className="modal-title">{item.title}</h2>
          
          <div className="info-grid">
            <div className="info-item">
              <span className="label">📍 장소</span>
              <span className="value">{item.location}</span>
            </div>
            <div className="info-item">
              <span className="label">📅 기간</span>
              <span className="value">{item.startDate} ~ {item.endDate}</span>
            </div>
            <div className="info-item">
              <span className="label">🏛️ 출처</span>
              <span className="value">{item.source}</span>
            </div>
            {item.target && (
              <div className="info-item">
                <span className="label">👥 대상</span>
                <span className="value">{item.target}</span>
              </div>
            )}
          </div>

          <div className="modal-description">
            <h3>상세 안내</h3>
            <p>본 정보는 {item.source}에서 제공하는 실시간 문화 정보입니다. 상세 일정이나 예약 방법은 아래 버튼을 눌러 원문 사이트에서 확인해 주세요.</p>
          </div>

          <div className="modal-footer">
            <a href="#" className="primary-btn" onClick={(e) => e.preventDefault()}>
              🚀 원문 사이트에서 확인하기 (외부 이동)
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
