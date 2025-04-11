import React from "react";
import {
  Radar, RadarChart, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend
} from "recharts";

const COLORS = ["#63b3ed", "#f6ad55"]; // azul claro & naranja pastel



const RadarChartComparison = ({ player1, player2, benchmarkMax }) => {
  if (!player1 || !player2 || !benchmarkMax) {
    console.warn("❌ Missing data for RadarStatsComparison", { player1, player2, benchmarkMax });
    return null;
  }

  const max = benchmarkMax[player1.gender]; // 👈 Acceso correcto al benchmark por género

  const normalize = (value, max) => {
    if (!max || max === 0 || value === null || value === undefined) return 0;
    return (value / max) * 100;
  };

  const calculateMetric = (values, maxValues, weights) => {
    const weighted = values.reduce((sum, val, i) => sum + (val || 0) * weights[i], 0);
    const maxWeighted = maxValues.reduce((sum, val, i) => sum + (val || 0) * weights[i], 0);
    return normalize(weighted, maxWeighted);
  };

  const data = [
    {
      metric: "General",
      [player1.player]: normalize(player1.ci_per_point, max.ci_per_point),
      [player2.player]: normalize(player2.ci_per_point, max.ci_per_point),
    },
    {
      metric: "Serve",
      [player1.player]: calculateMetric(
        [player1.num_direct_points_on_serve, player1.percentage_points_won_on_serve_team],
        [max.num_direct_points_on_serve, max.percentage_points_won_on_serve_team],
        [1, 1]
      ),
      [player2.player]: calculateMetric(
        [player2.num_direct_points_on_serve, player2.percentage_points_won_on_serve_team],
        [max.num_direct_points_on_serve, max.percentage_points_won_on_serve_team],
        [1, 1]
      ),
    },
    {
      metric: "Return",
      [player1.player]: calculateMetric(
        [player1.percentage_return_errors, player1.percentage_points_won_return_team],
        [max.percentage_return_errors, max.percentage_points_won_return_team],
        [1, 1]
      ),
      [player2.player]: calculateMetric(
        [player2.percentage_return_errors, player2.percentage_points_won_return_team],
        [max.percentage_return_errors, max.percentage_points_won_return_team],
        [1, 1]
      ),
    },
    {
      metric: "Aggressiveness",
      [player1.player]: calculateMetric(
        [player1.percentage_shots_smash, player1.num_bajadas, player1.percentage_viborejas_winners],
        [max.percentage_shots_smash, max.num_bajadas, max.percentage_viborejas_winners],
        [3, 2, 1]
      ),
      [player2.player]: calculateMetric(
        [player2.percentage_shots_smash, player2.num_bajadas, player2.percentage_viborejas_winners],
        [max.percentage_shots_smash, max.num_bajadas, max.percentage_viborejas_winners],
        [3, 2, 1]
      ),
    },
    {
      metric: "Attack",
      [player1.player]: calculateMetric(
        [player1.percentage_winners, player1.percentage_assists_shots, player1.percentage_error_setups],
        [max.percentage_winners, max.percentage_assists_shots, max.percentage_error_setups],
        [1.5, 0.75, 0.75]
      ),
      [player2.player]: calculateMetric(
        [player2.percentage_winners, player2.percentage_assists_shots, player2.percentage_error_setups],
        [max.percentage_winners, max.percentage_assists_shots, max.percentage_error_setups],
        [1.5, 0.75, 0.75]
      ),
    },
    {
      metric: "Consistency",
      [player1.player]: calculateMetric(
        [player1.percentage_ue, player1.percentage_pe, player1.percentage_winner_setups, player1.num_smash_defenses],
        [max.percentage_ue, max.percentage_pe, max.percentage_winner_setups, max.num_smash_defenses],
        [1.5, 0.75, 0.5, 0.2]
      ),
      [player2.player]: calculateMetric(
        [player2.percentage_ue, player2.percentage_pe, player2.percentage_winner_setups, player2.num_smash_defenses],
        [max.percentage_ue, max.percentage_pe, max.percentage_winner_setups, max.num_smash_defenses],
        [1.5, 0.75, 0.5, 0.2]
      ),
    },
  ];

  console.log("👤 Player 1 data:", player1);
  console.log("👤 Player 2 data:", player2);
  console.log("📊 Benchmark Max:", benchmarkMax);
  console.log("📊 Gender-based Max:", max);
  console.log("✅ Player labels:", player1.player, player2.player);
  console.log("📈 Final Radar Data:", data);

  return (
    <div className="chart-container">
<ResponsiveContainer width={700} height={400}>
  <RadarChart data={data}>
          <PolarGrid />
          <PolarAngleAxis dataKey="metric" tick={{ fill: "#ffffff", fontSize: 15 }} />

          <PolarRadiusAxis domain={[0, 100]} tick={false} />
          <Radar name={player1.player} dataKey={player1.player} stroke={COLORS[0]} fill={COLORS[0]} fillOpacity={0.6} />
          <Radar name={player2.player} dataKey={player2.player} stroke={COLORS[1]} fill={COLORS[1]} fillOpacity={0.4} />
          <Legend
  align="center"
  verticalAlign="bottom"
  wrapperStyle={{ marginTop: 50 }}
/>
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default RadarChartComparison;
