import React from 'react';
import AppRoutes from './routes/routes';
import GlobalStyle from './styles/GlobalStyle';
import Navbar from './components/Navbar';

const App = () => {
  return (
    <>
      <GlobalStyle />
      <Navbar />
      <AppRoutes />
    </>
  );
};

export default App;
