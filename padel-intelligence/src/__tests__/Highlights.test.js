import { describe, test, expect, beforeEach, afterEach } from '@jest/globals';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Highlights from '../pages/Highlights';

// Mock del componente HighlightCard
jest.mock('../components/HighlightCard', () => ({ icon, ...props }) => (
  <div data-testid="highlight-card">{props.title}</div>
));

describe('Highlights page', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const mockHighlights = [
    { title: 'Biggest Nevera of the Year', description: 'Match 1' },
    { title: 'Most Shots in a Match', description: 'Match 2' },
    { title: 'Most Lobs in a Match', description: 'Match 3' },
    { title: 'Most Points in a Match', description: 'Match 4' },
    { title: 'Most Door Exits per Match', description: 'Match 5' },
    { title: 'Most Smashes in a Match', description: 'Match 6' },
    { title: 'Fewest Smashes in a Match', description: 'Match 7' },
    { title: 'Fewest Unforced Errors', description: 'Match 8' },
    { title: 'Most Repeated Matchup', description: 'Match 9' },
    { title: 'Most Long Points Played', description: 'Match 10' },
    { title: 'Most Winners in a Match', description: 'Match 11' },
    { title: 'Most Forced Errors in a Match', description: 'Match 12' },
  ];

  const mockSummary = {
    matches_played: 1234,
    sets_played: 567,
    points_played: 8901,
  };

  test('renderiza todos los highlights y el resumen de temporada', async () => {
    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockHighlights,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockSummary,
      });

    render(<Highlights />);

    // Asegura que todas las tarjetas de highlight se renderizan
    const cards = await screen.findAllByTestId('highlight-card');
    expect(cards.length).toBe(12);

    // Comprueba que aparecen algunos títulos destacados
    expect(screen.getByText('Biggest Nevera of the Year')).toBeInTheDocument();
    expect(screen.getByText('Most Repeated Matchup')).toBeInTheDocument();

    // Comprueba los labels del resumen
    expect(screen.getByText(/Total Matches/i)).toBeInTheDocument();
    expect(screen.getByText(/Total Sets Played/i)).toBeInTheDocument();
    expect(screen.getByText(/Total Points/i)).toBeInTheDocument();

    // En lugar de formateos con coma, usamos el número directamente por compatibilidad
    expect(screen.getByText('1234')).toBeInTheDocument();
    expect(screen.getByText('567')).toBeInTheDocument();
    expect(screen.getByText('8901')).toBeInTheDocument();
  });
});
