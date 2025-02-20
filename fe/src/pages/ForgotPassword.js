import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { resetPasswordRequest } from "../api/auth";
import styled from "styled-components";
import Button from "../components/Button";
import Spinner from "../components/Spinner";

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
  margin: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
`;

const Message = styled.p`
  margin-top: 10px;
  font-size: 14px;
  color: ${({ success }) => (success ? "green" : "red")};
`;

const ForgotPassword = () => {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleResetRequest = async () => {
    if (!email.trim()) {
      setMessage("이메일을 입력해주세요.");
      return;
    }

    setIsLoading(true);
    setMessage("");

    try {
      await resetPasswordRequest(email);
      setMessage("비밀번호 재설정 링크가 이메일로 전송되었습니다.");

      setTimeout(() => navigate("/login"), 5000);
    } catch (error) {
      setMessage(error.response?.data?.error || "비밀번호 재설정 요청 실패");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container>
      <h2>비밀번호 찾기</h2>
      <Input
        type="email"
        placeholder="이메일 입력"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <Button onClick={handleResetRequest} disabled={isLoading}>
        {isLoading ? <Spinner /> : "비밀번호 재설정 요청"}
      </Button>
      {message && (
        <Message success={message.includes("성공")}>{message}</Message>
      )}
    </Container>
  );
};

export default ForgotPassword;
