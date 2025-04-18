import { describe, test, expect, beforeEach, afterEach } from '@jest/globals';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Prediction from '../pages/Prediction';

// Mock del componente hijo para evitar dependencias externas
jest.mock('../components/FormattedPredictionResult', () => () => (
  <div data-testid="formatted-result">Mocked Result</div>
));

describe('Prediction page', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const mockPairsResponse = { pairs: ['Team A', 'Team B'] };
  const mockPredictionResponse = { winner: 'Team A', probability: 0.65 };

  test('muestra las parejas en el autocompletado', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPairsResponse,
    });

    render(<Prediction />);

    const inputTeam1 = screen.getByPlaceholderText(/select team 1/i);
    fireEvent.change(inputTeam1, { target: { value: 'team' } });

    const option = await screen.findByText('Team A');
    expect(option).toBeInTheDocument();

    fireEvent.click(option);

    // 👇 Usa un selector más específico para evitar ambigüedad
    expect(screen.getByText('Team A', { selector: '.selected-team' })).toBeInTheDocument();
  });

  test('lanza la predicción y abre el modal', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPairsResponse,
    });
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPredictionResponse,
    });

    render(<Prediction />);

    fireEvent.change(screen.getByPlaceholderText(/select team 1/i), {
      target: { value: 'team a' },
    });
    fireEvent.click(await screen.findByText('Team A'));

    fireEvent.change(screen.getByPlaceholderText(/select team 2/i), {
      target: { value: 'team b' },
    });
    fireEvent.click(await screen.findByText('Team B'));

    const predictBtn = await screen.findByRole('button', { name: /predict/i });
    expect(predictBtn).toBeEnabled();

    fireEvent.click(predictBtn);

    expect(screen.getByText(/generating prediction/i)).toBeInTheDocument();

    const modalHeading = await screen.findByRole('heading', {
      name: /victory prediction/i,
    });
    expect(modalHeading).toBeInTheDocument();
    expect(screen.getByTestId('formatted-result')).toBeInTheDocument();

    expect(fetch).toHaveBeenCalledWith('/api/run_prediction/', expect.objectContaining({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    }));
  });

  test('cierra el modal al pulsar la ×', async () => {
    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockPairsResponse,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockPredictionResponse,
      });

    render(<Prediction />);

    fireEvent.change(screen.getByPlaceholderText(/select team 1/i), {
      target: { value: 'team a' },
    });
    fireEvent.click(await screen.findByText('Team A'));

    fireEvent.change(screen.getByPlaceholderText(/select team 2/i), {
      target: { value: 'team b' },
    });
    fireEvent.click(await screen.findByText('Team B'));

    fireEvent.click(await screen.findByRole('button', { name: /predict/i }));

    await screen.findByRole('heading', {
      name: /victory prediction/i,
    });

    fireEvent.click(screen.getByText('×'));

    await waitFor(() =>
      expect(
        screen.queryByRole('heading', { name: /victory prediction/i })
      ).not.toBeInTheDocument()
    );
  });
});
