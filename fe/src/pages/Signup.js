import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { signup, verifyEmailRequest, verifyEmail } from "../api/auth";
// import api from '../api/config';
import styled from "styled-components";
import Button from "../components/Button";
import ErrorMessage from "../components/ErrorMessage";
import { validatePassword, checkPasswordMatch } from "../utils/validation";
import Spinner from "../components/Spinner";

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
`;

const Title = styled.h2`
  margin-bottom: 50px;
`;

const FormContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 15px;
`;

const InputContainer = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

const EmailContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
`;

const Input = styled.input`
  width: 250px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-sizing: border-box;
`;

const EmailInput = styled(Input)`
  height: 40px;
`;

const EmailButton = styled(Button)`
  height: 40px;
  padding: 0 20px;
  white-space: nowrap;
  flex-shrink: 0;
`;

const SignupButtonWrapper = styled.div`
  width: 100%;
  display: flex;
`;

const SignupButton = styled(Button)`
  width: 250px;
  margin-top: 20px;
`;

const PasswordValidationText = styled.p`
  font-size: 12px;
  margin-top: 5px;
  color: ${(props) => (props.valid ? "green" : "red")};
`;


const Signup = () => {
  const [email, setEmail] = useState("");
  const [isEmailVerified, setIsEmailVerified] = useState(false);
  const [verificationSent, setVerificationSent] = useState(false);
  const [verificationCode, setVerificationCode] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordValidation, setPasswordValidation] = useState([]);
  const [passwordMatch, setPasswordMatch] = useState(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const [isEmailLoading, setIsEmailLoading] = useState(false); 
  const [isSignupLoading, setIsSignupLoading] = useState(false); 

  // 페이지 로딩 시 로컬스토리지 초기화
  useEffect(() => {
    console.log("컴포넌트 마운트, 이메일:", email);
    // 페이지가 처음 로딩될 때만 로컬 스토리지 초기화
    // localStorage.removeItem(`pending_user:${email}`);
    // localStorage.removeItem(`verification_code:${email}`);
  }, [email]);

  // 이메일 인증 요청
  const handleEmailVerificationRequest = async () => {
    try {
      setIsEmailLoading(true);
      setError("");

      console.log("인증 요청 이메일:", email);

      // 백엔드에 이메일 인증 요청
      const responseData = await verifyEmailRequest(email);
      console.log("서버 응답 데이터:", responseData);

      // 이미 가입된 이메일이면 처리
      if (responseData.error === "이미 가입된 이메일입니다.") {
        alert("이미 가입된 이메일입니다.");
        setEmail("");
        return;
      }

      // 인증 코드가 정상적으로 왔을 때 처리
      if (responseData.verificationCode) {
        console.log("저장할 인증 코드:", responseData.verificationCode);
        localStorage.setItem(
          `verification_code:${email}`,
          responseData.verificationCode
        );
        console.log(
          "저장 후 확인:",
          localStorage.getItem(`verification_code:${email}`)
        );
      } else {
        console.log("서버에서 인증 코드를 받지 못함");
        setError("서버 오류: 인증 코드가 없습니다.");
        return;
      }

      setVerificationSent(true);
      alert("이메일이 전송되었습니다. 인증 코드를 입력해주세요.");
    } catch (error) {
      console.error("이메일 인증 요청 실패:", error);
      setError(error.response?.data?.error || "서버 오류");
    } finally {
      setIsEmailLoading(false);
    }
  };

  const handleVerifyEmailCode = async () => {
    try {
      console.log("현재 이메일:", email);
      console.log("입력된 인증 코드:", verificationCode);

      const storedCode = localStorage.getItem(`verification_code:${email}`);
      console.log("저장된 인증 코드:", storedCode);
      console.log("localStorage 전체:", localStorage);

      if (!storedCode) {
        console.log("저장된 코드가 없음");
        alert("인증 코드가 만료되었거나 존재하지 않습니다.");
        return;
      }

      console.log("코드 비교:", {
        stored: storedCode.trim(),
        input: verificationCode.trim(),
        isEqual: storedCode.trim() === verificationCode.trim(),
      });

      if (storedCode.trim() === verificationCode.trim()) {
        await verifyEmail(email, verificationCode);
        setIsEmailVerified(true);
        alert("이메일 인증이 완료되었습니다.");

        // 인증 성공 후 로컬스토리지에서 코드 삭제
        localStorage.removeItem(`verification_code:${email}`);
      } else {
        alert("잘못된 인증 코드입니다.");
      }
    } catch (error) {
      console.error("인증 확인 실패:", error);
      console.error("에러 상세:", error.response);
      alert(error.response?.data?.error || "서버 오류");
    }
  };

  // 비밀번호 입력 변경 시 유효성 검사
  const handlePasswordChange = (e) => {
    const newPassword = e.target.value;
    setPassword(newPassword);
    setPasswordValidation(validatePassword(newPassword));
  };

  // 비밀번호 확인 입력 변경 시 검사
  const handleConfirmPasswordChange = (e) => {
    const newConfirmPassword = e.target.value;
    setConfirmPassword(newConfirmPassword);
    setPasswordMatch(checkPasswordMatch(password, newConfirmPassword));
  };

  // 회원가입 요청
  const handleSignup = async () => {
    if (!email || !password || !confirmPassword) {
      alert("모든 항목을 입력해주세요.");
      return;
    }

    if (!isEmailVerified) {
      alert("이메일 인증이 완료되지 않았습니다.");
      return;
    }

    if (passwordValidation.length > 0) {
      alert("비밀번호가 유효하지 않습니다.");
      return;
    }

    if (!passwordMatch) {
      alert("비밀번호가 일치하지 않습니다.");
      return;
    }

    setIsSignupLoading(true); 

    try {
      await signup(email, password, confirmPassword);
      alert("회원가입 성공! 로그인 페이지로 이동합니다.");
      navigate("/login");
    } catch (error) {
      setError(error.response?.data?.error || "회원가입 실패");
    } finally {
      setIsSignupLoading(false); 
    }
  };

  return (
    <Container>
      <Title>회원가입</Title>

      <FormContainer>
        {/* 이메일 입력 & 인증 요청 버튼 */}
        <EmailContainer>
          <EmailInput
            type="email"
            placeholder="이메일"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={isEmailVerified}
          />
          {isEmailLoading ? (
            <Spinner />
          ) : (
            <EmailButton
              onClick={handleEmailVerificationRequest}
              bgColor="#A3C6ED"
              hoverColor="#258DFB"
            >
              {verificationSent ? "재전송" : "인증 요청"}
            </EmailButton>
          )}
        </EmailContainer>

        {/* 인증 코드 입력 */}
        {verificationSent && !isEmailVerified && (
          <EmailContainer>
            <EmailInput
              type="text"
              placeholder="인증 코드 입력"
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value)}
            />
            <EmailButton
              onClick={handleVerifyEmailCode}
              bgColor="#A3C6ED"
              hoverColor="#258DFB"
            >
              인증 확인
            </EmailButton>
          </EmailContainer>
        )}

        {/* 비밀번호 입력 */}
        <InputContainer>
          <Input
            type="password"
            placeholder="비밀번호"
            value={password}
            onChange={handlePasswordChange}
          />
          {passwordValidation.map((msg, index) => (
            <PasswordValidationText key={index} valid={false.toString()}>
              {msg}
            </PasswordValidationText>
          ))}

          {password && passwordValidation.length === 0 && (
            <PasswordValidationText valid={true}>
              안전한 비밀번호입니다.
            </PasswordValidationText>
          )}
        </InputContainer>

        {/* 비밀번호 확인 입력 */}
        <InputContainer>
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
        </InputContainer>

        {/* 회원가입 버튼 */}
        <SignupButtonWrapper>
          {isSignupLoading ? (
            <Spinner />
          ) : (
            <SignupButton
              onClick={handleSignup}
              bgColor="#A3C6ED"
              hoverColor="#258DFB"
            >
              회원가입
            </SignupButton>
          )}
        </SignupButtonWrapper>
        <ErrorMessage message={error} />
      </FormContainer>
    </Container>
  );
};

export default Signup;
