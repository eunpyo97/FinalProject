import api from "./config";
import Cookies from "js-cookie";

/**
 * 회원가입 API
 */
export const signup = async (email, password, confirmPassword) => {
  try {
    const response = await api.post("/auth/register", {
      email,
      password,
      confirm_password: confirmPassword,
    });

    // 백엔드 응답에서 user_id 추출
    const { user_id } = response.data;

    if (!user_id) {
      throw new Error("서버에서 유효한 사용자 ID가 반환되지 않았습니다.");
    }

    // 로컬스토리지 및 쿠키에 저장
    localStorage.setItem("user_id", user_id);
    Cookies.set("user_id", user_id, { expires: 7 });

    return response.data;
  } catch (error) {
    console.error(
      "회원가입 실패:",
      error.response?.data?.error || error.message
    );
    throw error;
  }
};

/**
 * 로그인 API
 */
export const login = async (email, password, rememberMe) => {
  try {
    const response = await api.post("/auth/login", {
      email,
      password,
      remember_me: rememberMe,
    });

    // 백엔드 응답에서 user_id, access_token, refresh_token 추출
    const { user_id, access_token, refresh_token } = response.data;

    if (!access_token || !refresh_token) {
      throw new Error("서버에서 유효한 토큰이 반환되지 않았습니다.");
    }

    // 로컬스토리지 및 쿠키에 저장
    localStorage.setItem("user_id", user_id);
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("refresh_token", refresh_token);

    Cookies.set("user_id", user_id, { expires: rememberMe ? 7 : null });
    Cookies.set("access_token", access_token, {
      expires: rememberMe ? 7 : null,
    });
    Cookies.set("refresh_token", refresh_token, {
      expires: rememberMe ? 7 : null,
    });

    return { user_id, access_token };
  } catch (error) {
    console.error("로그인 실패:", error.response?.data?.error || error.message);
    throw error;
  }
};

/**
 * 로그인 상태 확인 함수
 */
export const isAuthenticated = () => {
  const accessToken =
    localStorage.getItem("access_token") || Cookies.get("access_token");
  return !!accessToken; // 액세스 토큰이 있으면 로그인 상태
};

/**
 * 로그아웃 API
 */
export const logout = async () => {
  try {
    const accessToken = Cookies.get("access_token") || localStorage.getItem("access_token");

    if (!accessToken) {
      console.warn("로그아웃 요청 실패: 액세스 토큰 없음");
      return;
    }

    console.log("로그아웃 API 요청 전송", { access_token: accessToken });

    await api.post("/auth/logout", { access_token: accessToken }); 

    console.log("로그아웃 API 호출 성공");

    // 토큰 삭제
    Cookies.remove("user_id");
    Cookies.remove("access_token");
    Cookies.remove("refresh_token");

    localStorage.removeItem("user_id");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");

    alert("로그아웃이 완료되었습니다.");
  } catch (error) {
    console.error("로그아웃 실패:", error.response?.data?.error || error.message);
    alert("로그아웃에 실패했습니다. 다시 시도해주세요.");
  }
};


/**
 * 토큰 갱신 (Refresh Token 사용)
 */
export const refreshAccessToken = async () => {
  try {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) throw new Error("Refresh Token이 없습니다.");

    const response = await api.post("/auth/refresh-token", {
      refresh_token: refreshToken,
    });

    if (!response.data.access_token) {
      throw new Error("서버에서 새로운 액세스 토큰이 반환되지 않았습니다.");
    }

    // 새로운 액세스 토큰 저장
    localStorage.setItem("access_token", response.data.access_token);
    Cookies.set("access_token", response.data.access_token);

    return response.data.access_token;
  } catch (error) {
    console.error(
      "토큰 갱신 실패:",
      error.response?.data?.error || error.message
    );

    // Refresh token이 만료된 경우 자동 로그아웃
    if (error.response?.status === 400 || error.response?.status === 401) {
      await logout();
    }
    throw error;
  }
};

/**
 * 이메일 인증 요청 (이메일 입력 후 요청)
 */
export const verifyEmailRequest = async (email) => {
  try {
    const response = await api.post("/auth/verify-email-request", { email });
    return response.data;
  } catch (error) {
    console.error(
      "이메일 인증 요청 실패:",
      error.response?.data?.error || error.message
    );
    throw error;
  }
};

/**
 * 이메일 인증 (6자리 코드 입력)
 */
export const verifyEmail = async (email, code) => {
  try {
    const response = await api.post("/auth/verify-email", { email, code });
    return response.data;
  } catch (error) {
    console.error(
      "이메일 인증 실패:",
      error.response?.data?.error || error.message
    );
    throw error;
  }
};

/**
 * 이메일 인증 코드 재전송
 */
export const resendVerificationCode = async (email) => {
  try {
    const response = await api.post("/auth/resend-verification-code", {
      email,
    });
    return response.data;
  } catch (error) {
    console.error(
      "인증 코드 재전송 실패:",
      error.response?.data?.error || error.message
    );
    throw error;
  }
};

/**
 * 비밀번호 재설정 요청 (이메일 입력 후 요청)
 */
export const resetPasswordRequest = async (email) => {
  try {
    const response = await api.post("/auth/request-password-reset", { email });
    return response.data;
  } catch (error) {
    console.error(
      "비밀번호 재설정 요청 실패:",
      error.response?.data?.error || error.message
    );
    throw error;
  }
};

/**
 * 비밀번호 재설정 페이지에서 토큰 검증 및 이메일 확인
 */
export const resetPassword = async (
  token,
  email,
  newPassword,
  confirmPassword
) => {
  try {
    const response = await api.post("/auth/reset-password", {
      token,
      email,
      new_password: newPassword,
      confirm_password: confirmPassword,
    });
    return response.data;
  } catch (error) {
    console.error(
      "비밀번호 재설정 실패:",
      error.response?.data?.error || error.message
    );
    throw error;
  }
};

/**
 * 비밀번호 재설정 페이지에서 토큰 검증 및 이메일 확인
 */
export const verifyResetToken = async (token) => {
  try {
    const response = await api.get(`/auth/reset-password?token=${token}`);
    return response.data; // { email: "사용자 이메일" }
  } catch (error) {
    console.error(
      "토큰 검증 실패:",
      error.response?.data?.error || error.message
    );
    throw error;
  }
};

/**
 * 이메일 인증 상태 확인
 */
export const verifyEmailStatus = async (email) => {
  try {
    const response = await api.get(`/auth/verify-email-status?email=${email}`);
    return response.data; // { verified: true } 또는 { verified: false }
  } catch (error) {
    console.error(
      "이메일 인증 상태 확인 실패:",
      error.response?.data?.error || error.message
    );
    throw error;
  }
};
