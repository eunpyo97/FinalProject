import React from 'react';
import styled from 'styled-components';

const ErrorText = styled.p`
  color: red;
  font-size: 14px;
  margin: 5px 0;
`;

const ErrorMessage = ({ message }) => {
  return message ? <ErrorText>{message}</ErrorText> : null;
};

export default ErrorMessage;
