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

const micBtn = document.getElementById("mic-btn");
let recorder = null;

micBtn.onclick = async () => {
  if (!recorder) {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recorder = new MediaRecorder(stream);
    recorder.start();
    micBtn.style.color = "#f00";
    recorder.ondataavailable = (e) => {
      const blob = new Blob([e.data], { type: "audio/webm" });
      fetch("/api/ceo/voice", {
        method: "POST",
        body: blob,
        headers: { "Content-Type": "audio/webm" },
      })
        .then((r) => r.json())
        .then((d) => {
          if (d.text) {
            document.getElementById("chat-input").value = d.text;
            document
              .getElementById("chat-form")
              .dispatchEvent(new Event("submit"));
          }
        });
    };
  } else {
    recorder.stop();
    recorder = null;
    micBtn.style.color = "";
  }
};

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
  "Hi, I'm Alex – AI CEO of Virsaas. Describe the problem you want solved.",
  speak(
    "Hi, I'm Alex – AI CEO of Virsaas. Please describe your idea and our team will call it forth from the cyber realm into this reality."
  )
);

function speak(text) {
  const lang = "{{ session.get('lang', 'en') }}";
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = lang;
  speechSynthesis.speak(utter);
}
