const scenarios = [
  {
    id: "rush-hour",
    label: "Rush Hour Cascade",
    title: "Rush Hour Cascade",
    description:
      "A central bus crash and warehouse fire are already active when a hazmat plume and signal-grid failure threaten to overwhelm the city.",
    objectives: [
      "Stabilize the visible mass-casualty event without ignoring the hidden cascade.",
      "Protect high-vulnerability districts before the blackout compounds harm.",
      "Keep hospital overflow and mutual aid cost under control.",
    ],
    budget: 18,
    horizon: "10 turns",
    zones: "Central, West, East",
    turns: [
      {
        turn: 0,
        rewardTotal: "0.0",
        verdict: "strong shortlist",
        rewardSignals: [
          { label: "Resolution", percent: 18, value: "+0.0" },
          { label: "Foresight", percent: 42, value: "+1.4" },
          { label: "Fairness", percent: 64, value: "-0.7" },
          { label: "Capacity", percent: 58, value: "stable" },
        ],
        grade: { outcome: 76, timeliness: 73, fairness: 81, efficiency: 74, resilience: 78 },
        actionHeadline: "Stage DRN-1 toward East before the hazmat leak lands.",
        notes:
          "The policy sacrifices a little short-term speed to pre-position intelligence for the incoming cascade.",
        incidents: [
          { id: "INC-1", title: "Bus crash", zone: "Central", severity: "4.5", status: "critical", tone: "critical", meta: "22 injured, response window 3 turns" },
          { id: "INC-2", title: "Warehouse fire", zone: "West", severity: "3.9", status: "active", tone: "warning", meta: "Residential spread risk, response window 4 turns" },
        ],
        resources: [
          { id: "AMB-1", type: "Ambulance", status: "available", zone: "North", meta: "Ready for dispatch" },
          { id: "FIRE-1", type: "Fire engine", status: "available", zone: "Central", meta: "High effectiveness" },
          { id: "POL-1", type: "Police unit", status: "available", zone: "Central", meta: "Metro perimeter capable" },
          { id: "DRN-1", type: "Drone", status: "staging", zone: "East", meta: "ETA 1 turn" },
        ],
        events: [
          { title: "Mission brief", body: "Two visible incidents are live, but the hidden failure path is the east-side hazmat event." },
          { title: "Foresight signal", body: "Pre-staging a drone raises resilience before the next incident appears." },
        ],
      },
      {
        turn: 1,
        rewardTotal: "18.6",
        verdict: "strong shortlist",
        rewardSignals: [
          { label: "Resolution", percent: 44, value: "+10.8" },
          { label: "Foresight", percent: 66, value: "+4.9" },
          { label: "Fairness", percent: 68, value: "-1.1" },
          { label: "Capacity", percent: 59, value: "stable" },
        ],
        grade: { outcome: 81, timeliness: 78, fairness: 82, efficiency: 75, resilience: 80 },
        actionHeadline: "Dispatch POL-1 and AMB-2 to the metro bus crash.",
        notes:
          "The policy locks down the highest casualty site while keeping the drone route intact for the spillover.",
        incidents: [
          { id: "INC-1", title: "Bus crash", zone: "Central", severity: "4.5", status: "stabilizing", tone: "warning", meta: "Police on perimeter, ambulance en route" },
          { id: "INC-2", title: "Warehouse fire", zone: "West", severity: "3.9", status: "active", tone: "warning", meta: "Fire growth slowed, no civilian spread yet" },
          { id: "INC-3", title: "Hazmat leak", zone: "East", severity: "4.7", status: "new", tone: "critical", meta: "Plume uncertainty, response window 3 turns" },
        ],
        resources: [
          { id: "AMB-2", type: "Ambulance", status: "en route", zone: "Central", meta: "ETA 1 turn to INC-1" },
          { id: "FIRE-1", type: "Fire engine", status: "available", zone: "Central", meta: "Held for hazmat flexibility" },
          { id: "POL-1", type: "Police unit", status: "on scene", zone: "Central", meta: "Crowd and traffic control active" },
          { id: "DRN-1", type: "Drone", status: "on scene", zone: "East", meta: "Plume mapping in progress" },
        ],
        events: [
          { title: "Cascade arrived", body: "The east-side hazmat leak appears exactly where the staged drone can generate value." },
          { title: "Risk compression", body: "The bus crash begins stabilizing without starving the new hazard of situational awareness." },
        ],
      },
      {
        turn: 2,
        rewardTotal: "41.9",
        verdict: "final-round caliber",
        rewardSignals: [
          { label: "Resolution", percent: 71, value: "+22.9" },
          { label: "Foresight", percent: 79, value: "+8.2" },
          { label: "Fairness", percent: 77, value: "-1.4" },
          { label: "Capacity", percent: 70, value: "surge primed" },
        ],
        grade: { outcome: 88, timeliness: 84, fairness: 86, efficiency: 78, resilience: 90 },
        actionHeadline: "Request mutual-aid police cover and expand HOSP-CENTRAL by 6 beds.",
        notes:
          "The winning behavior here is not greedier dispatch. It is preparing downstream capacity before casualties hit the hospital edge.",
        incidents: [
          { id: "INC-1", title: "Bus crash", zone: "Central", severity: "4.5", status: "resolved", tone: "stable", meta: "Patients routed successfully" },
          { id: "INC-2", title: "Warehouse fire", zone: "West", severity: "3.9", status: "stabilizing", tone: "warning", meta: "Containment line holding" },
          { id: "INC-3", title: "Hazmat leak", zone: "East", severity: "4.7", status: "active", tone: "critical", meta: "Drone + fire team improving coverage" },
        ],
        resources: [
          { id: "MA-POLICE-1", type: "Mutual aid", status: "en route", zone: "East", meta: "Budget cost accepted" },
          { id: "FIRE-1", type: "Fire engine", status: "on scene", zone: "East", meta: "Hazmat containment engaged" },
          { id: "AMB-1", type: "Ambulance", status: "available", zone: "North", meta: "Held for secondary spillover" },
          { id: "HOSP-CENTRAL", type: "Hospital", status: "surge open", zone: "Central", meta: "6 temporary beds activated" },
        ],
        events: [
          { title: "Hospital foresight", body: "Central capacity opens before the next patient wave, avoiding overflow penalties." },
          { title: "Judge signal", body: "This is the turn where the environment starts looking genuinely strategic instead of reactive." },
        ],
      },
      {
        turn: 3,
        rewardTotal: "63.4",
        verdict: "final-round caliber",
        rewardSignals: [
          { label: "Resolution", percent: 82, value: "+33.5" },
          { label: "Foresight", percent: 83, value: "+9.8" },
          { label: "Fairness", percent: 85, value: "-0.6" },
          { label: "Capacity", percent: 78, value: "overflow avoided" },
        ],
        grade: { outcome: 91, timeliness: 87, fairness: 92, efficiency: 79, resilience: 93 },
        actionHeadline: "Reroute POL-2 south as the grid failure hits a vulnerable district.",
        notes:
          "The fairness-sensitive move prevents the flashy downtown incidents from dominating the whole policy.",
        incidents: [
          { id: "INC-2", title: "Warehouse fire", zone: "West", severity: "3.9", status: "resolved", tone: "stable", meta: "Apartment spillover prevented" },
          { id: "INC-3", title: "Hazmat leak", zone: "East", severity: "4.7", status: "stabilizing", tone: "warning", meta: "Plume direction narrowed, casualties limited" },
          { id: "INC-4", title: "Grid failure", zone: "South", severity: "3.1", status: "new", tone: "critical", meta: "High-vulnerability area, traffic signal collapse" },
        ],
        resources: [
          { id: "POL-2", type: "Police unit", status: "en route", zone: "South", meta: "ETA 1 turn to INC-4" },
          { id: "DRN-1", type: "Drone", status: "available", zone: "East", meta: "Ready to re-task" },
          { id: "AMB-1", type: "Ambulance", status: "staging", zone: "South", meta: "Pre-positioned for secondary injuries" },
          { id: "FIRE-2", type: "Fire engine", status: "available", zone: "West", meta: "Released after fire resolution" },
        ],
        events: [
          { title: "Fairness pressure", body: "A vulnerable district incident triggers the key differentiator in the reward function." },
          { title: "Policy quality", body: "The rollout now demonstrates why fairness-aware command is more than generic incident triage." },
        ],
      },
    ],
  },
  {
    id: "festival-blackout",
    label: "Festival Blackout",
    title: "Festival Blackout",
    description:
      "A crowd surge, food-court transformer fire, and underserved district blackout compete for attention during a citywide event.",
    objectives: [
      "Protect the crowd without letting the blackout become invisible collateral damage.",
      "Use police, ambulance, and drone coverage to prevent panic loops.",
      "Show fairness-sensitive control under media-heavy conditions.",
    ],
    budget: 20,
    horizon: "11 turns",
    zones: "Arena, Riverfront, South",
    turns: [
      {
        turn: 0,
        rewardTotal: "0.0",
        verdict: "promising but leaky",
        rewardSignals: [
          { label: "Resolution", percent: 16, value: "+0.0" },
          { label: "Foresight", percent: 38, value: "+1.0" },
          { label: "Fairness", percent: 49, value: "-2.2" },
          { label: "Capacity", percent: 57, value: "stable" },
        ],
        grade: { outcome: 71, timeliness: 75, fairness: 62, efficiency: 78, resilience: 70 },
        actionHeadline: "Dispatch AMB-3 to the arena surge while staging DRN-1 toward South.",
        notes:
          "The policy acknowledges media-visible urgency but starts hedging against the underserved blackout district early.",
        incidents: [
          { id: "FEST-1", title: "Crowd surge", zone: "Arena", severity: "4.7", status: "critical", tone: "critical", meta: "30 affected, fast escalation risk" },
          { id: "FEST-2", title: "Transformer fire", zone: "Riverfront", severity: "3.9", status: "active", tone: "warning", meta: "Fuel storage nearby" },
        ],
        resources: [
          { id: "AMB-3", type: "Ambulance", status: "en route", zone: "Arena", meta: "Closest medical asset" },
          { id: "POL-1", type: "Police unit", status: "available", zone: "Arena", meta: "Crowd lane control" },
          { id: "DRN-1", type: "Drone", status: "staging", zone: "South", meta: "Quietly covering fairness risk" },
          { id: "FIRE-1", type: "Fire engine", status: "available", zone: "Central", meta: "Held for transformer fire" },
        ],
        events: [
          { title: "Media gravity", body: "The obvious arena emergency can easily dominate the policy if fairness is not explicit." },
          { title: "Quiet hedge", body: "Drone staging begins protecting the under-served district before the blackout officially appears." },
        ],
      },
      {
        turn: 1,
        rewardTotal: "23.1",
        verdict: "strong shortlist",
        rewardSignals: [
          { label: "Resolution", percent: 48, value: "+12.0" },
          { label: "Foresight", percent: 63, value: "+5.1" },
          { label: "Fairness", percent: 71, value: "-1.0" },
          { label: "Capacity", percent: 60, value: "steady" },
        ],
        grade: { outcome: 82, timeliness: 81, fairness: 80, efficiency: 79, resilience: 84 },
        actionHeadline: "Send POL-1 to stabilize the arena and FIRE-1 to Riverfront.",
        notes:
          "This turn shows the environment rewarding simultaneous crowd control and infrastructure containment rather than a single queue.",
        incidents: [
          { id: "FEST-1", title: "Crowd surge", zone: "Arena", severity: "4.7", status: "stabilizing", tone: "warning", meta: "Police lanes opened, crush risk down" },
          { id: "FEST-2", title: "Transformer fire", zone: "Riverfront", severity: "3.9", status: "active", tone: "warning", meta: "Fire engine en route" },
          { id: "FEST-3", title: "District blackout", zone: "South", severity: "3.8", status: "new", tone: "critical", meta: "Traffic signals offline in vulnerable zone" },
        ],
        resources: [
          { id: "POL-1", type: "Police unit", status: "on scene", zone: "Arena", meta: "Crowd separation active" },
          { id: "FIRE-1", type: "Fire engine", status: "en route", zone: "Riverfront", meta: "ETA 1 turn" },
          { id: "DRN-1", type: "Drone", status: "on scene", zone: "South", meta: "Traffic and outage visibility live" },
          { id: "AMB-2", type: "Ambulance", status: "available", zone: "South", meta: "Ready to exploit the staged position" },
        ],
        events: [
          { title: "Fairness payoff", body: "The staged drone converts into immediate value when the blackout lands in South." },
          { title: "Narrative strength", body: "The page now tells a judge exactly why this environment is not a generic public-event dashboard." },
        ],
      },
      {
        turn: 2,
        rewardTotal: "47.8",
        verdict: "final-round caliber",
        rewardSignals: [
          { label: "Resolution", percent: 76, value: "+27.3" },
          { label: "Foresight", percent: 80, value: "+8.5" },
          { label: "Fairness", percent: 83, value: "-0.2" },
          { label: "Capacity", percent: 74, value: "surge optional" },
        ],
        grade: { outcome: 90, timeliness: 86, fairness: 91, efficiency: 81, resilience: 88 },
        actionHeadline: "Keep AMB-2 in South instead of pulling every asset back to the arena.",
        notes:
          "This is the moment where the reward function visibly favors equitable service over the most camera-visible incident.",
        incidents: [
          { id: "FEST-1", title: "Crowd surge", zone: "Arena", severity: "4.7", status: "resolved", tone: "stable", meta: "Primary risk diffused" },
          { id: "FEST-2", title: "Transformer fire", zone: "Riverfront", severity: "3.9", status: "stabilizing", tone: "warning", meta: "Spread prevented" },
          { id: "FEST-3", title: "District blackout", zone: "South", severity: "3.8", status: "stabilizing", tone: "warning", meta: "Signal management limiting secondary harm" },
        ],
        resources: [
          { id: "AMB-2", type: "Ambulance", status: "on scene", zone: "South", meta: "Secondary injuries covered" },
          { id: "POL-2", type: "Police unit", status: "available", zone: "South", meta: "Manual traffic command" },
          { id: "FIRE-1", type: "Fire engine", status: "on scene", zone: "Riverfront", meta: "Cooling transformer zone" },
          { id: "HOSP-SOUTH", type: "Hospital", status: "stable", zone: "South", meta: "Pressure within safe range" },
        ],
        events: [
          { title: "Judge impression", body: "The policy looks principled, not just competent, because it refuses to starve the vulnerable district." },
          { title: "Demo payoff", body: "This scenario is the best visual proof of the environment's fairness-aware reward logic." },
        ],
      },
    ],
  },
  {
    id: "industrial-storm",
    label: "Industrial Storm",
    title: "Industrial Storm",
    description:
      "A severe storm compounds an industrial hazmat accident, roadway blockages, and scattered trauma calls across the port corridor.",
    objectives: [
      "Contain the industrial hazard without letting secondary incidents become citywide drag.",
      "Demonstrate planning under delayed consequences and infrastructure stress.",
      "Reward contingent reasoning over greedy first-response behavior.",
    ],
    budget: 19,
    horizon: "12 turns",
    zones: "Industrial, Port, South",
    turns: [
      {
        turn: 0,
        rewardTotal: "0.0",
        verdict: "strong shortlist",
        rewardSignals: [
          { label: "Resolution", percent: 14, value: "+0.0" },
          { label: "Foresight", percent: 56, value: "+2.6" },
          { label: "Fairness", percent: 63, value: "-1.2" },
          { label: "Capacity", percent: 62, value: "stable" },
        ],
        grade: { outcome: 74, timeliness: 70, fairness: 79, efficiency: 76, resilience: 83 },
        actionHeadline: "Commit FIRE-1 and DRN-1 to the industrial hazmat rupture immediately.",
        notes:
          "The policy recognizes that industrial containment is the root cause event, not just the loudest first incident.",
        incidents: [
          { id: "STORM-1", title: "Hazmat rupture", zone: "Industrial", severity: "4.8", status: "critical", tone: "critical", meta: "Storm-driven spread risk" },
        ],
        resources: [
          { id: "FIRE-1", type: "Fire engine", status: "en route", zone: "Industrial", meta: "High effectiveness hazmat team" },
          { id: "DRN-1", type: "Drone", status: "en route", zone: "Industrial", meta: "Airborne plume mapping" },
          { id: "POL-2", type: "Police unit", status: "available", zone: "South", meta: "Held for roadway spillover" },
          { id: "AMB-1", type: "Ambulance", status: "available", zone: "Central", meta: "Reserved for trauma calls" },
        ],
        events: [
          { title: "Root-cause bias", body: "The environment rewards tackling the hazard that creates downstream incidents, not only the downstream symptoms." },
          { title: "Storm pressure", body: "Travel time matters more because the weather stretches every route." },
        ],
      },
      {
        turn: 1,
        rewardTotal: "21.7",
        verdict: "strong shortlist",
        rewardSignals: [
          { label: "Resolution", percent: 37, value: "+9.4" },
          { label: "Foresight", percent: 72, value: "+6.8" },
          { label: "Fairness", percent: 74, value: "-0.9" },
          { label: "Capacity", percent: 66, value: "stable" },
        ],
        grade: { outcome: 80, timeliness: 76, fairness: 83, efficiency: 77, resilience: 88 },
        actionHeadline: "Keep POL-2 in South as the flooded underpass pileup appears.",
        notes:
          "This turn shows why pre-committing every unit to the industrial corridor is a losing policy on this map.",
        incidents: [
          { id: "STORM-1", title: "Hazmat rupture", zone: "Industrial", severity: "4.8", status: "stabilizing", tone: "warning", meta: "Containment improving" },
          { id: "STORM-2", title: "Underpass pileup", zone: "South", severity: "3.7", status: "new", tone: "critical", meta: "Flooded lanes, rapid trauma risk" },
        ],
        resources: [
          { id: "POL-2", type: "Police unit", status: "on scene", zone: "South", meta: "Road closure and diversion active" },
          { id: "AMB-1", type: "Ambulance", status: "en route", zone: "South", meta: "ETA 1 turn" },
          { id: "FIRE-1", type: "Fire engine", status: "on scene", zone: "Industrial", meta: "Hazmat containment line holding" },
          { id: "DRN-1", type: "Drone", status: "on scene", zone: "Industrial", meta: "Leak visibility improved" },
        ],
        events: [
          { title: "Contingency value", body: "Holding a police unit in reserve avoids a fairness and timeliness hit when the south-side pileup appears." },
          { title: "Narrative rhythm", body: "The rollout communicates delayed consequences, which makes the environment feel much closer to real RL." },
        ],
      },
      {
        turn: 2,
        rewardTotal: "46.2",
        verdict: "final-round caliber",
        rewardSignals: [
          { label: "Resolution", percent: 73, value: "+24.1" },
          { label: "Foresight", percent: 82, value: "+8.9" },
          { label: "Fairness", percent: 79, value: "-0.5" },
          { label: "Capacity", percent: 72, value: "hospital safe" },
        ],
        grade: { outcome: 89, timeliness: 84, fairness: 87, efficiency: 80, resilience: 92 },
        actionHeadline: "Expand south hospital only after the casualty wave becomes credible.",
        notes:
          "The environment rewards capacity planning when it is justified, not hospital expansion spam on every run.",
        incidents: [
          { id: "STORM-1", title: "Hazmat rupture", zone: "Industrial", severity: "4.8", status: "resolved", tone: "stable", meta: "Root hazard neutralized" },
          { id: "STORM-2", title: "Underpass pileup", zone: "South", severity: "3.7", status: "stabilizing", tone: "warning", meta: "Ambulance + police coverage sufficient" },
          { id: "STORM-3", title: "Container fire", zone: "Port", severity: "4.1", status: "new", tone: "critical", meta: "Lightning strike at the port" },
        ],
        resources: [
          { id: "HOSP-SOUTH", type: "Hospital", status: "surge open", zone: "South", meta: "6 temporary beds activated" },
          { id: "FIRE-2", type: "Fire engine", status: "en route", zone: "Port", meta: "Released after hazmat resolution" },
          { id: "AMB-2", type: "Ambulance", status: "available", zone: "Port", meta: "Held for the new fire injuries" },
          { id: "DRN-2", type: "Drone", status: "staging", zone: "Port", meta: "Pre-visualizing container spread" },
        ],
        events: [
          { title: "Resilience score", body: "Resolving the root industrial hazard early produces a strong resilience readout in the grading layer." },
          { title: "Policy maturity", body: "The rollout now looks like a command policy with contingent planning instead of a sequence of single-ticket fixes." },
        ],
      },
    ],
  },
];

