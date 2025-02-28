import React, { useEffect, useState } from "react";
import styled, { keyframes } from "styled-components";

// 문구 애니메이션
const fadeIn = keyframes`
  0% { opacity: 0; }
  100% { opacity: 1; }
`;

const Container = styled.div`
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh; /* 화면 전체 높이를 차지하도록 설정 */
  background-color:rgb(255, 255, 255);
  overflow: hidden;
`;

const SliderContainer = styled.div`
  width: 80%; /* 기본 너비 */
  height: 60%; /* 기본 높이 */
  max-width: 800px; /* 최대 너비 제한 */
  max-height: 600px; /* 최대 높이 제한 */
  position: relative;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0px 10px 15px rgba(0, 0, 0, 0.1);
  margin-top: 25%; /* 기본값 */

  @media (max-width: 768px) {
    margin-top: 40%; /* 작은 화면에서는 이미지를 더 아래로 이동 */
  }

  @media (min-width: 768px) and (max-width: 1024px) {
    margin-top: 30%; /* 태블릿 화면에서 이미지 위치 조정 */
  }

  @media (min-width: 1024px) {
    margin-top: 25%; /* 큰 화면(PC)에서 이미지 위치 조정 */
  }
`;

const Slide = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: contain; /* 이미지가 잘리지 않도록 설정 */
  background-repeat: no-repeat; /* 반복 방지 */
  background-position: center; /* 중앙 정렬 */
  transition: opacity 1s ease-in-out;
  opacity: ${({ isVisible }) => (isVisible ? 1 : 0)};
  animation: ${fadeIn} 1s ease-out;
`;

const TextContainer = styled.div`
  position: absolute;
  top: 15%; /* 기본값 */
  left: 50%;
  transform: translateX(-50%);
  color: white;
  text-align: center;
  width: 90%;
  z-index: 2;

  @media (max-width: 768px) {
    top: 10%; /* 작은 화면에서는 조금 더 위로 이동 */
  }

  @media (min-width: 768px) and (max-width: 1024px) {
    top: 12%; /* 태블릿 화면에서 텍스트 위치 조정 */
  }

  @media (min-width: 1024px) {
    top: 25%; /* 큰 화면(PC)에서 텍스트 위치 조정 */
  }
`;

const HeadingText = styled.h1`
  font-size: 36px; /* 기본 글씨 크기 */
  font-weight: bold;
  margin-bottom: 10px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);

  @media (max-width: 768px) {
    font-size: 28px; /* 작은 화면에서는 글씨 크기 줄임 */
  }

  @media (min-width: 768px) and (max-width: 1024px) {
    font-size: 32px; /* 태블릿 화면에서 글씨 크기 조정 */
  }

  @media (min-width: 1024px) {
    font-size: 36px; /* 큰 화면(PC)에서 글씨 크기 유지 */
  }
`;

const DescriptionText = styled.p`
  font-size: 20px; /* 기본 글씨 크기 */
  line-height: 1.5;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);

  @media (max-width: 768px) {
    font-size: 16px; /* 작은 화면에서는 글씨 크기 줄임 */
  }

  @media (min-width: 768px) and (max-width: 1024px) {
    font-size: 18px; /* 태블릿 화면에서 글씨 크기 조정 */
  }

  @media (min-width: 1024px) {
    font-size: 20px; /* 큰 화면(PC)에서 글씨 크기 유지 */
  }
`;

const phrases = [
  {
    heading: "감정 캘린더",
    description:
      "감정 캘린더로 일상의 감정을 기록해 보세요. 언제, 어디서나 감정 변화를 쉽게 파악하고, 스스로의 마음을 돌아볼 수 있습니다.",
    bgImage: "/assets/calendar.jpg",
  },
  {
    heading: "친구처럼 대화하는 챗봇!",
    description:
      "혼자 있을 때, 챗봇이 항상 곁에 있습니다. 고민을 털어놓고, 지친 마음을 풀어보세요. 언제든지 대화가 기다리고 있어요.",
    bgImage: "/assets/chatbot.jpg",
  },
  {
    heading: "당신의 하루를 기록하는 일기장",
    description:
      "매일매일의 생각과 감정을 일기장에 담아보세요. 소중한 순간들이 기록되고, 나만의 이야기가 만들어집니다.",
    bgImage: "/assets/diary.jpg",
  },
  {
    heading: "나의 감정을 시각적으로 확인하세요!",
    description:
      "감정 그래프를 통해 일상의 감정 흐름을 시각적으로 분석해보세요. 나의 감정 패턴을 알면 더 나은 선택을 할 수 있습니다.",
    bgImage: "/assets/graph.jpg",
  },
];

const Landing = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % phrases.length);
    }, 3000); // 3초마다 슬라이드 전환
    return () => clearInterval(interval);
  }, []);

  return (
    <Container>
      {/* 문구 */}
      <TextContainer>
        <HeadingText>{phrases[currentIndex].heading}</HeadingText>
        <DescriptionText>{phrases[currentIndex].description}</DescriptionText>
      </TextContainer>

      {/* 이미지 슬라이더 */}
      <SliderContainer>
        {phrases.map((phrase, index) => (
          <Slide
            key={index}
            style={{ backgroundImage: `url(${phrase.bgImage})` }}
            isVisible={index === currentIndex}
          />
        ))}
      </SliderContainer>
    </Container>
  );
};

export default Landing;