import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { authService } from '../services/mockService';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';
import { ArrowLeft, CheckCircle2, Mail, Loader2 } from 'lucide-react';

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [emailError, setEmailError] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setEmailError('');

    const cleanEmail = email.trim();
    if (!cleanEmail) {
      setEmailError('Please enter your email address.');
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cleanEmail)) {
      setEmailError('Please enter a valid email address.');
      return;
    }

    setIsLoading(true);
    await authService.resetPassword(cleanEmail);
    setIsLoading(false);
    // Generic confirmation: Never reveal whether an email is registered
    setSubmitted(true);
  };

  return (
    <div className="min-h-screen w-full bg-[#0A0A0A] flex flex-col items-center justify-center p-4 text-[#EDEDED] relative overflow-hidden">
      {/* Background soft glow */}
      <div className="absolute top-1/4 left-1/3 w-96 h-96 bg-[#2DD4BF]/4 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md flex flex-col gap-6 z-10">
        {/* Brand Mark */}
        <div className="flex flex-col items-center text-center gap-2">
          <div className="w-8 h-8 rounded-[8px] bg-[#2DD4BF]/15 border border-[#2DD4BF]/40 flex items-center justify-center">
            <div className="w-3.5 h-3.5 bg-[#2DD4BF] rotate-45 rounded-[1px]" />
          </div>
          <h1 className="text-xl font-bold tracking-tight text-[#EDEDED]">EduMentor</h1>
          <p className="text-xs text-[#737373]">Study. Recall. Master.</p>
        </div>

        {/* Card */}
        <Card raised className="border-[#262626] p-6 sm:p-8">
          <CardHeader className="p-0 pb-6">
            <CardTitle className="text-xl">Reset your password</CardTitle>
            <CardDescription className="text-xs">
              Enter your account email to receive recovery instructions.
            </CardDescription>
          </CardHeader>

          <CardContent className="p-0">
            {submitted ? (
              <div className="flex flex-col items-center text-center gap-3.5 py-4 animate-fade-in">
                <div className="w-11 h-11 rounded-full bg-[#34D399]/15 border border-[#34D399]/30 flex items-center justify-center text-[#34D399]">
                  <Mail size={20} />
                </div>
                <div className="flex flex-col gap-1">
                  <h3 className="text-sm font-semibold text-[#EDEDED]">Check your inbox</h3>
                  <p className="text-xs text-[#A3A3A3] leading-relaxed max-w-xs">
                    If this email exists, we have sent a link to reset your password. Please check your spam folder if it doesn't appear shortly.
                  </p>
                </div>

                <div className="w-full pt-4 border-t border-[#262626] flex flex-col gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full text-xs"
                    onClick={() => {
                      setSubmitted(false);
                      setEmail('');
                    }}
                  >
                    Try another email
                  </Button>
                  <Link
                    to="/login"
                    className="inline-flex items-center justify-center gap-1.5 py-2 text-xs text-[#2DD4BF] hover:underline"
                  >
                    <ArrowLeft size={13} />
                    <span>Return to log in</span>
                  </Link>
                </div>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-medium text-[#A3A3A3]" htmlFor="reset-email">
                    Account Email
                  </label>
                  <Input
                    id="reset-email"
                    type="email"
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value);
                      if (emailError) setEmailError('');
                    }}
                    placeholder="name@example.com"
                    disabled={isLoading}
                    autoComplete="email"
                    className={emailError ? 'border-[#F87171]' : ''}
                  />
                  {emailError && (
                    <span className="text-[11px] text-[#F87171] leading-none mt-0.5">
                      {emailError}
                    </span>
                  )}
                </div>

                <Button
                  type="submit"
                  variant="default"
                  className="w-full mt-2"
                  disabled={isLoading}
                  id="btn-send-reset-link"
                >
                  {isLoading ? (
                    <>
                      <Loader2 size={15} className="animate-spin" />
                      <span>Sending reset link...</span>
                    </>
                  ) : (
                    <span>Send reset link</span>
                  )}
                </Button>

                <div className="text-center pt-2">
                  <Link
                    to="/login"
                    className="inline-flex items-center gap-1.5 text-xs text-[#737373] hover:text-[#EDEDED] transition-colors focus-visible:ring-2 focus-visible:ring-[#2DD4BF] rounded px-1"
                  >
                    <ArrowLeft size={13} />
                    <span>Back to log in</span>
                  </Link>
                </div>
              </form>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
