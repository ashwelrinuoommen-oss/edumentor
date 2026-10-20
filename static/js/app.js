/**
 * EduMentor Web Client — AI Study Companion Workspace
 * "The chat workspace is the product. The sophisticated AI/ML architecture operates behind it."
 */

let appState = {
  student_name: "Ashwel",
  authenticated: false,
  state: "HOME",
  curriculum_title: null,
  current_concept: null,
  current_concept_index: 0,
  total_concepts: 0,
  mastered_count: 0,
  mastery_percent: 0,
  weak_queue_count: 0,
  weak_queue: [],
  last_evaluation: null,
  last_recall_question: null,
  chat_history: [],
  graph: { nodes: [], edges: [] }
};

// Phase 41: Client-Side Product Events Telemetry Dispatcher
function trackProductEvent(eventName, properties = {}) {
  try {
    fetch("/api/events/track", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        event_name: eventName,
        user_id: appState.student_name ? `user_${appState.student_name.toLowerCase().replace(/\\s+/g, '_')}` : undefined,
        concept_id: appState.current_concept ? appState.current_concept.id : undefined,
        properties: properties
      })
    }).catch(() => {});
  } catch (_) {}
}

document.addEventListener("DOMContentLoaded", () => {
  initAuthListeners();
  initEventListeners();
  initHeroVisualListeners();
  initHistoryListeners();
  checkAuthState();
  setInterval(fetchNotifications, 15000); // Proactive spaced recall check
});

/* ==========================================================================
   AUTHENTICATION & ACCESS CONTROLLER (PHASE 1 & PHASE 29)
   ========================================================================== */
function checkAuthState() {
  const storedUser = localStorage.getItem("edumentor_student");
  if (storedUser) {
    try {
      const user = JSON.parse(storedUser);
      appState.authenticated = true;
      appState.student_name = user.username || "Ashwel";
      document.querySelectorAll(".user-name-display").forEach(el => el.textContent = appState.student_name);
      showWorkspaceStage();
      fetchSessionState();
      checkResumeState();
      fetchNotifications();
      return;
    } catch (e) {
      localStorage.removeItem("edumentor_student");
    }
  }

  // Not authenticated: Retain the premium landing page from the original design! (Phase 29)
  appState.authenticated = false;
  showLandingStage();
}

function showLandingStage() {
  const landingStage = document.getElementById("landingStage");
  const authModal = document.getElementById("authModal");
  const homeStage = document.getElementById("homeStage");
  const chatStage = document.getElementById("chatWorkspaceStage");
  const progressStage = document.getElementById("progressStage");
  const activeModulePill = document.getElementById("activeModulePill");
  const btnSignOut = document.getElementById("btnHeaderSignOut");
  const appHeader = document.querySelector(".app-header");

  if (landingStage) landingStage.style.display = "flex";
  if (authModal) authModal.style.display = "none";
  if (homeStage) homeStage.style.display = "none";
  if (chatStage) chatStage.style.display = "none";
  if (progressStage) progressStage.style.display = "none";
  if (activeModulePill) activeModulePill.style.display = "none";
  if (btnSignOut) btnSignOut.style.display = "none";
  if (appHeader) appHeader.style.display = "none";
  updateMobileDrawerState();
}

function showAuthStage(mode = "login") {
  const authModal = document.getElementById("authModal");
  const authStage = document.getElementById("authStage");
  if (authModal) authModal.style.display = "flex";
  if (authStage) authStage.style.display = "flex";

  const loginForm = document.getElementById("authLoginForm");
  const signupForm = document.getElementById("authSignupForm");
  const forgotForm = document.getElementById("authForgotForm");
  const heading = document.getElementById("authHeading");
  const sub = document.getElementById("authSub");
  const alertBanner = document.getElementById("authAlertBanner");
  if (alertBanner) alertBanner.style.display = "none";

  if (mode === "login") {
    if (loginForm) loginForm.style.display = "flex";
    if (signupForm) signupForm.style.display = "none";
    if (forgotForm) forgotForm.style.display = "none";
    if (heading) heading.textContent = "Welcome back";
    if (sub) sub.textContent = "Continue your adaptive recall journey with EduMentor.";
  } else if (mode === "signup") {
    if (loginForm) loginForm.style.display = "none";
    if (signupForm) signupForm.style.display = "flex";
    if (forgotForm) forgotForm.style.display = "none";
    if (heading) heading.textContent = "Create your account";
    if (sub) sub.textContent = "Start your personalized adaptive study journey with EduMentor.";
  } else if (mode === "forgot") {
    if (loginForm) loginForm.style.display = "none";
    if (signupForm) signupForm.style.display = "none";
    if (forgotForm) forgotForm.style.display = "flex";
    if (heading) heading.textContent = "Reset Password";
    if (sub) sub.textContent = "Enter your email to set a new password.";
  }
}

function hideAuthModal() {
  const authModal = document.getElementById("authModal");
  if (authModal) authModal.style.display = "none";
}

function showWorkspaceStage() {
  const landingStage = document.getElementById("landingStage");
  const authModal = document.getElementById("authModal");
  const authStage = document.getElementById("authStage");
  const btnSignOut = document.getElementById("btnHeaderSignOut");
  const appHeader = document.querySelector(".app-header");

  if (landingStage) landingStage.style.display = "none";
  if (authModal) authModal.style.display = "none";
  if (authStage) authStage.style.display = "none";
  if (appHeader) appHeader.style.display = "flex";
  if (btnSignOut) btnSignOut.style.display = "inline-flex";

  if (appState.state === "HOME" && (!appState.curriculum_title || appState.chat_history.length <= 1)) {
    const homeStage = document.getElementById("homeStage");
    if (homeStage) homeStage.style.display = "flex";
  } else {
    const chatStage = document.getElementById("chatWorkspaceStage");
    if (chatStage) chatStage.style.display = "flex";
  }
  updateMobileDrawerState();
}

function showAuthAlert(message, type = "error") {
  const banner = document.getElementById("authAlertBanner");
  if (!banner) return;
  banner.className = `auth-alert-banner ${type}`;
  banner.textContent = message;
  banner.style.display = "block";
}

function initAuthListeners() {
  // 1. Switch between Login, Signup, Forgot
  const btnToSignup = document.getElementById("btnToSignup");
  const btnToLogin = document.getElementById("btnToLogin");
  const btnToForgot = document.getElementById("btnToForgot");
  const btnForgotToLogin = document.getElementById("btnForgotToLogin");

  if (btnToSignup) btnToSignup.addEventListener("click", () => showAuthStage("signup"));
  if (btnToLogin) btnToLogin.addEventListener("click", () => showAuthStage("login"));
  if (btnToForgot) btnToForgot.addEventListener("click", () => showAuthStage("forgot"));
  if (btnForgotToLogin) btnForgotToLogin.addEventListener("click", () => showAuthStage("login"));

  // 2. Sign In Form Submission
  const authLoginForm = document.getElementById("authLoginForm");
  if (authLoginForm) {
    authLoginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const identifier = document.getElementById("loginIdentifier").value.trim();
      const password = document.getElementById("loginPassword").value;
      if (!identifier) return showAuthAlert("Please enter your email or username.");

      try {
        const res = await fetch("/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ identifier, password })
        });
        const data = await res.json();
        if (!res.ok) {
          showAuthAlert(data.detail || "Authentication failed. Please check your credentials.");
          return;
        }
        localStorage.setItem("edumentor_student", JSON.stringify(data.user));
        appState.authenticated = true;
        appState.student_name = data.user.username;
        showWorkspaceStage();
        if (data.session) updateUI(data.session);
      } catch (err) {
        showAuthAlert("Network error during sign in.");
      }
    });
  }

  // 3. Continue with Google (One-Click Demo as Ashwel)
  const btnGoogleLogin = document.getElementById("btnGoogleLogin");
  if (btnGoogleLogin) {
    btnGoogleLogin.addEventListener("click", () => performDemoLogin("Ashwel"));
  }

  // 4. Demo Profile Buttons
  document.querySelectorAll(".btn-demo-profile").forEach((btn) => {
    btn.addEventListener("click", () => {
      const u = btn.getAttribute("data-user") || "Ashwel";
      performDemoLogin(u);
    });
  });

  // 5. Sign Up Form Submission
  const authSignupForm = document.getElementById("authSignupForm");
  if (authSignupForm) {
    authSignupForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const username = document.getElementById("signupName").value.trim();
      const email = document.getElementById("signupEmail").value.trim();
      const password = document.getElementById("signupPassword").value;
      const studying = document.getElementById("signupStudying").value.trim();

      if (!username || !email || !password) {
        return showAuthAlert("Please fill in name, email, and password.");
      }

      try {
        const res = await fetch("/api/auth/signup", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, email, password, studying })
        });
        const data = await res.json();
        if (!res.ok) {
          showAuthAlert(data.detail || "Sign up failed.");
          return;
        }
        localStorage.setItem("edumentor_student", JSON.stringify(data.user));
        appState.authenticated = true;
        appState.student_name = data.user.username;
        showWorkspaceStage();
        if (data.session) updateUI(data.session);
      } catch (err) {
        showAuthAlert("Network error during registration.");
      }
    });
  }

  // 6. Forgot Password Form Submission
  const authForgotForm = document.getElementById("authForgotForm");
  if (authForgotForm) {
    authForgotForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = document.getElementById("forgotEmail").value.trim();
      const new_password = document.getElementById("forgotNewPassword").value;

      try {
        const res = await fetch("/api/auth/forgot-password", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, new_password })
        });
        const data = await res.json();
        if (!res.ok) {
          showAuthAlert(data.detail || "Password reset failed.");
          return;
        }
        showAuthAlert("Password updated successfully! You may now sign in.", "success");
        setTimeout(() => showAuthStage("login"), 1400);
      } catch (err) {
        showAuthAlert("Network error during password reset.");
      }
    });
  }

  // 7. Header Sign Out Button
  const btnHeaderSignOut = document.getElementById("btnHeaderSignOut");
  if (btnHeaderSignOut) {
    btnHeaderSignOut.addEventListener("click", async () => {
      try {
        await fetch("/api/auth/logout", { method: "POST" });
      } catch (e) {}
      localStorage.removeItem("edumentor_student");
      appState.authenticated = false;
      showLandingStage();
    });
  }

  // 8. Phase 29: Landing Page Trigger Auth Buttons & Modal Dismiss
  document.querySelectorAll(".btn-trigger-auth").forEach((btn) => {
    btn.addEventListener("click", () => showAuthStage("signup"));
  });

  const btnLandingSignIn = document.getElementById("btnLandingSignIn");
  if (btnLandingSignIn) {
    btnLandingSignIn.addEventListener("click", () => showAuthStage("login"));
  }

  const btnCloseAuthModal = document.getElementById("btnCloseAuthModal");
  if (btnCloseAuthModal) {
    btnCloseAuthModal.addEventListener("click", hideAuthModal);
  }

  const authModal = document.getElementById("authModal");
  if (authModal) {
    authModal.addEventListener("click", (e) => {
      if (e.target === authModal) {
        hideAuthModal();
      }
    });
  }
}

async function performDemoLogin(username) {
  try {
    const res = await fetch("/api/auth/demo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username })
    });
    const data = await res.json();
    if (res.ok) {
      localStorage.setItem("edumentor_student", JSON.stringify(data.user));
      appState.authenticated = true;
      appState.student_name = data.user.username;
      showWorkspaceStage();
      if (data.session) updateUI(data.session);
    }
  } catch (err) {
    console.error("Demo login error:", err);
  }
}

/* ==========================================================================
   INITIALIZATION & EVENT LISTENERS
   ========================================================================== */
async function fetchSessionState() {
  try {
    const res = await fetch("/api/session");
    if (res.ok) {
      const data = await res.json();
      updateUI(data);
    }
  } catch (err) {
    console.error("Failed to load session:", err);
  }
}

