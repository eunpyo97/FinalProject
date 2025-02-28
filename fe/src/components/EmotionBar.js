import React, { useEffect, useState } from "react";
import { getEmotionStats } from "../api/emotion";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import styled from "styled-components";
import { getEmotionIcon } from "./Emoji";

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

const EmotionBar = ({ startDate, endDate }) => {
  const [emotionData, setEmotionData] = useState([]);

  useEffect(() => {
    const fetchEmotionStats = async () => {
      if (!startDate || !endDate) return;
      const stats = await getEmotionStats(startDate, endDate);

      // const defaultEmotions = ["happy", "sadness", "angry", "panic"];
      let formattedData = [];

      if (stats && stats.summary) {
        formattedData = Object.entries(stats.summary).map(([emotion, count]) => ({
          emotion,
          count,
          icon: getEmotionIcon(emotion),
        }));
      }

      if (formattedData.length === 0 || formattedData.every((item) => item.count === 0)) {
        formattedData = [{ emotion: "neutral", count: 100, icon: "😐" }];
      }

      setEmotionData(formattedData);
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
      <h3 style={{ fontSize: "20px", marginBottom: "15px" }}>내 감정의 균형은?</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={emotionData} layout="vertical" margin={{ top: 20, right: 30, left: 30, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis dataKey="emotion" type="category" tickFormatter={(value) => `${getEmotionIcon(value)} ${value}`} />
          <Tooltip />
          <Bar dataKey="count" barSize={30}>
            {emotionData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[entry.emotion] || "#d3d3d3"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
};

export default EmotionBar;
