import { describe, test, expect, beforeEach, afterEach } from '@jest/globals';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Statistics from '../pages/Statistics';

// Mocks de componentes y assets
jest.mock('../components/LobsPieChart', () => () => <div data-testid="lobs-pie-chart" />);
jest.mock('../components/RadarStatsChart', () => () => <div data-testid="radar-stats-chart" />);
jest.mock('../assets/stats-icon.png', () => 'mock-stats-icon.png');

describe('Statistics page', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const mockPlayers = [
    {
      player: 'Juan Lebrón',
      nationality: 'Spain',
      gender: 'M',
      hand: 'Right',
      side: 'Right',
      brand: 'Bullpadel',
      photo: '/path/to/photo.jpg',
    },
    {
      player: 'Paquito Navarro',
      nationality: 'Spain',
      gender: 'M',
      hand: 'Left',
      side: 'Left',
      brand: 'Bullpadel',
      photo: '/path/to/photo2.jpg',
    },
  ];

  const mockPlayerStats = {
    tournaments_played: 10,
    matches_played: 25,
    win_rate: 70,
    percentage_1st_serves: 65,
    percentage_service_games_won: 75,
    percentage_cross: 40,
    percentage_parallel: 60,
    percentage_lobbed_returns: 30,
    percentage_flat_returns: 50,
    percentage_return_errors: 20,
    lobs_received_per_match: 5,
    percentage_smashes_from_lobs: 30,
    percentage_rulos_from_lobs: 10,
    percentage_viborejas_from_lobs: 15,
    percentage_bajadas_from_lobs: 20,
    winners_from_lobs: 25,
    outside_recoveries: 3,
    lobs_played_per_match: 8,
    net_recovery_with_lob: 45,
    unforced_errors_per_match: 2,
  };

  const mockBenchmark = {};
  const mockBenchmarkMax = {};

  test('renderiza jugadores y permite abrir modal con gráficos', async () => {
    // Mock de los tres fetchs iniciales (jugadores, benchmarkMax, benchmark)
    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockPlayers,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockBenchmarkMax,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockBenchmark,
      });

    render(<Statistics />);

    // Espera a que aparezca el jugador
    const playerCard = await screen.findByText('Juan Lebrón');
    expect(playerCard).toBeInTheDocument();

    // Mock de las estadísticas individuales (antes de abrir el modal)
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPlayerStats,
    });

    // Haz clic en el icono de estadísticas
    fireEvent.click(screen.getAllByAltText('Stats')[0]);

    // Espera a que aparezca el modal
    await waitFor(() => {
      expect(screen.getByText("Juan Lebrón's Stats")).toBeInTheDocument();
    });

    // Cambia a la pestaña de gráficos
    fireEvent.click(screen.getByRole('button', { name: /📊 Graphs/i }));
    expect(await screen.findByTestId('lobs-pie-chart')).toBeInTheDocument();
    expect(await screen.findByTestId('radar-stats-chart')).toBeInTheDocument();

    // Cierra el modal
    fireEvent.click(screen.getByText('×'));
    await waitFor(() =>
      expect(screen.queryByText("Juan Lebrón's Stats")).not.toBeInTheDocument()
    );
  });
});
