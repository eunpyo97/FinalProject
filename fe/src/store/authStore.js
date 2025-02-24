import { create } from "zustand";
import Cookies from "js-cookie";
import { logout as logoutApi } from "../api/auth";

const useAuthStore = create((set) => ({
  isAuthenticated: !!localStorage.getItem("access_token"),
  accessToken: localStorage.getItem("access_token") || null,
  userId: localStorage.getItem("user_id") || null, // 사용자 ID 추가

  // 로그인 시 userId 및 토큰 저장
  setLogin: (userId, token, rememberMe) => {
    if (rememberMe) {
      Cookies.set("user_id", userId, { expires: 7 });
      Cookies.set("access_token", token, { expires: 7 });
    } else {
      localStorage.setItem("user_id", userId);
      localStorage.setItem("access_token", token);
    }
    set({ isAuthenticated: true, accessToken: token, userId });
  },

  // // 로그아웃 시 상태 초기화
  // logout: () => {
  //   localStorage.removeItem("access_token");
  //   localStorage.removeItem("user_id");
  //   Cookies.remove("access_token");
  //   Cookies.remove("user_id");
  //   set({ isAuthenticated: false, accessToken: null, userId: null });
  // },


  // 로그아웃 API 호출 후 상태 초기화
  logout: async () => {
    await logoutApi(); 
    set({ isAuthenticated: false, accessToken: null, userId: null });
  },
}));

export default useAuthStore;
