import React from "react";
import {
  Radar, RadarChart, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer
} from "recharts";

const RadarStatsChart = ({ stats }) => {
  if (!stats) return null;

  const data = [
    {
      metric: "1st Serves",
      value: stats.percentage_1st_serves,
    },
    {
      metric: "Service Games Won",
      value: stats.percentage_service_games_won,
    },
    {
      metric: "Cross Shots",
      value: stats.percentage_cross,
    },
    {
      metric: "Lob Returns",
      value: stats.percentage_lobbed_returns,
    },
    {
      metric: "Smashes from Lobs",
      value: stats.percentage_smashes_from_lobs,
    },
    {
      metric: "Net Recovery w/ Lob",
      value: stats.net_recovery_with_lob,
    },
  ];

  return (
<div className="chart-container">
  <h3 style={{ textAlign: "center", marginBottom: "10px", color: "#fff" }}>
    📊 Tactical Profile
  </h3>
  <div className="chart-inner"> {/* ⬅️ Añade esto */}
  <ResponsiveContainer width={550} height={350}>
    <RadarChart data={data}>
      <PolarGrid />
      <PolarAngleAxis dataKey="metric" tick={{ fill: "#ffffff", fontSize: 15 }} />
      <PolarRadiusAxis domain={[0, 100]} />
      <Radar dataKey="value" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.5} />
    </RadarChart>
  </ResponsiveContainer>

  <p className="chart-description">
    This radar chart highlights the player's strengths across key performance areas.
  </p>
  </div>
</div>
)};

export default RadarStatsChart;
