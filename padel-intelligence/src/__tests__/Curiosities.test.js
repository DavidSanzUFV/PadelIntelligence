import { describe, test, expect, beforeEach, afterEach } from '@jest/globals';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Curiosities from '../pages/Curiosities';

jest.mock('../components/CuriosityCard', () => (props) => (
  <div data-testid="curiosity-card">
    {props.icon}
    <div>{props.title}</div>
    <div>{props.facts.join(', ')}</div>
  </div>
));

describe('Curiosities page', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const mockCuriosities = {
    "Rankings & Player Profiles": {
      "Nationality Ranking": [
        { nationality: "Spain", value: 25 },
        { nationality: "Argentina", value: 18 },
        { nationality: "France", value: 7 }
      ],
      "Racket Brand Usage": [
        { brand: "Bullpadel", value: 15 },
        { brand: "Nox", value: 10 },
        { brand: "Adidas", value: 5 }
      ],
    },
    "Serve & Return": {
      "1st vs 2nd Serve": [
        { player: "Player A", value: 0.68 },
        { player: "Player B", value: 0.64 },
        { player: "Player C", value: 0.61 }
      ]
    }
  };

  test('renderiza curiosidades y cambia de pestaña', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockCuriosities
    });

    render(<Curiosities />);

    const cards = await screen.findAllByTestId('curiosity-card');
    expect(cards.length).toBeGreaterThan(0);

    expect(screen.getByText(/season curiosities/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /serve & return/i }));

    await waitFor(() => {
        const cards = screen.getAllByTestId("curiosity-card");
        const matchingCard = cards.find((card) =>
          card.textContent.includes("1st vs 2nd Serve") &&
          card.textContent.includes("Player A") &&
          card.textContent.includes("0.68")
        );
        expect(matchingCard).not.toBeNull();
      });
  });
});
