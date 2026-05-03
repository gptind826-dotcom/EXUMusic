/* ─── Section navigation ──────────────────────────── */
const PAGE_TITLES = {
  dashboard:   ["Dashboard",        "EXU Music Bot Control Panel"],
  credentials: ["Credentials",      "Manage all bot environment variables"],
  images:      ["Bot Images",       "Change startup, ping and stream images"],
  session:     ["Generate Session", "Login with phone OTP to create a fresh assistant session"],
};

function showSection(name, linkEl) {
  document.querySelectorAll("[id^='section-']").forEach(el => el.style.display = "none");
  const sec = document.getElementById("section-" + name);
  if (sec) sec.style.display = "";
  document.querySelectorAll(".nav-item").forEach(el => el.classList.remove("active"));
  if (linkEl) linkEl.classList.add("active");
  const [title, sub] = PAGE_TITLES[name] || ["", ""];
  document.getElementById("page-heading").textContent = title;
  document.getElementById("page-sub").textContent = sub;
  if (name === "credentials" || name === "images") loadEnv();
}

/* ─── Clock ───────────────────────────────────────── */
function updateClock() {
  document.getElementById("clock").textContent = new Date().toUTCString().replace("GMT","UTC");
}

/* ─── Stats ───────────────────────────────────────── */
function setBar(id, pct) { const el=document.getElementById(id); if(el) el.style.width=Math.min(pct,100)+"%"; }
function setText(id, val) { const el=document.getElementById(id); if(el) el.textContent=val; }

async function fetchStats() {
  try {
    const res = await fetch("/api/stats");
    if (!res.ok) return;
    const d = await res.json();
    setText("uptime",       d.uptime);
    setText("cpu",          d.cpu + "%");
    setText("ram",          d.ram_used + " / " + d.ram_total + " GB");
    setText("disk",         d.disk_used + " / " + d.disk_total + " GB");
    setText("cpu-pct",      d.cpu + "%");
    setText("ram-pct",      d.ram_percent + "%");
    setText("disk-pct",     d.disk_percent + "%");
    setBar("cpu-bar",       d.cpu);
    setBar("ram-bar",       d.ram_percent);
    setBar("disk-bar",      d.disk_percent);
    setText("bot-name",      d.bot_name || "—");
    setText("bot-username",  d.bot_username || "—");
    setText("bot-status",    d.status.charAt(0).toUpperCase() + d.status.slice(1));
    const ownerDisplay = [d.owner_name, d.owner_username].filter(Boolean).join(" · ") || d.owner_id || "—";
    setText("bot-owner",     ownerDisplay);
    const asstDisplay  = [d.assistant_name, d.assistant_username].filter(Boolean).join(" · ") || (d.assistant_name ? d.assistant_name : "Not connected");
    setText("bot-assistant", asstDisplay);
    setText("python-ver",    "Python " + d.python);
    setText("platform",      d.platform);
    setText("last-refresh",  d.timestamp);
  } catch(e) { console.warn("Stats error:", e); }
}

/* ─── Credentials builder ─────────────────────────── */
let envData = [];

const IMAGE_KEYS = ["START_IMG_URL","PING_IMG_URL","STREAM_IMG_URL","YOUTUBE_IMG_URL",
                    "PLAYLIST_IMG_URL","STATS_IMG_URL","TELEGRAM_AUDIO_URL","TELEGRAM_VIDEO_URL",
                    "SOUNCLOUD_IMG_URL","SPOTIFY_ALBUM_IMG_URL","SPOTIFY_ARTIST_IMG_URL","SPOTIFY_PLAYLIST_IMG_URL"];

const IMAGE_LABELS = {
  START_IMG_URL:           "Startup / Welcome",
  PING_IMG_URL:            "Ping Command",
  STREAM_IMG_URL:          "Now Streaming",
  YOUTUBE_IMG_URL:         "YouTube Play",
  PLAYLIST_IMG_URL:        "Playlist",
  STATS_IMG_URL:           "Bot Stats",
  TELEGRAM_AUDIO_URL:      "Telegram Audio",
  TELEGRAM_VIDEO_URL:      "Telegram Video",
  SOUNCLOUD_IMG_URL:       "SoundCloud Play",
  SPOTIFY_ALBUM_IMG_URL:   "Spotify Album",
  SPOTIFY_ARTIST_IMG_URL:  "Spotify Artist",
  SPOTIFY_PLAYLIST_IMG_URL:"Spotify Playlist",
};

