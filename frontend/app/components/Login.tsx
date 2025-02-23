'use client';
import React, { JSX, useState, useCallback } from 'react';
import isEmail from 'validator/es/lib/isEmail';
import { SendOtp } from './SendOtp';
import { ValidateOtp } from './ValidateOtp';

type View = 'send-otp' | 'validate-otp';

export const Login = (): JSX.Element => {
  const [email, setEmail] = useState('scottleejason@gmail.com');
  const [otp, setOtp] = useState('');
  const [view, setView] = useState<View>('send-otp');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const onRequestOtp = useCallback(async () => {
    if (!isEmail(email)) {
      setError('Invalid email address');
      return;
    }
    setError('');
    setLoading(true);
    const reqUrl = `${process.env.NEXT_PUBLIC_API_URL}/generate-otp`;
    try {
      const response = await fetch(reqUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_email: email }),
      });

      if (!response.ok) throw new Error('Failed to request OTP');
      const data = await response.json();
      const nonce = data.nonce;
      const encryptedEmail = data.encrypted_email;
      const protocol = window.location.protocol;
      const url = `${protocol}//${window.location.host}/api/set-otp-session`;
      await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nonce, encryptedEmail }),
      });
      setView('validate-otp');
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [email]);

  const onValidateOtp = useCallback(async () => {
    setError('');
    setLoading(true);
    const reqUrl = `${process.env.NEXT_PUBLIC_API_URL}/validate-otp`;
    try {
      const response = await fetch(reqUrl, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ otp }),
      });
      console.log(response);
    } catch (err) {
      setError((err as Error).message);
    }
  }, [otp]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0A0E1F] via-[#0A1A2F] to-[#081020] flex items-center justify-center">
      <div className="w-full max-w-md p-8 bg-white bg-opacity-5 backdrop-blur-md rounded-2xl shadow-lg">
        <h1 className="text-2xl font-extralight text-center text-gray-200 mb-6 tracking-wide">
          Passwordless Login
        </h1>
        {view === 'send-otp' ? (
          <SendOtp
            email={email}
            setEmail={setEmail}
            onRequestOtp={onRequestOtp}
            loading={loading}
            error={error}
          />
        ) : (
          <ValidateOtp
            otp={otp}
            setOtp={setOtp}
            onValidateOtp={onValidateOtp}
            loading={loading}
            error={error}
          />
        )}
      </div>
    </div>
  );
};
