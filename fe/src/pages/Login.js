import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../api/auth";
import useAuthStore from "../store/authStore";
import styled from "styled-components";
import Button from "../components/Button";
import Spinner from "../components/Spinner";

const Title = styled.h2`
  margin-bottom: 40px;
`;

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
`;

const Input = styled.input`
  width: 250px;
  padding: 10px;
  margin: 5px;
  border: 1px solid #ccc;
  border-radius: 5px;
`;

const CheckboxContainer = styled.div`
  display: flex;
  align-items: center;
  margin: 5px;
`;

const ForgotPassword = styled.p`
  margin-top: 10px;
  font-size: 14px;
  color: #98bde6;
  cursor: pointer;

  &:hover {
    color: #0056b3;
  }
`;

const LoginButtonWrapper = styled.div`
  width: 250px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 15px;
`;

const LoginButton = styled(Button)`
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
`;


const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const { setLogin } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      setIsLoading(true);
  
      console.log("[DEBUG] 로그인 요청 시작", { email, password, rememberMe });
  
      const response = await login(email, password, rememberMe);
  
      console.log("[DEBUG] 로그인 성공, 응답 데이터:", response);
  
      // Zustand 상태 업데이트 (user_id 포함)
      setLogin(response.user_id, response.access_token, rememberMe);
  
      alert("로그인 성공! 홈 화면으로 이동합니다.");
      navigate("/home");
    } catch (error) {
      alert("로그인 실패: " + (error.response?.data?.error || "서버 오류"));
    } finally {
      setIsLoading(false);
    }
  };
  
  

  return (
    <Container>
      <Title>로그인</Title>
      <Input
        type="email"
        placeholder="이메일"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <Input
        type="password"
        placeholder="비밀번호"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <CheckboxContainer>
        <input
          type="checkbox"
          checked={rememberMe}
          onChange={(e) => setRememberMe(e.target.checked)}
        />
        <label>로그인 유지</label>
      </CheckboxContainer>
      <LoginButtonWrapper>
        <LoginButton onClick={handleLogin} disabled={isLoading}>
          {isLoading ? <Spinner /> : "로그인"}
        </LoginButton>
      </LoginButtonWrapper>

      <ForgotPassword onClick={() => navigate("/forgot-password")}>
        비밀번호를 잊으셨나요?
      </ForgotPassword>
    </Container>
  );
};

export default Login;
