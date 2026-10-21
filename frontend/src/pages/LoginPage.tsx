import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { useToast } from '../components/ui/Toast';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';
import { 
  Eye, 
  EyeOff, 
  ArrowRight, 
  UploadCloud, 
  MessageSquare, 
  Clock, 
  AlertCircle,
  Sparkles,
  Loader2
} from 'lucide-react';

export function LoginPage() {
  const [email, setEmail] = useState('alex@edumentor.app');
  const [password, setPassword] = useState('password123');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);

  // Field validation states
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [authError, setAuthError] = useState('');

  const { login, isLoading, sessionExpired, clearSessionExpired } = useAppStore();
  const { toast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();

  const from = (location.state as any)?.from?.pathname || '/home';

  // Check if session expired
  useEffect(() => {
    if (sessionExpired) {
      toast({
        title: 'Session Expired',
        description: 'Your 7-day session has ended. Please log in again.',
        type: 'caution'
      });
      clearSessionExpired();
    }
  }, [sessionExpired, toast, clearSessionExpired]);

  const validateForm = () => {
    let isValid = true;
    setEmailError('');
    setPasswordError('');
    setAuthError('');

    const cleanEmail = email.trim();
    if (!cleanEmail) {
      setEmailError('Email is required.');
      isValid = false;
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cleanEmail)) {
      setEmailError('Please enter a valid email address.');
      isValid = false;
    }

    if (!password) {
      setPasswordError('Password is required.');
      isValid = false;
    }

    return isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm() || isLoading) return;

    try {
      await login(email, password, rememberMe);
      navigate(from, { replace: true });
    } catch (err: any) {
      setAuthError(err?.message || 'Email or password is incorrect');
    }
  };

  const handleGoogleSignIn = async () => {
    // Mock Google SSO sign-in
    try {
      await login('alex@edumentor.app', 'demo', true);
      toast({
        title: 'Google Sign-In Successful',
        description: 'Authenticated via Google OAuth (Mock).',
        type: 'success'
      });
      navigate(from, { replace: true });
    } catch {
      setAuthError('Google authentication failed.');
    }
  };

  return (
    <div className="min-h-screen w-full bg-[#0A0A0A] flex flex-col md:flex-row text-[#EDEDED] relative overflow-hidden">
      {/* Background Soft Glow & Grid Effect */}
      <div className="absolute inset-0 pointer-events-none opacity-40">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#2DD4BF]/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/3 right-1/4 w-96 h-96 bg-[#2DD4BF]/3 rounded-full blur-3xl" />
        <div 
          className="absolute inset-0" 
          style={{
            backgroundImage: `radial-gradient(#262626 1px, transparent 1px)`,
            backgroundSize: '24px 24px'
          }} 
        />
      </div>

      {/* ==========================================================================
          LEFT PANEL: Brand, Tagline, & Three Stacked Steps
          (On mobile: compact header)
         ========================================================================== */}
      <div className="w-full md:w-1/2 p-8 md:p-16 flex flex-col justify-between z-10 border-b md:border-b-0 md:border-r border-[#262626] bg-[#0A0A0A]/80 backdrop-blur-sm">
        {/* Brand Header */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-[7px] bg-[#2DD4BF]/15 border border-[#2DD4BF]/40 flex items-center justify-center">
              <div className="w-3 h-3 bg-[#2DD4BF] rotate-45 rounded-[1px]" />
            </div>
            <span className="text-lg font-bold tracking-tight text-[#EDEDED]">EduMentor</span>
          </div>
          <p className="text-xs text-[#2DD4BF] font-medium tracking-wide uppercase">
            Study. Recall. Master.
          </p>
        </div>

        {/* Center: Value Proposition & 3 Steps (Hidden/compact on small mobile, expanded on desktop) */}
        <div className="my-8 md:my-auto flex flex-col gap-8 max-w-md">
          <div className="flex flex-col gap-2">
            <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-[#EDEDED] leading-tight">
              Master complex topics through active memory retrieval.
            </h2>
            <p className="text-xs text-[#A3A3A3] leading-relaxed">
              EduMentor closes the loop between reading notes and durable cognitive retention.
            </p>
          </div>

          {/* 3 Short Steps Stacked Vertically */}
          <div className="flex flex-col gap-5">
            {/* Step 1 */}
            <div className="flex items-start gap-3.5">
              <div className="w-8 h-8 rounded-full bg-[#171717] border border-[#262626] flex items-center justify-center text-[#2DD4BF] shrink-0 mt-0.5">
                <UploadCloud size={15} />
              </div>
              <div className="flex flex-col gap-0.5">
                <h4 className="text-xs font-semibold text-[#EDEDED]">1. Upload your notes</h4>
                <p className="text-[11px] text-[#737373] leading-relaxed">
                  Paste lecture notes or slides. EduMentor extracts key concepts and orders them by prerequisite dependency.
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="flex items-start gap-3.5">
              <div className="w-8 h-8 rounded-full bg-[#171717] border border-[#262626] flex items-center justify-center text-[#2DD4BF] shrink-0 mt-0.5">
                <MessageSquare size={15} />
              </div>
              <div className="flex flex-col gap-0.5">
                <h4 className="text-xs font-semibold text-[#EDEDED]">2. Recall in your own words</h4>
                <p className="text-[11px] text-[#737373] leading-relaxed">
                  A conversational Socratic mentor prompts you to articulate core mechanisms without re-reading.
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="flex items-start gap-3.5">
              <div className="w-8 h-8 rounded-full bg-[#171717] border border-[#262626] flex items-center justify-center text-[#2DD4BF] shrink-0 mt-0.5">
                <Clock size={15} />
              </div>
              <div className="flex flex-col gap-0.5">
                <h4 className="text-xs font-semibold text-[#EDEDED]">3. Review what is weak</h4>
                <p className="text-[11px] text-[#737373] leading-relaxed">
                  The SM-2 spaced repetition scheduler schedules weak concepts back right as retention begins to decay.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Note */}
        <div className="text-[11px] text-[#737373] hidden md:block">
          Calm, focused, ad-free study environment.
        </div>
      </div>

      {/* ==========================================================================
          RIGHT PANEL: Login Form Card
         ========================================================================== */}
      <div className="w-full md:w-1/2 p-6 md:p-16 flex items-center justify-center z-10 bg-[#0A0A0A]">
        <div className="w-full max-w-md flex flex-col gap-4">
          {/* Top Error Banner for Wrong Credentials */}
          {authError && (
            <div className="p-3 rounded-[10px] bg-[#F87171]/10 border border-[#F87171]/30 flex items-center gap-2.5 text-xs text-[#F87171] animate-fade-in" id="auth-error-banner">
              <AlertCircle size={15} className="shrink-0" />
              <span>{authError}</span>
            </div>
          )}

          {/* Form Card */}
          <Card raised className="border-[#262626] p-6 sm:p-8">
            <CardHeader className="p-0 pb-6">
              <CardTitle className="text-xl">Welcome back</CardTitle>
              <CardDescription className="text-xs">
                Sign in to continue your active recall sessions and spaced reviews.
              </CardDescription>
            </CardHeader>

            <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
              {/* Email Field */}
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-medium text-[#A3A3A3]" htmlFor="login-email">
                  Email
                </label>
                <Input
                  id="login-email"
                  type="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (emailError) setEmailError('');
                    if (authError) setAuthError('');
                  }}
                  placeholder="name@example.com"
                  disabled={isLoading}
                  autoComplete="email"
                  className={emailError ? 'border-[#F87171] focus-visible:border-[#F87171]' : ''}
                />
                {emailError && (
                  <span className="text-[11px] text-[#F87171] leading-none mt-0.5">
                    {emailError}
                  </span>
                )}
              </div>

              {/* Password Field with Show/Hide Toggle */}
              <div className="flex flex-col gap-1.5">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-medium text-[#A3A3A3]" htmlFor="login-password">
                    Password
                  </label>
                  <Link
                    to="/forgot-password"
                    className="text-[11px] text-[#2DD4BF] hover:underline focus-visible:ring-2 focus-visible:ring-[#2DD4BF] rounded px-1"
                  >
                    Forgot password?
                  </Link>
                </div>

                <div className="relative flex items-center">
                  <Input
                    id="login-password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => {
                      setPassword(e.target.value);
                      if (passwordError) setPasswordError('');
                      if (authError) setAuthError('');
                    }}
                    placeholder="••••••••"
                    disabled={isLoading}
                    autoComplete="current-password"
                    className={`pr-10 ${passwordError ? 'border-[#F87171] focus-visible:border-[#F87171]' : ''}`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    tabIndex={0}
                    className="absolute right-3 p-1 text-[#737373] hover:text-[#EDEDED] transition-colors focus-visible:ring-2 focus-visible:ring-[#2DD4BF] rounded"
                    title={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? <EyeOff size={14} /> : <Eye size={14} />}
                  </button>
                </div>
                {passwordError && (
                  <span className="text-[11px] text-[#F87171] leading-none mt-0.5">
                    {passwordError}
                  </span>
                )}
              </div>

              {/* Remember Me Checkbox */}
              <div className="flex items-center gap-2 mt-0.5">
                <input
                  type="checkbox"
                  id="remember-me-checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  disabled={isLoading}
                  className="w-4 h-4 rounded border-[#262626] bg-[#111111] accent-[#2DD4BF] text-[#2DD4BF] focus-visible:ring-2 focus-visible:ring-[#2DD4BF]"
                />
                <label htmlFor="remember-me-checkbox" className="text-xs text-[#A3A3A3] select-none cursor-pointer">
                  Remember me for 7 days
                </label>
              </div>

              {/* Primary Submit Button */}
              <Button
                type="submit"
                variant="default"
                className="w-full mt-2"
                disabled={isLoading}
                id="btn-login-submit"
              >
                {isLoading ? (
                  <>
                    <Loader2 size={15} className="animate-spin" />
                    <span>Signing in...</span>
                  </>
                ) : (
                  <>
                    <span>Log in</span>
                    <ArrowRight size={14} />
                  </>
                )}
              </Button>

              {/* Divider with "or" */}
              <div className="relative my-2 text-center text-xs text-[#737373]">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-[#262626]" />
                </div>
                <span className="relative bg-[#171717] px-3 text-[11px] uppercase tracking-wider">
                  or
                </span>
              </div>

              {/* Secondary Continue with Google (Mock) */}
              <Button
                type="button"
                variant="secondary"
                onClick={handleGoogleSignIn}
                disabled={isLoading}
                className="w-full text-xs gap-2.5"
                id="btn-google-login"
              >
                <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
                  <path
                    fill="#EA4335"
                    d="M12 5c1.6 0 3 .6 4.1 1.6l3.1-3.1C17.3 1.7 14.8 1 12 1 7.5 1 3.7 3.6 1.9 7.3l3.7 2.9C6.5 7.2 9 5 12 5z"
                  />
                  <path
                    fill="#4285F4"
                    d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.6h6.5c-.3 1.5-1.1 2.8-2.4 3.7l3.7 2.9c2.2-2 3.7-5 3.7-8.9z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.6 14.8c-.2-.7-.4-1.5-.4-2.3s.2-1.6.4-2.3L1.9 7.3C.7 9.7 0 12.3 0 15s.7 5.3 1.9 7.7l3.7-2.9z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3 0-5.5-2.2-6.4-5.2L1.9 16c1.8 3.7 5.6 7 10.1 7z"
                  />
                </svg>
                <span>Continue with Google</span>
              </Button>
            </form>
          </Card>

          {/* New Here? Link */}
          <p className="text-center text-xs text-[#737373]">
            New here?{' '}
            <Link
              to="/signup"
              className="text-[#2DD4BF] hover:underline font-medium focus-visible:ring-2 focus-visible:ring-[#2DD4BF] rounded px-1"
            >
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