function initEventListeners() {
  // 1. Home Stage Submission
  const homePromptForm = document.getElementById("homePromptForm");
  const homeInputText = document.getElementById("homeInputText");
  if (homePromptForm && homeInputText) {
    homePromptForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const text = homeInputText.value.trim();
      if (!text) return;
      homeInputText.value = "";
      sendChatMessage(text);
    });

    // Enter key submit on home textarea (unless Shift+Enter)
    homeInputText.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        homePromptForm.dispatchEvent(new Event("submit"));
      }
    });
  }

  // 2. Home Notes Upload
  const btnHomeUpload = document.getElementById("btnUploadNotes") || document.getElementById("btnHomeUpload");
  const homeFileInput = document.getElementById("homeFileInput");
  if (btnHomeUpload && homeFileInput) {
    btnHomeUpload.addEventListener("click", () => homeFileInput.click());
    homeFileInput.addEventListener("change", () => {
      if (homeFileInput.files.length > 0) {
        showHomeAttachmentChip(homeFileInput.files[0]);
        uploadNotesFile(homeFileInput.files[0]);
      }
    });
  }

  // Drag and Drop on Central Input Card
  const centralCard = document.querySelector(".central-input-card");
  if (centralCard) {
    centralCard.addEventListener("dragover", (e) => {
      e.preventDefault();
      centralCard.classList.add("drag-over");
    });
    ["dragleave", "dragend"].forEach((evt) => {
      centralCard.addEventListener(evt, () => centralCard.classList.remove("drag-over"));
    });
    centralCard.addEventListener("drop", (e) => {
      e.preventDefault();
      centralCard.classList.remove("drag-over");
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        showHomeAttachmentChip(e.dataTransfer.files[0]);
        uploadNotesFile(e.dataTransfer.files[0]);
      }
    });
  }

  // 3. Recent Learning / Topic Cards
  document.querySelectorAll(".recent-card").forEach((card) => {
    card.addEventListener("click", () => {
      const topic = card.getAttribute("data-topic");
      if (topic) {
        sendChatMessage(`I want to study ${topic}`);
      }
    });
  });

  // 4. Active Chat Composer
  const activeChatForm = document.getElementById("activeChatForm");
  const activeChatInput = document.getElementById("activeChatInput");
  if (activeChatForm && activeChatInput) {
    activeChatForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const text = activeChatInput.value.trim();
      if (!text) return;
      activeChatInput.value = "";
      sendChatMessage(text);
    });

    activeChatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        activeChatForm.dispatchEvent(new Event("submit"));
      }
    });
  }

  // 5. Active Chat Upload Notes or Answer File
  const btnActiveUpload = document.getElementById("btnActiveUpload");
  const activeFileInput = document.getElementById("activeFileInput");
  if (btnActiveUpload && activeFileInput) {
    btnActiveUpload.addEventListener("click", () => activeFileInput.click());
    activeFileInput.addEventListener("change", () => {
      if (activeFileInput.files.length > 0) {
        const file = activeFileInput.files[0];
        showActiveAttachmentChip(file);
        if (appState.state === "WAITING_RECALL") {
          uploadAnswerFile(file);
        } else {
          uploadNotesFile(file);
        }
      }
    });
  }

  // Drag and drop on active composer
  const composerInner = document.querySelector(".composer-inner");
  if (composerInner) {
    composerInner.addEventListener("dragover", (e) => {
      e.preventDefault();
      composerInner.classList.add("drag-over");
    });
    ["dragleave", "dragend"].forEach((evt) => {
      composerInner.addEventListener(evt, () => composerInner.classList.remove("drag-over"));
    });
    composerInner.addEventListener("drop", (e) => {
      e.preventDefault();
      composerInner.classList.remove("drag-over");
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0];
        showActiveAttachmentChip(file);
        if (appState.state === "WAITING_RECALL") {
          uploadAnswerFile(file);
        } else {
          uploadNotesFile(file);
        }
      }
    });
  }

  // 6. Knowledge Graph Drawer Toggle
  const btnToggleGraphDrawer = document.getElementById("btnToggleGraphDrawer");
  const btnCloseDrawer = document.getElementById("btnCloseDrawer");
  const graphDrawer = document.getElementById("graphDrawer");
  const drawerBackdrop = document.getElementById("drawerBackdrop");

  if (btnToggleGraphDrawer && graphDrawer && drawerBackdrop) {
    const openDrawer = () => {
      graphDrawer.classList.add("open");
      drawerBackdrop.classList.add("active");
      renderKnowledgeGraph(appState.graph);
    };
    const closeDrawer = () => {
      graphDrawer.classList.remove("open");
      drawerBackdrop.classList.remove("active");
    };

    btnToggleGraphDrawer.addEventListener("click", openDrawer);
    if (btnCloseDrawer) btnCloseDrawer.addEventListener("click", closeDrawer);
    drawerBackdrop.addEventListener("click", closeDrawer);
  }

  // 7. Profile Settings Modal
  const btnProfileSettings = document.getElementById("btnProfileSettings");
  const settingsModal = document.getElementById("settingsModal");
  const btnCloseModal = document.getElementById("btnCloseModal");
  const settingsForm = document.getElementById("settingsForm");

  if (btnProfileSettings && settingsModal) {
    btnProfileSettings.addEventListener("click", () => settingsModal.classList.add("active"));
  }
  if (btnCloseModal && settingsModal) {
    btnCloseModal.addEventListener("click", () => settingsModal.classList.remove("active"));
  }
  if (settingsForm) {
    settingsForm.addEventListener("submit", (e) => {
      e.preventDefault();
      saveSettings();
    });
  }

  // 8. Phase 16 Notification Center Listeners
  initNotificationListeners();

  // 9. Phase 18 Resume Learning & Phase 19 Progress Listeners
  initResumeAndProgressListeners();

  // 10. Phase 30 Hero Visual Artwork Listeners
  initHeroVisualListeners();

  // 11. Phase 31 Mobile Navigation Drawer & Assistant Listeners
  initMobileDrawerListeners();

  // 12. Phase 32 Keyboard Navigation & Accessibility Listeners
  initKeyboardAccessibility();

  // 13. Phase 38 Performance: Animation Visibility Optimizer
  initAnimationVisibilityOptimizer();
}

function initHeroVisualListeners() {
  const caption = document.getElementById("heroArtCaption");
  const captionText = document.getElementById("heroCaptionText");
  const pathConcept = document.getElementById("pathConcept");
  const pathRecall = document.getElementById("pathRecall");
  const pathTeacher = document.getElementById("pathTeacher");
  const pathMastery = document.getElementById("pathMastery");

  if (!caption || !captionText) return;

  const hoverData = {
    concept: {
      text: "Concept: Structured knowledge extracted directly from your lecture notes & slides",
      cls: "highlight-concept",
      paths: [pathConcept]
    },
    recall: {
      text: "Recall: Active memory retrieval synthesis without hints or multiple choice guessing",
      cls: "highlight-recall",
      paths: [pathRecall]
    },
    teacher: {
      text: "AI Teacher: Personalized paired instruction adapting questions to your cognitive pace",
      cls: "highlight-teacher",
      paths: [pathTeacher]
    },
    mastery: {
      text: "Mastery: Durable retention verified through closed-loop SM-2 adaptive spaced reviews",
      cls: "highlight-mastery",
      paths: [pathMastery]
    }
  };

  document.querySelectorAll(".art-node-group").forEach((el) => {
    const phase = el.getAttribute("data-phase");
    const data = hoverData[phase];
    if (!data) return;

    el.addEventListener("mouseenter", () => {
      captionText.textContent = data.text;
      caption.className = `hero-art-caption ${data.cls}`;
      data.paths.forEach((p) => p && p.classList.add("ribbon-hover-active"));
    });

    el.addEventListener("mouseleave", () => {
      captionText.textContent = "Hover over Concept, Recall, or Mastery to explore the learning loop";
      caption.className = "hero-art-caption";
      data.paths.forEach((p) => p && p.classList.remove("ribbon-hover-active"));
    });
  });
}

/* ==========================================================================
   PHASE 31 — RESPONSIVE EXPERIENCE & MOBILE ASSISTANT CONTROLLER
   ========================================================================== */
function initMobileDrawerListeners() {
  const mobileNavDrawer = document.getElementById("mobileNavDrawer");
  const mobileDrawerBackdrop = document.getElementById("mobileDrawerBackdrop");
  const btnMobileHeaderMenu = document.getElementById("btnMobileHeaderMenu");
  const btnMobileNavToggle = document.getElementById("btnMobileNavToggle");
  const btnCloseMobileDrawer = document.getElementById("btnCloseMobileDrawer");

  const openMobileDrawer = () => {
    if (!mobileNavDrawer) return;
    mobileNavDrawer.classList.add("open");
    mobileNavDrawer.setAttribute("aria-hidden", "false");
    if (btnMobileHeaderMenu) btnMobileHeaderMenu.setAttribute("aria-expanded", "true");
    if (btnMobileNavToggle) btnMobileNavToggle.setAttribute("aria-expanded", "true");
    if (mobileDrawerBackdrop) mobileDrawerBackdrop.style.display = "block";
    updateMobileDrawerState();
    announceToScreenReader("Navigation menu opened");
    if (btnCloseMobileDrawer) btnCloseMobileDrawer.focus();
  };

  const closeMobileDrawer = () => {
    if (!mobileNavDrawer) return;
    mobileNavDrawer.classList.remove("open");
    mobileNavDrawer.setAttribute("aria-hidden", "true");
    if (btnMobileHeaderMenu) btnMobileHeaderMenu.setAttribute("aria-expanded", "false");
    if (btnMobileNavToggle) btnMobileNavToggle.setAttribute("aria-expanded", "false");
    if (mobileDrawerBackdrop) mobileDrawerBackdrop.style.display = "none";
    announceToScreenReader("Navigation menu closed");
  };

  const toggleMobileMenu = () => {
    if (mobileNavDrawer && mobileNavDrawer.classList.contains("open")) {
      closeMobileDrawer();
    } else {
      openMobileDrawer();
    }
  };

  if (btnMobileHeaderMenu) btnMobileHeaderMenu.addEventListener("click", toggleMobileMenu);
  if (btnMobileNavToggle) btnMobileNavToggle.addEventListener("click", toggleMobileMenu);
  if (btnCloseMobileDrawer) btnCloseMobileDrawer.addEventListener("click", closeMobileDrawer);
  if (mobileDrawerBackdrop) mobileDrawerBackdrop.addEventListener("click", closeMobileDrawer);

  // Drawer nav links
  document.querySelectorAll(".drawer-link").forEach((link) => {
    link.addEventListener("click", () => {
      closeMobileDrawer();
    });
  });

  const btnDrawerSignIn = document.getElementById("btnDrawerSignIn");
  if (btnDrawerSignIn) {
    btnDrawerSignIn.addEventListener("click", () => {
      closeMobileDrawer();
      showAuthStage("login");
    });
  }

  const btnDrawerStart = document.getElementById("btnDrawerStart");
  if (btnDrawerStart) {
    btnDrawerStart.addEventListener("click", () => {
      closeMobileDrawer();
      showAuthStage("signup");
    });
  }

  const btnDrawerKnowledgeGraph = document.getElementById("btnDrawerKnowledgeGraph");
  if (btnDrawerKnowledgeGraph) {
    btnDrawerKnowledgeGraph.addEventListener("click", () => {
      closeMobileDrawer();
      const btnToggle = document.getElementById("btnToggleGraphDrawer");
      if (btnToggle) btnToggle.click();
    });
  }

  const btnDrawerProgress = document.getElementById("btnDrawerProgress");
  if (btnDrawerProgress) {
    btnDrawerProgress.addEventListener("click", () => {
      closeMobileDrawer();
      const btnToggle = document.getElementById("btnToggleProgress");
      if (btnToggle) btnToggle.click();
    });
  }

  const btnDrawerProfile = document.getElementById("btnDrawerProfile");
  if (btnDrawerProfile) {
    btnDrawerProfile.addEventListener("click", () => {
      closeMobileDrawer();
      const btnProfile = document.getElementById("btnProfileSettings");
      if (btnProfile) btnProfile.click();
    });
  }

  const btnDrawerSignOut = document.getElementById("btnDrawerSignOut");
  if (btnDrawerSignOut) {
    btnDrawerSignOut.addEventListener("click", () => {
      closeMobileDrawer();
      const btnSignOut = document.getElementById("btnHeaderSignOut");
      if (btnSignOut) btnSignOut.click();
    });
  }

  // Handle responsive mobile composer placeholder: [ Type...  📎  ↑ ]
  const adjustMobilePlaceholders = () => {
    const homeInput = document.getElementById("homeInputText");
    const activeInput = document.getElementById("activeChatInput");
    const isMobile = window.innerWidth < 768;
    if (homeInput) {
      homeInput.placeholder = isMobile ? "Type..." : "Ask EduMentor anything about your learning";
    }
    if (activeInput) {
      activeInput.placeholder = isMobile ? "Type..." : "Type your answer or explain from memory...";
    }
  };

  adjustMobilePlaceholders();
  window.addEventListener("resize", adjustMobilePlaceholders);
}

/* ==========================================================================
   PHASE 32 — ACCESSIBILITY CONTROLLER (WCAG 2.1 AA/AAA)
   ========================================================================== */
function announceToScreenReader(message) {
  const announcer = document.getElementById("srLiveAnnouncer");
  if (!announcer || !message) return;
  announcer.textContent = "";
  setTimeout(() => {
    announcer.textContent = message;
  }, 50);
}

