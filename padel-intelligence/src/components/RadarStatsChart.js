import React from "react";
import {
  Radar, RadarChart, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend
} from "recharts";

const RadarStatsChart = ({ stats, benchmark, benchmarkMax, gender }) => {
  if (!stats || !benchmark || !benchmarkMax || !gender) {
    console.warn("❌ Missing data for RadarStatsChart", { stats, benchmark, benchmarkMax, gender });
    return null;
  }

  // Obtener el benchmark correspondiente al género
  const genderBenchmark = benchmark[gender];
  const genderBenchmarkMax = benchmarkMax[gender];

  if (!genderBenchmark || !genderBenchmarkMax) {
    console.warn("❌ Benchmark not found for gender:", gender);
    return null;
  }

  console.log("✅ Data received in RadarStatsChart:", { stats, genderBenchmark, genderBenchmarkMax });

  const normalize = (value, max) => {
    if (max === 0 || max === undefined || max === null) return 0;
    return (value / max) * 100;
  };

  // Calcular el valor normalizado y ponderado de cada métrica
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
      metric: "Servicio",
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
      metric: "Resto",
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
      metric: "Agresividad",
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
      metric: "Ataque",
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
      metric: "Consistencia",
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
      <h3 style={{ textAlign: "center", marginBottom: "10px", color: "#fff" }}>
        📊 Tactical Profile
      </h3>
      <ResponsiveContainer width={550} height={350}>
        <RadarChart data={data}>
          <PolarGrid />
          <PolarAngleAxis dataKey="metric" tick={{ fill: "#ffffff", fontSize: 15 }} />
          <PolarRadiusAxis domain={[0, 100]} tick={false} /> {/* Quitar los números */}
          <Radar name="Player" dataKey="player" stroke="#0088FE" fill="#0088FE" fillOpacity={0.6} />
          <Radar name="Benchmark" dataKey="benchmark" stroke="#FFBB28" fill="#FFBB28" fillOpacity={0.4} />
          <Legend />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default RadarStatsChart;
