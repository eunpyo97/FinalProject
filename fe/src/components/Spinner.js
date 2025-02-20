import React from "react";
import styled, { keyframes } from "styled-components";

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const Loader = styled.div`
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid #fff; 
  border-radius: 50%;
  width: 3em;  
  height: 1.5em; 
  animation: ${spin} 1s linear infinite;
`;

const Spinner = () => {
  return <Loader />;
};

export default Spinner;
