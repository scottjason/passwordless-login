'use client';
import { useState } from 'react';

export const Login = () => {
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const requestOtp = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/generate-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_email: email, user_id: 'user123' }),
      });

      if (!response.ok) throw new Error('Failed to request OTP');

      setStep(2);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0A0E1F] via-[#0A1A2F] to-[#081020] flex items-center justify-center">
      <div className="w-full max-w-md p-8 bg-white bg-opacity-5 backdrop-blur-md rounded-2xl shadow-lg">
        <h1 className="text-2xl font-extralight text-center text-gray-200 mb-6 tracking-wide">
          Passwordless Login
        </h1>
        {step === 1 ? (
          <>
            <input
              type="email"
              className="w-full p-3 mb-4 bg-white bg-opacity-10 text-white placeholder-gray-400 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <button
              className={`w-full p-3 rounded-md bg-[#1E90FF] hover:bg-[#1A78D6] transition-all text-[#F0F8FF] font-semibold tracking-wide uppercase ${
                loading ? 'opacity-50' : ''
              }`}
              onClick={requestOtp}
              disabled={loading}
            >
              {loading ? 'Requesting...' : 'Request OTP'}
            </button>
          </>
        ) : (
          <>
            <input
              type="text"
              className="w-full p-3 mb-4 bg-white bg-opacity-10 text-white placeholder-gray-400 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter OTP"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
            />
            <button
              className={`w-full p-3 rounded-md bg-blue-700 hover:bg-blue-800 transition-all ${
                loading ? 'opacity-50' : ''
              } text-white`}
              onClick={() => setStep(1)}
              disabled={loading}
            >
              {loading ? 'Validating...' : 'Validate OTP'}
            </button>
          </>
        )}
        {error && <p className="text-red-400 mt-4 text-center">{error}</p>}
      </div>
    </div>
  );
};
