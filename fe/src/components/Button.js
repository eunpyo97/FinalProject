import styled from 'styled-components';

const StyledButton = styled.button.attrs((props) => ({
  // props로 받은 bgColor, hoverColor 그대로 적용
  style: {
    backgroundColor: props.bgColor || '#A3C6ED',
    color: props.color || 'white',
    fontSize: props.size || '16px',
    transition: 'background 0.3s',
  }
}))`
  padding: 10px 15px;
  border: none;
  border-radius: 5px;

  &:hover {
    background-color: ${(props) => props.hoverColor || '#258DFB'};
  }
`;

const Button = ({ children, onClick, bgColor, color, size, hoverColor }) => {
  return (
    <StyledButton onClick={onClick} bgColor={bgColor} color={color} size={size} hoverColor={hoverColor}>
      {children}
    </StyledButton>
  );
};

export default Button;