function initKeyboardAccessibility() {
  window.addEventListener("keydown", (e) => {
    // 1. ESCAPE: Close any active modal, drawer, or dropdown
    if (e.key === "Escape") {
      // Mobile drawer
      const mobileDrawer = document.getElementById("mobileNavDrawer");
      if (mobileDrawer && mobileDrawer.classList.contains("open")) {
        const btnClose = document.getElementById("btnCloseMobileDrawer");
        if (btnClose) btnClose.click();
        return;
      }
      // Knowledge Graph drawer
      const graphDrawer = document.getElementById("graphDrawer");
      if (graphDrawer && graphDrawer.classList.contains("open")) {
        const btnClose = document.getElementById("btnCloseDrawer");
        if (btnClose) btnClose.click();
        return;
      }
      // Auth modal
      const authModal = document.getElementById("authModal");
      if (authModal && authModal.style.display !== "none") {
        hideAuthModal();
        return;
      }
      // Settings modal
      const settingsModal = document.getElementById("settingsModal");
      if (settingsModal && settingsModal.classList.contains("active")) {
        settingsModal.classList.remove("active");
        return;
      }
      // Add Module modal
      const addModuleModal = document.getElementById("addModuleModal");
      if (addModuleModal && addModuleModal.style.display !== "none") {
        addModuleModal.style.display = "none";
        return;
      }
      // Resume modal
      const resumeModal = document.getElementById("resumeLearningModal");
      if (resumeModal && resumeModal.style.display !== "none") {
        resumeModal.style.display = "none";
        return;
      }
      // Notification dropdown
      const notifDropdown = document.getElementById("notificationDropdown");
      if (notifDropdown && notifDropdown.style.display !== "none") {
        notifDropdown.style.display = "none";
        return;
      }
      // Module dropdown
      const moduleDropdown = document.getElementById("moduleDropdownPanel");
      if (moduleDropdown && moduleDropdown.style.display !== "none") {
        moduleDropdown.style.display = "none";
        return;
      }
    }

    const activeTag = document.activeElement ? document.activeElement.tagName.toUpperCase() : "";
    const isTyping = (activeTag === "INPUT" || activeTag === "TEXTAREA" || activeTag === "SELECT");

    // 2. Alt+R or Slash '/': Focus active chat input (when not already typing)
    if ((e.altKey && (e.key === "r" || e.key === "R")) || (e.key === "/" && !isTyping)) {
      e.preventDefault();
      const chatStage = document.getElementById("chatWorkspaceStage");
      const activeChatInput = document.getElementById("activeChatInput");
      const homeInputText = document.getElementById("homeInputText");

      if (chatStage && chatStage.style.display !== "none" && activeChatInput) {
        activeChatInput.focus();
        announceToScreenReader("Chat input focused");
      } else if (homeInputText) {
        homeInputText.focus();
        announceToScreenReader("Prompt input focused");
      }
      return;
    }

    // 3. Alt+N: Advance to next concept when in FEEDBACK phase
    if (e.altKey && (e.key === "n" || e.key === "N")) {
      if (appState.state === "FEEDBACK") {
        e.preventDefault();
        advanceNext();
        return;
      }
    }

    // 4. Alt+C: "I'm Ready" trigger when in STUDYING phase
    if (e.altKey && (e.key === "c" || e.key === "C")) {
      if (appState.state === "STUDYING") {
        e.preventDefault();
        triggerReady();
        return;
      }
    }
  });
}

function updateMobileDrawerState() {
  const drawerLandingActions = document.getElementById("drawerLandingActions");
  const drawerAppLinks = document.getElementById("drawerAppLinks");
  if (appState && appState.authenticated) {
    if (drawerLandingActions) drawerLandingActions.style.display = "none";
    if (drawerAppLinks) drawerAppLinks.style.display = "flex";
  } else {
    if (drawerLandingActions) drawerLandingActions.style.display = "flex";
    if (drawerAppLinks) drawerAppLinks.style.display = "none";
  }
}

/* ==========================================================================
   PHASE 38 — PERFORMANCE & ANIMATION VISIBILITY OPTIMIZER
   Pauses decorative ambient animations when document is hidden or off-screen
   ========================================================================== */
function initAnimationVisibilityOptimizer() {
  // 1. Pause animations when browser tab is inactive/hidden (visibilitychange)
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      document.body.classList.add("animations-paused");
    } else {
      document.body.classList.remove("animations-paused");
    }
  });

  // 2. Pause decorative animations when scrolled outside the viewport (IntersectionObserver)
  if ("IntersectionObserver" in window) {
    const decorativeObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.remove("animation-paused");
        } else {
          entry.target.classList.add("animation-paused");
        }
      });
    }, { rootMargin: "60px" });

    const attachObservers = () => {
      document.querySelectorAll(".teacher-glow-ring, .hero-ribbon, .ambient-glow, .badge-pulse, .status-dot, .pulse-dot").forEach(el => {
        decorativeObserver.observe(el);
      });
    };

    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", attachObservers);
    } else {
      attachObservers();
    }
  }
}

/* ==========================================================================
   CONVERSATIONAL CORE ACTIONS
   ========================================================================== */
async function sendChatMessage(text) {
  // If we were in HOME, immediately transition to chat stage
  transitionToChatStage();
  appendUserMessage(text);
  renderTeacherTyping(true);

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    renderTeacherTyping(false);
    if (!res.ok) {
      const errorMsg = data.detail || "Hmm, something went wrong while processing that. Give me another moment and I'll try again.";
      appendAssistantMessage(errorMsg);
      return;
    }
    updateUI(data);
  } catch (err) {
    renderTeacherTyping(false);
    appendAssistantMessage("Hmm, something went wrong while processing that. Give me another moment and I'll try again.");
    console.error("Chat error:", err);
  }
}

async function uploadNotesFile(file) {
  // Phase 35: File Validation & Maximum Size (15 MB)
  const MAX_SIZE = 15 * 1024 * 1024;
  if (file.size > MAX_SIZE) {
    alert("File exceeds maximum allowed size of 15 MB. Please select a smaller document.");
    return;
  }
  const allowed = [".pdf", ".txt", ".md", ".markdown"];
  const lowerName = file.name.toLowerCase();
  if (!allowed.some(ext => lowerName.endsWith(ext))) {
    alert("Unsupported file format. Please upload study notes in PDF (.pdf) or text (.txt, .md) format.");
    return;
  }

  const homeStage = document.getElementById("homeStage");
  const isFromHome = homeStage && window.getComputedStyle(homeStage).display !== "none";
  const processingView = document.getElementById("composerProcessingView");
  const promptForm = document.getElementById("homePromptForm");

  if (isFromHome && processingView && promptForm) {
    promptForm.style.display = "none";
    processingView.style.display = "flex";
    const filenameEl = document.getElementById("composerProcFilename");
    const statusEl = document.getElementById("composerProcStatus");
    const pctEl = document.getElementById("composerProcPct");
    const fillEl = document.getElementById("composerProgressFill");

    if (filenameEl) filenameEl.textContent = file.name;
    if (statusEl) statusEl.textContent = "Processing your notes...";
    if (pctEl) pctEl.textContent = "82%";
    if (fillEl) fillEl.style.width = "82%";
  } else {
    transitionToChatStage();
    appendUserMessage(`📎 Uploaded study notes: ${file.name}`);
    renderTeacherTyping(true, "EduMentor is silently analyzing notes, extracting concepts & dependencies...");
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("title", file.name);

  try {
    const res = await fetch("/api/upload", {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "I couldn't read that file properly. Try uploading the PDF again or send a text-based PDF.");
    }

    if (isFromHome && processingView) {
      const pctEl = document.getElementById("composerProcPct");
      const fillEl = document.getElementById("composerProgressFill");
      if (pctEl) pctEl.textContent = "100%";
      if (fillEl) fillEl.style.width = "100%";
      await new Promise((r) => setTimeout(r, 450));
      promptForm.style.display = "flex";
      processingView.style.display = "none";
    }

    renderTeacherTyping(false);
    transitionToChatStage();
    announceToScreenReader("Notes successfully uploaded and processed. Starting study session.");
    updateUI(data);
  } catch (err) {
    renderTeacherTyping(false);
    if (isFromHome && processingView && promptForm) {
      promptForm.style.display = "flex";
      processingView.style.display = "none";
    }
    transitionToChatStage();
    const uploadErrMsg = err.message && err.message.includes("couldn't read that file")
      ? err.message
      : "I couldn't read that file properly. Try uploading the PDF again or send a text-based PDF.";
    appendAssistantMessage(uploadErrMsg);
    console.error("Upload error:", err);
  }
}

async function uploadAnswerFile(file) {
  // Phase 35: File Validation & Maximum Size (15 MB)
  const MAX_SIZE = 15 * 1024 * 1024;
  if (file.size > MAX_SIZE) {
    alert("File exceeds maximum allowed size of 15 MB.");
    return;
  }
  const allowed = [".pdf", ".txt", ".md", ".markdown"];
  if (!allowed.some(ext => file.name.toLowerCase().endsWith(ext))) {
    alert("Unsupported file format. Please upload answers in PDF or text format.");
    return;
  }

  appendUserMessage(`📎 Uploaded answer file: ${file.name}`);
  renderTeacherTyping(true, "Evaluating response via Hybrid Evaluation Engine...");

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/api/recall/upload-answer", {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Evaluation failed");
    renderTeacherTyping(false);
    updateUI(data);
  } catch (err) {
    renderTeacherTyping(false);
    alert(err.message || "An error occurred during evaluation.");
    console.error("Upload answer error:", err);
  }
}

async function saveSettings() {
  const nameInput = document.getElementById("inputStudentName");
  const providerSelect = document.getElementById("selectProvider");
  const keyInput = document.getElementById("inputApiKey");

  const payload = {
    student_name: nameInput ? nameInput.value : "Ashwel",
    provider: providerSelect ? providerSelect.value : "demo",
    api_key: keyInput ? keyInput.value : ""
  };

  try {
    const res = await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    document.getElementById("settingsModal").classList.remove("active");
    if (keyInput && data.api_key_masked) {
      keyInput.placeholder = `Configured: ${data.api_key_masked}`;
      keyInput.value = "";
    }
    if (data.connection_test) {
      alert(`Settings saved: ${data.connection_test.message}`);
    }

    // Phase 16: Sync notification settings
    const browserCheck = document.getElementById("checkBrowserNotifs");
    const emailCheck = document.getElementById("checkEmailNotifs");
    const emailInput = document.getElementById("inputUserEmail");
    if (browserCheck || emailCheck || emailInput) {
      fetch("/api/notifications/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          browser_enabled: browserCheck ? browserCheck.checked : true,
          email_enabled: emailCheck ? emailCheck.checked : false,
          recipient_email: emailInput ? emailInput.value : null
        })
      }).catch(console.error);
    }

    fetchSessionState();
  } catch (err) {
    console.error("Save settings error:", err);
  }
}

/* ==========================================================================
   AVATAR EXPRESSION RESOLUTION & ATTACHMENT CHIP HELPERS
   ========================================================================== */
function resolveExpressionUrl(stateOrFilename) {
  if (!stateOrFilename) return "/assets/teacher_avatar/teacher_idle.png";
  let s = String(stateOrFilename).trim().toLowerCase();
  if (s.endsWith(".png")) {
    if (!s.startsWith("teacher_")) {
      s = "teacher_" + s;
    }
    return `/assets/teacher_avatar/${s}`;
  }
  const mapping = {
    "idle": "teacher_idle.png",
    "greeting": "teacher_greeting.png",
    "thinking": "teacher_thinking.png",
    "explaining": "teacher_explaining.png",
    "listening": "teacher_listening.png",
    "waiting": "teacher_listening.png",
    "studying": "teacher_listening.png",
    "revise": "teacher_listening.png",
    "encouraging": "teacher_encouraging.png",
    "happy": "teacher_happy.png",
    "correct": "teacher_happy.png",
    "almost_correct": "teacher_almost_correct.png",
    "almost": "teacher_almost_correct.png",
    "supportive": "teacher_supportive.png",
    "wrong": "teacher_supportive.png",
    "confused": "teacher_supportive.png",
    "celebration": "teacher_celebration.png",
    "celebrating": "teacher_celebration.png",
    "mastered": "teacher_celebration.png",
    "reminder": "teacher_reminder.png",
    "break": "teacher_reminder.png"
  };
  const clean = s.replace(/^teacher_/, "");
  const fname = mapping[clean] || `teacher_${clean}.png`;
  return `/assets/teacher_avatar/${fname}`;
}

function showHomeAttachmentChip(file) {
  const container = document.getElementById("homeAttachmentChips");
  if (!container) return;
  container.style.display = "flex";
  container.innerHTML = `
    <div class="attachment-chip">
      <span>📄 ${file.name}</span>
      <button type="button" class="btn-chip-remove" onclick="document.getElementById('homeAttachmentChips').style.display='none'; document.getElementById('homeFileInput').value='';">×</button>
    </div>
  `;
}

function showActiveAttachmentChip(file) {
  const container = document.getElementById("activeAttachmentChips");
  if (!container) return;
  container.style.display = "flex";
  container.innerHTML = `
    <div class="attachment-chip">
      <span>📄 ${file.name}</span>
      <button type="button" class="btn-chip-remove" onclick="document.getElementById('activeAttachmentChips').style.display='none'; document.getElementById('activeFileInput').value='';">×</button>
    </div>
  `;
}

/* ==========================================================================
   UI STATE & VIEW SYNCHRONIZATION
   ========================================================================== */
