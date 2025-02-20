import { create } from 'zustand';
import Cookies from 'js-cookie';

const useAuthStore = create((set) => ({
  isAuthenticated: !!localStorage.getItem('access_token'),
  accessToken: localStorage.getItem('access_token') || null, // 상태로 accessToken 관리

  // 로그인 시 토큰 저장 및 상태 변경
  setLogin: (token, rememberMe) => {
    if (rememberMe) {
      Cookies.set('access_token', token, { expires: 7 });
    } else {
      localStorage.setItem('access_token', token);
    }
    set({ isAuthenticated: true, accessToken: token });
  },

  // 로그아웃 시 상태 초기화
  logout: () => {
    localStorage.removeItem('access_token');
    Cookies.remove('access_token');
    set({ isAuthenticated: false, accessToken: null });
  }
}));

export default useAuthStore;
