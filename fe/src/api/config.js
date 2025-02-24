import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/'; // Flask 백엔드 주소

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 시 Access Token 자동 추가
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 응답에서 401 (토큰 만료) 발생 시 자동으로 리프레시 토큰 요청
api.interceptors.response.use(
  (response) => response,  // 정상 응답은 그대로 반환
  async (error) => {
    if (error.response && error.response.status === 401) {
      console.warn("액세스 토큰이 만료되었습니다. 자동으로 갱신을 시도합니다.");

      try {
        // 리프레시 토큰으로 새로운 액세스 토큰 요청
        const refreshResponse = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
          withCredentials: true, // 쿠키 기반 리프레시 토큰이 있다면 사용
        });

        const newAccessToken = refreshResponse.data.access_token;

        // 새로운 토큰을 로컬 스토리지에 저장
        localStorage.setItem('access_token', newAccessToken);

        // 원래 요청을 새로운 토큰으로 다시 시도
        error.config.headers.Authorization = `Bearer ${newAccessToken}`;
        return axios(error.config);
      } catch (refreshError) {
        console.error("토큰 갱신 실패. 로그아웃이 필요합니다.");
        localStorage.removeItem('access_token');
        window.location.href = "/login";  // 로그인 페이지로 리디렉션
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