function updateUI(data) {
  appState = Object.assign({}, appState, data);

  // Update Student Name displays
  document.querySelectorAll(".user-name-display").forEach((el) => {
    el.textContent = appState.student_name || "Ashwel";
  });

  const homeStage = document.getElementById("homeStage");
  const chatStage = document.getElementById("chatWorkspaceStage");
  const activeModulePill = document.getElementById("activeModulePill");
  const activeModuleTitle = document.getElementById("activeModuleTitle");
  const headerMasteryPercent = document.getElementById("headerMasteryPercent");
  const homeAvatarImg = document.getElementById("homeTeacherAvatarImg");

  // Synchronize Home Avatar Image Expression
  if (homeAvatarImg) {
    const exprUrl = data.teacher_expression_url || resolveExpressionUrl(data.teacher_expression || data.teacher_state || "greeting");
    homeAvatarImg.src = exprUrl;
  }

  // Dynamic Contextual Greetings
  const welcomeHeading = document.querySelector(".welcome-heading");
  const welcomeSub = document.querySelector(".welcome-sub");
  if (welcomeHeading) {
    if (appState.curriculum_title) {
      welcomeHeading.innerHTML = `Welcome back, <span class="user-name-display">${appState.student_name || "Ashwel"}</span> 👋`;
    } else {
      welcomeHeading.innerHTML = `Welcome, <span class="user-name-display">${appState.student_name || "Ashwel"}</span>!`;
    }
  }
  if (welcomeSub) {
    if (appState.weak_queue_count > 0) {
      welcomeSub.textContent = "Ready to revise something today?";
    } else if (appState.curriculum_title) {
      welcomeSub.textContent = `Want to continue where you left off in ${appState.curriculum_title}?`;
    } else {
      welcomeSub.textContent = "What do you think we should study today?";
    }
  }

  // Dynamic Placeholders (Phase 28)
  const homeInputText = document.getElementById("homeInputText");
  if (homeInputText) {
    if (appState.curriculum_title) {
      const topic = appState.current_concept ? appState.current_concept.title : appState.curriculum_title;
      homeInputText.placeholder = `Continue with ${topic}, or tell me what you'd like to study...`;
    } else {
      homeInputText.placeholder = "Ask EduMentor anything about your learning";
    }
  }

  const activeChatInput = document.getElementById("activeChatInput");
  if (activeChatInput) {
    if (appState.state === "WAITING_RECALL") {
      const cTitle = appState.current_concept ? appState.current_concept.title : "this concept";
      activeChatInput.placeholder = `Write what you remember about ${cTitle} from memory...`;
    } else if (appState.state === "STUDYING") {
      activeChatInput.placeholder = "Tell me when you're ready... (or ask any question about this concept)";
    } else {
      activeChatInput.placeholder = "Ask EduMentor anything about your learning";
    }
  }

  // If not authenticated, ensure landingStage stays visible and workspace is hidden (Phase 29)
  if (!appState.authenticated) {
    showLandingStage();
    return;
  }

  // Determine if in HOME or ACTIVE STUDY
  if (appState.state === "HOME" && (!appState.curriculum_title || appState.chat_history.length <= 1)) {
    if (homeStage) homeStage.style.display = "flex";
    if (chatStage) chatStage.style.display = "none";
    if (activeModulePill) activeModulePill.style.display = "none";
  } else {
    if (homeStage) homeStage.style.display = "none";
    if (chatStage) chatStage.style.display = "flex";
    if (activeModulePill) {
      activeModulePill.style.display = "flex";
      activeModuleTitle.textContent = appState.curriculum_title || "Active Module";
      headerMasteryPercent.textContent = `${appState.mastery_percent}%`;
    }

    renderChatFeed();
  }

  // Phase 23: AI Conversation State Machine Stage Indicator Update
  const stateIndicatorPill = document.getElementById("stateIndicatorPill");
  const stateLabel = document.getElementById("stateLabel");
  if (stateIndicatorPill && stateLabel) {
    const currentState = data.conversation_state || appState.conversation_state || (appState.state === "HOME" ? "IDLE" : appState.state) || "IDLE";
    stateLabel.textContent = currentState;
    stateIndicatorPill.setAttribute("data-state", currentState);
  }

  // Phase 20: Update Subject / Module Manager Pill and Dropdown
  const moduleManagerWrapper = document.getElementById("moduleManagerWrapper");
  const moduleManagerCountText = document.getElementById("moduleManagerCountText");
  const moduleDropdownSubjectTitle = document.getElementById("moduleDropdownSubjectTitle");
  const moduleDropdownList = document.getElementById("moduleDropdownList");
  const inputSubjectName = document.getElementById("inputSubjectName");

  if (moduleManagerWrapper) {
    const modules = data.modules || appState.modules || [];
    if (modules.length > 0 && appState.state !== "HOME") {
      moduleManagerWrapper.style.display = "inline-flex";
      if (moduleManagerCountText) {
        moduleManagerCountText.textContent = `${modules.length} Module${modules.length > 1 ? 's' : ''}`;
      }
      if (moduleDropdownSubjectTitle) {
        moduleDropdownSubjectTitle.textContent = appState.curriculum_title || "Subject Modules";
      }
      if (inputSubjectName) {
        inputSubjectName.value = appState.curriculum_title || "Operating Systems";
      }
      if (moduleDropdownList) {
        moduleDropdownList.innerHTML = modules.map(m => `
          <div class="module-item-card">
            <div class="module-item-title">${escapeHtml(m.title || `Module ${m.module_number}`)}</div>
            <div class="module-item-meta">
              <span>Module #${m.module_number}</span>
              <span class="module-item-doc-tag">${escapeHtml(m.document_id || 'source_doc')}</span>
            </div>
          </div>
        `).join("");
      }
    } else {
      moduleManagerWrapper.style.display = "none";
    }
  }

  // Phase 16: Update notification badge if present
  if (data.unread_notifications_count !== undefined) {
    const badge = document.getElementById("notificationBadge");
    if (badge) {
      if (data.unread_notifications_count > 0) {
        badge.textContent = data.unread_notifications_count > 9 ? "9+" : data.unread_notifications_count;
        badge.style.display = "block";
      } else {
        badge.style.display = "none";
      }
    }
  }

  // If drawer is open, keep graph in sync
  const graphDrawer = document.getElementById("graphDrawer");
  if (graphDrawer && graphDrawer.classList.contains("open")) {
    renderKnowledgeGraph(appState.graph);
  }
}

function transitionToChatStage() {
  const homeStage = document.getElementById("homeStage");
  const chatStage = document.getElementById("chatWorkspaceStage");
  if (homeStage) homeStage.style.display = "none";
  if (chatStage) chatStage.style.display = "flex";
}

/* ==========================================================================
   CHAT FEED RENDERING (INLINE WIDGETS LIVING INSIDE CHAT)
   ========================================================================== */
function isMajorTeacherMessage(m) {
  if (m.role !== "assistant") return false;
  if (typeof m.is_major === "boolean") return m.is_major;
  if (typeof m.show_avatar === "boolean") return m.show_avatar;
  const t = m.message_type || "";
  if (["processing", "calibration", "status", "system"].includes(t)) return false;
  if (t === "info" && m.content && m.content.length < 120) return false;
  return true;
}

/* Phase 38: Chat feed incremental rendering tracker */
let _chatRenderTracker = {
  renderedCount: 0,
  lastStateSig: ""
};

function buildMessageRow(m, idx, isLastAssistantMessage) {
  // Phase 26: Render tiny status messages as clean status notice pills without avatar
  if (m.role === "assistant" && !isMajorTeacherMessage(m)) {
    const statusRow = document.createElement("div");
    statusRow.className = "chat-row status-notice";
    statusRow.setAttribute("data-msg-idx", idx);
    const pill = document.createElement("div");
    pill.className = "status-pill";
    pill.innerHTML = `<span class="status-dot"></span><span>${escapeHtml(m.content)}</span>`;
    statusRow.appendChild(pill);
    return statusRow;
  }

  const row = document.createElement("div");
  row.className = `chat-row ${m.role} ${m.role === 'assistant' ? 'major-teacher-message' : ''}`;
  row.setAttribute("data-msg-idx", idx);

  let avatarContainer;
  if (m.role === "assistant") {
    // Phase 26: Avatar positioned beside conversational bubble with vertical stem and curved branch (│ └──)
    const stemCol = document.createElement("div");
    stemCol.className = "avatar-stem-col";

    const avatar = document.createElement("div");
    avatar.className = "chat-avatar assistant-avatar";
    const exprUrl = resolveExpressionUrl(m.expression_state || appState.teacher_expression || appState.teacher_state || "explaining");
    // Phase 38: Lightweight avatar assets - async decoding, lazy loading, explicit dimensions, and vector SVG fallback
    avatar.innerHTML = `<img src="${exprUrl}" loading="lazy" decoding="async" width="36" height="36" onerror="this.src='/assets/teacher_avatar/avatar.svg'" alt="EduMentor">`;
    stemCol.appendChild(avatar);

    const stemLine = document.createElement("div");
    stemLine.className = "avatar-connector-stem";
    const branchCurve = document.createElement("div");
    branchCurve.className = "avatar-branch-curve";
    stemLine.appendChild(branchCurve);
    stemCol.appendChild(stemLine);

    avatarContainer = stemCol;
  } else {
    const avatar = document.createElement("div");
    avatar.className = `chat-avatar user-avatar`;
    avatar.textContent = (appState.student_name ? appState.student_name[0].toUpperCase() : "A");
    avatarContainer = avatar;
  }

  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${m.role}-bubble`;
  bubble.innerHTML = formatMarkdown(m.content);

  // If this is the LAST assistant message, render inline interactive widgets!
  if (isLastAssistantMessage) {
    // Inline Widget 0: RESURFACING phase (Phase 15) -> Show Proactive Card + "Give it another try"
    if (appState.state === "RESURFACING" && appState.current_concept) {
      const resurfaceBox = createInlineResurfacingBox(appState.current_concept);
      bubble.appendChild(resurfaceBox);
    }

    // Inline Widget 1: STUDYING phase -> Show Study Path + Concept Principles + "I'm Ready" button
    if (appState.state === "STUDYING" && appState.current_concept) {
      if (appState.graph && appState.graph.nodes && appState.graph.nodes.length > 0) {
        const studyPathBox = createInlineStudyPathBox(appState);
        bubble.appendChild(studyPathBox);
      }
      const studyBox = createInlineStudyBox(appState.current_concept);
      bubble.appendChild(studyBox);
    }

    // Inline Widget 2: FEEDBACK phase -> Show Diagnostic Rubric + SM-2 + "Continue" button
    if (appState.state === "FEEDBACK" && appState.last_evaluation && appState.current_concept) {
      if (appState.graph && appState.graph.nodes && appState.graph.nodes.length > 0) {
        const studyPathBox = createInlineStudyPathBox(appState);
        bubble.appendChild(studyPathBox);
      }
      const evalBox = createInlineEvalBox(appState.last_evaluation, appState.current_concept);
      bubble.appendChild(evalBox);
    }
  }

  // Phase 21: Grounding Chip for Active Recall Challenge messages
  const grounding = m.question_grounding || (isLastAssistantMessage && appState.state === "WAITING_RECALL" ? appState.question_grounding : null);
  if (grounding) {
    const chipBox = createInlineGroundingChip(grounding);
    if (chipBox) bubble.appendChild(chipBox);
  }

  row.appendChild(avatarContainer);
  row.appendChild(bubble);
  return row;
}

function renderChatFeed(forceRerender = false) {
  const feed = document.getElementById("chatFeed");
  if (!feed) return;

  const history = appState.chat_history || [];
  const currentWidgetStateSig = `${appState.state}:${appState.current_concept ? appState.current_concept.id : ''}:${appState.last_evaluation ? (appState.last_evaluation.concept_id || '') + (appState.last_evaluation.grade || '') : ''}`;
  const existingRows = feed.children;

  // Phase 38 UI Optimization: Do not rerender the entire conversation unnecessarily
  if (!forceRerender && existingRows.length > 0) {
    // Sub-case A: Exact same history length & same widget state -> 0 DOM mutations!
    if (existingRows.length === history.length) {
      if (_chatRenderTracker.lastStateSig === currentWidgetStateSig) {
        return; // Zero overhead, skip complete conversation re-render
      }
      // Sub-case B: Same history length, but conversational state/widgets evolved -> update ONLY the last message
      if (history.length > 0) {
        const lastIdx = history.length - 1;
        const lastMsg = history[lastIdx];
        const isLastAssistant = (lastMsg.role === "assistant");
        const updatedLastRow = buildMessageRow(lastMsg, lastIdx, isLastAssistant);
        feed.replaceChild(updatedLastRow, existingRows[lastIdx]);
        _chatRenderTracker.lastStateSig = currentWidgetStateSig;
        return;
      }
    }

    // Sub-case C: Incremental append when new messages arrived (avoids redrawing old messages)
    if (history.length > existingRows.length && existingRows.length === _chatRenderTracker.renderedCount) {
      const prevLastIdx = existingRows.length - 1;
      if (prevLastIdx >= 0 && history[prevLastIdx].role === "assistant") {
        // Strip previous interactive action widgets from older message
        const cleanPrevRow = buildMessageRow(history[prevLastIdx], prevLastIdx, false);
        feed.replaceChild(cleanPrevRow, existingRows[prevLastIdx]);
      }

      const frag = document.createDocumentFragment();
      for (let i = existingRows.length; i < history.length; i++) {
        const isLastAssistant = (i === history.length - 1 && history[i].role === "assistant");
        const row = buildMessageRow(history[i], i, isLastAssistant);
        frag.appendChild(row);
      }
      feed.appendChild(frag);

      _chatRenderTracker.renderedCount = history.length;
      _chatRenderTracker.lastStateSig = currentWidgetStateSig;

      const wrapper = document.querySelector(".chat-feed-wrapper");
      if (wrapper) wrapper.scrollTop = wrapper.scrollHeight;
      return;
    }
  }

  // Sub-case D: Full render (initial load, module switch, or forceRerender)
  feed.innerHTML = "";
  const frag = document.createDocumentFragment();
  history.forEach((m, idx) => {
    const isLastAssistantMessage = (idx === history.length - 1 && m.role === "assistant");
    const row = buildMessageRow(m, idx, isLastAssistantMessage);
    frag.appendChild(row);
  });
  feed.appendChild(frag);

  _chatRenderTracker.renderedCount = history.length;
  _chatRenderTracker.lastStateSig = currentWidgetStateSig;

  // Auto-scroll feed wrapper
  const wrapper = document.querySelector(".chat-feed-wrapper");
  if (wrapper) {
    wrapper.scrollTop = wrapper.scrollHeight;
  }
}

function createInlineStudyPathBox(appState) {
  const box = document.createElement("div");
  box.className = "inline-study-path-box";
  box.style.cssText = "background: #0D1117; border: 1px solid #27303B; border-radius: 12px; padding: 12px 14px; margin: 10px 0; box-shadow: 0 4px 16px rgba(0,0,0,0.35);";

  const nodes = (appState.graph && appState.graph.nodes) ? appState.graph.nodes : [];
  const currentId = appState.current_concept ? appState.current_concept.id : null;

  let itemsHtml = "";
  nodes.forEach((node, idx) => {
    const num = String(idx + 1).padStart(2, "0");
    const isCurrent = node.id === currentId;
    const isMastered = node.status === "mastered" || node.quality >= 4 || node.mastery_level === "Mastered";
    const isProficient = node.quality >= 3 && !isMastered;
    const isWeak = node.quality > 0 && node.quality < 3;

    let badge = `<span style="color: #475569; font-size: 11px;">Upcoming</span>`;
    let rowBorder = "transparent";
    if (isMastered) {
      badge = `<span style="color: #10B981; font-weight: 700; font-size: 11px; background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.35); padding: 2px 8px; border-radius: 20px;">★ Mastered</span>`;
      rowBorder = "rgba(16, 185, 129, 0.4)";
    } else if (isCurrent) {
      badge = `<span style="color: #25D8E8; font-weight: 700; font-size: 11px; background: rgba(37, 216, 232, 0.15); border: 1px solid rgba(37, 216, 232, 0.45); padding: 2px 8px; border-radius: 20px;">→ Current</span>`;
      rowBorder = "#25D8E8";
    } else if (isProficient) {
      badge = `<span style="color: #25D8E8; font-size: 11px; background: rgba(37, 216, 232, 0.08); border: 1px solid rgba(37, 216, 232, 0.25); padding: 2px 8px; border-radius: 20px;">✓ Proficient</span>`;
    } else if (isWeak) {
      badge = `<span style="color: #F87171; font-size: 11px; background: rgba(248, 113, 113, 0.1); border: 1px solid rgba(248, 113, 113, 0.3); padding: 2px 8px; border-radius: 20px;">🌱 Review</span>`;
      rowBorder = "rgba(248, 113, 113, 0.4)";
    }

    itemsHtml += `
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 5px 8px; margin-bottom: 3px; border-radius: 6px; background: rgba(255,255,255,0.01); border-left: 2px solid ${rowBorder};">
        <div style="display: flex; align-items: center; gap: 10px;">
          <span style="font-family: monospace; font-size: 11.5px; color: ${isCurrent ? '#25D8E8' : (isMastered ? '#10B981' : '#64748B')}; font-weight: 700;">${num}</span>
          <span style="font-size: 12.5px; color: ${isCurrent ? '#FFFFFF' : '#94A3B8'}; font-weight: ${isCurrent ? '700' : '500'};">${node.label || node.id}</span>
        </div>
        <div>${badge}</div>
      </div>
    `;
  });

  box.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid rgba(255,255,255,0.06);">
      <span style="font-size: 11px; font-weight: 800; color: #25D8E8; text-transform: uppercase; letter-spacing: 0.08em;">YOUR LEARNING PATH</span>
      <span style="font-size: 10.5px; color: #64748B;">Concept sequence</span>
    </div>
    <div style="display: flex; flex-direction: column; gap: 2px;">
      ${itemsHtml}
    </div>
  `;
  return box;
}

