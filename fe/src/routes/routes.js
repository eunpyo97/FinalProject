import { Routes, Route } from "react-router-dom";
import Landing from "../pages/Landing";
import Login from "../pages/Login";
import Signup from "../pages/Signup";
import Home from "../pages/Home";
import PrivateRoute from "./PrivateRoute";
import ForgotPassword from "../pages/ForgotPassword";
import ResetPassword from "../pages/ResetPassword";
import Chat from "../pages/Chat";
import ChatList from "../pages/ChatList";
import ChatRoomDetail from "../pages/ChatRoomDetail";
import ChatSettings from "../pages/ChatSettings";

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />

      {/* 로그인한 사용자만 접근 가능 */}
      <Route element={<PrivateRoute />}>
        <Route path="/home" element={<Home />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/chatlist" element={<ChatList />} />
        <Route path="/chatroom/:chatroomId" element={<ChatRoomDetail />} />
        <Route path="/chat-settings" element={<ChatSettings />} />
      </Route>
    </Routes>
  );
};

export default AppRoutes;
