// Habit Tracker frontend: talks to the FastAPI backend with fetch().

const WEEKS = 13;

const list = document.getElementById("habits");
const template = document.getElementById("habit-template");
const errorBox = document.getElementById("error");
const emptyMsg = document.getElementById("empty");

// "2026-11-17" in the user's own timezone (toISOString() would use UTC).
function isoDate(d) {
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${mm}-${dd}`;
}

const today = new Date();
const TODAY = isoDate(today);

// Small wrapper: throws with the API's error message if the request fails.
async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(typeof body.detail === "string" ? body.detail : `Request failed (${res.status})`);
  }
  return res.status === 204 ? null : res.json();
}

function showError(err) {
  errorBox.textContent = err ? err.message : "";
  errorBox.hidden = !err;
}

// Build the 13-week grid. Columns are weeks, rows are Sunday..Saturday,
// and the last column is the current week (days after today are hidden).
function renderHeatmap(container, recentDays) {
  const done = new Set(recentDays);
  const start = new Date(today);
  start.setDate(start.getDate() - (WEEKS - 1) * 7 - today.getDay());

  container.replaceChildren();
  for (let i = 0; i < WEEKS * 7; i++) {
    const day = new Date(start);
    day.setDate(start.getDate() + i);
    const key = isoDate(day);

    const cell = document.createElement("div");
    cell.className = "cell";
    if (key > TODAY) cell.classList.add("future");
    else if (done.has(key)) cell.classList.add("on");
    cell.title = key;
    container.append(cell);
  }
}

function renderHabit(habit) {
  const item = template.content.firstElementChild.cloneNode(true);
  item.style.setProperty("--habit-color", habit.color);

  item.querySelector(".habit-name").textContent = habit.name;
  item.querySelector(".stats").textContent =
    `🔥 ${habit.current_streak} day streak · best ${habit.longest_streak}`;

  const check = item.querySelector(".check");
  check.classList.toggle("done", habit.done_today);
  check.title = habit.done_today ? "Undo today" : "Mark today as done";
  check.addEventListener("click", () => toggleToday(habit));

  item.querySelector(".delete").addEventListener("click", () => deleteHabit(habit));

  renderHeatmap(item.querySelector(".heatmap"), habit.recent_days);
  return item;
}

async function load() {
  try {
    const habits = await api(`/habits?today=${TODAY}`);
    list.replaceChildren(...habits.map(renderHabit));
    emptyMsg.hidden = habits.length > 0;
    showError(null);
  } catch (err) {
    showError(err);
  }
}

async function toggleToday(habit) {
  try {
    if (habit.done_today) {
      await api(`/habits/${habit.id}/checkin/${TODAY}`, { method: "DELETE" });
    } else {
      await api(`/habits/${habit.id}/checkin?day=${TODAY}`, { method: "POST" });
    }
    await load();
  } catch (err) {
    showError(err);
  }
}

async function deleteHabit(habit) {
  if (!confirm(`Delete "${habit.name}" and all its check-ins?`)) return;
  try {
    await api(`/habits/${habit.id}`, { method: "DELETE" });
    await load();
  } catch (err) {
    showError(err);
  }
}

document.getElementById("new-habit").addEventListener("submit", async (event) => {
  event.preventDefault(); // stop the browser from reloading the page
  const nameInput = document.getElementById("habit-name");
  const name = nameInput.value.trim();
  if (!name) return;
  try {
    await api("/habits", {
      method: "POST",
      body: JSON.stringify({ name, color: document.getElementById("habit-color").value }),
    });
    nameInput.value = "";
    await load();
  } catch (err) {
    showError(err);
  }
});

document.getElementById("today-label").textContent = today.toLocaleDateString(undefined, {
  weekday: "long", month: "long", day: "numeric",
});
load();
