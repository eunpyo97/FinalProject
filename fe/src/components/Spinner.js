import React from "react";
import styled, { keyframes } from "styled-components";

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const Loader = styled.div`
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 2.5em;
  height: 2.5em;
  animation: ${spin} 0.8s linear infinite;
`;

const Spinner = () => {
  return <Loader />;
};

export default Spinner;
