import { describe, test, expect, beforeEach, afterEach, jest } from "@jest/globals";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import Comparator from "../pages/Comparator";

// Mock del radar chart
jest.mock("../components/RadarChartComparison", () => () => (
  <div data-testid="radar-chart-comparison" />
));

beforeEach(() => {
  global.fetch = jest.fn();
});

afterEach(() => {
  jest.clearAllMocks();
});

describe("Comparator page", () => {
  test("renderiza jugadores y compara métricas", async () => {
    const mockPlayers = [
      {
        player: "Player One",
        nationality: "Spain",
        gender: "M",
        hand: "Right",
        side: "Right",
        brand: "Nox",
        photo: "/photo1.jpg"
      },
      {
        player: "Player Two",
        nationality: "Argentina",
        gender: "M",
        hand: "Left",
        side: "Left",
        brand: "Bullpadel",
        photo: "/photo2.jpg"
      }
    ];

    const mockStats1 = {
      win_rate: 75,
      percentage_1st_serves: 65,
      percentage_parallel: 50,
      tournaments_played: 10,
      matches_played: 25,
      percentage_service_games_won: 70,
      percentage_cross: 60,
      percentage_lobbed_returns: 45,
      percentage_flat_returns: 30,
      percentage_return_errors: 10,
      lobs_received_per_match: 5,
      percentage_smashes_from_lobs: 40,
      percentage_rulos_from_lobs: 15,
      percentage_viborejas_from_lobs: 20,
      percentage_bajadas_from_lobs: 25,
      winners_from_lobs: 30,
      outside_recoveries: 4,
      lobs_played_per_match: 6,
      net_recovery_with_lob: 50,
      unforced_errors_per_match: 2
    };

    const mockStats2 = {
      ...mockStats1,
      win_rate: 60,
      percentage_1st_serves: 75,
      percentage_parallel: 40
    };

    const mockBenchmarkMax = {
      win_rate: 100,
      percentage_1st_serves: 100,
      percentage_parallel: 100
    };

    fetch
      .mockResolvedValueOnce({ ok: true, json: async () => mockPlayers }) // players
      .mockResolvedValueOnce({ ok: true, json: async () => mockBenchmarkMax }) // benchmark max
      .mockResolvedValueOnce({ ok: true, json: async () => mockStats1 }) // player 1
      .mockResolvedValueOnce({ ok: true, json: async () => mockStats2 }); // player 2

    render(<Comparator />);

    const input1 = await screen.findByPlaceholderText("Search player 1...");
    const input2 = await screen.findByPlaceholderText("Search player 2...");

    fireEvent.change(input1, { target: { value: "Player One" } });
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith("/api/player_stats/Player One");
    });

    fireEvent.change(input2, { target: { value: "Player Two" } });
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith("/api/player_stats/Player Two");
    });

    expect(await screen.findByText("Player One")).toBeInTheDocument();
    expect(await screen.findByText("Player Two")).toBeInTheDocument();
    expect(await screen.findByTestId("radar-chart-comparison")).toBeInTheDocument();

    // ✔️ Validar específicamente la fila de "Win Rate"
    const winRateRow = screen.getByText("Win Rate").closest("tr");
    expect(winRateRow).toHaveTextContent("75%");
    expect(winRateRow).toHaveTextContent("60%");
  });
});
