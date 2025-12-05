// CEO-chat widget for landing page
const OPEN_CHAT = document.getElementById("open-chat");
const CLOSE_CHAT = document.getElementById("close-chat");
const CHAT_SECT = document.getElementById("chat-section");
const MESSAGES = document.getElementById("chat-messages");
const FORM = document.getElementById("chat-form");
const INPUT = document.getElementById("chat-input");

let msgCount = 0;
const MAX_FREE = 5;
const SESSION = crypto.randomUUID();

function addMessage(sender, text) {
  const div = document.createElement("div");
  div.classList.add("message", sender);
  div.textContent = text;
  MESSAGES.appendChild(div);
  MESSAGES.scrollTop = MESSAGES.scrollHeight;
}

async function sendToCEO(text) {
  try {
    const res = await fetch("/api/ceo/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, session_id: SESSION }),
    });
    const data = await res.json();
    if (data.reply) addMessage("ceo", data.reply);
    if (data.limit_reached) {
      addMessage("ceo", "Create a free account to continue the briefing.");
      INPUT.disabled = true;
      FORM.insertAdjacentHTML(
        "afterend",
        `
        <div style="text-align:center;margin-top:1rem;">
          <a class="btn-primary" href="/register">Start Building</a>
        </div>`
      );
    }
  } catch (e) {
    addMessage("ceo", "Network error – please refresh.");
  }
}

// open / close
OPEN_CHAT.addEventListener("click", () => CHAT_SECT.classList.remove("hidden"));
CLOSE_CHAT.addEventListener("click", () => CHAT_SECT.classList.add("hidden"));

// send message
FORM.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = INPUT.value.trim();
  if (!text) return;
  addMessage("user", text);
  INPUT.value = "";
  msgCount++;
  sendToCEO(text);
});

// welcome message
addMessage(
  "ceo",
  "Hi, I'm Alex – AI CEO of Virsaas. Describe the problem you want solved."
);
