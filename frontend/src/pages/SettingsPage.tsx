import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Dialog } from '../components/ui/Dialog';
import { useToast } from '../components/ui/Toast';
import { 
  Settings, 
  User as UserIcon, 
  Lock, 
  Clock, 
  Target, 
  Download, 
  Trash2, 
  RotateCcw, 
  Check, 
  AlertTriangle,
  LogOut,
  Sliders,
  Shield,
  Calendar
} from 'lucide-react';
import { cn } from '../utils/cn';
import { setSimulatedMockError } from '../services/api';

const GOAL_OPTIONS = [5, 10, 15, 20, 30];
const TIME_OPTIONS = [
  { value: '08:00', label: '8:00 AM (Early Morning)' },
  { value: '09:00', label: '9:00 AM (Morning Study)' },
  { value: '12:00', label: '12:00 PM (Midday)' },
  { value: '18:00', label: '6:00 PM (Evening Review)' },
  { value: '21:00', label: '9:00 PM (Night Routine)' }
];

export function SettingsPage() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { 
    user, 
    useMock, 
    toggleMockMode, 
    loadInitialData, 
    simulateExpiry, 
    logout,
    updateProfile,
    changePassword,
    deleteAccount,
    exportUserData
  } = useAppStore();

  // Profile Form state
  const [name, setName] = useState(user?.name || 'Alex Rivera');
  const [email, setEmail] = useState(user?.email || 'alex@edumentor.app');
  const [isSavingProfile, setIsSavingProfile] = useState(false);

  // Password Change state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  // Review Preferences state
  const [dailyGoal, setDailyGoal] = useState<number>(user?.dailyReviewGoal || 10);
  const [preferredTime, setPreferredTime] = useState<string>(user?.preferredReviewTime || '09:00');
  const [isSavingPreferences, setIsSavingPreferences] = useState(false);

  // Delete Account Dialog state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteConfirmationText, setDeleteConfirmationText] = useState('');
  const [isDeletingAccount, setIsDeletingAccount] = useState(false);

  // 1. Handle Profile Update
  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !email.trim()) {
      toast({
        title: 'Validation Error',
        description: 'Name and email address cannot be empty.',
        variant: 'caution'
      });
      return;
    }

    setIsSavingProfile(true);
    try {
      await updateProfile(name.trim(), email.trim());
      toast({
        title: 'Profile Updated',
        description: 'Your user profile details have been saved successfully.',
        variant: 'success'
      });
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to update profile. Please try again.',
        variant: 'weak'
      });
    } finally {
      setIsSavingProfile(false);
    }
  };

  // 2. Handle Password Change
  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError(null);

    if (!currentPassword) {
      setPasswordError('Please enter your current password.');
      return;
    }
    if (!newPassword || newPassword.length < 6) {
      setPasswordError('New password must be at least 6 characters long.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordError('New password and confirm password do not match.');
      return;
    }

    setIsChangingPassword(true);
    try {
      await changePassword(currentPassword, newPassword);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      toast({
        title: 'Password Changed',
        description: 'Your account password has been updated securely.',
        variant: 'success'
      });
    } catch (err: any) {
      setPasswordError(err?.message || 'Failed to update password.');
    } finally {
      setIsChangingPassword(false);
    }
  };

  // 3. Handle Preferences Save
  const handleSavePreferences = async () => {
    setIsSavingPreferences(true);
    try {
      await updateProfile(user?.name || name, user?.email || email, dailyGoal, preferredTime);
      toast({
        title: 'Review Preferences Saved',
        description: `Daily goal set to ${dailyGoal} concepts at ${preferredTime}.`,
        variant: 'success'
      });
    } catch {
      toast({
        title: 'Error',
        description: 'Could not save review preferences.',
        variant: 'weak'
      });
    } finally {
      setIsSavingPreferences(false);
    }
  };

  // 4. Handle Export Data (JSON)
  const handleExportData = () => {
    exportUserData();
    toast({
      title: 'Data Exported',
      description: 'Your complete study history, concepts, and review schedule have been downloaded as JSON.',
      variant: 'success'
    });
  };

  // 5. Handle Delete Account
  const handleDeleteAccountConfirmed = async () => {
    setIsDeletingAccount(true);
    try {
      await deleteAccount();
      setDeleteDialogOpen(false);
      toast({
        title: 'Account Deleted',
        description: 'Your account and all associated data have been permanently wiped.',
        variant: 'weak'
      });
      navigate('/login');
    } catch {
      toast({
        title: 'Error',
        description: 'Could not delete account. Please try again.',
        variant: 'weak'
      });
    } finally {
      setIsDeletingAccount(false);
    }
  };

  // Dev Demo helpers
  const handleResetData = () => {
    if (confirm('Reset mock database to initial sample decks? This will restore original concepts and sessions.')) {
      localStorage.clear();
      loadInitialData();
      toast({
        title: 'Mock Database Reset',
        description: 'Sample decks and original data have been restored.',
        variant: 'teal'
      });
    }
  };

  const handleSimulateExpiry = () => {
    simulateExpiry();
    navigate('/login');
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="p-4 sm:p-8 max-w-4xl mx-auto flex flex-col gap-6 select-none pb-16">
      {/* Page Header */}
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-2">
          <Badge variant="neutral" className="gap-1">
            <Settings size={11} />
            <span>Preferences & Account</span>
          </Badge>
          <span className="text-xs text-[#737373]">•</span>
          <span className="text-xs text-[#A3A3A3]">User Settings</span>
        </div>
        <h1 className="text-xl sm:text-2xl font-bold text-[#EDEDED] tracking-tight">
          Settings
        </h1>
        <p className="text-xs text-[#A3A3A3]">
          Manage your personal profile, spaced repetition review goals, security, and account data.
        </p>
      </div>

      {/* Section 1: User Profile (Name, Email) */}
      <Card raised className="p-5 border-[#262626]">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-[#2DD4BF]/15 text-[#2DD4BF] flex items-center justify-center">
              <UserIcon size={16} />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-[#EDEDED]">Profile Details</h2>
              <p className="text-[11px] text-[#737373]">Your public learner name and primary email address.</p>
            </div>
          </div>

          <Button variant="outline" size="sm" onClick={handleLogout} className="text-xs">
            <LogOut size={13} className="mr-1" />
            <span>Sign Out</span>
          </Button>
        </div>

        <form onSubmit={handleSaveProfile} className="flex flex-col gap-4 text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <label htmlFor="input-profile-name" className="text-[#A3A3A3] font-medium">
                Full Name
              </label>
              <input
                id="input-profile-name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="px-3 py-2 bg-[#111111] border border-[#262626] rounded-[8px] text-[#EDEDED] outline-none focus:border-[#2DD4BF] focus:ring-1 focus:ring-[#2DD4BF]"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="input-profile-email" className="text-[#A3A3A3] font-medium">
                Email Address
              </label>
              <input
                id="input-profile-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="px-3 py-2 bg-[#111111] border border-[#262626] rounded-[8px] text-[#EDEDED] outline-none focus:border-[#2DD4BF] focus:ring-1 focus:ring-[#2DD4BF]"
              />
            </div>
          </div>

          <div className="flex justify-end pt-1">
            <Button
              type="submit"
              size="sm"
              disabled={isSavingProfile}
              className="bg-[#2DD4BF] text-[#0A0A0A] hover:bg-[#14B8A6] font-semibold text-xs px-4"
              id="btn-save-profile"
            >
              <span>{isSavingProfile ? 'Saving...' : 'Save Profile'}</span>
            </Button>
          </div>
        </form>
      </Card>

      {/* Section 2: Password Change */}
      <Card raised className="p-5 border-[#262626]">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-full bg-[#1F1F1F] text-[#EDEDED] flex items-center justify-center">
            <Lock size={16} />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-[#EDEDED]">Password & Security</h2>
            <p className="text-[11px] text-[#737373]">Update your account credentials to keep your study decks protected.</p>
          </div>
        </div>

        {passwordError && (
          <div className="mb-4 p-2.5 rounded-[8px] bg-[#F87171]/15 border border-[#F87171]/30 text-xs text-[#F87171] flex items-center gap-2">
            <AlertTriangle size={14} className="shrink-0" />
            <span>{passwordError}</span>
          </div>
        )}

        <form onSubmit={handleChangePassword} className="flex flex-col gap-4 text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="flex flex-col gap-1.5">
              <label htmlFor="input-current-password" className="text-[#A3A3A3] font-medium">
                Current Password
              </label>
              <input
                id="input-current-password"
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                placeholder="••••••••"
                className="px-3 py-2 bg-[#111111] border border-[#262626] rounded-[8px] text-[#EDEDED] outline-none focus:border-[#2DD4BF] focus:ring-1 focus:ring-[#2DD4BF]"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="input-new-password" className="text-[#A3A3A3] font-medium">
                New Password
              </label>
              <input
                id="input-new-password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="At least 6 chars"
                className="px-3 py-2 bg-[#111111] border border-[#262626] rounded-[8px] text-[#EDEDED] outline-none focus:border-[#2DD4BF] focus:ring-1 focus:ring-[#2DD4BF]"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="input-confirm-password" className="text-[#A3A3A3] font-medium">
                Confirm New Password
              </label>
              <input
                id="input-confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Re-enter new password"
                className="px-3 py-2 bg-[#111111] border border-[#262626] rounded-[8px] text-[#EDEDED] outline-none focus:border-[#2DD4BF] focus:ring-1 focus:ring-[#2DD4BF]"
              />
            </div>
          </div>

          <div className="flex justify-end pt-1">
            <Button
              type="submit"
              variant="secondary"
              size="sm"
              disabled={isChangingPassword || !currentPassword || !newPassword}
              className="text-xs px-4"
              id="btn-update-password"
            >
              <span>{isChangingPassword ? 'Updating...' : 'Update Password'}</span>
            </Button>
          </div>
        </form>
      </Card>

      {/* Section 3: Daily Review Goal & Preferred Review Time */}
      <Card raised className="p-5 border-[#262626]">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-full bg-[#2DD4BF]/15 text-[#2DD4BF] flex items-center justify-center">
            <Target size={16} />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-[#EDEDED]">Review Preferences & Daily Targets</h2>
            <p className="text-[11px] text-[#737373]">Configure your optimal spaced repetition review cadence.</p>
          </div>
        </div>

        <div className="flex flex-col gap-5 text-xs">
          {/* Daily Review Goal */}
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <span className="text-[#EDEDED] font-medium">Daily Review Goal</span>
              <span className="font-mono text-[#2DD4BF] font-semibold">{dailyGoal} concepts / day</span>
            </div>
            <p className="text-[11px] text-[#737373]">
              Target number of spaced repetition cards to review each day to maintain mastery and streak.
            </p>

            <div className="flex flex-wrap gap-2 pt-1">
              {GOAL_OPTIONS.map((goal) => (
                <button
                  key={goal}
                  type="button"
                  onClick={() => setDailyGoal(goal)}
                  className={cn(
                    'px-3.5 py-1.5 rounded-[8px] text-xs font-semibold border transition-all cursor-pointer',
                    dailyGoal === goal
                      ? 'bg-[#2DD4BF] text-[#0A0A0A] border-[#2DD4BF]'
                      : 'bg-[#111111] text-[#A3A3A3] border-[#262626] hover:text-[#EDEDED] hover:bg-[#1A1A1A]'
                  )}
                >
                  {goal} cards
                </button>
              ))}
            </div>
          </div>

          {/* Preferred Review Time */}
          <div className="flex flex-col gap-2 pt-2 border-t border-[#262626]">
            <div className="flex items-center justify-between">
              <span className="text-[#EDEDED] font-medium">Preferred Review Time</span>
              <span className="font-mono text-[#2DD4BF] font-semibold">{preferredTime}</span>
            </div>
            <p className="text-[11px] text-[#737373]">
              Your preferred study window when EduMentor prepares your daily recall queue.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
              {TIME_OPTIONS.map((item) => (
                <button
                  key={item.value}
                  type="button"
                  onClick={() => setPreferredTime(item.value)}
                  className={cn(
                    'flex items-center justify-between p-2.5 rounded-[8px] text-xs border text-left transition-all cursor-pointer',
                    preferredTime === item.value
                      ? 'bg-[#171717] border-[#2DD4BF] text-[#EDEDED]'
                      : 'bg-[#111111] border-[#262626] text-[#A3A3A3] hover:text-[#EDEDED] hover:bg-[#161616]'
                  )}
                >
                  <span>{item.label}</span>
                  {preferredTime === item.value && <Check size={14} className="text-[#2DD4BF]" />}
                </button>
              ))}
            </div>
          </div>

          <div className="flex justify-end pt-1">
            <Button
              type="button"
              size="sm"
              onClick={handleSavePreferences}
              disabled={isSavingPreferences}
              className="bg-[#2DD4BF] text-[#0A0A0A] hover:bg-[#14B8A6] font-semibold text-xs px-4"
              id="btn-save-preferences"
            >
              <span>{isSavingPreferences ? 'Saving...' : 'Save Preferences'}</span>
            </Button>
          </div>
        </div>
      </Card>

      {/* Section 4: Data Management (Export JSON & Delete Account) */}
      <Card raised className="p-5 border-[#262626]">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-full bg-[#1F1F1F] text-[#EDEDED] flex items-center justify-center">
            <Download size={16} />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-[#EDEDED]">Data & Portability</h2>
            <p className="text-[11px] text-[#737373]">Export your notes, concepts, and SM-2 progress or permanently wipe your account.</p>
          </div>
        </div>

        <div className="flex flex-col gap-4 text-xs">
          {/* Export Data */}
          <div className="flex items-center justify-between p-3.5 rounded-[10px] bg-[#111111] border border-[#262626]">
            <div className="flex flex-col gap-0.5">
              <span className="font-semibold text-[#EDEDED]">Export my data (JSON)</span>
              <span className="text-[11px] text-[#737373]">
                Download a complete, portable archive of your concepts, evaluations, and review decay curves.
              </span>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={handleExportData}
              className="border-[#2DD4BF]/40 text-[#2DD4BF] hover:bg-[#2DD4BF]/10 shrink-0 text-xs gap-1.5"
              id="btn-export-data-json"
            >
              <Download size={13} />
              <span>Export JSON</span>
            </Button>
          </div>

          {/* Delete Account */}
          <div className="flex items-center justify-between p-3.5 rounded-[10px] bg-[#F87171]/5 border border-[#F87171]/20">
            <div className="flex flex-col gap-0.5">
              <span className="font-semibold text-[#F87171]">Delete my account</span>
              <span className="text-[11px] text-[#A3A3A3]">
                Permanently delete your profile, concepts, recall scores, and spaced schedules. Confirmation required.
              </span>
            </div>

            <Button
              variant="danger"
              size="sm"
              onClick={() => {
                setDeleteConfirmationText('');
                setDeleteDialogOpen(true);
              }}
              className="shrink-0 text-xs gap-1.5"
              id="btn-open-delete-account-dialog"
            >
              <Trash2 size={13} />
              <span>Delete account</span>
            </Button>
          </div>
        </div>
      </Card>

      {/* Section 5: Developer & Demo Controls */}
      <Card raised className="p-5 border-[#262626]">
        <div className="flex items-center gap-2 mb-3">
          <Sliders size={16} className="text-[#737373]" />
          <h2 className="text-sm font-semibold text-[#EDEDED]">Developer & Evaluation Controls</h2>
        </div>

        <div className="flex flex-col gap-3 text-xs">
          {/* Mock Flag */}
          <div className="flex items-center justify-between p-3 rounded-[8px] bg-[#111111] border border-[#262626]">
            <div>
              <span className="font-medium text-[#EDEDED]">Mock Service Layer</span>
              <p className="text-[11px] text-[#737373] mt-0.5">Standalone client-side execution with localStorage persistence.</p>
            </div>
            <Button
              variant={useMock ? 'default' : 'secondary'}
              size="sm"
              onClick={toggleMockMode}
              className="text-xs"
            >
              <span>{useMock ? 'Mock: Enabled' : 'Mock: Disabled'}</span>
            </Button>
          </div>

          {/* 7-Day Expiry Simulation */}
          <div className="flex items-center justify-between p-3 rounded-[8px] bg-[#111111] border border-[#262626]">
            <div>
              <span className="font-medium text-[#EDEDED]">Simulate 7-Day Session Expiration</span>
              <p className="text-[11px] text-[#737373] mt-0.5">Triggers auth guard logout with expiration notice.</p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleSimulateExpiry}
              className="border-[#FBBF24]/40 text-[#FBBF24] hover:bg-[#FBBF24]/10 text-xs shrink-0"
              id="btn-simulate-expiry"
            >
              <Clock size={13} className="mr-1" />
              <span>Simulate Expiry</span>
            </Button>
          </div>

          {/* Error Injection & Retry Tester */}
          <div className="flex items-center justify-between p-3 rounded-[8px] bg-[#111111] border border-[#262626]">
            <div>
              <span className="font-medium text-[#EDEDED]">Simulate API Error & Automatic Retry</span>
              <p className="text-[11px] text-[#737373] mt-0.5">Injects a 500 server error to test client exponential backoff and auto-retry.</p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setSimulatedMockError("Simulated transient 500 server error");
                toast({
                  title: 'Error Injected for Next Call',
                  description: 'The next API request will trigger a 500 error, retry with backoff, and succeed automatically.',
                  variant: 'caution'
                });
              }}
              className="border-[#F87171]/40 text-[#F87171] hover:bg-[#F87171]/10 text-xs shrink-0"
              id="btn-simulate-api-error"
            >
              <AlertTriangle size={13} className="mr-1" />
              <span>Inject Error</span>
            </Button>
          </div>

          {/* Reset Demo Data */}
          <div className="flex items-center justify-between p-3 rounded-[8px] bg-[#111111] border border-[#262626]">
            <div>
              <span className="font-medium text-[#EDEDED]">Reset Demo Data</span>
              <p className="text-[11px] text-[#737373] mt-0.5">Re-seed sample decks (Operating Systems, Neuroscience, Biology).</p>
            </div>
            <Button
              variant="danger"
              size="sm"
              onClick={handleResetData}
              className="text-xs shrink-0"
            >
              <RotateCcw size={13} className="mr-1" />
              <span>Reset Demo Decks</span>
            </Button>
          </div>
        </div>

        {/* Backend Contract Reference for Python Team */}
        <div className="mt-4 pt-4 border-t border-[#262626] flex flex-col gap-2">
          <span className="font-semibold text-xs text-[#EDEDED]">Python Backend REST Contract</span>
          <p className="text-[11px] text-[#737373] leading-relaxed">
            The frontend communicates with 10 standard REST endpoints (switched via <code>USE_MOCK</code>). When real mode is active, requests are routed to <code>VITE_API_BASE_URL</code>:
          </p>
          <div className="p-3 rounded-[8px] bg-[#0A0A0A] border border-[#262626] font-mono text-[10px] text-[#2DD4BF] flex flex-col gap-1 overflow-x-auto">
            <div>POST /auth/signup &#123;name, email, password&#125; → &#123;user, token&#125;</div>
            <div>POST /auth/login &#123;email, password&#125; → &#123;user, token&#125;</div>
            <div>POST /modules (multipart: files, pasted_text, module_name) → &#123;module_id, status&#125;</div>
            <div>GET /modules/&#123;id&#125;/status → &#123;steps:[&#123;name, state&#125;], error?&#125;</div>
            <div>GET /modules/&#123;id&#125;/concepts → &#123;concepts:[&#123;id, name, definition, depends_on&#125;]&#125;</div>
            <div>GET /modules/&#123;id&#125;/path → &#123;order:[ids], cycles_removed:[edges]&#125;</div>
            <div>PATCH /concepts/&#123;id&#125; → updates name, definition, or dependencies</div>
            <div>POST /recall/evaluate &#123;concept_id, answer, hinted&#125; → &#123;final_score, similarity, keyword, llm_score, ...&#125;</div>
            <div>GET /review/due → &#123;items:[&#123;concept_id, name, module, last_score, days_overdue&#125;]&#125;</div>
            <div>GET /progress → &#123;stats, charts, table&#125;</div>
          </div>
        </div>
      </Card>

      {/* Delete Account Confirmation Dialog */}
      <Dialog
        isOpen={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        title="Delete Account Permanently"
      >
        <div className="flex flex-col gap-4 text-xs">
          <div className="p-3 rounded-[10px] bg-[#F87171]/10 border border-[#F87171]/30 flex items-start gap-2.5 text-[#F87171]">
            <AlertTriangle size={16} className="shrink-0 mt-0.5" />
            <p className="leading-relaxed">
              <strong>Warning:</strong> This action cannot be undone. All your study sessions, concepts, SM-2 retention curves, and scores will be permanently deleted.
            </p>
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="input-confirm-delete-text" className="text-[#A3A3A3]">
              Type <strong className="text-[#EDEDED]">DELETE</strong> to confirm:
            </label>
            <input
              id="input-confirm-delete-text"
              type="text"
              value={deleteConfirmationText}
              onChange={(e) => setDeleteConfirmationText(e.target.value)}
              placeholder="DELETE"
              className="px-3 py-2 bg-[#111111] border border-[#262626] rounded-[8px] text-[#EDEDED] outline-none focus:border-[#F87171]"
            />
          </div>

          <div className="flex items-center justify-end gap-2.5 pt-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setDeleteDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              size="sm"
              disabled={deleteConfirmationText.trim() !== 'DELETE' || isDeletingAccount}
              onClick={handleDeleteAccountConfirmed}
              className="bg-[#F87171] text-white hover:bg-[#ef4444] font-semibold text-xs px-4 disabled:opacity-30 disabled:cursor-not-allowed"
              id="btn-confirm-delete-account"
            >
              <span>{isDeletingAccount ? 'Deleting...' : 'Permanently Delete Account'}</span>
            </Button>
          </div>
        </div>
      </Dialog>
    </div>
  );
}
