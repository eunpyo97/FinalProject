import { createGlobalStyle } from 'styled-components';

const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: 'Arial', sans-serif;
    background-color: #f5f5f5;
    color: #333;
  }

  a {
    text-decoration: none;
    color: inherit;
  }

  button {
    cursor: pointer;
    padding: 10px 15px;
    border: none;
    background-color:#A3C6ED;
    color: white;
    font-size: 16px;
    border-radius: 5px;
    transition: background 0.3s;
  }

  button:hover {
    background-color:#258DFB;
  }

  /* 반응형 스타일 */
  @media (max-width: 768px) {
    body {
      font-size: 14px;
    }
    button {
      font-size: 14px;
      padding: 8px 12px;
    }
  }

`;

export default GlobalStyle;