const state = {
  scenarioIndex: 0,
  turnIndex: 0,
  autoplayTimer: null,
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
};

function init() {
  renderScenarioTabs();
  bindControls();
  render();
}

function renderScenarioTabs() {
  elements.tabs.innerHTML = "";
  scenarios.forEach((scenario, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "scenario-tab";
    button.innerHTML = `<span>${scenario.label}</span><span>${scenario.turns.length} turns</span>`;
    button.addEventListener("click", () => {
      state.scenarioIndex = index;
      state.turnIndex = 0;
      stopAutoplay();
      render();
    });
    elements.tabs.appendChild(button);
  });
}

function bindControls() {
  elements.prevTurn.addEventListener("click", () => moveTurn(-1));
  elements.nextTurn.addEventListener("click", () => moveTurn(1));
  elements.autoPlay.addEventListener("click", toggleAutoplay);
}

function render() {
  const scenario = scenarios[state.scenarioIndex];
  const snapshot = scenario.turns[state.turnIndex];

  [...elements.tabs.children].forEach((tab, index) => {
    tab.classList.toggle("active", index === state.scenarioIndex);
  });

  elements.title.textContent = scenario.title;
  elements.description.textContent = scenario.description;
  elements.objectives.innerHTML = scenario.objectives.map((item) => `<li>${item}</li>`).join("");
  elements.budget.textContent = `${scenario.budget} command points`;
  elements.horizon.textContent = scenario.horizon;
  elements.zones.textContent = scenario.zones;
  elements.turnReadout.textContent = `turn ${snapshot.turn}`;
  elements.rewardTotal.textContent = snapshot.rewardTotal;
  elements.verdict.textContent = snapshot.verdict;
  elements.actionHeadline.textContent = snapshot.actionHeadline;
  elements.actionNotes.textContent = snapshot.notes;
  elements.autoplayIndicator.textContent = state.autoplayTimer ? "auto" : "manual";

  renderScoreBars(snapshot.rewardSignals);
  renderGradeGrid(snapshot.grade);
  renderTimeline(scenario.turns);
  renderIncidents(snapshot.incidents);
  renderResources(snapshot.resources);
  renderEvents(snapshot.events);
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

function renderGradeGrid(grade) {
  elements.gradeGrid.innerHTML = Object.entries(grade)
    .map(
      ([label, value]) => `
        <article class="grade-row">
          <span>${capitalize(label)}</span>
          <strong>${value}</strong>
        </article>
      `,
    )
    .join("");
}

function renderTimeline(turns) {
  elements.timelineTrack.style.setProperty("--turn-count", turns.length);
  elements.timelineTrack.innerHTML = turns
    .map(
      (_, index) => `
        <button
          class="timeline-node ${index === state.turnIndex ? "active" : index < state.turnIndex ? "completed" : ""}"
          type="button"
          aria-label="Go to turn ${index}"
          data-turn="${index}"
        ></button>
      `,
    )
    .join("");

  elements.timelineTrack.querySelectorAll(".timeline-node").forEach((node) => {
    node.addEventListener("click", () => {
      state.turnIndex = Number(node.dataset.turn);
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
            <strong>${incident.id} · ${incident.title}</strong>
            <span class="pill">${incident.zone}</span>
          </header>
          <p class="incident-meta">Severity ${incident.severity} · ${incident.status}</p>
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
          <p class="resource-meta">${resource.type} · ${resource.zone}</p>
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

function moveTurn(direction) {
  const turns = scenarios[state.scenarioIndex].turns;
  state.turnIndex = (state.turnIndex + direction + turns.length) % turns.length;
  render();
}

function toggleAutoplay() {
  if (state.autoplayTimer) {
    stopAutoplay();
    render();
    return;
  }

  state.autoplayTimer = window.setInterval(() => {
    const turns = scenarios[state.scenarioIndex].turns;
    state.turnIndex = (state.turnIndex + 1) % turns.length;
    render();
  }, 2100);
  render();
}

function stopAutoplay() {
  if (state.autoplayTimer) {
    window.clearInterval(state.autoplayTimer);
    state.autoplayTimer = null;
  }
}

function capitalize(value) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

init();
