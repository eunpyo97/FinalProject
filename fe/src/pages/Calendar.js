import React, { useState, useEffect } from "react";
import Calendar from "react-calendar";
import "react-calendar/dist/Calendar.css";
import styled from "styled-components";
import { getChatEndStatus } from "../api/calendar";
import { getUserChatHistory } from "../api/chat";
import { getDiaryList } from "../api/diary";
import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";
import DiaryList from "./DiaryList";
import { RingLoader } from "react-spinners";
import { useMemo } from "react";

dayjs.extend(utc);
dayjs.extend(timezone);

const CalendarWrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  min-height: 100vh;
  background: linear-gradient(to top, rgb(214, 231, 249), #f0f4f8);
  padding: 20px;
  box-sizing: border-box;
  h2 {
    margin-top: 20px;
    margin-bottom: 20px;
    color: rgb(7, 75, 130);
  }
`;
const LoadingText = styled.div`
  margin-top: 20px;
  font-size: 18px;
  color: #666;
  text-align: center;
`;
const LoadingContainer = styled.div`
  display: flex;
  justify-content: flex-start;
  align-items: center;
  height: 100%;
  width: 100%;
  flex-direction: column;
  padding-top: 60px;
`;
const StyledCalendar = styled(Calendar)`
  border: none;
  border-radius: 20px;
  box-shadow: 0px 20px 20px rgba(1, 34, 53, 0.1);
  background: white;
  padding: 20px;
  font-size: 15px;
  width: 90%;
  max-width: 800px;
  min-width: 430px;
  min-height: 535px;
  margin: 0 auto;

  .react-calendar__month-view__days__day--neighboringMonth {
    color: rgba(157, 157, 157, 0.31) !important;
    pointer-events: none;
    background-color: rgb(254, 254, 254) !important;
  }
  .react-calendar__navigation {
    background: #90caf9;
    border-radius: 10px;
    padding: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    min-height: 50px;
    box-shadow: 0px 10px 15px rgba(0, 0, 0, 0.1);
  }
  .react-calendar__navigation button {
    color: white;
    font-weight: bold;
    font-size: 20px;
    padding: 8px 12px;
    border-radius: 5px;
    background-color: transparent;
    transition: background 0.3s ease-in-out, color 0.3s ease-in-out;
  }
  .react-calendar__navigation button:hover {
    background-color: rgb(11, 104, 180);
    color: white;
  }
  .react-calendar__month-view__weekdays {
    text-align: center;
    font-size: 16px;
    font-weight: bold;
    padding: 5px 0;
    background-color: rgb(247, 218, 238);
    border-radius: 10px;
    margin-bottom: 15px;
    box-shadow: 0px 10px 15px rgba(0, 0, 0, 0.1);
  }
  .react-calendar__tile {
    height: 80px;
    width: 100px;
    flex-grow: 1;
    color: rgb(60, 68, 76);
    font-weight: bold;
    font-size: 15px;
    display: flex;
    align-items: flex-start;
    justify-content: flex-start;
    padding: 5px;
    background-color: rgb(255, 246, 252);
    position: relative;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }
  .react-calendar__tile:hover {
    background: #bbdefb;
    transform: scale(1.07) translateY(-3px);
    color: #03396c;
    font-weight: bold;
    box-shadow: 0px 10px 15px rgba(0, 0, 0, 0.2);
  }
  .react-calendar__tile--active {
    background: #64b5f6 !important;
    color: white;
    font-weight: bold;
  }
  .emotion-icon {
    position: absolute;
    bottom: 5px;
    right: 5px;
    font-size: 18px;
    display: flex;
    flex-wrap: wrap;
  }
  .emotion-icon span {
    margin: 2px;
  }
`;
const emotionIcons = {
  happy: "😄",
  sadness: "😭",
  angry: "😡",
  panic: "😨",
  default: "😐",
};
const CalendarPage = () => {
  const [date, setDate] = useState(new Date());
  const [chatEmotions, setChatEmotions] = useState({});
  const [selectedDate, setSelectedDate] = useState(null);
  const [diaryEntries, setDiaryEntries] = useState([]);
  const [loading, setLoading] = useState(true);

  // 캐시 데이터의 유효성 검사 함수
  const isCacheValid = (cachedData, maxAge = 60 * 1000) => {
    if (!cachedData) return false;
    const { timestamp } = JSON.parse(cachedData);
    return Date.now() - timestamp < maxAge; // 캐시 유효 시간
  };

  useEffect(() => {
    const fetchChatEndStatuses = async () => {
      try {
        setLoading(true);

        // 캐시 데이터 확인 및 유효성 검사
        const cachedData = localStorage.getItem("chatEmotions");
        if (cachedData && isCacheValid(cachedData)) {
          setChatEmotions(JSON.parse(cachedData).data);
          setLoading(false);
          return;
        }

        // API 호출로 최신 데이터 가져오기
        const chatrooms = await getUserChatHistory();
        const chatroomIds = chatrooms.map((room) => room.chatroom_id);

        const chatStatusPromises = chatroomIds.map(async (chatroomId) => {
          try {
            const response = await getChatEndStatus(chatroomId);
            return { chatroomId, ...response };
          } catch (error) {
            console.error(
              `[ERROR] 채팅방(${chatroomId}) 종료 상태 조회 실패:`,
              error
            );
            return null;
          }
        });

        const resolvedStatuses = await Promise.all(chatStatusPromises);

        const emotionsMap = {};
        resolvedStatuses.forEach((status) => {
          if (!status || !status.conversation_end) return;

          const formattedDate = processEmotionData(status);
          if (!formattedDate) return;

          const { date, emoji } = formattedDate;
          if (!emotionsMap[date]) {
            emotionsMap[date] = [];
          }
          emotionsMap[date].push(emoji);
        });

        // 상태 업데이트 및 캐싱 (타임스탬프 추가)
        const dataToCache = { data: emotionsMap, timestamp: Date.now() };
        setChatEmotions(emotionsMap);
        localStorage.setItem("chatEmotions", JSON.stringify(dataToCache));
      } catch (error) {
        console.error("[ERROR] 감정 캘린더 데이터 불러오기 실패:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchChatEndStatuses();

    // 페이지 포커스 시 데이터 갱신
    const handleFocus = () => {
      fetchChatEndStatuses();
    };

    window.addEventListener("focus", handleFocus);

    return () => {
      window.removeEventListener("focus", handleFocus);
    };
  }, []);

  const processEmotionData = (status) => {
    let { conversation_end_timestamp, emotions } = status;
    let representativeEmotion = null;
    let computedTimestamp = conversation_end_timestamp;

    if (Array.isArray(emotions) && emotions.length > 0) {
      const freq = {};
      let latestTimestamp = emotions[0].timestamp;

      emotions.forEach((item) => {
        freq[item.emotion] = (freq[item.emotion] || 0) + 1;
        if (dayjs(item.timestamp).isAfter(dayjs(latestTimestamp))) {
          latestTimestamp = item.timestamp;
        }
      });

      let maxCount = 0;
      for (const [emotion, count] of Object.entries(freq)) {
        if (count > maxCount) {
          maxCount = count;
          representativeEmotion = emotion;
        }
      }

      computedTimestamp = computedTimestamp || latestTimestamp;
    } else {
      representativeEmotion = "default";
      computedTimestamp = computedTimestamp || new Date().toISOString();
    }

    if (!computedTimestamp || !representativeEmotion) return null;

    const formattedDate = dayjs(computedTimestamp)
      .tz("Asia/Seoul")
      .format("YYYY-MM-DD");
    const emoji = emotionIcons[representativeEmotion] || "😐";
    return { date: formattedDate, emoji };
  };

  const tileContent = useMemo(() => {
    return ({ date }) => {
      const formattedDate = dayjs(date).tz("Asia/Seoul").format("YYYY-MM-DD");
      const chatEmotionsForDate = chatEmotions[formattedDate];
      return chatEmotionsForDate ? (
        <span className="emotion-icon">
          {chatEmotionsForDate.map((emotion, index) => (
            <span key={index}>{emotion}</span>
          ))}
        </span>
      ) : null;
    };
  }, [chatEmotions]);

  const handleDateClick = async (selectedDate) => {
    const formattedDate = dayjs(selectedDate)
      .tz("Asia/Seoul")
      .format("YYYY-MM-DD");
    setSelectedDate(formattedDate);
    try {
      const diaries = await getDiaryList(formattedDate);
      setDiaryEntries(
        diaries.map((diary) => ({
          id: diary._id,
          emoji: emotionIcons[diary.emotion] || "😐",
          link: `/diary/${diary._id}`,
          timestamp: diary.date,
          title: diary.title || "",
          content: diary.content || "",
        }))
      );
    } catch (error) {
      console.error(`[ERROR] ${formattedDate} 일기 목록 불러오기 실패:`, error);
      setDiaryEntries([]);
    }
  };

  return (
    <CalendarWrapper>
      <h2>😍 감정 캘린더 🥰</h2>
      {/* 로딩 상태일 때만 로딩 스피너와 텍스트 표시 */}
      {loading ? (
        <LoadingContainer>
          <RingLoader color="#5f71f5" loading={loading} size={80} />
          <LoadingText>달력을 불러오는 중입니다...</LoadingText>
        </LoadingContainer>
      ) : (
        <StyledCalendar
          onChange={setDate}
          value={date}
          tileContent={tileContent}
          locale="ko"
          calendarType="hebrew"
          onClickDay={handleDateClick}
          tileClassName={({ date, view, activeStartDate }) => {
            if (view === "month") {
              const isCurrentMonth =
                date.getMonth() === activeStartDate.getMonth();
              return isCurrentMonth
                ? ""
                : "react-calendar__month-view__days__day--neighboringMonth";
            }
            return "";
          }}
        />
      )}
      {selectedDate && (
        <DiaryList selectedDate={selectedDate} diaryEntries={diaryEntries} />
      )}
    </CalendarWrapper>
  );
};

export default CalendarPage;
