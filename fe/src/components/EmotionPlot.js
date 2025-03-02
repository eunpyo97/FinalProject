import React, { useEffect, useState } from "react";
import { getEmotionStats } from "../api/emotion";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import styled from "styled-components";
import { getEmotionIcon } from "../components/Emoji";

const ChartContainer = styled.div`
  width: 100%;
  max-width: 800px;
  margin: 20px auto;
  padding: 10px;
  text-align: center;
`;

const LegendContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 15px;
`;

const LegendItem = styled.div`
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
`;

const ColorBox = styled.div`
  width: 15px;
  height: 15px;
  border-radius: 50%;
  background-color: ${(props) => props.color};
`;

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const { date, emotion, confidence } = payload[0].payload;
    return (
      <div
        style={{
          backgroundColor: "#ffff",
          padding: "8px",
          borderRadius: "8px",
          boxShadow: "0px 0px 8px rgba(0,0,0,0.2)",
        }}
      >
        <p style={{ margin: 0, fontSize: "14px", fontWeight: "bold" }}>
          <span style={{ marginRight: "5px" }}>{getEmotionIcon(emotion)}</span>
          {emotion}: <strong>{confidence}%</strong> ({date})
        </p>
      </div>
    );
  }
  return null;
};

const EmotionPlot = ({ startDate, endDate }) => {
  const [emotionData, setEmotionData] = useState([]);

  useEffect(() => {
    const fetchEmotionStats = async () => {
      if (!startDate || !endDate) return;
      const stats = await getEmotionStats(startDate, endDate);
      if (stats) {
        let formattedData = stats.trend.map(
          ({ date, emotion, confidence }) => ({
            date,
            emotion,
            confidence: Math.round(confidence * 100),
            icon: getEmotionIcon(emotion),
          })
        );

        if (formattedData.length === 0) {
          formattedData = [
            {
              date: startDate,
              emotion: "neutral",
              confidence: 100,
              icon: "😐",
            },
          ];
        }

        setEmotionData(formattedData);
      }
    };

    fetchEmotionStats();
  }, [startDate, endDate]);

  const COLORS = {
    happy: "#FFD700",
    sadness: "#87CEEB",
    angry: "#FF4500",
    panic: "#32CD32",
    neutral: "#d3d3d3",
  };

  return (
    <ChartContainer>
      <h3 style={{ fontSize: "20px", marginBottom: "15px" }}>
        나의 감정의 흐름은?
      </h3>

      {emotionData.length === 1 && emotionData[0].emotion === "neutral" && (
        <p>선택한 날짜에 대화를 나누지 않았나 봐요. 감정 데이터가 없어요 😥</p>
      )}

      <ResponsiveContainer width="100%" height={300}>
        <ScatterChart margin={{ top: 20, right: 30, left: 30, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" type="category" />
          <YAxis dataKey="confidence" type="number" domain={[0, 100]} />
          <Tooltip
            content={<CustomTooltip />}
            cursor={{ strokeDasharray: "3 3" }}
          />

          {Object.keys(COLORS).map((emotion) => (
            <Scatter
              key={emotion}
              name={emotion}
              data={emotionData.filter((d) => d.emotion === emotion)}
              fill={COLORS[emotion]}
            >
              {emotionData
                .filter((d) => d.emotion === emotion)
                .map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[emotion]} />
                ))}
            </Scatter>
          ))}
        </ScatterChart>
      </ResponsiveContainer>

      {/* 범례 */}
      <LegendContainer>
        {Object.keys(COLORS).map((emotion) => (
          <LegendItem key={emotion}>
            <ColorBox color={COLORS[emotion]} />
            {getEmotionIcon(emotion)} {emotion}
          </LegendItem>
        ))}
      </LegendContainer>
    </ChartContainer>
  );
};

export default EmotionPlot;
