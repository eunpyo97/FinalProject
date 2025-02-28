import React, { useEffect, useState } from "react";
import { getEmotionStats } from "../api/emotion";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import styled from "styled-components";

const ChartContainer = styled.div`
  width: 100%;
  max-width: 800px;
  margin: 20px auto;
  padding: 10px;
  text-align: center;
`;

const EmotionStream = ({ startDate, endDate }) => {
  const [emotionData, setEmotionData] = useState([]);

  useEffect(() => {
    const fetchEmotionStats = async () => {
      if (!startDate || !endDate) return;
      const stats = await getEmotionStats(startDate, endDate);
      if (stats) {
        const formattedData = stats.trend.reduce((acc, { date, emotion, confidence }) => {
          const existingEntry = acc.find((item) => item.date === date);
          if (existingEntry) {
            existingEntry[emotion] = (existingEntry[emotion] || 0) + Math.round(confidence * 100);
          } else {
            acc.push({
              date,
              [emotion]: Math.round(confidence * 100),
            });
          }
          return acc;
        }, []);
        setEmotionData(formattedData);
      }
    };

    fetchEmotionStats();
  }, [startDate, endDate]);

  return (
    <ChartContainer>
      <h3 style={{ fontSize: "20px", marginBottom: "15px" }}>🌊 감정 변화 스트림</h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={emotionData} margin={{ top: 20, right: 30, left: 30, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Area type="monotone" dataKey="happy" stackId="1" stroke="#FFD700" fill="#FFD700" fillOpacity={0.6} />
          <Area type="monotone" dataKey="sadness" stackId="1" stroke="#87CEEB" fill="#87CEEB" fillOpacity={0.6} />
          <Area type="monotone" dataKey="angry" stackId="1" stroke="#FF4500" fill="#FF4500" fillOpacity={0.6} />
          <Area type="monotone" dataKey="panic" stackId="1" stroke="#32CD32" fill="#32CD32" fillOpacity={0.6} />
        </AreaChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
};

export default EmotionStream;
