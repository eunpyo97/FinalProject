import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { updateDiary, getDiaryDetail } from "../api/diary";
import styled from "styled-components";
import { getEmotionIcon } from "../components/Emoji";

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start; /* 상단 정렬 */
  padding: 30px;
  background: linear-gradient(
    to bottom,
    rgb(222, 237, 252),
    rgb(255, 255, 255)
  );
  min-height: 100vh;
`;

const Title = styled.h2`
  font-size: 35px;
  color: #ff6b81;
  margin-bottom: 20px;
  font-family: "Dongle", sans-serif;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 500px;
  gap: 15px;
`;

const Label = styled.label`
  font-size: 16px;
  font-weight: bold;
  color: #444;
`;

const EmotionContainer = styled.div`
  font-size: 18px;
  font-weight: bold;
  color: #ff4757;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 10px;
`;

const EmotionIcon = styled.span`
  font-size: 26px;
`;

const TextArea = styled.textarea`
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-size: 22px;
  font-family: "Dongle", sans-serif;
  resize: none;
  height: 300px;
  overflow-y: auto;
  background-color: #fff;
  box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.1),
    -5px -5px 10px rgba(255, 255, 255, 0.5);
  transition: transform 0.3s ease, box-shadow 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 8px 8px 15px rgba(0, 0, 0, 0.2),
      -8px -8px 15px rgba(255, 255, 255, 0.5);
  }

  &:focus {
    outline: none;
    border-color: #ff9aa2;
    box-shadow: 0 0 10px rgba(255, 154, 162, 0.5),
      5px 5px 15px rgba(0, 0, 0, 0.1);
  }

  /* 스크롤바 전체 영역 스타일 */
  &::-webkit-scrollbar {
    width: 14px;
  }

  /* 스크롤바 트랙 (배경) 스타일 */
  &::-webkit-scrollbar-track {
    background: rgba(240, 240, 240, 0.5);
    border-radius: 10px;
  }

  /* 스크롤바 핸들 (움직이는 부분) 스타일 */
  &::-webkit-scrollbar-thumb {
    background: #ff9aa2;
    border-radius: 10px;
    border: 2px solid #ffffff;
    cursor: grab;
  }

  /* 마우스 오버 시 스크롤바 핸들 스타일 */
  &::-webkit-scrollbar-thumb:hover {
    background: #ffb6c1;
    cursor: grabbing;
  }

  &:focus {
    outline: none;
    border-color: #ff9aa2;
    box-shadow: 0 0 5px rgba(255, 154, 162, 0.5);
  }
`;

// const Select = styled.select`
//   padding: 15px;
//   border: 1px solid #ddd;
//   border-radius: 10px;
//   font-size: 16px;
//   box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.1),
//     -5px -5px 10px rgba(255, 255, 255, 0.5);
//   transition: transform 0.3s ease, box-shadow 0.3s ease;

//   &:hover {
//     transform: translateY(-2px);
//     box-shadow: 8px 8px 15px rgba(0, 0, 0, 0.2),
//       -8px -8px 15px rgba(255, 255, 255, 0.5);
//   }

//   &:focus {
//     outline: none;
//     border-color: #ff9aa2;
//     box-shadow: 0 0 10px rgba(255, 154, 162, 0.5),
//       5px 5px 15px rgba(0, 0, 0, 0.1);
//   }
// `;

const ButtonGroup = styled.div`
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
`;

const Button = styled.button`
  background-color: ${(props) => (props.primary ? "#ffb6c1" : "#f0f0f0")};
  color: ${(props) => (props.primary ? "#fff" : "#444")};
  border: none;
  padding: 12px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition: all 0.3s ease;

  &:hover {
    transform: scale(1.05);
    background-color: ${(props) => (props.primary ? "#ff9aa2" : "#e0e0e0")};
  }
`;

const EditDiary = () => {
  const { diaryId } = useParams();
  const navigate = useNavigate();

  const [content, setContent] = useState("");
  const [emotion, setEmotion] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // const emotions = ["happy", "sad", "angry", "neutral"];

  useEffect(() => {
    const fetchDiary = async () => {
      try {
        const diary = await getDiaryDetail(diaryId);
        setContent(diary.content || "");
        setEmotion(diary.emotion || "");
      } catch (error) {
        console.error("Failed to fetch diary", error);
        alert("일기를 불러오는 데 실패했습니다.");
      }
    };
    fetchDiary();
  }, [diaryId]);

  const handleUpdate = async () => {
    if (!content.trim()) {
      alert("일기 내용은 필수입니다!");
      return;
    }

    setIsLoading(true);

    try {
      await updateDiary(diaryId, content, emotion);
      alert("일기 수정 완료!");
      navigate(`/diary/${diaryId}`, { replace: true });
      window.scrollTo(0, 0);
    } catch (error) {
      console.error("일기 수정 실패", error);
      alert("일기 수정에 실패했습니다.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    if (window.confirm("수정을 취소하시겠습니까?")) {
      navigate(`/diary/${diaryId}`, { replace: true });
    }
  };

  return (
    <Container>
      <Title>일기 수정</Title>
      <Form>
        {/* 감정 드롭다운 -> 나중에 감정변경할 수 있도록..*/}
        {/* <Label>감정 선택</Label>
        <Select value={emotion} onChange={(e) => setEmotion(e.target.value)}>
          <option value="" disabled hidden>
            감정을 선택하세요
          </option>
          {emotions.map((emo) => (
            <option key={emo} value={emo}>
              {emo.charAt(0).toUpperCase() + emo.slice(1)}
            </option>
          ))}
        </Select> */}
        <Label>감정</Label>
        <EmotionContainer>
          <EmotionIcon>{getEmotionIcon(emotion)}</EmotionIcon>
          <span>
            {emotion
              ? emotion.charAt(0).toUpperCase() + emotion.slice(1)
              : "감정 없음"}
          </span>
        </EmotionContainer>

        {/* 일기 내용 입력 */}
        <Label>일기 내용</Label>
        <TextArea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="일기 내용을 입력하세요"
        />

        {/* 버튼 그룹 */}
        <ButtonGroup>
          <Button onClick={handleCancel}>취소</Button>
          <Button primary onClick={handleUpdate} disabled={isLoading}>
            {isLoading ? "저장 중..." : "수정 완료"}
          </Button>
        </ButtonGroup>
      </Form>
    </Container>
  );
};

export default EditDiary;
