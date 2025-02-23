import React, { JSX } from 'react';

type Props = {
  email: string;
  setEmail: (email: string) => void;
  onRequestOtp: () => void;
  loading: boolean;
  error: string;
};

export const SendOtp = ({
  email,
  setEmail,
  onRequestOtp,
  loading,
  error,
}: Props): JSX.Element => {
  return (
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
        onClick={onRequestOtp}
        disabled={loading}
      >
        {loading ? 'Requesting...' : 'Request OTP'}
      </button>
      {error && <p className="text-red-400 mt-4 text-center">{error}</p>}
    </>
  );
};
