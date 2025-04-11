import React from "react";
import {
  Radar, RadarChart, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend
} from "recharts";

const COLORS = ["#a5d6ff", "#9fe2bf", "#fdd36e", "#f28b82", "#cdb4db"]; // Colores pastel suaves

const RadarStatsChart = ({ stats, benchmark, benchmarkMax, gender, label }) => {
  if (!stats || !benchmark || !benchmarkMax || !gender) {
    console.warn("❌ Missing data for RadarStatsChart", { stats, benchmark, benchmarkMax, gender });
    return null;
  }

  const genderBenchmark = benchmark[gender];
  const genderBenchmarkMax = benchmarkMax[gender];

  if (!genderBenchmark || !genderBenchmarkMax) {
    console.warn("❌ Benchmark not found for gender:", gender);
    return null;
  }

  const normalize = (value, max) => {
    if (max === 0 || max === undefined || max === null) return 0;
    return (value / max) * 100;
  };

  const calculateMetric = (statValues, benchmarkValues, weights) => {
    const weightedStat = statValues.reduce((sum, val, idx) => sum + (val * weights[idx]), 0);
    const weightedBenchmark = benchmarkValues.reduce((sum, val, idx) => sum + (val * weights[idx]), 0);
    return normalize(weightedStat, weightedBenchmark);
  };

  const data = [
    {
      metric: "General",
      player: normalize(stats.ci_per_point, genderBenchmarkMax.ci_per_point),
      benchmark: normalize(genderBenchmark.ci_per_point, genderBenchmarkMax.ci_per_point),
    },
    {
      metric: "Serve",
      player: calculateMetric(
        [stats.num_direct_points_on_serve, stats.percentage_points_won_on_serve_team],
        [genderBenchmarkMax.num_direct_points_on_serve, genderBenchmarkMax.percentage_points_won_on_serve_team],
        [1, 1]
      ),
      benchmark: calculateMetric(
        [genderBenchmark.num_direct_points_on_serve, genderBenchmark.percentage_points_won_on_serve_team],
        [genderBenchmarkMax.num_direct_points_on_serve, genderBenchmarkMax.percentage_points_won_on_serve_team],
        [1, 1]
      ),
    },
    {
      metric: "Return",
      player: calculateMetric(
        [stats.percentage_return_errors, stats.percentage_points_won_return_team],
        [genderBenchmarkMax.percentage_return_errors, genderBenchmarkMax.percentage_points_won_return_team],
        [1, 1]
      ),
      benchmark: calculateMetric(
        [genderBenchmark.percentage_return_errors, genderBenchmark.percentage_points_won_return_team],
        [genderBenchmarkMax.percentage_return_errors, genderBenchmarkMax.percentage_points_won_return_team],
        [1, 1]
      ),
    },
    {
      metric: "Aggressiveness",
      player: calculateMetric(
        [stats.percentage_shots_smash, stats.num_bajadas, stats.percentage_viborejas_winners],
        [genderBenchmarkMax.percentage_shots_smash, genderBenchmarkMax.num_bajadas, genderBenchmarkMax.percentage_viborejas_winners],
        [3, 2, 1]
      ),
      benchmark: calculateMetric(
        [genderBenchmark.percentage_shots_smash, genderBenchmark.num_bajadas, genderBenchmark.percentage_viborejas_winners],
        [genderBenchmarkMax.percentage_shots_smash, genderBenchmarkMax.num_bajadas, genderBenchmarkMax.percentage_viborejas_winners],
        [3, 2, 1]
      ),
    },
    {
      metric: "Attack",
      player: calculateMetric(
        [stats.percentage_winners, stats.percentage_assists_shots, stats.percentage_error_setups],
        [genderBenchmarkMax.percentage_winners, genderBenchmarkMax.percentage_assists_shots, genderBenchmarkMax.percentage_error_setups],
        [1.5, 0.75, 0.75]
      ),
      benchmark: calculateMetric(
        [genderBenchmark.percentage_winners, genderBenchmark.percentage_assists_shots, genderBenchmark.percentage_error_setups],
        [genderBenchmarkMax.percentage_winners, genderBenchmarkMax.percentage_assists_shots, genderBenchmarkMax.percentage_error_setups],
        [1.5, 0.75, 0.75]
      ),
    },
    {
      metric: "Consistency",
      player: calculateMetric(
        [stats.percentage_ue, stats.percentage_pe, stats.percentage_winner_setups, stats.num_smash_defenses],
        [genderBenchmarkMax.percentage_ue, genderBenchmarkMax.percentage_pe, genderBenchmarkMax.percentage_winner_setups, genderBenchmarkMax.num_smash_defenses],
        [1.5, 0.75, 0.5, 0.2]
      ),
      benchmark: calculateMetric(
        [genderBenchmark.percentage_ue, genderBenchmark.percentage_pe, genderBenchmark.percentage_winner_setups, genderBenchmark.num_smash_defenses],
        [genderBenchmarkMax.percentage_ue, genderBenchmarkMax.percentage_pe, genderBenchmarkMax.percentage_winner_setups, genderBenchmarkMax.num_smash_defenses],
        [1.5, 0.75, 0.5, 0.2]
      ),
    },
  ];

  return (
    <div className="chart-container">
      <h3 className="chart-title">📊 Tactical Profile</h3>
      <div className="chart-inner">
        <ResponsiveContainer width={500} height={400}>
          <RadarChart data={data}>
            <PolarGrid />
            <PolarAngleAxis dataKey="metric" tick={{ fill: "#ffffff", fontSize: 15 }} />
            <PolarRadiusAxis domain={[0, 100]} tick={false} />
            <Radar name={label || "Player"} dataKey="player" stroke={COLORS[0]} fill={COLORS[0]} fillOpacity={0.6} />
            <Radar name="Benchmark" dataKey="benchmark" stroke={COLORS[2]} fill={COLORS[2]} fillOpacity={0.4} />
            <Legend layout="horizontal" verticalAlign="bottom" align="center" />
          </RadarChart>
        </ResponsiveContainer>
        <p className="chart-description">
  This chart visualizes the {label?.toLowerCase() === "couple" ? "couple's" : "player's"} tactical profile based on six core dimensions. 
  Values are normalized against gender-specific benchmarks to highlight strengths 
  and improvement areas compared to the average {label?.toLowerCase() === "couple" ? "couple" : "player"}.
</p>
      </div>
    </div>
  );
};

export default RadarStatsChart;

