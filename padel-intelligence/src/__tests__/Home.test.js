import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import Home from '../pages/Home';
import '@testing-library/jest-dom';

// Simula el paso del tiempo para el cambio de slide
jest.useFakeTimers();

describe('Home Component', () => {
  test('renders the main title', () => {
    render(<Home />);
    expect(screen.getByText(/Welcome to Padel Intelligence/i)).toBeInTheDocument();
  });

  test('renders carousel with initial slide', () => {
    render(<Home />);
    const image = screen.getByAltText(/Slide 1/i);
    expect(image).toBeInTheDocument();
  });

  test('changes carousel slide automatically after 3 seconds', () => {
    render(<Home />);
    act(() => {
      jest.advanceTimersByTime(3000);
    });
    expect(screen.getByText(/Discover each player's strengths/i)).toBeInTheDocument();
  });

  test('clicking next and prev buttons changes slide', () => {
    render(<Home />);
    const nextButton = document.querySelector('.carousel-button.next');
    const prevButton = document.querySelector('.carousel-button.prev');

    fireEvent.click(nextButton);
    expect(screen.getByText(/Discover each player's strengths/i)).toBeInTheDocument();

    fireEvent.click(prevButton);
    expect(screen.getByText(/Statistics and data/i)).toBeInTheDocument();
  });

  test('renders all three benefit cards', () => {
    render(<Home />);
    expect(screen.getByText(/Improve Data Analysis in Padel/i)).toBeInTheDocument();
    expect(screen.getByText(/Support the Development of Padel/i)).toBeInTheDocument();
    expect(screen.getByText(/Enhance and Add Value for Professionals/i)).toBeInTheDocument();
  });
});
