import React, { useEffect, useState } from "react";
import styled, { keyframes } from "styled-components";

const fadeIn = keyframes`
  0% { opacity: 0; }
  100% { opacity: 1; }
`;

const typing = keyframes`
  from { max-width: 0; }
  to { max-width: 100%; }
`;

const colorChange = keyframes`
  0% { color:rgb(128, 5, 54); }
  50% { color:rgb(23, 80, 93); }
  100% { color:rgb(5, 66, 5); }
`;

const slideIn = keyframes`
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
`;

const Container = styled.div`
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: linear-gradient(
    135deg,
    rgb(255, 177, 208),
    rgb(184, 247, 250),
    rgb(217, 191, 255)
  );
  overflow: hidden;
`;

const SliderContainer = styled.div`
  width: 80%;
  height: 60%;
  max-width: 800px;
  max-height: 600px;
  position: relative;
  overflow: hidden;
  margin-top: 20%;
  @media (max-width: 768px) {
    margin-top: 20%;
  }
  @media (min-width: 768px) and (max-width: 1024px) {
    margin-top: 20%;
  }
  @media (min-width: 1024px) {
    margin-top: 20%;
  }
`;

const Slide = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
  animation: ${slideIn} 1s ease-out, ${fadeIn} 1s ease-out;
  opacity: ${({ isVisible }) => (isVisible ? 1 : 0)};
  transform: ${({ isVisible }) =>
    isVisible ? "translateX(0)" : "translateX(100%)"};
  transition: opacity 1s ease-in-out, transform 1s ease-in-out;
`;

const TextContainer = styled.div`
  position: absolute;
  top: 10%;
  left: 50%;
  transform: translateX(-50%);
  color: white;
  text-align: center;
  width: 90%;
  z-index: 2;
  @media (max-width: 768px) {
    top: 8%;
  }
  @media (min-width: 768px) and (max-width: 1024px) {
    top: 10%;
  }
  @media (min-width: 1024px) {
    top: 14%;
  }
`;

const HeadingText = styled.h1`
  font-size: 36px;
  font-weight: bold;
  margin: 0 auto;
  text-align: center;
  display: inline-block;
  white-space: nowrap;
  overflow: hidden;
  animation: ${typing} 3s steps(30, end), ${colorChange} 5s infinite;
  border-right: 2px solid white;
  max-width: fit-content;
  @media (max-width: 768px) {
    font-size: 28px;
  }
  @media (min-width: 768px) and (max-width: 1024px) {
    font-size: 32px;
  }
  @media (min-width: 1024px) {
    font-size: 36px;
  }
`;

const DescriptionText = styled.p`
  font-size: 20px;
  line-height: 1.5;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
  white-space: pre-line;
  margin-top: 13px;
  animation: ${colorChange} 5s infinite;
  @media (max-width: 768px) {
    font-size: 16px;
  }
  @media (min-width: 768px) and (max-width: 1024px) {
    font-size: 18px;
  }
  @media (min-width: 1024px) {
    font-size: 20px;
  }
`;

const phrases = [
  {
    heading: "감정 캘린더",
    description:
      "감정 캘린더로 일상의 감정을 기록해 보세요. \n언제, 어디서나 감정 변화를 쉽게 파악하고, 스스로의 마음을 돌아볼 수 있습니다.",
    bgImage: "/assets/calendar2.jpg",
  },
  {
    heading: "친구처럼 대화하는 감정을 읽는 챗봇",
    description:
      "고민을 털어놓고, 지친 마음을 풀어보세요. \n웹캠을 통해 실시간으로 감정을 분석하고, 그에 맞는 따뜻한 대화를 제공합니다. \n언제든지 당신의 감정에 맞춘 대화가 기다리고 있어요.",
    bgImage: "/assets/chatbot2.jpg",
  },
  {
    heading: "당신의 하루를 기록하는 일기장",
    description:
      "매일매일의 생각과 감정을 일기장에 담아보세요. \n소중한 순간들이 기록되고, 나만의 이야기가 만들어집니다.",
    bgImage: "/assets/diary2.jpg",
  },
  {
    heading: "나의 감정을 시각적으로 확인하세요!",
    description:
      "감정 그래프를 통해 일상의 감정 흐름을 시각적으로 분석해보세요. \n나의 감정 패턴을 알면 더 나은 선택을 할 수 있습니다.",
    bgImage: "/assets/graph2.jpg",
  },
];

const Landing = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % phrases.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Container>
      <TextContainer>
        <HeadingText key={currentIndex}>
          {phrases[currentIndex].heading}
        </HeadingText>
        <DescriptionText>{phrases[currentIndex].description}</DescriptionText>
      </TextContainer>
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
