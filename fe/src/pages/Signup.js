import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { signup, verifyEmailRequest, verifyEmail } from "../api/auth";
// import api from '../api/config';
import styled from "styled-components";
import ErrorMessage from "../components/ErrorMessage";
import { validatePassword, checkPasswordMatch } from "../utils/validation";
import Spinner from "../components/Spinner";
import Cookies from "js-cookie"; 

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 75vh;
`;

const Title = styled.h2`
  margin-bottom: 40px;
  font-size: 30px;
  font-weight: bold;
  color: rgb(3, 69, 135);
  text-shadow: 2px 2px 0px rgba(0, 0, 0, 0.2), 4px 4px 0px rgba(0, 0, 0, 0.15);
  letter-spacing: 1px;
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
  width: 260px;
  height: 45px;
  padding: 10px;
  border: 1px solid rgba(199, 229, 248, 0.5);
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease-in-out;
  box-shadow: inset 0px 2px 5px rgba(0, 0, 0, 0.05);

  &:hover {
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.15);
    transform: scale(1.02);
  }

  &:focus {
    outline: none;
    border-color: #3498db;
    background: white;
    box-shadow: 0px 0px 10px rgba(52, 152, 219, 0.5);
    transform: scale(1.03);
  }
`;

const EmailInput = styled(Input)`
  width: 260px;
  height: 45px;
  transition: all 0.3s ease-in-out;
  box-shadow: inset 0px 2px 5px rgba(0, 0, 0, 0.05);

  &:hover {
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.15);
    transform: scale(1.02);
  }

  &:focus {
    outline: none;
    border-color: #3498db;
    background: white;
    box-shadow: 0px 0px 10px rgba(52, 152, 219, 0.5);
    transform: scale(1.03);
  }
`;

const EmailButton = styled.button`
  height: 45px;
  padding: 0 20px;
  white-space: nowrap;
  flex-shrink: 0;
  border: none;
  border-radius: 8px;
  background: linear-gradient(to right, #3498db, #2980b9);
  color: white;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease-in-out;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);

  &:hover {
    background: linear-gradient(to right, #2980b9, #217dbb);
    box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.3);
  }

  &:disabled {
    background: #bdc3c7;
    cursor: not-allowed;
    box-shadow: none;
  }
`;

const SignupButtonWrapper = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 10px;
`;

const SignupButton = styled.button`
  width: 260px;
  height: 45px;
  margin-top: 10px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(to right, #3498db, #2980b9);
  color: white;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease-in-out;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);

  &:hover {
    background: linear-gradient(to right, #2980b9, #217dbb);
    box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.3);
    transform: scale(1.05);
  }

  &:active {
    transform: scale(0.98);
    box-shadow: inset 2px 2px 5px rgba(0, 0, 0, 0.2);
  }

  &:disabled {
    background: #bdc3c7;
    cursor: not-allowed;
    box-shadow: none;
    opacity: 0.7;
  }

  &::before {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    width: 150%;
    height: 150%;
    background: rgba(255, 255, 255, 0.2);
    transition: all 0.3s ease-in-out;
    transform: translate(-50%, -50%) scale(0);
    border-radius: 50%;
  }

  &:hover::before {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0;
  }
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
    const response = await signup(email, password, confirmPassword);

    console.log("[DEBUG] 회원가입 성공, 서버 응답:", response);

    const { user_id } = response;

    if (!user_id) {
      throw new Error("서버에서 user_id가 반환되지 않았습니다.");
    }

    // 회원가입 후 user_id를 저장
    localStorage.setItem("user_id", user_id);
    Cookies.set("user_id", user_id, { expires: 7 });

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