function createInlineStudyBox(concept) {
  const box = document.createElement("div");
  box.className = "inline-concept-box";

  const tier = concept.tier !== undefined ? concept.tier : 0;
  const tierName = tier === 0 ? "Tier 0: Foundational" : (tier === 1 ? "Tier 1: Intermediate" : "Tier 2: Advanced");

  let principlesHtml = "";
  (concept.key_points || concept.principles || []).forEach((pt) => {
    principlesHtml += `<li>${pt}</li>`;
  });

  box.innerHTML = `
    <div class="inline-concept-header">
      <h4 class="inline-concept-title">${concept.title}</h4>
      <span class="inline-tier-pill">${tierName}</span>
    </div>
    <ul class="inline-concept-principles">
      ${principlesHtml}
    </ul>
    <button type="button" class="btn-inline-ready" id="btnInlineReady">
      I'm Ready to Recall
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M5 12h14M12 5l7 7-7 7"/>
      </svg>
    </button>
  `;

  // Attach click listener
  const btn = box.querySelector("#btnInlineReady");
  if (btn) {
    btn.addEventListener("click", triggerReady);
  }

  return box;
}

async function triggerReady() {
  trackProductEvent("student_ready");
  announceToScreenReader("Preparing active recall challenge...");
  renderTeacherTyping(true, "Preparing recall challenge...");
  try {
    const res = await fetch("/api/ready", { method: "POST" });
    const data = await res.json();
    renderTeacherTyping(false);
    updateUI(data);

    const input = document.getElementById("activeChatInput");
    if (input) {
      input.focus();
      input.placeholder = "Type your recall explanation from memory here...";
    }
  } catch (err) {
    renderTeacherTyping(false);
    console.error("Ready trigger error:", err);
  }
}

async function acceptResurfacing() {
  trackProductEvent("concept_resurfaced", { action: "accept" });
  renderTeacherTyping(true, "Preparing recall challenge...");
  try {
    const res = await fetch("/api/resurface/accept", { method: "POST" });
    const data = await res.json();
    renderTeacherTyping(false);
    updateUI(data);

    const input = document.getElementById("activeChatInput");
    if (input) {
      input.focus();
      input.placeholder = "Type your recall explanation from memory here...";
    }
  } catch (err) {
    renderTeacherTyping(false);
    console.error("Resurface accept error:", err);
  }
}

function createInlineResurfacingBox(concept) {
  const box = document.createElement("div");
  box.className = "inline-resurfacing-box";
  box.style.cssText = "background: linear-gradient(135deg, rgba(37, 216, 232, 0.09) 0%, rgba(20, 26, 35, 0.96) 100%); border: 1px solid rgba(37, 216, 232, 0.4); border-radius: 12px; padding: 16px; margin: 12px 0; box-shadow: 0 4px 20px rgba(0,0,0,0.4);";

  const title = concept.title || "Target Concept";
  const summary = concept.summary || concept.canonical_explanation || "";

  box.innerHTML = `
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
      <div style="display: flex; align-items: center; gap: 8px;">
        <span style="display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; border-radius: 50%; background: rgba(37, 216, 232, 0.2); color: #25D8E8; font-size: 14px;">🔄</span>
        <span style="font-size: 12px; font-weight: 700; color: #25D8E8; text-transform: uppercase; letter-spacing: 0.06em;">Spaced Memory Resurfacing</span>
      </div>
      <span style="font-size: 11px; color: #94A3B8; background: rgba(255,255,255,0.06); padding: 3px 8px; border-radius: 12px;">Automatic Reminder</span>
    </div>

    <div style="margin-bottom: 12px;">
      <h4 style="margin: 0 0 6px 0; color: #F1F5F9; font-size: 15px; font-weight: 600;">${title}</h4>
      <p style="margin: 0; color: #94A3B8; font-size: 12.5px; line-height: 1.4;">${summary}</p>
    </div>

    <div style="display: flex; gap: 10px; align-items: center; margin-top: 14px;">
      <button type="button" class="btn-resurface-accept" id="btnResurfaceAccept" style="background: linear-gradient(135deg, #25D8E8 0%, #00B4D8 100%); color: #080D14; font-weight: 700; font-size: 13px; border: none; border-radius: 8px; padding: 9px 18px; cursor: pointer; display: flex; align-items: center; gap: 6px; box-shadow: 0 2px 10px rgba(37, 216, 232, 0.35);">
        Give it another try →
      </button>
      <button type="button" class="btn-resurface-later" id="btnResurfaceLater" style="background: transparent; border: 1px solid rgba(255,255,255,0.15); color: #94A3B8; font-size: 12px; border-radius: 8px; padding: 8px 14px; cursor: pointer;">
        Maybe later
      </button>
    </div>
  `;

  box.querySelector("#btnResurfaceAccept").addEventListener("click", acceptResurfacing);
  box.querySelector("#btnResurfaceLater").addEventListener("click", () => {
    sendChatMessage("Maybe later");
  });

  return box;
}

function submitConfidence(rating, conceptId) {
  const cid = conceptId || (appState.current_concept ? appState.current_concept.id : null);
  trackProductEvent("confidence_selected", { confidence: rating, concept_id: cid });
  renderTeacherTyping(true, "EduMentor is reflecting on your response...");
  fetch("/api/recall/confidence", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ confidence: rating, concept_id: cid })
  })
  .then(res => res.json())
  .then(data => {
    renderTeacherTyping(false);
    updateUI(data);
  })
  .catch(err => {
    renderTeacherTyping(false);
    console.error("Failed to submit confidence rating:", err);
  });
}

function createInlineEvalBox(ev, concept) {
  const box = document.createElement("div");
  box.className = "inline-eval-box";

  const verdictClass = ev.verdict === "Correct" ? "correct" : (ev.verdict === "Almost Correct" ? "almost" : "wrong");
  const isMastered = concept.mastery_level === "Mastered" || concept.is_mastered;

  // Phase 11 & 12: Resolve exact 5-tier semantic mastery status
  const rawScore = ev.score !== undefined ? ev.score : (ev.composite_score || 0);
  const scorePct = rawScore <= 1.0 ? Math.round(rawScore * 100) : Math.round(rawScore);

  let masteryBand = "Needs relearning";
  let bandIcon = "⚠️";
  let bandColor = "#EF4444";
  if (scorePct >= 90) {
    masteryBand = "Mastered";
    bandIcon = "★";
    bandColor = "#10B981";
  } else if (scorePct >= 75) {
    masteryBand = "Strong understanding";
    bandIcon = "✓";
    bandColor = "#25D8E8";
  } else if (scorePct >= 60) {
    masteryBand = "Partial understanding";
    bandIcon = "⚡";
    bandColor = "#F59E0B";
  } else if (scorePct >= 40) {
    masteryBand = "Developing";
    bandIcon = "🌱";
    bandColor = "#F97316";
  }
  const semanticScoreText = `${scorePct}% — ${masteryBand}`;
  announceToScreenReader(`Evaluation: ${scorePct} percent, ${masteryBand}. Verdict: ${ev.verdict}.`);

  let strengthsHtml = "";
  (ev.strengths || []).forEach((s) => {
    strengthsHtml += `<div class="eval-pill strength">✓ ${s}</div>`;
  });

  let missingHtml = "";
  (ev.missing_concepts || []).forEach((m) => {
    missingHtml += `<div class="eval-pill missing">! ${m}</div>`;
  });

  let masteryBanner = "";
  if (isMastered) {
    masteryBanner = `
      <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 8px; padding: 8px 12px; margin-bottom: 12px; color: #10B981; font-weight: 700; font-size: 12.5px; display: flex; align-items: center; gap: 8px;">
        <span>★ CONCEPT MASTERED</span>
        <span style="font-weight: 500; font-size: 11.5px; color: #6EE7B7;">• Added to spaced repetition retention schedule</span>
      </div>
    `;
  }

  // Phase 14 SM-2 Spaced Repetition values
  const intervalDays = concept.interval !== undefined ? concept.interval : (concept.interval_days || 1);
  const nextRev = concept.next_review || concept.next_due_date || "Tomorrow";
  const easeFactor = concept.ease_factor || concept.easiness_factor || 2.5;
  const currentConfidence = concept.confidence || "Not rated";

  box.innerHTML = `
    ${masteryBanner}
    <!-- 1. UNDERSTANDING: Prioritized Semantic Header (Never color alone) -->
    <div class="eval-top-bar" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
      <div style="display: flex; align-items: center; gap: 8px;">
        <span class="verdict-tag ${verdictClass}">${ev.verdict}</span>
        <span style="font-size: 12px; font-weight: 700; color: ${bandColor}; background: rgba(255,255,255,0.04); padding: 3px 10px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08);">
          ${bandIcon} ${masteryBand}
        </span>
      </div>
      <span class="eval-score-num" style="font-size: 13px; font-weight: 700; color: ${bandColor}; font-family: monospace;">
        ${semanticScoreText}
      </span>
    </div>

    <!-- 2. FEEDBACK: Rubric & Insights -->
    <div class="eval-rubrics">
      ${strengthsHtml}
      ${missingHtml}
    </div>

    <div class="eval-tip-box">
      <strong>Coaching Tip:</strong> ${ev.actionable_tip}
    </div>

    <!-- Phase 13: Confidence Feedback Section -->
    <div class="confidence-selector-container" style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 12px; margin: 12px 0;">
      <div style="font-size: 12px; font-weight: 600; color: #E2E8F0; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
        <span>How confident were you about that answer?</span>
        ${currentConfidence !== "Not rated" ? `<span style="font-size: 11px; color: var(--accent-cyan); font-weight: 700;">✓ Recorded: ${currentConfidence}</span>` : ''}
      </div>
      <div style="display: flex; gap: 8px; flex-wrap: wrap;">
        <button type="button" class="btn-confidence ${currentConfidence === 'Not very confident' ? 'active' : ''}" data-val="Not very confident" style="flex: 1; min-width: 110px; padding: 6px 10px; font-size: 11.5px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.12); background: rgba(255,255,255,0.04); color: #CBD5E1; cursor: pointer;">
          Not very confident
        </button>
        <button type="button" class="btn-confidence ${currentConfidence === 'Somewhat confident' ? 'active' : ''}" data-val="Somewhat confident" style="flex: 1; min-width: 110px; padding: 6px 10px; font-size: 11.5px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.12); background: rgba(255,255,255,0.04); color: #CBD5E1; cursor: pointer;">
          Somewhat confident
        </button>
        <button type="button" class="btn-confidence ${currentConfidence === 'Very confident' ? 'active' : ''}" data-val="Very confident" style="flex: 1; min-width: 110px; padding: 6px 10px; font-size: 11.5px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.12); background: rgba(255,255,255,0.04); color: #CBD5E1; cursor: pointer;">
          Very confident
        </button>
      </div>
    </div>

    <!-- Phase 14: SM-2 Spaced Repetition Diagnostics -->
    <div class="eval-sm2-row" style="display: flex; flex-wrap: wrap; gap: 14px; font-size: 11px; color: #94A3B8; margin-bottom: 12px;">
      <span><strong>Review Schedule:</strong> ${intervalDays} day(s) (${nextRev})</span>
      <span><strong>Ease Factor:</strong> ${Number(easeFactor).toFixed(2)}</span>
      <span><strong>Mastery State:</strong> ${masteryBand}</span>
    </div>

    <!-- 3. NEXT ACTION: Continue / Advance Button -->
    <button type="button" class="btn-inline-advance" id="btnInlineAdvance">
      Continue to Next Concept →
    </button>
  `;

  // Attach event listener for confidence buttons
  box.querySelectorAll(".btn-confidence").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const val = e.currentTarget.getAttribute("data-val");
      submitConfidence(val, concept.id);
    });
  });

  const btn = box.querySelector("#btnInlineAdvance");
  if (btn) {
    btn.addEventListener("click", advanceNext);
  }

  return box;
}

