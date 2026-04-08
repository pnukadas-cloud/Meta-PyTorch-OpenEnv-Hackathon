const state = {
  manifest: null,
  scenarioIndex: 0,
  sessionId: null,
  snapshots: [],
  historyIndex: 0,
  autoplayTimer: null,
  busy: false,
  apiBase: resolveApiBase(),
  offlineMode: false,
};

const AUTH_SESSION_KEY = "crisisCommanderAuthSession";

const fallbackScenarios = [
  {
    id: "rush_hour_cascade",
    label: "Rush Hour Cascade",
    title: "Rush Hour Cascade",
    description:
      "A bus crash and warehouse fire are active when a hazmat leak stretches limited responders.",
    objective: "Keep casualties low and prevent hospital overflow.",
    budget: 18,
    horizon: 10,
    zones: ["North", "East", "South", "West", "Central"],
    snapshots: [
      {
        turn: 0,
        clock_minutes: 0,
        reward_total: 0,
        step_reward: 0,
        verdict: "good",
        summary: "2 active incidents, 0 resolved, 4 units ready, hospital overflow=0.",
        action_headline: "Initial state",
        action_notes: "Open the session and inspect the first incident priorities.",
        reward_signals: [
          { label: "Resolution", percent: 12, value: "+0.0" },
          { label: "Stabilization", percent: 16, value: "+0.0" },
          { label: "Foresight", percent: 22, value: "+0.5" },
          { label: "Fairness", percent: 82, value: "-0.4" },
          { label: "Capacity", percent: 88, value: "-0.2" },
        ],
        grade: { outcome: 74, timeliness: 70, fairness: 79, efficiency: 78, resilience: 75 },
        metrics: { resolved: 0, failed: 0, lives_lost: 0.8, lives_stabilized: 0, hospital_overflow: 0 },
        incidents: [
          { id: "INC-1", title: "Medical", zone: "Central", severity: "4.4", status: "active", tone: "critical", meta: "Age 0 turns, window 3, resources 0" },
          { id: "INC-2", title: "Fire", zone: "West", severity: "3.8", status: "active", tone: "warning", meta: "Age 0 turns, window 4, resources 0" },
        ],
        resources: [
          { id: "AMB-1", type: "Ambulance", status: "available", zone: "North", meta: "Ambulance in North" },
          { id: "FIRE-1", type: "Fire Engine", status: "available", zone: "Central", meta: "Fire Engine in Central" },
          { id: "POL-1", type: "Police Unit", status: "available", zone: "Central", meta: "Police Unit in Central" },
          { id: "HOSP-CENTRAL", type: "Hospital", status: "stable", zone: "Central", meta: "0/24 beds in use (0% utilized)" },
        ],
        events: [
          { title: "Mission update", body: "Rush Hour Cascade initialized." },
          { title: "Ops update", body: "Use the preview controls or start the backend for live simulation." },
        ],
      },
      {
        turn: 1,
        clock_minutes: 5,
        reward_total: 18.7,
        step_reward: 18.7,
        verdict: "excellent",
        summary: "3 active incidents, 1 resolved, 3 units ready, hospital overflow=0.",
        action_headline: "Fairness-Aware Baseline: Dispatch",
        action_notes: "The preview shows a staged response and surge protection before the cascade expands.",
        reward_signals: [
          { label: "Resolution", percent: 54, value: "+12.4" },
          { label: "Stabilization", percent: 48, value: "+7.1" },
          { label: "Foresight", percent: 44, value: "+6.3" },
          { label: "Fairness", percent: 90, value: "-0.1" },
          { label: "Capacity", percent: 92, value: "-0.1" },
        ],
        grade: { outcome: 88, timeliness: 83, fairness: 90, efficiency: 80, resilience: 87 },
        metrics: { resolved: 1, failed: 0, lives_lost: 1.4, lives_stabilized: 18.2, hospital_overflow: 0 },
        incidents: [
          { id: "INC-1", title: "Medical", zone: "Central", severity: "4.4", status: "resolved", tone: "stable", meta: "Age 1 turns, window 3, resources 0" },
          { id: "INC-2", title: "Fire", zone: "West", severity: "3.8", status: "active", tone: "warning", meta: "Age 1 turns, window 4, resources 1" },
          { id: "INC-3", title: "Hazmat", zone: "East", severity: "4.6", status: "active", tone: "critical", meta: "Age 0 turns, window 3, resources 2" },
        ],
        resources: [
          { id: "AMB-2", type: "Ambulance", status: "on_scene", zone: "Central", meta: "Ambulance in Central" },
          { id: "FIRE-1", type: "Fire Engine", status: "on_scene", zone: "East", meta: "Fire Engine in East" },
          { id: "DRN-1", type: "Drone", status: "on_scene", zone: "East", meta: "Drone in East" },
          { id: "HOSP-CENTRAL", type: "Hospital", status: "stable", zone: "Central", meta: "6/24 beds in use (25% utilized)" },
        ],
        events: [
          { title: "Cascade event", body: "New incident INC-3 detected in East." },
          { title: "Incident resolved", body: "INC-1 resolved with patients routed to care." },
        ],
      },
    ],
  },
  {
    id: "festival_blackout",
    label: "Festival Blackout",
    title: "Festival Blackout",
    description:
      "A crowd surge, transformer fire, and district blackout compete for attention during a city event.",
    objective: "Protect the crowd and maintain equitable response coverage.",
    budget: 20,
    horizon: 11,
    zones: ["Arena", "OldTown", "Riverfront", "South", "Central"],
    snapshots: [
      {
        turn: 0,
        clock_minutes: 0,
        reward_total: 0,
        step_reward: 0,
        verdict: "fair",
        summary: "2 active incidents, 0 resolved, 5 units ready, hospital overflow=0.",
        action_headline: "Initial state",
        action_notes: "Arena pressure is visible, but the blackout risk will matter for fairness.",
        reward_signals: [
          { label: "Resolution", percent: 10, value: "+0.0" },
          { label: "Stabilization", percent: 14, value: "+0.0" },
          { label: "Foresight", percent: 20, value: "+0.3" },
          { label: "Fairness", percent: 74, value: "-1.0" },
          { label: "Capacity", percent: 88, value: "-0.2" },
        ],
        grade: { outcome: 69, timeliness: 72, fairness: 64, efficiency: 79, resilience: 71 },
        metrics: { resolved: 0, failed: 0, lives_lost: 1.2, lives_stabilized: 0, hospital_overflow: 0 },
        incidents: [
          { id: "FEST-1", title: "Crowd Control", zone: "Arena", severity: "4.7", status: "active", tone: "critical", meta: "Age 0 turns, window 2, resources 0" },
          { id: "FEST-2", title: "Fire", zone: "Riverfront", severity: "3.9", status: "active", tone: "warning", meta: "Age 0 turns, window 3, resources 0" },
        ],
        resources: [
          { id: "POL-1", type: "Police Unit", status: "available", zone: "Arena", meta: "Police Unit in Arena" },
          { id: "AMB-3", type: "Ambulance", status: "available", zone: "Arena", meta: "Ambulance in Arena" },
          { id: "DRN-1", type: "Drone", status: "available", zone: "Central", meta: "Drone in Central" },
          { id: "HOSP-ARENA", type: "Hospital", status: "stable", zone: "Arena", meta: "0/18 beds in use (0% utilized)" },
        ],
        events: [
          { title: "Mission update", body: "Festival Blackout initialized." },
          { title: "Ops update", body: "Arena visibility is high, but blackout spillover is not yet visible." },
        ],
      },
      {
        turn: 1,
        clock_minutes: 5,
        reward_total: 15.4,
        step_reward: 15.4,
        verdict: "good",
        summary: "3 active incidents, 0 resolved, 4 units ready, hospital overflow=0.",
        action_headline: "Fairness-Aware Baseline: Stage",
        action_notes: "The preview keeps coverage on the quieter south-side failure instead of chasing only the visible crowd event.",
        reward_signals: [
          { label: "Resolution", percent: 26, value: "+4.8" },
          { label: "Stabilization", percent: 34, value: "+5.0" },
          { label: "Foresight", percent: 40, value: "+6.2" },
          { label: "Fairness", percent: 88, value: "-0.2" },
          { label: "Capacity", percent: 90, value: "-0.1" },
        ],
        grade: { outcome: 82, timeliness: 79, fairness: 86, efficiency: 77, resilience: 83 },
        metrics: { resolved: 0, failed: 0, lives_lost: 2.0, lives_stabilized: 9.4, hospital_overflow: 0 },
        incidents: [
          { id: "FEST-1", title: "Crowd Control", zone: "Arena", severity: "4.7", status: "active", tone: "warning", meta: "Age 1 turns, window 2, resources 2" },
          { id: "FEST-2", title: "Fire", zone: "Riverfront", severity: "3.9", status: "active", tone: "warning", meta: "Age 1 turns, window 3, resources 1" },
          { id: "FEST-3", title: "Grid Failure", zone: "South", severity: "3.8", status: "active", tone: "critical", meta: "Age 0 turns, window 2, resources 1" },
        ],
        resources: [
          { id: "POL-1", type: "Police Unit", status: "on_scene", zone: "Arena", meta: "Police Unit in Arena" },
          { id: "DRN-1", type: "Drone", status: "on_scene", zone: "South", meta: "Drone in South" },
          { id: "AMB-2", type: "Ambulance", status: "available", zone: "South", meta: "Ambulance in South" },
          { id: "HOSP-SOUTH", type: "Hospital", status: "stable", zone: "South", meta: "2/14 beds in use (14% utilized)" },
        ],
        events: [
          { title: "Cascade event", body: "FEST-3 detected in South." },
          { title: "Ops update", body: "Coverage is split across crowd control, fire, and blackout response." },
        ],
      },
    ],
  },
  {
    id: "industrial_storm",
    label: "Industrial Storm",
    title: "Industrial Storm",
    description:
      "A severe storm compounds an industrial hazard, roadway blockages, and scattered medical calls.",
    objective: "Contain the root hazard while reserving capacity for secondary incidents.",
    budget: 19,
    horizon: 12,
    zones: ["Port", "North", "South", "Industrial", "Central"],
    snapshots: [
      {
        turn: 0,
        clock_minutes: 0,
        reward_total: 0,
        step_reward: 0,
        verdict: "good",
        summary: "1 active incident, 0 resolved, 6 units ready, hospital overflow=0.",
        action_headline: "Initial state",
        action_notes: "The root industrial hazard should be treated before downstream effects spread.",
        reward_signals: [
          { label: "Resolution", percent: 10, value: "+0.0" },
          { label: "Stabilization", percent: 18, value: "+0.0" },
          { label: "Foresight", percent: 28, value: "+1.2" },
          { label: "Fairness", percent: 86, value: "-0.3" },
          { label: "Capacity", percent: 92, value: "-0.1" },
        ],
        grade: { outcome: 76, timeliness: 71, fairness: 81, efficiency: 77, resilience: 84 },
        metrics: { resolved: 0, failed: 0, lives_lost: 0.6, lives_stabilized: 0, hospital_overflow: 0 },
        incidents: [
          { id: "STORM-1", title: "Hazmat", zone: "Industrial", severity: "4.8", status: "active", tone: "critical", meta: "Age 0 turns, window 3, resources 0" },
        ],
        resources: [
          { id: "FIRE-1", type: "Fire Engine", status: "available", zone: "Industrial", meta: "Fire Engine in Industrial" },
          { id: "DRN-1", type: "Drone", status: "available", zone: "Port", meta: "Drone in Port" },
          { id: "AMB-1", type: "Ambulance", status: "available", zone: "Central", meta: "Ambulance in Central" },
          { id: "HOSP-CENTRAL", type: "Hospital", status: "stable", zone: "Central", meta: "0/20 beds in use (0% utilized)" },
        ],
        events: [
          { title: "Mission update", body: "Industrial Storm initialized." },
          { title: "Ops update", body: "A single root hazard is active before secondary storm incidents appear." },
        ],
      },
      {
        turn: 1,
        clock_minutes: 5,
        reward_total: 16.2,
        step_reward: 16.2,
        verdict: "excellent",
        summary: "2 active incidents, 0 resolved, 4 units ready, hospital overflow=0.",
        action_headline: "Severity-First Baseline: Dispatch",
        action_notes: "The preview shows early hazard containment while a second incident enters from the south.",
        reward_signals: [
          { label: "Resolution", percent: 30, value: "+5.6" },
          { label: "Stabilization", percent: 42, value: "+6.8" },
          { label: "Foresight", percent: 38, value: "+4.4" },
          { label: "Fairness", percent: 90, value: "-0.2" },
          { label: "Capacity", percent: 94, value: "-0.1" },
        ],
        grade: { outcome: 85, timeliness: 80, fairness: 87, efficiency: 79, resilience: 89 },
        metrics: { resolved: 0, failed: 0, lives_lost: 1.5, lives_stabilized: 6.4, hospital_overflow: 0 },
        incidents: [
          { id: "STORM-1", title: "Hazmat", zone: "Industrial", severity: "4.8", status: "active", tone: "warning", meta: "Age 1 turns, window 3, resources 2" },
          { id: "STORM-2", title: "Medical", zone: "South", severity: "3.7", status: "active", tone: "critical", meta: "Age 0 turns, window 2, resources 1" },
        ],
        resources: [
          { id: "FIRE-1", type: "Fire Engine", status: "on_scene", zone: "Industrial", meta: "Fire Engine in Industrial" },
          { id: "DRN-1", type: "Drone", status: "on_scene", zone: "Industrial", meta: "Drone in Industrial" },
          { id: "POL-2", type: "Police Unit", status: "on_scene", zone: "South", meta: "Police Unit in South" },
          { id: "HOSP-SOUTH", type: "Hospital", status: "stable", zone: "South", meta: "3/15 beds in use (20% utilized)" },
        ],
        events: [
          { title: "Cascade event", body: "STORM-2 detected in South." },
          { title: "Ops update", body: "The preview illustrates root-hazard containment with reserve capacity." },
        ],
      },
    ],
  },
];

