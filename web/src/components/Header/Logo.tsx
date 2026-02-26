interface Props {
  onLogoClick: () => void;
}

export const Logo = ({ onLogoClick }: Props) => {
  return (
    <div className="logo" onClick={onLogoClick} style={{ cursor: 'pointer' }}>
      🏛️ <span>무료문화생활</span>
    </div>
  );
};
