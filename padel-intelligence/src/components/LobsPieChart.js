// src/components/LobsPieChart.js
import React from "react";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

const COLORS = ["#a5d6ff", "#9fe2bf", "#fdd36e", "#f28b82", "#cdb4db"]; // pastel suave

const LobsPieChart = ({ stats }) => {
  if (!stats) return null;

  const smash = stats.percentage_smashes_from_lobs || 0;
  const rulos = stats.percentage_rulos_from_lobs || 0;
  const viborejas = stats.percentage_viborejas_from_lobs || 0;
  const bajadas = stats.percentage_bajadas_from_lobs || 0;

  const total = smash + rulos + viborejas + bajadas;
  const missing = Math.max(0, 100 - total);

  const data = [
    { name: "Smashes", value: smash },
    { name: "Rulos", value: rulos },
    { name: "Viborejas", value: viborejas },
    { name: "Bajadas", value: bajadas },
  ];

  if (missing > 0.5) {
    data.push({ name: "Others", value: parseFloat(missing.toFixed(2)) });
  }

  return (
<div className="chart-container">
  <h3 className="chart-title">📊 Distribution of Shots After Lobs</h3>

  <div className="chart-inner"> {/* ⬅️ Añade esto */}
    <ResponsiveContainer width={350} height={350}>
      <PieChart>
      <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            outerRadius={100}
            label={({ value }) => `${value.toFixed(1)}%`}>

          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip formatter={(value) => `${value.toFixed(1)}%`} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
    <p className="chart-description">
    This chart illustrates how the player responds to lobs during a match. 
    A higher percentage of *smashes* indicates aggressive overhead play, 
    while a more balanced distribution might suggest tactical variation.
    </p>
  </div>
</div>

  );
};

export default LobsPieChart;
