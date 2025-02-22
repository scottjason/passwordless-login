import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Login } from '../Login'; // Adjust path if needed

describe('Login Component', () => {
  test('renders email input and request OTP button', () => {
    render(<Login />);

    // Check if email input is present
    expect(screen.getByPlaceholderText('Enter your email')).toBeInTheDocument();

    // Check if "Request OTP" button is present
    expect(screen.getByText('Request OTP')).toBeInTheDocument();
  });

  test('updates email input value', () => {
    render(<Login />);

    const emailInput = screen.getByPlaceholderText('Enter your email');
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

    expect(emailInput).toHaveValue('test@example.com');
  });

  test('switches to OTP input after requesting OTP', async () => {
    render(<Login />);

    // Mock fetch to prevent actual API call
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ message: 'OTP sent', nonce: '123456' }),
      })
    ) as jest.Mock;

    const requestOtpButton = screen.getByText('Request OTP');

    fireEvent.click(requestOtpButton);

    // Check if OTP input appears
    expect(await screen.findByPlaceholderText('Enter OTP')).toBeInTheDocument();

    // Restore original fetch after test
    global.fetch.mockRestore();
  });
});