const elements = {
  authEntry: document.querySelector("#auth-entry"),
  adminLoginLink: document.querySelector("#admin-login-link"),
  userLoginLink: document.querySelector("#user-login-link"),
  authChip: document.querySelector("#auth-chip"),
  logoutButton: document.querySelector("#logout-button"),
  heroAdminLink: document.querySelector("#hero-admin-link"),
  heroUserLink: document.querySelector("#hero-user-link"),
  tabs: document.querySelector("#scenario-tabs"),
  title: document.querySelector("#scenario-title"),
  description: document.querySelector("#scenario-description"),
  objectives: document.querySelector("#scenario-objectives"),
  budget: document.querySelector("#scenario-budget"),
  horizon: document.querySelector("#scenario-horizon"),
  zones: document.querySelector("#scenario-zones"),
  turnReadout: document.querySelector("#turn-readout"),
  rewardTotal: document.querySelector("#reward-total"),
  scoreBars: document.querySelector("#score-bars"),
  verdict: document.querySelector("#verdict-pill"),
  gradeGrid: document.querySelector("#grade-grid"),
  timelineTrack: document.querySelector("#timeline-track"),
  autoplayIndicator: document.querySelector("#autoplay-indicator"),
  actionHeadline: document.querySelector("#action-headline"),
  actionNotes: document.querySelector("#action-notes"),
  incidentCount: document.querySelector("#incident-count"),
  incidentList: document.querySelector("#incident-list"),
  resourceCount: document.querySelector("#resource-count"),
  resourceList: document.querySelector("#resource-list"),
  eventList: document.querySelector("#event-list"),
  prevTurn: document.querySelector("#prev-turn"),
  nextTurn: document.querySelector("#next-turn"),
  autoPlay: document.querySelector("#auto-play"),
  resetSession: document.querySelector("#reset-session"),
  stepSession: document.querySelector("#step-session"),
  difficultySelect: document.querySelector("#difficulty-select"),
  policySelect: document.querySelector("#policy-select"),
  seedInput: document.querySelector("#seed-input"),
  difficultyPill: document.querySelector("#difficulty-pill"),
  sessionState: document.querySelector("#session-state"),
  sessionDetail: document.querySelector("#session-detail"),
  statusNotice: document.querySelector("#status-notice"),
  statusNoteTitle: document.querySelector("#status-note-title"),
  statusNoteBody: document.querySelector("#status-note-body"),
  statusNoteMeta: document.querySelector("#status-note-meta"),
  logMode: document.querySelector("#log-mode"),
  visualScenarioTitle: document.querySelector("#visual-scenario-title"),
  visualPrioritySignal: document.querySelector("#visual-priority-signal"),
  visualWinningMove: document.querySelector("#visual-winning-move"),
};

