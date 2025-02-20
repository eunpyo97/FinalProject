import React, { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { verifyResetToken, resetPassword } from "../api/auth";
import styled from "styled-components";
import Button from "../components/Button";
import { validatePassword, checkPasswordMatch } from "../utils/validation";
import Spinner from "../components/Spinner";

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 70vh;
`;

const Title = styled.h2`
  margin-bottom: 40px;
`;

const Input = styled.input`
  width: 250px;
  padding: 10px;
  margin: 5px;
  border: 1px solid #ccc;
  border-radius: 5px;
`;

const Message = styled.p`
  margin-top: 10px;
  font-size: 14px;
  color: ${({ success }) => (success ? "green" : "red")};
`;

const PasswordValidationText = styled.p`
  font-size: 12px;
  margin-top: 5px;
  color: ${({ valid }) => (valid ? "green" : "red")};
`;

const StyledButton = styled(Button)`
  margin-top: 15px;
`;

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const [email, setEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordValidation, setPasswordValidation] = useState([]);
  const [passwordMatch, setPasswordMatch] = useState(null);
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const token = searchParams.get("token");
    if (!token) {
      setMessage("유효하지 않은 요청입니다.");
      return;
    }

    // 토큰 확인 요청 (백엔드에서 이메일 받아오기)
    verifyResetToken(token)
      .then((data) => {
        if (data.email) {
          setEmail(data.email);
        } else {
          setMessage(data.error || "토큰이 유효하지 않습니다.");
        }
      })
      .catch(() => setMessage("서버 오류가 발생했습니다."));
  }, [searchParams]);

  // 비밀번호 입력 변경 시 유효성 검사
  const handlePasswordChange = (e) => {
    const newPassword = e.target.value;
    setNewPassword(newPassword);
    setPasswordValidation(validatePassword(newPassword));
  };

  // 비밀번호 확인 입력 변경 시 검사
  const handleConfirmPasswordChange = (e) => {
    const newConfirmPassword = e.target.value;
    setConfirmPassword(newConfirmPassword);
    setPasswordMatch(checkPasswordMatch(newPassword, newConfirmPassword));
  };

  const handleResetPassword = async () => {
    if (passwordValidation.length > 0) {
      setMessage("비밀번호가 유효하지 않습니다.");
      return;
    }

    if (!passwordMatch) {
      setMessage("비밀번호가 일치하지 않습니다.");
      return;
    }

    setIsLoading(true);
    setMessage("");

    try {
      await resetPassword(
        searchParams.get("token"),
        email,
        newPassword,
        confirmPassword
      );
      alert("비밀번호가 변경되었습니다.");
      navigate("/login");
      // setMessage("비밀번호가 성공적으로 변경되었습니다.");
      // setTimeout(() => navigate("/login"), 3000);
    } catch (error) {
      setMessage(error.response?.data?.error || "비밀번호 변경 실패");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container>
      <Title>비밀번호 재설정</Title>
      {message && (
        <Message success={message.includes("성공")}>{message}</Message>
      )}
      <Input type="email" value={email} disabled />

      <Input
        type="password"
        placeholder="새 비밀번호"
        value={newPassword}
        onChange={handlePasswordChange}
      />
      {passwordValidation.map((msg, index) => (
        <PasswordValidationText key={index} valid={false.toString()}>
          {msg}
        </PasswordValidationText>
      ))}
      {newPassword && passwordValidation.length === 0 && (
        <PasswordValidationText valid={true}>
          안전한 비밀번호입니다.
        </PasswordValidationText>
      )}

      <Input
        type="password"
        placeholder="비밀번호 확인"
        value={confirmPassword}
        onChange={handleConfirmPasswordChange}
      />
      {confirmPassword && (
        <PasswordValidationText valid={passwordMatch}>
          {passwordMatch
            ? "비밀번호가 일치합니다."
            : "비밀번호가 일치하지 않습니다."}
        </PasswordValidationText>
      )}

      <StyledButton onClick={handleResetPassword} disabled={isLoading}>
        {isLoading ? <Spinner /> : "비밀번호 변경"}
      </StyledButton>
    </Container>
  );
};

export default ResetPassword;
