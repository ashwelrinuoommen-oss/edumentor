import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';
import { 
  Eye, 
  EyeOff, 
  ArrowRight, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  Shield 
} from 'lucide-react';
import { cn } from '../utils/cn';

export function SignupPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [agreeTerms, setAgreeTerms] = useState(false);

  // Field validation states
  const [nameError, setNameError] = useState('');
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [confirmError, setConfirmError] = useState('');
  const [termsError, setTermsError] = useState('');
  const [authError, setAuthError] = useState('');

  const { signup, isLoading } = useAppStore();
  const navigate = useNavigate();

  // Password Strength Calculation
  const calculatePasswordStrength = (pwd: string) => {
    if (!pwd) return { score: 0, label: '', color: '' };
    let score = 0;
    if (pwd.length >= 8) score += 1;
    if (pwd.length >= 12) score += 1;
    if (/[A-Z]/.test(pwd) && /[a-z]/.test(pwd)) score += 1;
    if (/[0-9]/.test(pwd)) score += 1;
    if (/[^A-Za-z0-9]/.test(pwd)) score += 1;

    if (score <= 1) return { score: 1, label: 'Weak', color: '#F87171' };
    if (score === 2 || score === 3) return { score: 2, label: 'Fair', color: '#FBBF24' };
    if (score === 4) return { score: 3, label: 'Good', color: '#2DD4BF' };
    return { score: 4, label: 'Strong', color: '#34D399' };
  };

  const strength = calculatePasswordStrength(password);

  const validate = () => {
    let valid = true;
    setNameError('');
    setEmailError('');
    setPasswordError('');
    setConfirmError('');
    setTermsError('');
    setAuthError('');

    if (!name.trim()) {
      setNameError('Full name is required.');
      valid = false;
    }

    const cleanEmail = email.trim();
    if (!cleanEmail) {
      setEmailError('Email is required.');
      valid = false;
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cleanEmail)) {
      setEmailError('Please enter a valid email address.');
      valid = false;
    }

    if (!password) {
      setPasswordError('Password is required.');
      valid = false;
    } else if (password.length < 8) {
      setPasswordError('Password must be at least 8 characters.');
      valid = false;
    }

    if (!confirmPassword) {
      setConfirmError('Please confirm your password.');
      valid = false;
    } else if (password !== confirmPassword) {
      setConfirmError('Passwords do not match.');
      valid = false;
    }

    if (!agreeTerms) {
      setTermsError('You must agree to the Terms of Service to continue.');
      valid = false;
    }

    return valid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate() || isLoading) return;

    try {
      await signup(name, email, password);
      navigate('/home');
    } catch (err: any) {
      setAuthError(err?.message || 'Failed to create account.');
    }
  };

  return (
    <div className="min-h-screen w-full bg-[#0A0A0A] flex flex-col items-center justify-center p-4 text-[#EDEDED] relative overflow-hidden">
      {/* Background soft glow */}
      <div className="absolute top-1/4 left-1/3 w-96 h-96 bg-[#2DD4BF]/4 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md flex flex-col gap-6 z-10 my-8">
        {/* Brand Mark */}
        <div className="flex flex-col items-center text-center gap-2">
          <div className="w-8 h-8 rounded-[8px] bg-[#2DD4BF]/15 border border-[#2DD4BF]/40 flex items-center justify-center">
            <div className="w-3.5 h-3.5 bg-[#2DD4BF] rotate-45 rounded-[1px]" />
          </div>
          <h1 className="text-xl font-bold tracking-tight text-[#EDEDED]">EduMentor</h1>
          <p className="text-xs text-[#737373]">Study. Recall. Master.</p>
        </div>

        {/* Top error message */}
        {authError && (
          <div className="p-3 rounded-[10px] bg-[#F87171]/10 border border-[#F87171]/30 flex items-center gap-2.5 text-xs text-[#F87171] animate-fade-in" id="signup-error-banner">
            <AlertCircle size={15} className="shrink-0" />
            <span>{authError}</span>
          </div>
        )}

        {/* Form Card */}
        <Card raised className="border-[#262626] p-6 sm:p-8">
          <CardHeader className="p-0 pb-6">
            <CardTitle className="text-xl">Create an account</CardTitle>
            <CardDescription className="text-xs">
              Start structuring your lecture notes and mastering recall.
            </CardDescription>
          </CardHeader>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
            {/* Full Name */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-[#A3A3A3]" htmlFor="signup-name">
                Full Name
              </label>
              <Input
                id="signup-name"
                type="text"
                value={name}
                onChange={(e) => {
                  setName(e.target.value);
                  if (nameError) setNameError('');
                  if (authError) setAuthError('');
                }}
                placeholder="Alex Rivera"
                disabled={isLoading}
                className={nameError ? 'border-[#F87171]' : ''}
              />
              {nameError && (
                <span className="text-[11px] text-[#F87171] leading-none mt-0.5">
                  {nameError}
                </span>
              )}
            </div>

            {/* Email */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-[#A3A3A3]" htmlFor="signup-email">
                Email
              </label>
              <Input
                id="signup-email"
                type="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (emailError) setEmailError('');
                  if (authError) setAuthError('');
                }}
                placeholder="alex@edumentor.app"
                disabled={isLoading}
                className={emailError ? 'border-[#F87171]' : ''}
              />
              {emailError && (
                <span className="text-[11px] text-[#F87171] leading-none mt-0.5">
                  {emailError}
                </span>
              )}
            </div>

            {/* Password with Strength Meter */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-[#A3A3A3]" htmlFor="signup-password">
                Password
              </label>
              <div className="relative flex items-center">
                <Input
                  id="signup-password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    if (passwordError) setPasswordError('');
                    if (authError) setAuthError('');
                  }}
                  placeholder="At least 8 characters"
                  disabled={isLoading}
                  className={`pr-10 ${passwordError ? 'border-[#F87171]' : ''}`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 p-1 text-[#737373] hover:text-[#EDEDED] transition-colors focus-visible:ring-2 focus-visible:ring-[#2DD4BF] rounded"
                  title={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff size={14} /> : <Eye size={14} />}
                </button>
              </div>

              {/* Password Strength Indicator */}
              {password && (
                <div className="flex flex-col gap-1 mt-1">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-[#737373]">Password strength:</span>
                    <span className="font-semibold" style={{ color: strength.color }}>
                      {strength.label}
                    </span>
                  </div>
                  <div className="grid grid-cols-4 gap-1 h-1.5 w-full bg-[#1F1F1F] rounded-full overflow-hidden">
                    <div className={cn('h-full rounded-full transition-all', strength.score >= 1 ? 'bg-[#F87171]' : 'bg-transparent')} />
                    <div className={cn('h-full rounded-full transition-all', strength.score >= 2 ? 'bg-[#FBBF24]' : 'bg-transparent')} />
                    <div className={cn('h-full rounded-full transition-all', strength.score >= 3 ? 'bg-[#2DD4BF]' : 'bg-transparent')} />
                    <div className={cn('h-full rounded-full transition-all', strength.score >= 4 ? 'bg-[#34D399]' : 'bg-transparent')} />
                  </div>
                </div>
              )}

              {passwordError && (
                <span className="text-[11px] text-[#F87171] leading-none mt-0.5">
                  {passwordError}
                </span>
              )}
            </div>

            {/* Confirm Password */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-[#A3A3A3]" htmlFor="signup-confirm-password">
                Confirm Password
              </label>
              <Input
                id="signup-confirm-password"
                type={showPassword ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value);
                  if (confirmError) setConfirmError('');
                  if (authError) setAuthError('');
                }}
                placeholder="Re-enter password"
                disabled={isLoading}
                className={confirmError ? 'border-[#F87171]' : ''}
              />
              {confirmError && (
                <span className="text-[11px] text-[#F87171] leading-none mt-0.5">
                  {confirmError}
                </span>
              )}
            </div>

            {/* Terms Checkbox */}
            <div className="flex flex-col gap-1 mt-1">
              <div className="flex items-start gap-2">
                <input
                  type="checkbox"
                  id="signup-terms"
                  checked={agreeTerms}
                  onChange={(e) => {
                    setAgreeTerms(e.target.checked);
                    if (termsError) setTermsError('');
                  }}
                  disabled={isLoading}
                  className="mt-0.5 w-4 h-4 rounded border-[#262626] bg-[#111111] accent-[#2DD4BF] text-[#2DD4BF] focus-visible:ring-2 focus-visible:ring-[#2DD4BF]"
                />
                <label htmlFor="signup-terms" className="text-xs text-[#A3A3A3] select-none leading-relaxed cursor-pointer">
                  I agree to the Terms of Service and Privacy Policy
                </label>
              </div>
              {termsError && (
                <span className="text-[11px] text-[#F87171] leading-none pl-6">
                  {termsError}
                </span>
              )}
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              variant="default"
              className="w-full mt-2"
              disabled={isLoading}
              id="btn-signup-submit"
            >
              {isLoading ? (
                <>
                  <Loader2 size={15} className="animate-spin" />
                  <span>Creating account...</span>
                </>
              ) : (
                <>
                  <span>Create account</span>
                  <ArrowRight size={14} />
                </>
              )}
            </Button>
          </form>
        </Card>

        {/* Footer Link back to login */}
        <p className="text-center text-xs text-[#737373]">
          Already have an account?{' '}
          <Link
            to="/login"
            className="text-[#2DD4BF] hover:underline font-medium focus-visible:ring-2 focus-visible:ring-[#2DD4BF] rounded px-1"
          >
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
