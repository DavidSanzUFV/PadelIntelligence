import React from "react";

const FormattedPredictionResult = ({ predictionResult, team1Name, team2Name }) => {
  if (!predictionResult) return null;

  const round = (value) => {
    const num = parseFloat(value);
    return isNaN(num) ? "0%" : `${Math.round(num)}%`;
  };  
  
  const game = predictionResult.game_probability || {};
  const set = predictionResult.set_probability || {};
  const match = predictionResult.match_probability || {};

  const renderDeuceBreakdown = (breakdown) => {
    if (!Array.isArray(breakdown) || breakdown.length === 0) return null;
    return (
      <>
        <p>
          If the game reaches deuce, here is how the probability of <strong>{team1Name}</strong> winning evolves over the next deuces:
        </p>
        <ul>
          {breakdown.slice(0, 3).map((s, i) => (
            <li key={i}>
              <strong>{s.Scenario}</strong>: <strong>{round(s.Probability)}</strong>
            </li>
          ))}
        </ul>
      </>
    );
  };

  return (
    <div className="formatted-result">
      {/* Match */}
      <h3>
        The probability of <strong>{team1Name}</strong> winning the match is <strong>{round(match.match_total)}</strong>
      </h3>
      <p style={{ fontWeight: "bold", color: "#2b61c8" }}>
        💡 What if {team1Name} wins this set? Their match win probability rises to <strong>{round(match.if_win_set)}</strong>!
      </p>
      <p style={{ fontWeight: "bold", color: "#2b61c8" }}>
        💡 And if they lose it? Their match win probability drops to <strong>{round(match.if_loss_set)}</strong>!
      </p>
      
      {!(game["tiebreak_probability_t1"] && game["tiebreak_probability_t2"]) && (
        <>
      {/* Set */}
      <h3>
        The probability of <strong>{team1Name}</strong> winning the current set is <strong>{round(set.calculated)}</strong>
      </h3>
      <p>
        If they win this game, their set win probability increases to <strong>{round(set.if_win)}</strong>.
      </p>
      <p>
        If they lose this game, it drops to <strong>{round(set.if_loss)}</strong>.
      </p>


      {/* Game (only if not in tiebreak) */}

          <h3>
            The probability of <strong>{team1Name}</strong> winning the current game is <strong>{round(game["Total probability to win the game"])}</strong>
          </h3>
          <p>
            <strong>{team1Name}</strong> has a <strong>{round(game["Probability before deuce"])}</strong> chance of winning the game before reaching deuce (40-40).
          </p>
          <p>
            The chance of reaching deuce is <strong>{round(game["Probability to reach deuce"])}</strong>.
          </p>
          {parseFloat(game["Probability to reach deuce"]) > 0 && (
            <p>
              If the game goes to deuce, <strong>{team1Name}</strong> has a <strong>{round(game["Probability after deuce"])}</strong> chance of winning.
            </p>
          )}
          {/* Deuce breakdown */}
          {parseFloat(game["Probability to reach deuce"]) > 0 && game["Breakdown after deuce"] &&
            renderDeuceBreakdown(game["Breakdown after deuce"])}
        </>
      )}

      {/* Tiebreak */}
      {game["tiebreak_probability_t1"] && game["tiebreak_probability_t2"] && (
        <>
          <h3>Tiebreak</h3>
          <p>
            The match is currently in a tiebreak. <strong>{team1Name}</strong> has a <strong>{round(game["tiebreak_probability_t1"])}</strong> chance of winning it.
          </p>
          {game["if_win_next_point"] && game["if_lose_next_point"] && (
            <>
              <p>
                If <strong>{team1Name}</strong> wins the next point, their probability of winning the tiebreak increases to <strong>{round(game["if_win_next_point"])}</strong>.
              </p>
              <p>
                If they lose the next point, it drops to <strong>{round(game["if_lose_next_point"])}</strong>.
              </p>
            </>
          )}
        </>
      )}
    </div>
  );
};

export default FormattedPredictionResult;