async function loadEnv() {
  try {
    const res = await fetch("/api/env");
    envData = await res.json();
    renderCredentials();
    renderImages();
  } catch(e) { console.warn("Env load error:", e); }
}

function buildField(item) {
  const wrap = document.createElement("div");
  wrap.className = "cred-field";
  const isSet = item.is_set;
  wrap.innerHTML = `
    <div class="cred-field-top">
      <span class="cred-label">${item.label}</span>
      <span class="cred-badge ${isSet ? 'badge-set' : 'badge-unset'}">${isSet ? '✓ Set' : '✗ Not set'}</span>
    </div>
    <div style="font-size:0.72rem;color:var(--text-muted);margin-bottom:8px">${item.hint}</div>
    <div class="cred-input-wrap">
      <input
        class="cred-input ${item.sensitive ? 'is-secret' : ''}"
        data-key="${item.key}"
        type="${item.sensitive ? 'password' : 'text'}"
        placeholder="${isSet ? (item.sensitive ? '(leave blank to keep current)' : item.value) : 'Enter value…'}"
        value="${item.sensitive ? '' : (item.value || '')}"
      />
      ${item.sensitive ? `
      <button class="eye-btn" type="button" onclick="toggleEye(this)" title="Show/hide">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
      </button>` : ''}
    </div>
  `;
  return wrap;
}

function toggleEye(btn) {
  const inp = btn.previousElementSibling;
  inp.type = inp.type === "password" ? "text" : "password";
}

function renderCredentials() {
  const sections = { identity: [], database: [], settings: [], sessions: [], optional: [] };
  for (const item of envData) {
    if (sections[item.section]) sections[item.section].push(item);
  }
  for (const [sec, items] of Object.entries(sections)) {
    const grid = document.getElementById("cred-" + sec);
    if (!grid) continue;
    grid.innerHTML = "";
    for (const item of items) grid.appendChild(buildField(item));
  }
}

function renderImages() {
  const grid = document.getElementById("img-grid");
  if (!grid) return;
  grid.innerHTML = "";

  // Merge API data + extra image keys
  const fromApi = {};
  for (const item of envData) {
    if (IMAGE_KEYS.includes(item.key)) fromApi[item.key] = item.value;
  }

  for (const key of IMAGE_KEYS) {
    const label = IMAGE_LABELS[key] || key;
    const val   = fromApi[key] || "";
    const card  = document.createElement("div");
    card.className = "img-card";
    card.innerHTML = `
      <div class="img-card-preview">
        <img src="${val || ''}" alt="" ${val ? 'style="display:block"' : ''} onerror="this.style.display='none';this.nextElementSibling.style.display='flex'" onload="this.style.display='block';this.nextElementSibling.style.display='none'" />
        <span class="img-placeholder" ${val ? 'style="display:none"' : ''}>No preview</span>
      </div>
      <div class="img-card-body">
        <span class="img-card-label">${label}</span>
        <span class="img-card-hint">${key}</span>
        <input class="img-url-input" data-key="${key}" type="url" value="${val}" placeholder="https://..." oninput="updateImgPreview(this)" />
      </div>
    `;
    grid.appendChild(card);
  }
}

function updateImgPreview(input) {
  const card = input.closest(".img-card");
  const img = card.querySelector("img");
  const ph  = card.querySelector(".img-placeholder");
  const url = input.value.trim();
  if (url && url.startsWith("http")) {
    img.src = url;
    img.style.display = "block";
    if (ph) ph.style.display = "none";
  } else {
    img.style.display = "none";
    if (ph) ph.style.display = "flex";
  }
}

