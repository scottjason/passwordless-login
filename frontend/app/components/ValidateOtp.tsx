import React, { JSX } from 'react';

type Props = {
  otp: string;
  setOtp: (otp: string) => void;
  onValidateOtp: () => void;
  loading: boolean;
  error: string;
};

export const ValidateOtp = ({
  otp,
  setOtp,
  onValidateOtp,
  loading,
  error,
}: Props): JSX.Element => {
  return (
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
        onClick={onValidateOtp}
        disabled={loading}
      >
        {loading ? 'Validating...' : 'Validate OTP'}
      </button>
      {error && <p className="text-red-400 mt-4 text-center">{error}</p>}
    </>
  );
};
