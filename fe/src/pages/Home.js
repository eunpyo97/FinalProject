import React, { useEffect, useState } from "react";
import useAuthStore from "../store/authStore";
import styled from "styled-components";
import { useNavigate } from "react-router-dom";
import EmotionStats from "../components/EmotionStats";
import EmotionBar from "../components/EmotionBar";
// import EmotionStream from "../components/EmotionStream";
// import EmotionPlot from "../components/EmotionPlot";

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  min-height: 100vh;
  padding: 80px 20px 20px;
  background: linear-gradient(to right, rgb(249, 255, 187), rgb(255, 213, 235));
`;

const DateContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin: 15px 0;
  flex-wrap: wrap;
`;

const DateInput = styled.input`
  padding: 8px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 5px;
`;

const Title = styled.h1`
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
  text-align: center;
`;

const Description = styled.p`
  font-size: 18px;
  color: #666;
  margin-bottom: 20px;
  text-align: center;
`;

const Label = styled.label`
  font-size: 16px;
  font-weight: bold;
  color: #444;
`;

const ChartWrapper = styled.div`
  width: 100%;
  max-width: 800px;
  margin-bottom: 30px;
  padding: 10px;
  display: flex;
  justify-content: center;
`;

const Home = () => {
  const { isAuthenticated } = useAuthStore();
  const navigate = useNavigate();
  const [dates, setDates] = useState(() => {
    const today = new Date();
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(today.getDate() - 6);
    
    const formatDate = (date) => {
      return new Date(date.getTime() - date.getTimezoneOffset() * 60000)
        .toISOString()
        .split("T")[0];
    };
  
    return {
      startDate: formatDate(sevenDaysAgo),
      endDate: formatDate(today, true),
    };
  });

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
    }
  }, [isAuthenticated, navigate]);

  return (
    <Container>
      <Title>오늘 하루, 어떤 감정을 느꼈나요?</Title>
      <Description>최근 감정 변화를 그래프로 확인해보세요</Description>

      {/* 날짜 선택 필드 한 줄 배치 */}
      <DateContainer>
        <Label>시작 날짜:</Label>
        <DateInput
          type="date"
          value={dates.startDate}
          onChange={(e) => setDates({ ...dates, startDate: e.target.value })}
        />
        <Label>종료 날짜:</Label>
        <DateInput
          type="date"
          value={dates.endDate}
          onChange={(e) => setDates({ ...dates, endDate: e.target.value })}
        />
      </DateContainer>

      {/* 감정 비율 차트 */}
      <ChartWrapper>
        <EmotionStats startDate={dates.startDate} endDate={dates.endDate} />
      </ChartWrapper>

      {/* 감정 플롯 */}
      {/* <ChartWrapper>
        <EmotionPlot startDate={dates.startDate} endDate={dates.endDate} />
      </ChartWrapper> */}

      {/* 감정 스트림 */}
      {/* <ChartWrapper>
        <EmotionStream startDate={dates.startDate} endDate={dates.endDate} />
      </ChartWrapper> */}

      {/* 감정 빈도 그래프 */}
      <ChartWrapper>
        <EmotionBar startDate={dates.startDate} endDate={dates.endDate} />
      </ChartWrapper>
    </Container>
  );
};

export default Home;
