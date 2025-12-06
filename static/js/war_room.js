const socket = io();
const projectId = "{{ project.project_id }}";
const voiceToggle = document.getElementById("voice-toggle");
const codePanel = document.getElementById("diff-content");
const terminalPanel = document.getElementById("terminal-lines");
const thoughtsPanel = document.getElementById("thoughts-list");
const deployBar = document.getElementById("deploy-bar");
const deployUrl = document.getElementById("deploy-url");

// join room
socket.emit("join_project", { project_id: projectId });

// incoming events
socket.on("agent_event", (data) => {
  const { agent_id, type, payload } = data;

  if (type === "thought") {
    addThought(agent_id, payload.text);
    if (voiceToggle.checked) speak(`${agent_id} says: ${payload.text}`);
  }
  if (type === "code") {
    codePanel.textContent = payload.diff || "// no diff";
  }
  if (type === "terminal") {
    addTerminal(payload.lines);
  }
  if (type === "deploy") {
    deployUrl.href = payload.url;
    deployBar.classList.remove("hidden");
    if (voiceToggle.checked) speak("Deployment complete!");
  }
});

function addThought(agent, text) {
  const div = document.createElement("div");
  div.className = "thought-bubble";
  div.innerHTML = `<strong>${agent}</strong>: ${text}`;
  thoughtsPanel.appendChild(div);
  thoughtsPanel.scrollTop = thoughtsPanel.scrollHeight;
}

function addTerminal(lines) {
  lines.forEach((line) => {
    const div = document.createElement("div");
    div.className = "terminal-line";
    div.textContent = line;
    terminalPanel.appendChild(div);
  });
  terminalPanel.scrollTop = terminalPanel.scrollHeight;
}

function speak(text) {
  if ("speechSynthesis" in window && voiceToggle.checked) {
    const utter = new SpeechSynthesisUtterance(text);
    utter.rate = 1.1;
    utter.pitch = 1;
    speechSynthesis.speak(utter);
  }
}

// fullscreen toggle
document.getElementById("fullscreen").onclick = () => {
  document.documentElement.requestFullscreen?.();
};

document.getElementById("figma-import").onclick = async () => {
  const url = document.getElementById("figma-url").value;
  if (!url) return;
  const res = await fetch("/api/figma/import", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, project_id: "{{ project.project_id }}" }),
  });
  const data = await res.json();
  if (data.success) {
    addThought(
      "FIGMA",
      "Assets downloaded – converting to React components..."
    );
  }
};

socket.on("agent_event", (data) => {
  if (data.type === "selfie") {
    const img = document.createElement("img");
    img.src = data.payload.url; // ← Puter CDN URL
    img.className = "selfie";
    img.alt = data.agent_id + " selfie";
    thoughtsPanel.appendChild(img);
  }
  if (data.type === "sprite") {
    renderAgentSprite(data.agent_id, data.payload);
  }
});

function renderAgentSprite(agentId, payload) {
  const url = payload.url;
  const frames = payload.frames;
  const strip = new Image();
  strip.src = url;
  strip.onload = () => {
    const canvas = document.createElement("canvas");
    canvas.width = 256;
    canvas.height = 256;
    canvas.className = "sprite-canvas";
    canvas.id = `sprite-${agentId}`;
    // replace old canvas if exists
    const old = document.getElementById(`sprite-${agentId}`);
    if (old) old.replaceWith(canvas);

    const ctx = canvas.getContext("2d");
    let frame = 0;
    const step = () => {
      ctx.clearRect(0, 0, 256, 256);
      ctx.drawImage(strip, frame * 256, 0, 256, 256, 0, 0, 256, 256);
      frame = (frame + 1) % frames;
      requestAnimationFrame(step);
    };
    step();
  };
}
