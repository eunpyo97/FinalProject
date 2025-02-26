import React, { useState, useEffect } from "react";
import Calendar from "react-calendar";
import "react-calendar/dist/Calendar.css";
import styled from "styled-components";
import { getChatEndStatus } from "../api/calendar";
import { getUserChatHistory } from "../api/chat";
import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";
import DiaryList from "./DiaryList";

dayjs.extend(utc);
dayjs.extend(timezone);

const CalendarWrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  min-height: 100vh;
  background-color: rgb(233, 243, 251);
  padding: 20px;
  box-sizing: border-box;
  h2 {
    margin-top: 20px;
    margin-bottom: 20px;
    color: rgb(7, 75, 130);
  }
`;

const StyledCalendar = styled(Calendar)`
  border: none;
  border-radius: 20px;
  box-shadow: 0px 20px 20px rgba(1, 34, 53, 0.1);
  background: white;
  padding: 20px;
  font-size: 15px;
  width: 90%;
  min-height: 535px;
  min-width: 430px;

  /* 해당 월에 속하지 않는 날짜 스타일 */
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

  /* 요일 */
  .react-calendar__month-view__weekdays {
    text-align: center;
    font-size: 16px;
    font-weight: bold;
    padding: 5px 0;
    background-color: rgb(247, 218, 238);
    border-radius: 10px;
    margin-bottom: 15px;
  }

  /* 날짜 칸 */
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
  }

  .react-calendar__tile:hover {
    background: #bbdefb;
    transform: scale(1.05);
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
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

// 감정 이모지 매핑
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

  useEffect(() => {
    const fetchChatEndStatuses = async () => {
      try {
        // 사용자 채팅방 목록 불러오기
        const chatrooms = await getUserChatHistory();
        const chatroomIds = chatrooms.map((room) => room.chatroom_id);

        console.log("[DEBUG] 사용자 채팅방 목록:", chatroomIds);

        // 각 채팅방의 종료 상태 확인
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
        console.log("[DEBUG] 종료된 채팅방 감정 데이터:", resolvedStatuses);

        const emotionsMap = {};

        resolvedStatuses.forEach((status) => {
          // 종료되지 않은 채팅방은 무시
          if (!status || !status.conversation_end) return;

          let { conversation_end_timestamp, emotions } = status;
          let representativeEmotion = null;
          let computedTimestamp = conversation_end_timestamp;

          // 감정 데이터가 존재하는 경우
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
            // conversation_end_timestamp 없으면 가장 늦은 timestamp 사용
            computedTimestamp = computedTimestamp || latestTimestamp;
          } else {
            representativeEmotion = "default";
            computedTimestamp = computedTimestamp || new Date().toISOString();
          }

          if (!computedTimestamp || !representativeEmotion) return;

          const formattedDate = dayjs(computedTimestamp)
            .tz("Asia/Seoul")
            .format("YYYY-MM-DD");

          if (!emotionsMap[formattedDate]) {
            emotionsMap[formattedDate] = [];
          }

          const emoji = emotionIcons[representativeEmotion] || "😐";
          emotionsMap[formattedDate].push(emoji);
        });

        setChatEmotions(emotionsMap);
      } catch (error) {
        console.error("[ERROR] 감정 캘린더 데이터 불러오기 실패:", error);
      }
    };

    fetchChatEndStatuses();
  }, []);

  // 달력 날짜별 대표 이모지 표시
  const tileContent = ({ date }) => {
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

  const handleDateClick = (selectedDate) => {
    const formattedDate = dayjs(selectedDate)
      .tz("Asia/Seoul")
      .format("YYYY-MM-DD");
    setSelectedDate(formattedDate);
    const entries = chatEmotions[formattedDate] || [];

    setDiaryEntries(
      entries.map((emoji, index) => ({
        id: index,
        emoji,
        link: `/diary/${formattedDate}/${index}`,
        timestamp: formattedDate + " 23:59",
      }))
    );
  };

  return (
    <CalendarWrapper>
      <h2>😍 감정 캘린더 🥰</h2>
      <StyledCalendar
        onChange={setDate}
        value={date}
        tileContent={tileContent}
        locale="ko"
        calendarType="hebrew"
        onClickDay={handleDateClick}
        tileClassName={({ date, view }) => {
          // 'month' 뷰에서만 적용
          if (view === "month") {
            const isCurrentMonth = date.getMonth() === new Date().getMonth(); // 현재 달과 비교
            return isCurrentMonth
              ? ""
              : "react-calendar__month-view__days__day--neighboringMonth";
          }
          return "";
        }}
      />
      {selectedDate && (
        <DiaryList selectedDate={selectedDate} diaryEntries={diaryEntries} />
      )}
    </CalendarWrapper>
  );
};

export default CalendarPage;
