// Register service worker
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/static/js/sw.js").then((reg) => {
    console.log("SW registered", reg);
    reg.pushManager
      .subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlB64ToUint8Array("{{ vapid_public }}"),
      })
      .then((sub) => {
        // send sub to backend
        fetch("/api/push/subscribe", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(sub),
        });
      });
  });
}

function urlB64ToUint8Array(base64String) {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, "+")
    .replace(/_/g, "/");
  const rawData = window.atob(base64);
  return Uint8Array.from([...rawData].map((char) => char.charCodeAt(0)));
}