async function init() {
  syncAuthUi();
  bindControls();
  renderLoadingState();

  try {
    const manifest = await api("/api/manifest");
    state.manifest = manifest;
    state.offlineMode = false;
    hydrateControls(manifest);

    const defaultIndex = manifest.scenarios.findIndex(
      (scenario) => scenario.id === manifest.default_scenario,
    );
    state.scenarioIndex = defaultIndex >= 0 ? defaultIndex : 0;
    elements.difficultySelect.value = manifest.default_difficulty;
    elements.policySelect.value = manifest.policies[0]?.id ?? "fairness_aware";

    renderScenarioTabs();
    await resetSession();
  } catch (error) {
    activateOfflineMode(error.message);
  }
}

function bindControls() {
  elements.logoutButton?.addEventListener("click", () => {
    clearAuthSession();
    syncAuthUi();
  });
  elements.prevTurn.addEventListener("click", () => browseHistory(-1));
  elements.nextTurn.addEventListener("click", () => browseHistory(1));
  elements.autoPlay.addEventListener("click", toggleAutoplay);
  elements.resetSession.addEventListener("click", () => {
    stopAutoplay();
    resetSession();
  });
  elements.stepSession.addEventListener("click", () => {
    stopAutoplay();
    runLiveStep();
  });
}

