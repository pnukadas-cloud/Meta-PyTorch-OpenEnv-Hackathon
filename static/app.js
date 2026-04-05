const state = {
  manifest: null,
  scenarioIndex: 0,
  sessionId: null,
  snapshots: [],
  historyIndex: 0,
  autoplayTimer: null,
  busy: false,
  hfAdvisor: null,
};

const elements = {
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
  logMode: document.querySelector("#log-mode"),
  visualScenarioTitle: document.querySelector("#visual-scenario-title"),
  visualPrioritySignal: document.querySelector("#visual-priority-signal"),
  visualWinningMove: document.querySelector("#visual-winning-move"),
  askHf: document.querySelector("#ask-hf"),
  hfStatusPill: document.querySelector("#hf-status-pill"),
  hfModelPill: document.querySelector("#hf-model-pill"),
  hfTitle: document.querySelector("#hf-title"),
  hfDescription: document.querySelector("#hf-description"),
  hfOutput: document.querySelector("#hf-output"),
};

async function init() {
  bindControls();
  renderLoadingState();

  try {
    const manifest = await api("/api/manifest");
    state.manifest = manifest;
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
    renderErrorState(error.message);
  }
}

function bindControls() {
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
  elements.askHf.addEventListener("click", () => {
    requestHFAdvice();
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
    state.hfAdvisor = null;
    render();
  } catch (error) {
    renderErrorState(error.message);
  } finally {
    setBusy(false);
  }
}

async function runLiveStep() {
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

async function requestHFAdvice() {
  if (!state.sessionId || state.busy) {
    return;
  }

  setBusy(true);
  elements.hfStatusPill.textContent = "thinking";
  elements.hfOutput.innerHTML = `
    <article class="strategist-card">
      <h4>Generating advice</h4>
      <p>Sending the live simulator snapshot to the Hugging Face strategist model...</p>
    </article>
  `;

  try {
    const response = await api(`/api/sessions/${state.sessionId}/advisor`, {
      method: "POST",
      body: JSON.stringify({}),
    });
    state.hfAdvisor = response.advisor;
  } catch (error) {
    state.hfAdvisor = {
      configured: false,
      error: true,
      model: state.manifest?.hf?.model || "unavailable",
      provider: state.manifest?.hf?.provider || "auto",
      content: error.message,
    };
  } finally {
    setBusy(false);
    renderHFPanel();
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

function render() {
  if (!state.manifest || !state.snapshots.length) {
    renderHFPanel();
    return;
  }

  renderScenarioTabs();

  const scenario = state.manifest.scenarios[state.scenarioIndex];
  const snapshot = state.snapshots[state.historyIndex];
  const latestSnapshot = state.snapshots[state.snapshots.length - 1];
  const isLatest = snapshot === latestSnapshot;

  elements.title.textContent = snapshot.scenario_title || scenario.title;
  elements.description.textContent = snapshot.scenario_description || scenario.description;
  elements.objectives.innerHTML = [
    snapshot.scenario_objective || scenario.objective,
    snapshot.submission_story || scenario.submission_story,
  ]
    .map((item) => `<li>${item}</li>`)
    .join("");
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
  renderHFPanel();
}

function renderSessionBanner(snapshot, isLatest) {
  const mode = snapshot.done
    ? "Mission complete"
    : isLatest
      ? "Connected to live Python session"
      : "Viewing earlier snapshot";
  const detail = [
    `Session ${snapshot.session_id.slice(0, 8)}`,
    `Policy ${labelize(snapshot.policy)}`,
    `Clock ${snapshot.clock_minutes} min`,
  ].join(" | ");

  elements.sessionState.textContent = mode;
  elements.sessionDetail.textContent = detail;
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

function renderHFPanel() {
  const hf = state.manifest?.hf;
  const advisor = state.hfAdvisor;
  const configured = Boolean(hf?.configured);

  elements.hfStatusPill.textContent = advisor?.error
    ? "error"
    : advisor
      ? "ready"
      : configured
        ? "online"
        : "token needed";
  elements.hfModelPill.textContent = hf?.model || "model unavailable";
  elements.hfTitle.textContent = configured
    ? "Hugging Face command advisor is available"
    : "Connect a Hugging Face token to activate AI advice";
  elements.hfDescription.textContent = advisor?.error
    ? advisor.content
    : hf?.message ||
      "The app can call a real Hugging Face instruct model to interpret the live simulator state and suggest a next move.";

  if (advisor?.content && !advisor.error) {
    elements.hfOutput.innerHTML = `
      <article class="strategist-card">
        <h4>${escapeHtml(advisor.model)} via ${escapeHtml(advisor.provider)}</h4>
        <p>${escapeHtml(advisor.content)}</p>
      </article>
    `;
    return;
  }

  if (advisor?.error) {
    elements.hfOutput.innerHTML = `
      <article class="strategist-card">
        <h4>HF strategist unavailable</h4>
        <p>${escapeHtml(advisor.content)}</p>
      </article>
    `;
    return;
  }

  elements.hfOutput.innerHTML = `
    <article class="strategist-card">
      <h4>How to use it</h4>
      <p>${escapeHtml(
        configured
          ? "Click 'Ask HF Strategist' to send the current mission snapshot to the model and receive an actionable recommendation."
          : "Set HF_TOKEN or run `hf auth login` in the same environment as the server, then restart the app and click 'Ask HF Strategist'.",
      )}</p>
    </article>
  `;
}

function renderLoadingState() {
  elements.sessionState.textContent = "Connecting to backend...";
  elements.sessionDetail.textContent = "Start the FastAPI server, then reload this page if needed.";
  renderHFPanel();
}

function renderErrorState(message) {
  elements.sessionState.textContent = "Backend unavailable";
  elements.sessionDetail.textContent = message;
  elements.actionHeadline.textContent = "Run python -m server.app";
  elements.actionNotes.textContent =
    "Open the app from http://127.0.0.1:8000/ after the server starts so the UI can talk to the Python environment.";
  elements.eventList.innerHTML = `
    <article class="event-card">
      <strong>Connection error</strong>
      <p>${escapeHtml(message)}</p>
    </article>
  `;
  renderHFPanel();
}

function setBusy(value) {
  state.busy = value;
  elements.resetSession.disabled = value;
  elements.stepSession.disabled = value;
  elements.autoPlay.disabled = value && !state.autoplayTimer;
  elements.askHf.disabled = value;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  let payload = null;
  try {
    payload = await response.json();
  } catch (error) {
    payload = null;
  }

  if (!response.ok) {
    const detail = payload?.detail || `Request failed with status ${response.status}`;
    throw new Error(detail);
  }

  return payload;
}

function buildPrioritySignal(snapshot) {
  const active = snapshot.incidents.find((incident) => incident.tone === "critical") || snapshot.incidents[0];
  if (!active) {
    return "No active incidents. City stabilized.";
  }
  return `${active.id} is the current priority in ${active.zone}.`;
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

init();
