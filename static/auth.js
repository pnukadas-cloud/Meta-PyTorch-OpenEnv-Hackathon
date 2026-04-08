const authState = {
  loginMethod: "email",
  recoveryMethod: "email",
};

const roleContent = {
  admin: {
    loginLabel: "Work email",
    loginPlaceholder: "admin@controlroom.io",
    loginHelp: "Use the registered admin email for your operations account.",
    phoneLabel: "Admin phone",
    phonePlaceholder: "+91 98765 43210",
    phoneHelp: "Use the phone number registered for admin alerts.",
    submitText: "Sign in as admin",
    recoveryTitle: "Recover admin password",
    recoveryDescription: "Choose email or phone to receive your reset instructions.",
  },
  user: {
    loginLabel: "Email address",
    loginPlaceholder: "user@example.com",
    loginHelp: "Use the email registered for your standard user account.",
    phoneLabel: "Mobile number",
    phonePlaceholder: "+91 91234 56789",
    phoneHelp: "Use the phone number linked to your user account.",
    submitText: "Sign in as user",
    recoveryTitle: "Recover user password",
    recoveryDescription: "Choose email or phone to receive your reset instructions.",
  },
};

const strengthLabels = [
  "Start typing",
  "Weak",
  "Moderate",
  "Strong",
  "Very strong",
];

document.addEventListener("DOMContentLoaded", () => {
  const role = document.body.dataset.role || "user";
  const content = roleContent[role] || roleContent.user;

  const elements = {
    loginButtons: [...document.querySelectorAll("[data-auth-method]")],
    identityLabel: document.querySelector("#identity-label"),
    identityInput: document.querySelector("#identity-input"),
    identityHelp: document.querySelector("#identity-help"),
    passwordInput: document.querySelector("#password-input"),
    togglePassword: document.querySelector("#toggle-password"),
    strengthLabel: document.querySelector("#strength-label"),
    strengthBars: [...document.querySelectorAll(".strength-bar")],
    rules: {
      length: document.querySelector('[data-rule="length"]'),
      mixed: document.querySelector('[data-rule="mixed"]'),
      number: document.querySelector('[data-rule="number"]'),
      symbol: document.querySelector('[data-rule="symbol"]'),
    },
    form: document.querySelector("#auth-form"),
    status: document.querySelector("#auth-status"),
    submit: document.querySelector("#auth-submit"),
    forgotTrigger: document.querySelector("#forgot-password-trigger"),
    recoveryOverlay: document.querySelector("#recovery-overlay"),
    recoveryClose: document.querySelector("#recovery-close"),
    recoveryButtons: [...document.querySelectorAll("[data-recovery-method]")],
    recoveryTitle: document.querySelector("#recovery-title"),
    recoveryDescription: document.querySelector("#recovery-description"),
    recoveryLabel: document.querySelector("#recovery-label"),
    recoveryInput: document.querySelector("#recovery-input"),
    recoveryHelp: document.querySelector("#recovery-help"),
    recoveryForm: document.querySelector("#recovery-form"),
    recoveryStatus: document.querySelector("#recovery-status"),
    recoverySubmit: document.querySelector("#recovery-submit"),
  };

  if (!elements.form) {
    return;
  }

  elements.submit.textContent = content.submitText;
  elements.recoveryTitle.textContent = content.recoveryTitle;
  elements.recoveryDescription.textContent = content.recoveryDescription;

  updateLoginMethod(elements, content);
  updateRecoveryMethod(elements, content);
  updateStrength(elements.passwordInput.value, elements);

  elements.loginButtons.forEach((button) => {
    button.addEventListener("click", () => {
      authState.loginMethod = button.dataset.authMethod || "email";
      updateLoginMethod(elements, content);
    });
  });

  elements.recoveryButtons.forEach((button) => {
    button.addEventListener("click", () => {
      authState.recoveryMethod = button.dataset.recoveryMethod || "email";
      updateRecoveryMethod(elements, content);
    });
  });

  elements.togglePassword.addEventListener("click", () => {
    const isHidden = elements.passwordInput.type === "password";
    elements.passwordInput.type = isHidden ? "text" : "password";
    elements.togglePassword.textContent = isHidden ? "Hide" : "Show";
  });

  elements.passwordInput.addEventListener("input", () => {
    updateStrength(elements.passwordInput.value, elements);
  });

  elements.form.addEventListener("submit", (event) => {
    event.preventDefault();

    const identifier = elements.identityInput.value.trim();
    const password = elements.passwordInput.value;
    const issues = [];

    if (!validateIdentifier(authState.loginMethod, identifier)) {
      issues.push(
        authState.loginMethod === "email"
          ? "Enter a valid email address."
          : "Enter a valid phone number with at least 10 digits.",
      );
    }

    if (password.length < 8) {
      issues.push("Password must be at least 8 characters.");
    }

    if (issues.length) {
      showStatus(elements.status, issues.join(" "), "error");
      return;
    }

    showStatus(
      elements.status,
      role === "admin" ? "Admin login validation passed." : "User login validation passed.",
      "success",
    );
  });

  elements.forgotTrigger.addEventListener("click", () => {
    elements.recoveryOverlay.classList.remove("hidden");
  });

  elements.recoveryClose.addEventListener("click", () => {
    elements.recoveryOverlay.classList.add("hidden");
  });

  elements.recoveryOverlay.addEventListener("click", (event) => {
    if (event.target === elements.recoveryOverlay) {
      elements.recoveryOverlay.classList.add("hidden");
    }
  });

  elements.recoveryForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const value = elements.recoveryInput.value.trim();
    if (!validateIdentifier(authState.recoveryMethod, value)) {
      showStatus(
        elements.recoveryStatus,
        authState.recoveryMethod === "email"
          ? "Enter a valid recovery email."
          : "Enter a valid recovery phone number.",
        "error",
      );
      return;
    }

    const message =
      authState.recoveryMethod === "email"
        ? `Reset link prepared for ${value}.`
        : `Reset code prepared for ${value}.`;
    showStatus(elements.recoveryStatus, message, "success");
  });
});

