import React from "react";

const FormattedPredictionResult = ({ predictionResult }) => {
  if (!predictionResult) {
    return null;
  }

  // Limitar el breakdown a un máximo de 3 deuces
  const renderDeuceBreakdown = (breakdown) => {
    return (
      <div>
        {breakdown.slice(0, 3).map((scenario, index) => (
          <div key={index}>
            <p>{scenario.Scenario}: {scenario.Probability.toFixed(2)}%</p>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="formatted-result">
      <h3>Prediction Result:</h3>

      {/* Game Probability */}
      {predictionResult.game_probability && (
        <div>
          <h4>Game Probability:</h4>
          {predictionResult.game_probability["Probability before deuce"] && (
            <p>Probability before deuce: {predictionResult.game_probability["Probability before deuce"].toFixed(2)}%</p>
          )}
          {predictionResult.game_probability["Probability after deuce"] && (
            <p>Probability after deuce: {predictionResult.game_probability["Probability after deuce"].toFixed(2)}%</p>
          )}
          {predictionResult.game_probability["Probability to reach deuce"] && (
            <p>Probability to reach deuce: {predictionResult.game_probability["Probability to reach deuce"].toFixed(2)}%</p>
          )}
          {predictionResult.game_probability["Total probability to win the game"] && (
            <p>Total probability to win the game: {predictionResult.game_probability["Total probability to win the game"].toFixed(2)}%</p>
          )}
          {predictionResult.game_probability["Breakdown after deuce"] && renderDeuceBreakdown(predictionResult.game_probability["Breakdown after deuce"])}

          {predictionResult.game_probability["tiebreak_probability_t1"] && (
            <p>Tiebreak probability T1: {predictionResult.game_probability["tiebreak_probability_t1"]}</p>
          )}
          {predictionResult.game_probability["tiebreak_probability_t2"] && (
            <p>Tiebreak probability T2: {predictionResult.game_probability["tiebreak_probability_t2"]}</p>
          )}
          {predictionResult.game_probability["if_win_next_point"] && (
            <p>If win next point: {predictionResult.game_probability["if_win_next_point"]}</p>
          )}
          {predictionResult.game_probability["if_lose_next_point"] && (
            <p>If lose next point: {predictionResult.game_probability["if_lose_next_point"]}</p>
          )}
        </div>
      )}

      {/* Set Probability */}
      {predictionResult.set_probability && (
        <div>
          <h4>Set Probability:</h4>
          <p>If Win: {predictionResult.set_probability.if_win}</p>
          <p>If Loss: {predictionResult.set_probability.if_loss}</p>
          <p>Calculated: {predictionResult.set_probability.calculated}</p>
        </div>
      )}

      {/* Match Probability */}
      {predictionResult.match_probability && (
        <div>
          <h4>Match Probability:</h4>
          {predictionResult.match_probability.if_win_set && (
            <p>If Win Set: {predictionResult.match_probability.if_win_set}</p>
          )}
          {predictionResult.match_probability.if_loss_set && (
            <p>If Loss Set: {predictionResult.match_probability.if_loss_set}</p>
          )}
          {predictionResult.match_probability.if_win_tiebreak && (
            <p>If Win Tiebreak: {predictionResult.match_probability.if_win_tiebreak}</p>
          )}
          {predictionResult.match_probability.if_loss_tiebreak && (
            <p>If Loss Tiebreak: {predictionResult.match_probability.if_loss_tiebreak}</p>
          )}
          <p>Match Total: {predictionResult.match_probability.match_total}</p>
        </div>
      )}

      {/* Set Win Probability */}
      {predictionResult.set_win_probability && (
        <div>
          <h4>Set Win Probability:</h4>
          <p>{predictionResult.set_win_probability}</p>
        </div>
      )}
    </div>
  );
};

export default FormattedPredictionResult;
