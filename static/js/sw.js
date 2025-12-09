self.addEventListener("push", (event) => {
  const data = event.data.json();
  self.registration.showNotification(data.title, {
    body: data.body,
    icon: "/static/img/icon-192.png",
    vibrate: [200, 100, 200],
    tag: "virsaas-build",
  });
});
