export const emotionIcons = {
    happy: "😄",
    sadness: "😭",
    angry: "😡",
    panic: "😨",
    default: "😐",
  };
  
  // 감정 값을 받아 이모지를 반환
  export const getEmotionIcon = (emotion) => {
    return emotionIcons[emotion?.trim().toLowerCase()] || emotionIcons.default;
  };
  