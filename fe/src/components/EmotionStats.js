import React, { useEffect, useState } from "react";
import { getEmotionStats } from "../api/emotion";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";
import { getEmotionIcon } from "../components/Emoji";
import styled from "styled-components";

const ChartContainer = styled.div`
  width: 100%;
  max-width: 800px;
  margin: 20px auto;
  padding: 10px;
  text-align: center;
  background:rgb(243, 255, 233);
  border-radius: 15px;
  overflow: hidden; 
  flex-grow: 0; 
`;

const EmotionStats = ({ startDate, endDate }) => {
  const [emotionData, setEmotionData] = useState({ summary: {}, trend: [] });

  useEffect(() => {
    if (!startDate || !endDate) return;
    console.log("[DEBUG] 감정 데이터 요청 startDate:", startDate);
    console.log("[DEBUG] 감정 데이터 요청 endDate:", endDate);
    const fetchEmotionStats = async () => {
      const stats = await getEmotionStats(startDate, endDate);
      console.log("[DEBUG] API 응답 데이터:", stats);
      
      if (stats) setEmotionData(stats);
    };
    fetchEmotionStats();
  }, [startDate, endDate]);

  // 감정 비율 (Pie Chart)
  let summaryData = Object.entries(emotionData.summary).map(
    ([emotion, percentage]) => ({
      name: emotion,
      value: percentage,
      icon: getEmotionIcon(emotion) || "🙂",
    })
  );

  // 데이터가 없거나 모든 값이 0이면 기본값(neutral)으로 대체
  const totalValue = summaryData.reduce((acc, item) => acc + item.value, 0);
  if (summaryData.length === 0 || totalValue === 0) {
    summaryData = [{ name: "neutral", value: 100, icon: "😐" }];
  }

  // neutral 상태인지 체크
  const isNeutral =
    summaryData.length === 1 && summaryData[0].name === "neutral";

  console.log("summaryData:", summaryData);

  const COLORS = ["#FF4500", "#fc8217", "#FFD700", "#ff4fbe", "#d3d3d3"];

  // 커스텀 툴팁
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const { name, value } = payload[0];
      return (
        <div
          style={{
            backgroundColor: "#fff",
            padding: "8px",
            borderRadius: "8px",
            boxShadow: "0px 0px 8px rgba(0,0,0,0.2)",
          }}
        >
          <p style={{ margin: 0, fontSize: "14px", fontWeight: "bold" }}>
            {getEmotionIcon(name) || "😐"} {name}: <strong>{value}%</strong>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <ChartContainer>
      <h3 style={{ fontSize: "20px", marginBottom: "15px" }}>나는 어떤 감정을 제일 많이 느꼈을까?</h3>

      {/* neutral이면 안내 문구 추가 */}
      {isNeutral && <p>선택한 날짜에 대화를 나누지 않았나 봐요. 감정 데이터가 없어요 😥</p>}

      {/* neutral이어도 항상 그래프 표시 */}
      <ResponsiveContainer width="100%" height={400}>
        <PieChart margin={{ top: 20, bottom: 20 }}>
          <Pie
            data={summaryData}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={120}
            label={({ name, percent }) =>
              `${getEmotionIcon(name) || "😐"} ${name} (${(
                percent * 100
              ).toFixed(0)}%)`
            }
          >
            {summaryData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={
                  entry.name === "neutral"
                    ? "#d3d3d3" 
                    : COLORS[index % COLORS.length]
                }
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            formatter={(value) => `${getEmotionIcon(value) || "😐"} ${value}`}
          />
        </PieChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
};

export default EmotionStats;