function hydrateControls(manifest) {
  elements.difficultySelect.innerHTML = manifest.difficulties
    .map((difficulty) => `<option value="${difficulty}">${labelize(difficulty)}</option>`)
    .join("");

  elements.policySelect.innerHTML = manifest.policies
    .map((policy) => `<option value="${policy.id}">${policy.label}</option>`)
    .join("");
}

function renderScenarioTabs() {
  if (!state.manifest) {
    return;
  }

  elements.tabs.innerHTML = "";
  state.manifest.scenarios.forEach((scenario, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "scenario-tab";
    button.innerHTML = `<span>${scenario.label}</span><span>${scenario.horizon} turns</span>`;
    button.addEventListener("click", async () => {
      if (state.busy) {
        return;
      }
      stopAutoplay();
      state.scenarioIndex = index;
      renderScenarioTabs();
      await resetSession();
    });
    if (index === state.scenarioIndex) {
      button.classList.add("active");
    }
    elements.tabs.appendChild(button);
  });
}

async function resetSession() {
  if (!state.manifest) {
    return;
  }
  if (state.offlineMode) {
    resetOfflineSession();
    return;
  }

  setBusy(true);
  const scenario = state.manifest.scenarios[state.scenarioIndex];
  const payload = {
    scenario_id: scenario.id,
    difficulty: elements.difficultySelect.value,
    seed: Number(elements.seedInput.value || 7),
    policy: elements.policySelect.value,
  };

  try {
    const response = await api("/api/sessions", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    state.sessionId = response.session_id;
    state.snapshots = [response.snapshot];
    state.historyIndex = 0;
    render();
  } catch (error) {
    renderErrorState(error.message);
  } finally {
    setBusy(false);
  }
}

async function runLiveStep() {
  if (state.offlineMode) {
    runOfflineStep();
    return;
  }
  if (!state.sessionId || state.busy) {
    return;
  }

  setBusy(true);
  state.historyIndex = Math.max(0, state.snapshots.length - 1);

  try {
    const response = await api(`/api/sessions/${state.sessionId}/step`, {
      method: "POST",
      body: JSON.stringify({ policy: elements.policySelect.value }),
    });

    const snapshot = response.snapshot;
    const lastSnapshot = state.snapshots[state.snapshots.length - 1];
    const isNewTurn =
      !lastSnapshot ||
      snapshot.turn !== lastSnapshot.turn ||
      snapshot.reward_total !== lastSnapshot.reward_total;

    if (isNewTurn) {
      state.snapshots.push(snapshot);
      state.historyIndex = state.snapshots.length - 1;
    } else {
      state.snapshots[state.snapshots.length - 1] = snapshot;
      state.historyIndex = state.snapshots.length - 1;
    }

    render();
    if (snapshot.done) {
      stopAutoplay();
    }
  } catch (error) {
    stopAutoplay();
    renderErrorState(error.message);
  } finally {
    setBusy(false);
  }
}

function browseHistory(direction) {
  if (!state.snapshots.length) {
    return;
  }
  state.historyIndex = clamp(state.historyIndex + direction, 0, state.snapshots.length - 1);
  render();
}

function toggleAutoplay() {
  if (state.autoplayTimer) {
    stopAutoplay();
    render();
    return;
  }
  if (!state.sessionId) {
    return;
  }
  state.autoplayTimer = window.setInterval(async () => {
    if (state.busy) {
      return;
    }
    await runLiveStep();
  }, 1800);
  render();
}

function stopAutoplay() {
  if (state.autoplayTimer) {
    window.clearInterval(state.autoplayTimer);
    state.autoplayTimer = null;
  }
}

function readAuthSession() {
  try {
    const raw = window.localStorage.getItem(AUTH_SESSION_KEY);
    if (!raw) {
      return null;
    }
    const parsed = JSON.parse(raw);
    if (!parsed || (parsed.role !== "admin" && parsed.role !== "user")) {
      return null;
    }
    return parsed;
  } catch (error) {
    return null;
  }
}

function clearAuthSession() {
  window.localStorage.removeItem(AUTH_SESSION_KEY);
}

function syncAuthUi() {
  const session = readAuthSession();
  const isLoggedIn = Boolean(session);

  elements.authEntry?.classList.toggle("hidden", isLoggedIn);
  elements.adminLoginLink?.classList.toggle("hidden", isLoggedIn);
  elements.userLoginLink?.classList.toggle("hidden", isLoggedIn);
  elements.heroAdminLink?.classList.toggle("hidden", isLoggedIn);
  elements.heroUserLink?.classList.toggle("hidden", isLoggedIn);
  elements.authChip?.classList.toggle("hidden", !isLoggedIn);
  elements.logoutButton?.classList.toggle("hidden", !isLoggedIn);

  if (session && elements.authChip) {
    elements.authChip.textContent = `${labelize(session.role)} logged in`;
  }
}

function render() {
  if (!state.manifest || !state.snapshots.length) {
    return;
  }

  renderScenarioTabs();

  const scenario = state.manifest.scenarios[state.scenarioIndex];
  const snapshot = state.snapshots[state.historyIndex];
  const latestSnapshot = state.snapshots[state.snapshots.length - 1];
  const isLatest = snapshot === latestSnapshot;

  elements.title.textContent = snapshot.scenario_title || scenario.title;
  elements.description.textContent = snapshot.scenario_description || scenario.description;
  elements.objectives.innerHTML = `<li>${snapshot.scenario_objective || scenario.objective}</li>`;
  elements.budget.textContent = `${snapshot.budget_remaining} command points left`;
  elements.horizon.textContent = `${snapshot.max_turns} turns`;
  elements.zones.textContent = snapshot.zones.join(", ");
  elements.turnReadout.textContent = `turn ${snapshot.turn}/${snapshot.max_turns}`;
  elements.rewardTotal.innerHTML = `${snapshot.reward_total.toFixed(1)}<small>Step reward ${formatSigned(snapshot.step_reward)}</small>`;
  elements.verdict.textContent = snapshot.verdict;
  elements.actionHeadline.textContent = snapshot.action_headline;
  elements.actionNotes.textContent = snapshot.action_notes;
  elements.autoplayIndicator.textContent = state.autoplayTimer ? "auto" : "manual";
  elements.difficultyPill.textContent = snapshot.difficulty;
  elements.logMode.textContent = isLatest ? "live backend session" : "history replay";

  renderSessionBanner(snapshot, isLatest);
  renderHero(snapshot);
  renderScoreBars(snapshot.reward_signals);
  renderGradeGrid(snapshot.grade, snapshot.metrics);
  renderTimeline();
  renderIncidents(snapshot.incidents);
  renderResources(snapshot.resources);
  renderEvents(snapshot.events);
}

function renderSessionBanner(snapshot, isLatest) {
  const mode = state.offlineMode
    ? "Offline preview"
    : snapshot.done
      ? "Complete"
      : isLatest
        ? "Live session"
        : "Snapshot";
  const detail = [
    `Session ${snapshot.session_id.slice(0, 8)}`,
    `Policy ${labelize(snapshot.policy)}`,
    `Clock ${snapshot.clock_minutes} min`,
  ].join(" | ");

  elements.sessionState.textContent = mode;
  elements.sessionDetail.textContent = detail;
  hideStatusNotice();
}

function renderHero(snapshot) {
  elements.visualScenarioTitle.textContent = snapshot.scenario_title;
  elements.visualPrioritySignal.textContent = buildPrioritySignal(snapshot);
  elements.visualWinningMove.textContent = snapshot.action_headline;
}

function renderScoreBars(bars) {
  elements.scoreBars.innerHTML = bars
    .map(
      (bar) => `
        <article class="bar-row">
          <header><span>${bar.label}</span><strong>${bar.value}</strong></header>
          <div class="bar-track"><div class="bar-fill" style="width:${bar.percent}%"></div></div>
        </article>
      `,
    )
    .join("");
}

function renderGradeGrid(grade, metrics) {
  const rows = [
    ...Object.entries(grade).map(([label, value]) => ({
      label: labelize(label),
      value,
    })),
    { label: "Resolved", value: metrics.resolved },
    { label: "Hospital Overflow", value: metrics.hospital_overflow },
  ];

  elements.gradeGrid.innerHTML = rows
    .map(
      (row) => `
        <article class="grade-row">
          <span>${row.label}</span>
          <strong>${row.value}</strong>
        </article>
      `,
    )
    .join("");
}

function renderTimeline() {
  elements.timelineTrack.style.setProperty("--turn-count", state.snapshots.length || 1);
  elements.timelineTrack.innerHTML = state.snapshots
    .map(
      (_, index) => `
        <button
          class="timeline-node ${index === state.historyIndex ? "active" : index < state.historyIndex ? "completed" : ""}"
          type="button"
          aria-label="Go to snapshot ${index}"
          data-index="${index}"
        ></button>
      `,
    )
    .join("");

  elements.timelineTrack.querySelectorAll(".timeline-node").forEach((node) => {
    node.addEventListener("click", () => {
      state.historyIndex = Number(node.dataset.index);
      render();
    });
  });
}

function renderIncidents(incidents) {
  elements.incidentCount.textContent = `${incidents.length} tracked`;
  elements.incidentList.innerHTML = incidents
    .map(
      (incident) => `
        <article class="incident-card ${incident.tone}">
          <header>
            <strong>${incident.id} | ${incident.title}</strong>
            <span class="pill">${incident.zone}</span>
          </header>
          <p class="incident-meta">Severity ${incident.severity} | ${incident.status}</p>
          <p class="incident-meta">${incident.meta}</p>
        </article>
      `,
    )
    .join("");
}

function renderResources(resources) {
  elements.resourceCount.textContent = `${resources.length} active assets`;
  elements.resourceList.innerHTML = resources
    .map(
      (resource) => `
        <article class="resource-card">
          <header>
            <strong>${resource.id}</strong>
            <span class="pill resource-status">${resource.status}</span>
          </header>
          <p class="resource-meta">${resource.type} | ${resource.zone}</p>
          <p class="resource-meta">${resource.meta}</p>
        </article>
      `,
    )
    .join("");
}

function renderEvents(events) {
  elements.eventList.innerHTML = events
    .map(
      (event) => `
        <article class="event-card">
          <strong>${event.title}</strong>
          <p>${event.body}</p>
        </article>
      `,
    )
    .join("");
}

function renderLoadingState() {
  elements.sessionState.textContent = "Connecting to backend...";
  elements.sessionDetail.textContent = `Backend: ${state.apiBase}`;
  showStatusNotice("Connecting", "Trying to reach the backend API.", state.apiBase);
}

function renderErrorState(message) {
  const error = describeMessage(message, "backend");
  elements.sessionState.textContent = "Backend unavailable";
  elements.sessionDetail.textContent = error.detail;
  elements.actionHeadline.textContent = "Run python -m server.app";
  elements.actionNotes.textContent = error.action;
  elements.eventList.innerHTML = `
    <article class="event-card">
      <strong>${escapeHtml(error.title)}</strong>
      <p>${escapeHtml(error.detail)}</p>
    </article>
  `;
  showStatusNotice(error.title, error.action, error.meta);
}

function activateOfflineMode(message) {
  state.offlineMode = true;
  state.manifest = buildFallbackManifest();
  state.scenarioIndex = 0;
  hydrateControls(state.manifest);
  elements.difficultySelect.value = state.manifest.default_difficulty;
  elements.policySelect.value = state.manifest.policies[0]?.id ?? "fairness_aware";
  renderScenarioTabs();
  resetOfflineSession();
  const error = describeMessage(message, "backend");
  showStatusNotice(
    "Offline preview",
    "Live backend is not available, so the dashboard is showing built-in sample data.",
    error.detail,
  );
}

function resetOfflineSession() {
  const scenario = fallbackScenarios[state.scenarioIndex];
  const policy = elements.policySelect.value || "fairness_aware";
  const difficulty = elements.difficultySelect.value || "advanced";
  state.sessionId = `offline-${scenario.id}`;
  state.snapshots = scenario.snapshots.map((snapshot, index) =>
    buildOfflineSnapshot(scenario, snapshot, index, difficulty, policy),
  );
  state.historyIndex = 0;
  render();
}

function runOfflineStep() {
  if (!state.snapshots.length) {
    return;
  }
  state.historyIndex = Math.min(state.historyIndex + 1, state.snapshots.length - 1);
  if (state.historyIndex >= state.snapshots.length - 1) {
    stopAutoplay();
  }
  render();
}

function setBusy(value) {
  state.busy = value;
  elements.resetSession.disabled = value;
  elements.stepSession.disabled = value;
  elements.autoPlay.disabled = value && !state.autoplayTimer;
}

async function api(path, options = {}) {
  let response;
  try {
    response = await fetch(buildApiUrl(path), {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      ...options,
    });
  } catch (error) {
    throw new Error(`Could not reach backend at ${state.apiBase}`);
  }

  let payload = null;
  try {
    payload = await response.json();
  } catch (error) {
    payload = null;
  }

  if (!response.ok) {
    if (
      response.status === 404 &&
      state.apiBase === window.location.origin &&
      window.location.origin !== "http://127.0.0.1:8000"
    ) {
      state.apiBase = "http://127.0.0.1:8000";
      return api(path, options);
    }
    const detail =
      payload?.detail || `Request failed with status ${response.status} from ${buildApiUrl(path)}`;
    throw new Error(detail);
  }

  return payload;
}

function resolveApiBase() {
  const params = new URLSearchParams(window.location.search);
  const explicitBase = params.get("api");
  if (explicitBase) {
    return explicitBase.replace(/\/+$/, "");
  }
  if (window.location.protocol === "file:") {
    return "http://127.0.0.1:8000";
  }
  if (window.location.hostname.endsWith("github.io")) {
    return "http://127.0.0.1:8000";
  }
  return window.location.origin;
}

function buildApiUrl(path) {
  const normalizedBase = state.apiBase.replace(/\/+$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${normalizedBase}${normalizedPath}`;
}

function buildPrioritySignal(snapshot) {
  const active = snapshot.incidents.find((incident) => incident.tone === "critical") || snapshot.incidents[0];
  if (!active) {
    return "No active incidents. City stabilized.";
  }
  return `${active.id} is the current priority in ${active.zone}.`;
}

function buildFallbackManifest() {
  return {
    name: "crisis_commander_env",
    default_scenario: fallbackScenarios[0].id,
    default_difficulty: "advanced",
    difficulties: ["easy", "standard", "advanced", "expert"],
    policies: [
      { id: "fairness_aware", label: "Fairness-Aware Baseline" },
      { id: "severity_first", label: "Severity-First Baseline" },
    ],
    scenarios: fallbackScenarios.map((scenario) => ({
      id: scenario.id,
      label: scenario.label,
      title: scenario.title,
      description: scenario.description,
      objective: scenario.objective,
      budget: scenario.budget,
      horizon: scenario.horizon,
      zones: scenario.zones,
    })),
  };
}

function buildOfflineSnapshot(scenario, snapshot, index, difficulty, policy) {
  return {
    session_id: `offline-${scenario.id}`,
    scenario_id: scenario.id,
    scenario_title: scenario.title,
    scenario_description: scenario.description,
    scenario_objective: scenario.objective,
    difficulty,
    seed: 7,
    policy,
    policy_label: labelize(policy),
    turn: snapshot.turn,
    max_turns: scenario.horizon,
    clock_minutes: snapshot.clock_minutes,
    budget_remaining: scenario.budget,
    summary: snapshot.summary,
    done: index === scenario.snapshots.length - 1,
    step_reward: snapshot.step_reward,
    reward_total: snapshot.reward_total,
    reward_signals: snapshot.reward_signals,
    verdict: snapshot.verdict,
    grade: snapshot.grade,
    metrics: snapshot.metrics,
    action_headline: snapshot.action_headline,
    action_notes: snapshot.action_notes,
    incidents: snapshot.incidents,
    resources: snapshot.resources,
    events: snapshot.events,
    zones: scenario.zones,
  };
}

function labelize(value) {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function formatSigned(value) {
  const numeric = Number(value || 0);
  return `${numeric >= 0 ? "+" : ""}${numeric.toFixed(1)}`;
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function showStatusNotice(title, body, meta = "") {
  elements.statusNoteTitle.textContent = title;
  elements.statusNoteBody.textContent = body;
  elements.statusNoteMeta.textContent = meta;
  elements.statusNoteMeta.classList.toggle("hidden", !meta);
  elements.statusNotice.classList.remove("hidden");
}

function hideStatusNotice() {
  elements.statusNotice.classList.add("hidden");
}

function describeMessage(message, source = "backend") {
  const text = String(message || "").trim();
  const lowered = text.toLowerCase();

  if (!text) {
    return {
      title: "Request failed",
      detail: "The operation did not complete.",
      action: "Retry the action.",
      meta: "",
    };
  }

  if (lowered.includes("could not reach backend")) {
    return {
      title: "Backend not reachable",
      detail: "The browser could not connect to the API server.",
      action: "Start the server with `python -m server.app`, then refresh the page.",
      meta: state.apiBase,
    };
  }

  if (lowered.includes("status 404")) {
    return {
      title: "API route not found",
      detail: "The page reached a server, but the required API endpoint was not available.",
      action: "Open the app from `http://127.0.0.1:8000/` after the backend starts.",
      meta: text,
    };
  }

  if (lowered.includes("ui assets are missing")) {
    return {
      title: "UI assets missing",
      detail: "The deployment is missing the frontend files required by the app.",
      action: "Rebuild and redeploy the project.",
      meta: "",
    };
  }

  return {
    title: "Request failed",
    detail: text,
    action: "Retry the action after checking the backend.",
    meta: "",
  };
}

init();