function updateLoginMethod(elements, content) {
  const useEmail = authState.loginMethod === "email";
  elements.loginButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.authMethod === authState.loginMethod);
  });

  elements.identityLabel.textContent = useEmail ? content.loginLabel : content.phoneLabel;
  elements.identityInput.type = useEmail ? "email" : "tel";
  elements.identityInput.placeholder = useEmail ? content.loginPlaceholder : content.phonePlaceholder;
  elements.identityInput.inputMode = useEmail ? "email" : "tel";
  elements.identityHelp.textContent = useEmail ? content.loginHelp : content.phoneHelp;
}

function updateRecoveryMethod(elements, content) {
  const useEmail = authState.recoveryMethod === "email";
  elements.recoveryButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.recoveryMethod === authState.recoveryMethod);
  });

  elements.recoveryLabel.textContent = useEmail ? content.loginLabel : content.phoneLabel;
  elements.recoveryInput.type = useEmail ? "email" : "tel";
  elements.recoveryInput.placeholder = useEmail ? content.loginPlaceholder : content.phonePlaceholder;
  elements.recoveryInput.inputMode = useEmail ? "email" : "tel";
  elements.recoveryHelp.textContent = useEmail
    ? "We will send a password reset link."
    : "We will send a password reset code.";
  elements.recoverySubmit.textContent = useEmail ? "Send reset link" : "Send reset code";
}

function updateStrength(password, elements) {
  const checks = {
    length: password.length >= 8,
    mixed: /[a-z]/.test(password) && /[A-Z]/.test(password),
    number: /\d/.test(password),
    symbol: /[^A-Za-z0-9]/.test(password),
  };

  const score = Object.values(checks).filter(Boolean).length;
  const level = score <= 1 ? "weak" : score === 2 ? "medium" : score === 3 ? "strong" : "very-strong";

  elements.strengthLabel.textContent = password ? strengthLabels[Math.max(1, score)] : strengthLabels[0];
  elements.strengthBars.forEach((bar, index) => {
    const active = index < Math.max(1, score) && password.length > 0;
    bar.className = "strength-bar";
    if (active) {
      bar.classList.add("active", `is-${level}`);
    }
  });

  Object.entries(checks).forEach(([key, passed]) => {
    elements.rules[key].classList.toggle("complete", passed);
  });
}

function validateIdentifier(method, value) {
  if (!value) {
    return false;
  }
  if (method === "email") {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  }
  const digits = value.replace(/\D/g, "");
  return digits.length >= 10;
}

function showStatus(element, message, tone) {
  element.textContent = message;
  element.className = `auth-status ${tone}`;
  element.classList.remove("hidden");
}