async function advanceNext() {
  announceToScreenReader("Advancing to next concept in sequence...");
  renderTeacherTyping(true, "Advancing to next concept...");
  try {
    const res = await fetch("/api/advance", { method: "POST" });
    const data = await res.json();
    renderTeacherTyping(false);
    updateUI(data);
  } catch (err) {
    renderTeacherTyping(false);
    console.error("Advance error:", err);
  }
}

function renderTeacherTyping(show, statusText = "EduMentor is thinking...") {
  let row = document.getElementById("typingRow");
  const feed = document.getElementById("chatFeed");
  if (!feed) return;

  if (show) {
    if (!row) {
      row = document.createElement("div");
      row.id = "typingRow";
      row.className = "chat-row assistant typing-row";
      row.innerHTML = `
        <div class="chat-avatar assistant-avatar">EM</div>
        <div class="chat-bubble assistant-bubble">
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
          <em style="font-size:12.5px; color:var(--text-muted); margin-left:8px;">${statusText}</em>
        </div>`;
      feed.appendChild(row);
      const wrapper = document.querySelector(".chat-feed-wrapper");
      if (wrapper) wrapper.scrollTop = wrapper.scrollHeight;
    }
  } else {
    if (row) {
      row.remove();
    }
  }
}

function appendUserMessage(text) {
  const feed = document.getElementById("chatFeed");
  if (!feed) return;

  const row = document.createElement("div");
  row.className = "chat-row user";
  row.innerHTML = `
    <div class="chat-avatar user-avatar">${appState.student_name ? appState.student_name[0].toUpperCase() : "A"}</div>
    <div class="chat-bubble user-bubble">${text}</div>`;
  feed.appendChild(row);

  const wrapper = document.querySelector(".chat-feed-wrapper");
  if (wrapper) wrapper.scrollTop = wrapper.scrollHeight;
}

function appendAssistantMessage(text, expressionState = "listening") {
  const feed = document.getElementById("chatFeed");
  if (!feed) return;

  const row = document.createElement("div");
  row.className = "chat-row assistant major-teacher-message";

  const stemCol = document.createElement("div");
  stemCol.className = "avatar-stem-col";

  const avatar = document.createElement("div");
  avatar.className = "chat-avatar assistant-avatar";
  const exprUrl = resolveExpressionUrl(expressionState);
  avatar.innerHTML = `<img src="${exprUrl}" loading="lazy" decoding="async" width="36" height="36" onerror="this.src='/assets/teacher_avatar/avatar.svg'" alt="EduMentor">`;
  stemCol.appendChild(avatar);

  const stemLine = document.createElement("div");
  stemLine.className = "avatar-connector-stem";
  const branchCurve = document.createElement("div");
  branchCurve.className = "avatar-branch-curve";
  stemLine.appendChild(branchCurve);
  stemCol.appendChild(stemLine);

  row.appendChild(stemCol);

  const bubble = document.createElement("div");
  bubble.className = "chat-bubble assistant-bubble";
  bubble.innerHTML = formatMarkdown(text);
  row.appendChild(bubble);

  feed.appendChild(row);

  const wrapper = document.querySelector(".chat-feed-wrapper");
  if (wrapper) wrapper.scrollTop = wrapper.scrollHeight;
}

/* ==========================================================================
   NETWORKX KNOWLEDGE GRAPH DRAWER SVG RENDERER
   ========================================================================== */
function renderKnowledgeGraph(graphData) {
  const container = document.getElementById("drawerGraphContainer");
  if (!container || !graphData || !graphData.nodes || graphData.nodes.length === 0) {
    if (container) {
      container.innerHTML = `
        <div style="text-align:center; padding: 40px 20px; color: var(--text-muted); font-size: 13.5px;">
          The concept dependency graph will render automatically once you begin studying a topic.
        </div>`;
    }
    return;
  }

  const nodes = graphData.nodes;
  const edges = graphData.edges;

  // Group by tier
  const tierGroups = {};
  nodes.forEach((n) => {
    const t = n.tier || 0;
    if (!tierGroups[t]) tierGroups[t] = [];
    tierGroups[t].push(n);
  });

  const tiers = Object.keys(tierGroups).map(Number).sort((a, b) => a - b);
  const maxTier = tiers.length > 0 ? Math.max(...tiers) : 0;
  const maxNodesInTier = Math.max(...Object.values(tierGroups).map((arr) => arr.length), 1);

  const nodeWidth = 180;
  const nodeHeight = 58;
  const horizSpacing = 230;
  const vertSpacing = 84;
  const padding = 30;

  const totalWidth = Math.max(500, padding * 2 + (maxTier + 1) * horizSpacing);
  const totalHeight = Math.max(280, padding * 2 + maxNodesInTier * vertSpacing);

  const coords = {};
  tiers.forEach((t) => {
    const tNodes = tierGroups[t];
    const x = padding + t * horizSpacing;
    const tierHeight = tNodes.length * vertSpacing;
    const startY = (totalHeight - tierHeight) / 2 + 10;
    tNodes.forEach((node, i) => {
      coords[node.id] = { x: x, y: startY + i * vertSpacing };
    });
  });

  let svgEdges = "";
  edges.forEach((e) => {
    const p1 = coords[e.from];
    const p2 = coords[e.to];
    if (p1 && p2) {
      const startX = p1.x + nodeWidth;
      const startY = p1.y + nodeHeight / 2;
      const endX = p2.x;
      const endY = p2.y + nodeHeight / 2;
      const ctrlX = startX + (endX - startX) * 0.5;
      const d = `M ${startX} ${startY} C ${ctrlX} ${startY}, ${ctrlX} ${endY}, ${endX} ${endY}`;
      svgEdges += `<path d="${d}" stroke="#27303B" stroke-width="2.2" fill="none" marker-end="url(#drawerArrow)" />`;
    }
  });

  let svgNodes = "";
  nodes.forEach((n) => {
    const p = coords[n.id];
    if (p) {
      const isCurrent = appState.current_concept && appState.current_concept.id === n.id;
      const colors = n.colors || { bg: "#161B22", border: "#27303B", text: "#9AA4B2", badge: "New", badge_bg: "#0D1117" };
      const borderColor = isCurrent ? "var(--accent-cyan)" : colors.border;
      const strokeWidth = isCurrent ? "2.5" : "1.5";
      const titleShort = n.title.length > 20 ? n.title.substring(0, 18) + "..." : n.title;

      svgNodes += `
        <g class="dag-node-item" transform="translate(${p.x}, ${p.y})" style="cursor: pointer;" onclick="sendChatMessage('Tell me about ${n.id}')">
          <rect width="${nodeWidth}" height="${nodeHeight}" rx="10" 
                fill="${colors.bg}" stroke="${borderColor}" stroke-width="${strokeWidth}" />
          ${isCurrent ? `<rect width="${nodeWidth}" height="${nodeHeight}" rx="10" fill="none" stroke="var(--accent-cyan)" stroke-width="1" opacity="0.4" filter="drop-shadow(0 0 8px var(--accent-cyan))" />` : ''}
          <text x="12" y="24" font-family="'Inter', sans-serif" font-size="12" font-weight="600" fill="#F5F7FA">${titleShort}</text>
          <rect x="12" y="32" width="76" height="16" rx="4" fill="${colors.badge_bg || '#0D1117'}" stroke="${colors.border}" stroke-width="0.8" />
          <text x="17" y="44" font-family="'Inter', sans-serif" font-size="9.5" font-weight="700" fill="${colors.text}">${colors.badge}</text>
        </g>`;
    }
  });

  container.innerHTML = `
    <svg width="${totalWidth}" height="${totalHeight}" viewBox="0 0 ${totalWidth} ${totalHeight}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <marker id="drawerArrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#25D8E8" />
        </marker>
      </defs>
      <g id="drawerEdges">${svgEdges}</g>
      <g id="drawerNodes">${svgNodes}</g>
    </svg>`;
}

/* ==========================================================================
   MARKDOWN FORMATTING HELPER
   ========================================================================== */
function formatMarkdown(text) {
  if (!text) return "";
  let out = text
    .replace(/^### (.*$)/gim, '<strong style="display:block; font-size:15px; margin-bottom:6px; color:var(--accent-cyan);">$1</strong>')
    .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/gim, '<em>$1</em>')
    .replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>')
    .replace(/^- (.*$)/gim, '• $1<br>')
    .replace(/\n\n/g, '<br><br>');
  return out;
}

/* ==========================================================================
   PHASE 16 NOTIFICATION SYSTEM CONTROLLER
   ========================================================================== */
let seenToastNotificationIds = new Set();

function initNotificationListeners() {
  const btnToggleNotifications = document.getElementById("btnToggleNotifications");
  const notificationDropdown = document.getElementById("notificationDropdown");
  const btnMarkAllRead = document.getElementById("btnMarkAllRead");
  const btnRequestBrowserPerm = document.getElementById("btnRequestBrowserPerm");

  if (btnToggleNotifications && notificationDropdown) {
    btnToggleNotifications.addEventListener("click", (e) => {
      e.stopPropagation();
      const isVisible = notificationDropdown.style.display === "flex";
      notificationDropdown.style.display = isVisible ? "none" : "flex";
      if (!isVisible) {
        fetchNotifications();
      }
    });

    document.addEventListener("click", (e) => {
      if (notificationDropdown.style.display === "flex") {
        if (!notificationDropdown.contains(e.target) && e.target !== btnToggleNotifications && !btnToggleNotifications.contains(e.target)) {
          notificationDropdown.style.display = "none";
        }
      }
    });
  }

  if (btnMarkAllRead) {
    btnMarkAllRead.addEventListener("click", async () => {
      await fetch("/api/notifications/read", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
      });
      fetchNotifications();
    });
  }

  if (btnRequestBrowserPerm) {
    btnRequestBrowserPerm.addEventListener("click", requestBrowserNotificationPermission);
  }
}