/* ─── Save credentials ────────────────────────────── */
async function saveAll(inputs, feedbackId, btnEl) {
  const payload = {};
  for (const inp of inputs) {
    const key = inp.dataset.key;
    const val = inp.value.trim();
    if (!val) continue;
    if (inp.classList.contains("is-secret") && [...val].every(c => c === "•")) continue;
    payload[key] = val;
  }
  const fb = document.getElementById(feedbackId);
  btnEl.disabled = true;
  fb.textContent = "Saving…"; fb.className = "save-feedback";
  try {
    const res = await fetch("/api/env", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const d = await res.json();
    if (d.ok) {
      fb.className = "save-feedback ok";
      fb.textContent = "✓ " + d.message;
      await loadEnv();
    } else {
      fb.className = "save-feedback err";
      fb.textContent = "✗ " + d.message;
    }
  } catch(e) {
    fb.className = "save-feedback err";
    fb.textContent = "✗ Network error";
  }
  btnEl.disabled = false;
  setTimeout(() => { fb.textContent = ""; fb.className = "save-feedback"; }, 5000);
}

function saveAllCredentials() {
  const btn = document.querySelector("#section-credentials .btn-save");
  const inputs = document.querySelectorAll("#section-credentials .cred-input");
  saveAll(inputs, "cred-feedback", btn);
}

function saveAllImages() {
  const btn = document.querySelector("#section-images .btn-save");
  const inputs = document.querySelectorAll("#section-images .img-url-input");
  saveAll(inputs, "img-feedback", btn);
}

/* ─── Generate Session ────────────────────────────── */
async function genSendOtp(btn) {
  const phone = document.getElementById("gen-phone").value.trim();
  const fb = document.getElementById("gen-phone-fb");
  if (!phone) { fb.className = "save-feedback err"; fb.textContent = "✗ Enter a phone number"; return; }
  btn.disabled = true;
  fb.className = "save-feedback"; fb.textContent = "Sending OTP…";
  try {
    const res = await fetch("/api/login/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone }),
    });
    const d = await res.json();
    if (d.ok) {
      fb.className = "save-feedback ok"; fb.textContent = "✓ " + d.message;
      document.getElementById("gen-step-otp").style.display = "";
      document.getElementById("gen-otp").focus();
    } else {
      fb.className = "save-feedback err"; fb.textContent = "✗ " + d.message;
      btn.disabled = false;
    }
  } catch(e) {
    fb.className = "save-feedback err"; fb.textContent = "✗ Network error";
    btn.disabled = false;
  }
}

async function genFinishOtp(btn) {
  const otp  = document.getElementById("gen-otp").value.trim();
  const pass = document.getElementById("gen-pass").value.trim();
  const fb   = document.getElementById("gen-otp-fb");
  if (!otp) { fb.className = "save-feedback err"; fb.textContent = "✗ Enter the OTP code"; return; }
  btn.disabled = true;
  fb.className = "save-feedback"; fb.textContent = "Verifying…";
  try {
    const res = await fetch("/api/login/finish", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ otp, password: pass }),
    });
    const d = await res.json();
    if (d.ok) {
      document.getElementById("gen-step-phone").style.display = "none";
      document.getElementById("gen-step-otp").style.display  = "none";
      document.getElementById("gen-step-done").style.display = "";
      document.getElementById("gen-done-msg").textContent = d.message;
    } else {
      fb.className = "save-feedback err"; fb.textContent = "✗ " + d.message;
      btn.disabled = false;
    }
  } catch(e) {
    fb.className = "save-feedback err"; fb.textContent = "✗ Network error";
    btn.disabled = false;
  }
}

function genReset() {
  document.getElementById("gen-step-phone").style.display = "";
  document.getElementById("gen-step-otp").style.display  = "none";
  document.getElementById("gen-step-done").style.display = "none";
  document.getElementById("gen-phone").value = "";
  document.getElementById("gen-otp").value   = "";
  document.getElementById("gen-pass").value  = "";
  document.getElementById("gen-phone-fb").textContent = "";
  document.getElementById("gen-otp-fb").textContent   = "";
  document.querySelectorAll("#gen-step-phone .btn-save, #gen-step-otp .btn-save")
    .forEach(b => b.disabled = false);
}

/* ─── Init ────────────────────────────────────────── */
updateClock();
setInterval(updateClock, 1000);
fetchStats();
setInterval(fetchStats, 5000);
