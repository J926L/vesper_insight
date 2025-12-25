import Database from "@tauri-apps/plugin-sql";

interface HighRiskFlow {
  id: number;
  src_ip: string;
  dst_ip: string;
  src_port: number;
  dst_port: number;
  proto: string;
  score: number;
  timestamp: number;
}

interface CountResult {
  count: number;
}

interface MaxScoreResult {
  max_score: number | null;
}

let db: Database | null = null;
let currentView = "dashboard";

async function init() {
  // Always setup navigation first so UI remains responsive even if DB fails
  setupNavigation();

  try {
    // Attempt to connect to the SQLite database
    db = await Database.load("sqlite:/home/j/projects/vesper_insight/src/brain/alerts.db");
    console.log("Database connected");
    startPolling();
  } catch (err) {
    console.warn("Database connection skipped or failed (common in non-Tauri browsers):", err);
  }
}

function setupNavigation() {
  const navItems = {
    "nav-dashboard": "dashboard",
    "nav-alerts": "alerts",
    "nav-models": "models",
    "nav-settings": "settings"
  };

  Object.entries(navItems).forEach(([id, view]) => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("click", () => switchView(view));
    }
  });
}

function switchView(viewName: string) {
  currentView = viewName;

  // Update Title
  const titleEl = document.getElementById("view-title");
  if (titleEl) {
    titleEl.textContent = viewName.charAt(0).toUpperCase() + viewName.slice(1);
  }

  // Toggle Views
  document.querySelectorAll(".view").forEach(el => {
    (el as HTMLElement).style.display = "none";
  });

  const targetView = document.getElementById(`view-${viewName}`);
  if (targetView) {
    targetView.style.display = "block";
  }

  // Update Sidebar UI
  document.querySelectorAll(".nav-item").forEach(el => el.classList.remove("active"));
  const activeNavItem = document.getElementById(`nav-${viewName}`);
  if (activeNavItem) {
    activeNavItem.classList.add("active");
  }

  console.log(`Switched to view: ${viewName}`);
}

async function fetchStats() {
  if (!db || currentView !== "dashboard") return;

  const totalRes = await db.select<CountResult[]>("SELECT COUNT(*) as count FROM high_risk_flows");
  const maxScoreRes = await db.select<MaxScoreResult[]>("SELECT MAX(score) as max_score FROM high_risk_flows");

  const totalEl = document.getElementById("stat-total");
  const alertsEl = document.getElementById("stat-alerts");
  const maxScoreEl = document.getElementById("stat-max-score");
  const statusDot = document.getElementById("status-dot");

  const totalRow = totalRes?.[0];
  if (totalRow) {
    if (totalEl) totalEl.textContent = totalRow.count.toString();
    if (alertsEl) alertsEl.textContent = totalRow.count.toString();
    if (statusDot) {
      statusDot.className = "status-normal";
      statusDot.style.backgroundColor = "var(--success)";
    }
  }

  const maxScoreRow = maxScoreRes?.[0];
  if (maxScoreEl && maxScoreRow) {
    maxScoreEl.textContent = (maxScoreRow.max_score ?? 0).toFixed(4);
  }
}

async function fetchAlerts() {
  if (!db || currentView !== "dashboard") return;

  const alerts = await db.select<HighRiskFlow[]>("SELECT * FROM high_risk_flows ORDER BY timestamp DESC LIMIT 10");
  const tbody = document.querySelector("#alerts-table tbody");
  if (!tbody) return;

  tbody.innerHTML = "";

  alerts.forEach(alert => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${new Date(alert.timestamp * 1000).toLocaleString()}</td>
      <td>${alert.src_ip} -> ${alert.dst_ip}</td>
      <td><span style="color: ${alert.score > 0.8 ? 'var(--danger)' : 'var(--warning)'}">${alert.score.toFixed(4)}</span></td>
      <td><span class="status-badge status-alert">ALERT</span></td>
    `;
    tbody.appendChild(row);
  });
}

function startPolling() {
  setInterval(() => {
    fetchStats();
    fetchAlerts();
  }, 2000);
}

window.addEventListener("DOMContentLoaded", () => {
  init();
});