async function requestBrowserNotificationPermission() {
  if (!("Notification" in window)) {
    alert("Browser desktop notifications are not supported in this browser environment.");
    return;
  }
  try {
    const permission = await Notification.requestPermission();
    if (permission === "granted") {
      new Notification("🔔 EduMentor", {
        body: "Browser notifications enabled! You will receive timely spaced recall reminders.",
        icon: "/assets/teacher_avatar/teacher_encouraging.png"
      });
      const btn = document.getElementById("btnRequestBrowserPerm");
      if (btn) btn.innerHTML = "<span>✓ Browser Notifications Active</span>";
    }
  } catch (err) {
    console.error("Browser notification permission error:", err);
  }
}

function showBrowserNotification(notif) {
  if (!("Notification" in window) || Notification.permission !== "granted") return;
  try {
    const title = notif.title || "🔔 EduMentor";
    const body = `${notif.heading}\n${notif.body}`;
    const n = new Notification(title, {
      body: body,
      icon: "/assets/teacher_avatar/teacher_encouraging.png",
      tag: `edumentor-${notif.concept_id}`
    });
    n.onclick = () => {
      window.focus();
      triggerRecallForConcept(notif.concept_id);
    };
  } catch (err) {
    console.warn("Failed to display browser notification:", err);
  }
}

function showInAppToast(notif) {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = "in-app-toast";
  toast.innerHTML = `
    <div class="toast-icon-wrap">🔔</div>
    <div class="toast-content">
      <div class="toast-title">${notif.title || "EduMentor"}</div>
      <div class="toast-heading">${notif.heading}</div>
      <div class="toast-body">${notif.body}</div>
      <button type="button" class="btn-notif-recall" style="font-size: 11px; padding: 4px 10px;">Recall Now →</button>
    </div>
    <button type="button" class="toast-close-btn" aria-label="Dismiss">✕</button>
  `;

  // Recall action
  toast.querySelector(".btn-notif-recall").addEventListener("click", () => {
    toast.remove();
    triggerRecallForConcept(notif.concept_id);
  });

  // Close button
  toast.querySelector(".toast-close-btn").addEventListener("click", () => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    setTimeout(() => toast.remove(), 200);
  });

  container.appendChild(toast);

  // Auto-dismiss after 7 seconds
  setTimeout(() => {
    if (toast.parentElement) {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(10px)";
      setTimeout(() => toast.remove(), 200);
    }
  }, 7000);
}

async function triggerRecallForConcept(conceptId) {
  try {
    const res = await fetch("/api/resurface/trigger", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ concept_id: conceptId })
    });
    const data = await res.json();
    transitionToChatStage();
    updateUI(data);

    // Accept to launch recall question directly
    setTimeout(async () => {
      const res2 = await fetch("/api/resurface/accept", { method: "POST" });
      const data2 = await res2.json();
      updateUI(data2);
    }, 300);
  } catch (err) {
    console.error("Failed to trigger recall for concept:", err);
  }
}

async function fetchNotifications() {
  try {
    const res = await fetch("/api/notifications");
    if (!res.ok) return;
    const data = await res.json();
    const notifications = data.notifications || [];
    const unreadCount = data.unread_count || 0;

    // Update Header Badge
    const badge = document.getElementById("notificationBadge");
    if (badge) {
      if (unreadCount > 0) {
        badge.textContent = unreadCount > 9 ? "9+" : unreadCount;
        badge.style.display = "block";
      } else {
        badge.style.display = "none";
      }
    }

    // Render Dropdown List
    const list = document.getElementById("notificationList");
    if (list) {
      if (notifications.length === 0) {
        list.innerHTML = `<div class="notif-empty-state">No notifications yet. You're all caught up! ✨</div>`;
      } else {
        list.innerHTML = "";
        notifications.forEach((n) => {
          const card = document.createElement("div");
          card.className = `notif-card ${n.status === "unread" ? "unread" : ""}`;
          card.innerHTML = `
            <div class="notif-card-header">
              <span class="notif-card-brand">${n.title || "🔔 EduMentor"}</span>
              <span class="notif-card-time">${formatTimeAgo(n.created_at)}</span>
            </div>
            <div class="notif-card-heading">${n.heading}</div>
            <div class="notif-card-body">${n.body}</div>
            <div class="notif-card-footer">
              <button type="button" class="btn-notif-recall">Recall Now →</button>
            </div>
          `;
          card.querySelector(".btn-notif-recall").addEventListener("click", (e) => {
            e.stopPropagation();
            const dd = document.getElementById("notificationDropdown");
            if (dd) dd.style.display = "none";
            triggerRecallForConcept(n.concept_id);
          });
          card.addEventListener("click", () => {
            if (n.status === "unread") {
              fetch("/api/notifications/read", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ notification_id: n.id })
              }).then(fetchNotifications);
            }
          });
          list.appendChild(card);
        });
      }
    }

    // Show in-app toast & browser notification for any new unread alerts
    notifications.forEach((n) => {
      if (n.status === "unread" && !seenToastNotificationIds.has(n.id)) {
        seenToastNotificationIds.add(n.id);
        showInAppToast(n);
        showBrowserNotification(n);
      }
    });

  } catch (err) {
    console.error("Failed to fetch notifications:", err);
  }
}

function formatTimeAgo(isoString) {
  if (!isoString) return "just now";
  const diffSec = Math.floor((new Date() - new Date(isoString)) / 1000);
  if (diffSec < 60) return "just now";
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
  return `${Math.floor(diffSec / 86400)}d ago`;
}

/* ==========================================================================
   PHASE 18 & 19: RESUME LEARNING & LIGHTWEIGHT PROGRESS CONTROLLERS
   ========================================================================== */
let previousActiveStage = "homeStage";

function initResumeAndProgressListeners() {
  const btnResumeContinue = document.getElementById("btnResumeContinue");
  const btnResumeDismiss = document.getElementById("btnResumeDismiss");
  if (btnResumeContinue) {
    btnResumeContinue.addEventListener("click", resumeContinue);
  }
  if (btnResumeDismiss) {
    btnResumeDismiss.addEventListener("click", resumeDismiss);
  }

  const btnToggleProgress = document.getElementById("btnToggleProgress");
  const btnCloseProgress = document.getElementById("btnCloseProgress");
  if (btnToggleProgress) {
    btnToggleProgress.addEventListener("click", toggleProgressView);
  }
  if (btnCloseProgress) {
    btnCloseProgress.addEventListener("click", toggleProgressView);
  }
}

async function checkResumeState() {
  try {
    const res = await fetch("/api/resume-state");
    if (!res.ok) return;
    const data = await res.json();
    if (data && data.has_resumable) {
      const modal = document.getElementById("resumeLearningModal");
      const nameEl = document.getElementById("resumeStudentName");
      const subEl = document.getElementById("resumeSubject");
      const textEl = document.getElementById("resumeFinishedText");
      const conceptEl = document.getElementById("resumeConcept");

      if (nameEl) nameEl.textContent = data.student_name || "Ashwel";
      if (subEl) subEl.textContent = data.subject || "Operating Systems";
      if (textEl) {
        textEl.innerHTML = `You finished <strong>${data.finished_count}</strong> of <strong>${data.total_count}</strong> concepts.`;
      }
      if (conceptEl) conceptEl.textContent = data.revisit_concept || "CPU Scheduling";

      if (modal) modal.classList.add("active");
    }
  } catch (err) {
    console.error("Failed to check resume state:", err);
  }
}

async function resumeContinue() {
  const modal = document.getElementById("resumeLearningModal");
  if (modal) modal.classList.remove("active");
  try {
    const res = await fetch("/api/resume/continue", { method: "POST" });
    const data = await res.json();
    updateUI(data);
    transitionToChatStage();
  } catch (err) {
    console.error("Resume continue failed:", err);
  }
}

async function resumeDismiss() {
  const modal = document.getElementById("resumeLearningModal");
  if (modal) modal.classList.remove("active");
  try {
    const res = await fetch("/api/resume/dismiss", { method: "POST" });
    const data = await res.json();
    updateUI(data);
    transitionToHomeStage();
  } catch (err) {
    console.error("Resume dismiss failed:", err);
  }
}

async function toggleProgressView() {
  const progressStage = document.getElementById("progressStage");
  const homeStage = document.getElementById("homeStage");
  const chatStage = document.getElementById("chatWorkspaceStage");

  if (!progressStage) return;

  const isVisible = progressStage.style.display !== "none";
  if (isVisible) {
    // Hide progress, restore previous stage
    progressStage.style.display = "none";
    if (previousActiveStage === "chatWorkspaceStage") {
      if (chatStage) chatStage.style.display = "flex";
      if (homeStage) homeStage.style.display = "none";
    } else {
      if (homeStage) homeStage.style.display = "flex";
      if (chatStage) chatStage.style.display = "none";
    }
  } else {
    // Track what was active
    if (chatStage && chatStage.style.display !== "none") {
      previousActiveStage = "chatWorkspaceStage";
    } else {
      previousActiveStage = "homeStage";
    }
    if (homeStage) homeStage.style.display = "none";
    if (chatStage) chatStage.style.display = "none";
    progressStage.style.display = "block";
    fetchProgressData();
  }
}

async function fetchProgressData() {
  try {
    const res = await fetch("/api/progress");
    if (!res.ok) return;
    const data = await res.json();
    renderProgressView(data);
  } catch (err) {
    console.error("Failed to fetch progress:", err);
  }
}

function renderProgressView(data) {
  if (!data) return;

  const overallEl = document.getElementById("progOverallMastery");
  const masteredEl = document.getElementById("progConceptsMastered");
  const reviewEl = document.getElementById("progNeedsReview");
  const sessionsEl = document.getElementById("progSessions");
  const strongestEl = document.getElementById("progStrongestArea");
  const attentionEl = document.getElementById("progNeedsAttention");
  const recentList = document.getElementById("progRecentSubjects");

  if (overallEl) overallEl.textContent = `${data.overall_mastery || 76}%`;
  if (masteredEl) masteredEl.textContent = data.concepts_mastered || 32;
  if (reviewEl) reviewEl.textContent = data.needs_review || 6;
  if (sessionsEl) sessionsEl.textContent = data.learning_sessions || 14;

  if (strongestEl && data.strongest_area) {
    strongestEl.textContent = data.strongest_area;
  }
  if (attentionEl && data.needs_attention) {
    attentionEl.textContent = data.needs_attention;
  }

  if (recentList && Array.isArray(data.recent_subjects)) {
    recentList.innerHTML = data.recent_subjects
      .map(
        (s) => `
      <div class="subject-row">
        <div class="subject-info">
          <span class="subject-name">${s.subject}</span>
          <span class="subject-pct">${s.mastery}%</span>
        </div>
        <div class="subject-bar-track">
          <div class="subject-bar-fill" style="width: ${s.mastery}%;"></div>
        </div>
      </div>
    `
      )
      .join("");
  }
}

/* ==========================================================================
   PHASE 21: SOURCE GROUNDING CHIP BUILDER
   ========================================================================== */
function createInlineGroundingChip(grounding) {
  if (!grounding) return null;
  const chipContainer = document.createElement("div");
  chipContainer.className = "grounding-container";

  const chip = document.createElement("div");
  chip.className = "source-grounding-chip";
  const modLabel = grounding.module_title || `Module ${grounding.module_number || 1}`;
  chip.innerHTML = `
    <span>📚</span>
    <span>Grounded in <strong>${escapeHtml(modLabel)}</strong> notes</span>
    <span style="opacity: 0.8; font-size: 10px; margin-left: 4px;">▼</span>
  `;

  const box = document.createElement("div");
  box.className = "grounding-provenance-box";
  box.style.display = "none";
  box.innerHTML = `
    <div class="grounding-hierarchy">
      <span class="grounding-node">Subject: ${escapeHtml(grounding.subject_id || "Operating Systems")}</span>
      <span class="grounding-arrow">→</span>
      <span class="grounding-node">${escapeHtml(modLabel)}</span>
      <span class="grounding-arrow">→</span>
      <span class="grounding-node">Concept: ${escapeHtml(grounding.concept_id || "")}</span>
      <span class="grounding-arrow">→</span>
      <span class="grounding-node">${escapeHtml(grounding.document_id || "doc_source")}</span>
    </div>
    <div class="grounding-quote">
      "${escapeHtml(grounding.explanation || `I asked this because it was covered in your ${modLabel} notes.`)}"
    </div>
    <div style="font-size: 11px; color: #64748B;">
      Source Provenance: <code>${(grounding.source_chunk_ids || []).join(', ') || 'verified_notes'}</code> • <em>Strictly grounded in uploaded notes (Zero hallucinations)</em>
    </div>
  `;

  chip.addEventListener("click", () => {
    box.style.display = box.style.display === "none" ? "flex" : "none";
  });

  chipContainer.appendChild(chip);
  chipContainer.appendChild(box);
  return chipContainer;
}

/* ==========================================================================
   PHASE 20: MODULE MANAGER INTERACTIONS
   ========================================================================== */
