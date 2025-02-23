import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function POST(request: NextRequest): Promise<NextResponse> {
  const cookieStore = await cookies();
  const { nonce, encryptedEmail } = await request.json();
  const isDevelopment = process.env.NODE_ENV === 'development';
  const otpSession = {
    nonce,
    encrypted_email: encryptedEmail,
  };
  cookieStore.set('otp_s', JSON.stringify(otpSession), {
    httpOnly: true,
    secure: !isDevelopment,
  });
  return NextResponse.json({ message: 'Success' });
}
