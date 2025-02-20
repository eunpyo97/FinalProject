// 비밀번호 유효성 검사 함수
export const validatePassword = (password) => {
    const conditions = [];
    if (password.length < 8)
      conditions.push('비밀번호는 최소 8자 이상이어야 합니다.');
    if (!/[A-Z]/.test(password)) conditions.push('대문자를 포함해야 합니다.');
    if (!/[a-z]/.test(password)) conditions.push('소문자를 포함해야 합니다.');
    if (!/[0-9]/.test(password)) conditions.push('숫자를 포함해야 합니다.');
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password))
      conditions.push('특수문자를 포함해야 합니다.');
    return conditions;
  };
  
  // 비밀번호 확인 (일치 여부)
  export const checkPasswordMatch = (password, confirmPassword) => {
    return password === confirmPassword;
  };
  