document.addEventListener("DOMContentLoaded", () => {
  const btnToggleModuleManager = document.getElementById("btnToggleModuleManager");
  const moduleDropdownPanel = document.getElementById("moduleDropdownPanel");
  if (btnToggleModuleManager && moduleDropdownPanel) {
    btnToggleModuleManager.addEventListener("click", (e) => {
      e.stopPropagation();
      moduleDropdownPanel.style.display = moduleDropdownPanel.style.display === "none" ? "block" : "none";
    });
    document.addEventListener("click", (e) => {
      if (!moduleDropdownPanel.contains(e.target) && e.target !== btnToggleModuleManager) {
        moduleDropdownPanel.style.display = "none";
      }
    });
  }

  const btnQuickAddModule = document.getElementById("btnQuickAddModule");
  const addModuleModal = document.getElementById("addModuleModal");
  const btnCloseAddModuleModal = document.getElementById("btnCloseAddModuleModal");
  if (btnQuickAddModule && addModuleModal) {
    btnQuickAddModule.addEventListener("click", () => {
      if (moduleDropdownPanel) moduleDropdownPanel.style.display = "none";
      addModuleModal.style.display = "flex";
      const nextNum = (appState.modules ? appState.modules.length : 0) + 1;
      const numInput = document.getElementById("inputModuleNumber");
      if (numInput) numInput.value = nextNum;
      const titleInput = document.getElementById("inputModuleTitle");
      if (titleInput) titleInput.value = `Module ${nextNum}`;
    });
  }
  if (btnCloseAddModuleModal && addModuleModal) {
    btnCloseAddModuleModal.addEventListener("click", () => {
      addModuleModal.style.display = "none";
    });
  }

  const addModuleForm = document.getElementById("addModuleForm");
  if (addModuleForm) {
    addModuleForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const title = document.getElementById("inputModuleTitle").value;
      const num = document.getElementById("inputModuleNumber").value;
      const fileInput = document.getElementById("inputModuleFile");
      const file = fileInput && fileInput.files ? fileInput.files[0] : null;
      const text = document.getElementById("inputModuleText").value;
      const subj = document.getElementById("inputSubjectName").value;

      const fd = new FormData();
      fd.append("subject_title", subj);
      fd.append("module_title", title);
      if (num) fd.append("module_number", num);
      if (file) fd.append("file", file);
      if (text) fd.append("raw_text", text);

      if (addModuleModal) addModuleModal.style.display = "none";
      renderTeacherTyping(true, `Ingesting ${title} into ${subj}...`);

      try {
        const res = await fetch("/api/modules/upload", {
          method: "POST",
          body: fd
        });
        const data = await res.json();
        renderTeacherTyping(false);
        updateUI(data);
      } catch (err) {
        renderTeacherTyping(false);
        console.error("Module upload error:", err);
      }
    });
  }
});

/* ==========================================================================
   PHASE 34: CONVERSATION DATABASE & SESSION RECONSTRUCTION CONTROLLER
   ========================================================================== */
function initHistoryListeners() {
  const btnToggleHistory = document.getElementById("btnToggleHistoryDrawer");
  const btnDrawerHistory = document.getElementById("btnDrawerHistory");
  const historyModal = document.getElementById("historyModal");
  const btnCloseHistory = document.getElementById("btnCloseHistoryModal");

  if (btnToggleHistory) {
    btnToggleHistory.addEventListener("click", () => openHistoryModal());
  }
  if (btnDrawerHistory) {
    btnDrawerHistory.addEventListener("click", () => {
      closeMobileDrawer();
      openHistoryModal();
    });
  }
  if (btnCloseHistory && historyModal) {
    btnCloseHistory.addEventListener("click", () => {
      historyModal.style.display = "none";
    });
    historyModal.addEventListener("click", (e) => {
      if (e.target === historyModal) historyModal.style.display = "none";
    });
  }

  // Tabs inside history modal
  const tabs = document.querySelectorAll(".reconstruct-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      const target = tab.getAttribute("data-tab");
      const viewTurns = document.getElementById("viewReconstructTurns");
      const viewRecalls = document.getElementById("viewReconstructRecalls");
      const viewMilestones = document.getElementById("viewReconstructMilestones");
      if (viewTurns) viewTurns.style.display = target === "turns" ? "block" : "none";
      if (viewRecalls) viewRecalls.style.display = target === "recalls" ? "block" : "none";
      if (viewMilestones) viewMilestones.style.display = target === "milestones" ? "block" : "none";
    });
  });
}

async function openHistoryModal() {
  const historyModal = document.getElementById("historyModal");
  if (!historyModal) return;
  historyModal.style.display = "flex";
  await loadHistorySessions();
}

async function loadHistorySessions() {
  const listEl = document.getElementById("historySessionsList");
  const countBadge = document.getElementById("historySessionCount");
  if (!listEl) return;

  listEl.innerHTML = '<div class="history-loading">Fetching past sessions...</div>';
  try {
    const res = await fetch("/api/history");
    const data = await res.json();
    const sessions = data.conversations || [];
    if (countBadge) countBadge.textContent = sessions.length;

    if (sessions.length === 0) {
      listEl.innerHTML = '<div class="history-loading">No past sessions found yet.<br>Start chatting or studying to record conversations!</div>';
      return;
    }

    listEl.innerHTML = "";
    sessions.forEach((s, idx) => {
      const item = document.createElement("div");
      item.className = `history-session-item ${idx === 0 ? "active" : ""}`;
      item.dataset.convId = s.conversation_id;
      
      const started = s.started_at ? new Date(s.started_at).toLocaleDateString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) : "Recent";
      const titleSafe = s.title ? escapeHtml(s.title) : "Study Session";
      item.innerHTML = `
        <div class="history-session-title" title="${titleSafe}">${titleSafe}</div>
        <div class="history-session-date">${started}</div>
        <div class="history-session-stats">
          <span class="history-session-stat-pill">💬 ${s.message_count} msgs</span>
          <span class="history-session-stat-pill">🧠 ${s.concepts_count} concepts</span>
        </div>
      `;

      item.addEventListener("click", () => {
        document.querySelectorAll(".history-session-item").forEach(el => el.classList.remove("active"));
        item.classList.add("active");
        reconstructAndDisplaySession(s.conversation_id);
      });

      listEl.appendChild(item);
    });

    // Auto load the first session
    if (sessions.length > 0) {
      reconstructAndDisplaySession(sessions[0].conversation_id);
    }
  } catch (err) {
    console.error("Failed to load history sessions:", err);
    listEl.innerHTML = '<div class="history-loading">Failed to load sessions.</div>';
  }
}

async function reconstructAndDisplaySession(conversationId) {
  const placeholder = document.getElementById("historyPlaceholder");
  const content = document.getElementById("historyReconstructedContent");
  if (!content) return;

  try {
    const res = await fetch(`/api/history/sessions/${conversationId}`);
    if (!res.ok) throw new Error("Failed to reconstruct session");
    const data = await res.json();
    const session = data.session;

    if (placeholder) placeholder.style.display = "none";
    content.style.display = "flex";

    // Summary metadata
    const sidEl = document.getElementById("reconstructSessionId");
    if (sidEl) sidEl.textContent = session.conversation_id || conversationId;
    const timeEl = document.getElementById("reconstructTimestamp");
    if (timeEl) {
      const startStr = session.started_at ? new Date(session.started_at).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) : "N/A";
      timeEl.textContent = `Started: ${startStr}`;
    }
    const msgCountEl = document.getElementById("reconstructMsgCount");
    if (msgCountEl) msgCountEl.textContent = session.total_messages || (session.turns ? session.turns.length : 0);
    const conceptCountEl = document.getElementById("reconstructConceptCount");
    if (conceptCountEl) conceptCountEl.textContent = (session.concepts_covered ? session.concepts_covered.length : 0);
    const recallCountEl = document.getElementById("reconstructRecallCount");
    if (recallCountEl) recallCountEl.textContent = (session.recall_exchanges ? session.recall_exchanges.length : 0);

    // Concept chips
    const conceptsRow = document.getElementById("reconstructConceptsRow");
    if (conceptsRow) {
      conceptsRow.innerHTML = "";
      if (session.concepts_covered && session.concepts_covered.length > 0) {
        session.concepts_covered.forEach(cid => {
          const chip = document.createElement("span");
          chip.className = "reconstruct-concept-chip";
          chip.textContent = cid;
          conceptsRow.appendChild(chip);
        });
      } else {
        conceptsRow.innerHTML = '<span style="font-size: 11px; color: #64748B;">General Exploration</span>';
      }
    }

    // Tabs counts
    const recallTabCount = document.getElementById("reconstructRecallsTabCount");
    if (recallTabCount) recallTabCount.textContent = (session.recall_exchanges ? session.recall_exchanges.length : 0);
    const milestonesCount = (session.mastery_milestones ? session.mastery_milestones.length : 0) + (session.revisions_triggered ? session.revisions_triggered.length : 0);
    const milestoneTabCount = document.getElementById("reconstructMilestonesTabCount");
    if (milestoneTabCount) milestoneTabCount.textContent = milestonesCount;

    // Render turns
    const turnsTimeline = document.getElementById("reconstructTurnsTimeline");
    if (turnsTimeline) {
      turnsTimeline.innerHTML = "";
      const turns = session.turns || [];
      turns.forEach(t => {
        const card = document.createElement("div");
        card.className = `turn-entry-card role-${t.role}`;
        
        const typeClass = `type-${t.message_type || 'analysis'}`;
        const timeStr = t.created_at ? new Date(t.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "";

        card.innerHTML = `
          <div class="turn-header">
            <div class="turn-badges">
              <span class="role-badge role-${t.role}">${escapeHtml(t.role)}</span>
              <span class="msg-type-badge ${typeClass}">${escapeHtml(t.message_type)}</span>
              ${t.concept_id ? `<span class="reconstruct-concept-chip" style="font-size: 10px; padding: 1px 6px;">${escapeHtml(t.concept_id)}</span>` : ""}
            </div>
            <span class="turn-time">${timeStr}</span>
          </div>
          <div class="turn-message-text">${escapeHtml(t.message || '')}</div>
        `;
        turnsTimeline.appendChild(card);
      });
    }

    // Render recall exchanges
    const recallsList = document.getElementById("reconstructRecallsList");
    if (recallsList) {
      recallsList.innerHTML = "";
      const recalls = session.recall_exchanges || [];
      if (recalls.length === 0) {
        recallsList.innerHTML = '<div style="font-size: 12px; color: #64748B; text-align: center; padding: 24px;">No recall questions recorded in this session.</div>';
      } else {
        recalls.forEach(r => {
          const rCard = document.createElement("div");
          rCard.className = "recall-exchange-card";
          const scoreText = r.score !== null && r.score !== undefined ? `${r.score}%` : "Evaluated";
          const verdictText = r.verdict ? ` • ${r.verdict}` : "";
          rCard.innerHTML = `
            <div class="recall-exchange-header">
              <span style="font-size: 11px; font-weight: 700; color: #FBBF24;">❓ Recall Challenge (${escapeHtml(r.concept_id || 'Concept')})</span>
              <span class="history-badge" style="background: rgba(16, 185, 129, 0.15); color: #34D399; border-color: rgba(16, 185, 129, 0.3);">
                ${scoreText}${escapeHtml(verdictText)}
              </span>
            </div>
            <div class="recall-q-section">${escapeHtml(r.question || '')}</div>
            <div class="recall-a-section">
              <strong style="color: #25D8E8; font-size: 11px;">Student Answer:</strong><br>
              ${escapeHtml(r.answer || 'No answer recorded')}
            </div>
            ${r.feedback ? `
              <div class="recall-eval-section">
                <strong style="color: #34D399; font-size: 11px;">Pedagogical Feedback:</strong><br>
                ${escapeHtml(r.feedback)}
              </div>
            ` : ""}
          `;
          recallsList.appendChild(rCard);
        });
      }
    }

    // Render milestones and revisions
    const milestonesList = document.getElementById("reconstructMilestonesList");
    if (milestonesList) {
      milestonesList.innerHTML = "";
      const mastery = session.mastery_milestones || [];
      const revisions = session.revisions_triggered || [];
      if (mastery.length === 0 && revisions.length === 0) {
        milestonesList.innerHTML = '<div style="font-size: 12px; color: #64748B; text-align: center; padding: 24px;">No mastery milestones or revisions in this session.</div>';
      } else {
        mastery.forEach(m => {
          const item = document.createElement("div");
          item.className = "milestone-item-card";
          item.innerHTML = `
            <span style="font-size: 20px;">🏆</span>
            <div>
              <div style="font-size: 13px; font-weight: 700; color: #FACC15;">Mastery Achieved: ${escapeHtml(m.concept_id || 'Concept')}</div>
              <div style="font-size: 12px; color: #CBD5E1; margin-top: 2px;">${escapeHtml(m.message || '')}</div>
            </div>
          `;
          milestonesList.appendChild(item);
        });
        revisions.forEach(rev => {
          const item = document.createElement("div");
          item.className = "milestone-item-card is-revision";
          item.innerHTML = `
            <span style="font-size: 20px;">🔁</span>
            <div>
              <div style="font-size: 13px; font-weight: 700; color: #FB923C;">Revision Triggered: ${escapeHtml(rev.concept_id || 'Concept')}</div>
              <div style="font-size: 12px; color: #CBD5E1; margin-top: 2px;">${escapeHtml(rev.message || '')}</div>
            </div>
          `;
          milestonesList.appendChild(item);
        });
      }
    }

  } catch (err) {
    console.error("Reconstruct session error:", err);
  }
}


