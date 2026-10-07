self.addEventListener("push", (event) => {
  let data = { title: "New AMU CS notice", body: "Open Notices to view the latest update.", url: "/notices" };
  try {
    if (event.data) data = { ...data, ...event.data.json() };
  } catch (_) {
    // Keep safe default notification if the server payload is malformed.
  }
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: "/amu-logo.png",
      badge: "/amu-logo.png",
      tag: data.tag || "amu-cs-notice",
      data: { url: data.url || "/notices" },
    })
  );
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const target = event.notification.data?.url || "/notices";
  event.waitUntil(
    self.clients.matchAll({ type: "window", includeUncontrolled: true }).then((clients) => {
      const existing = clients.find((client) => "focus" in client);
      return existing ? existing.navigate(target).then((client) => client.focus()) : self.clients.openWindow(target);
    })
  );
});
