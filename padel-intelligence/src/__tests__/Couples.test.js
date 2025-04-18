import { describe, test, expect, beforeEach, afterEach } from '@jest/globals';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Couples from '../pages/Couples';

jest.mock('../components/LobsPieChart', () => () => <div data-testid="lobs-pie-chart" />);
jest.mock('../components/RadarStatsChart', () => () => <div data-testid="radar-stats-chart" />);
jest.mock('../assets/stats-icon.png', () => 'mock-stats-icon.png');

describe('Couples page', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const mockCouples = [
    {
      player1: 'Juan Lebrón',
      player2: 'Paquito Navarro',
      player1_id: 1,
      player2_id: 2,
      nationality1: 'Spain',
      nationality2: 'Spain',
      gender: 'M',
      photo1: '/photo1.jpg',
      photo2: '/photo2.jpg',
    },
  ];

  const mockStats = {
    tournaments_played: 12,
    matches_played: 28,
    win_rate: 72,
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

  test('renderiza pareja y permite abrir modal con estadísticas y gráficos', async () => {
    // Mock para fetch de /api/pairs y benchmarks
    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockCouples,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockBenchmarkMax,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockBenchmark,
      });

    render(<Couples />);

    // Espera a que se muestre la pareja
    expect(await screen.findByText('Juan Lebrón')).toBeInTheDocument();
    expect(screen.getByText('Paquito Navarro')).toBeInTheDocument();

    // Mock del fetch de stats de la pareja al abrir el modal
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockStats,
    });

    // Clic en icono de estadísticas
    fireEvent.click(screen.getByAltText('Stats'));

    // Espera al modal
    await waitFor(() =>
      expect(screen.getByText('Stats for Juan Lebrón & Paquito Navarro')).toBeInTheDocument()
    );

    // Clic en pestaña de gráficos
    fireEvent.click(screen.getByRole('button', { name: /📊 graphs/i }));

    // Comprueba que aparecen los gráficos
    expect(await screen.findByTestId('lobs-pie-chart')).toBeInTheDocument();
    expect(await screen.findByTestId('radar-stats-chart')).toBeInTheDocument();

    // Cierra el modal
    fireEvent.click(screen.getByText('×'));
    await waitFor(() =>
      expect(screen.queryByText('Stats for Juan Lebrón & Paquito Navarro')).not.toBeInTheDocument()
    );
  });
});
