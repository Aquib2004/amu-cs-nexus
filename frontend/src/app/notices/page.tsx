"use client";

import { useEffect, useState } from "react";

import { disableNotifications, enableNotifications, notificationsSupported } from "@/lib/notifications";
import { getNotices } from "@/services/notices";
import type { Notice } from "@/types";

export default function NoticesPage() {
  const [notices, setNotices] = useState<Notice[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [alertsEnabled, setAlertsEnabled] = useState(false);
  const [alertBusy, setAlertBusy] = useState(false);
  const [alertMessage, setAlertMessage] = useState<string | null>(null);

  useEffect(() => {
    getNotices({ limit: 50 })
      .then(setNotices)
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Unknown error"))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (notificationsSupported() && Notification.permission === "granted") {
      navigator.serviceWorker.ready
        .then((registration) => registration.pushManager.getSubscription())
        .then((subscription) => setAlertsEnabled(Boolean(subscription)))
        .catch(() => undefined);
    }
  }, []);

  async function toggleAlerts() {
    setAlertBusy(true);
    setAlertMessage(null);
    try {
      if (alertsEnabled) {
        await disableNotifications();
        setAlertsEnabled(false);
        setAlertMessage("Browser alerts disabled.");
      } else {
        await enableNotifications();
        setAlertsEnabled(true);
        setAlertMessage("Alerts enabled for newly published department notices.");
      }
    } catch (err: unknown) {
      setAlertMessage(err instanceof Error ? err.message : "Could not update notifications.");
    } finally {
      setAlertBusy(false);
    }
  }

  return (
    <main>
      <h1 className="page-title">Notices</h1>
      <p className="page-subtitle">Current notices from the official AMU Computer Science department feed.</p>
      <section className="notice-alert-panel">
        <div>
          <strong>New-notice alerts</strong>
          <p>Opt in to browser notifications. Permission is requested only after you enable this.</p>
          {alertMessage && <span className="alert-message">{alertMessage}</span>}
        </div>
        <button type="button" className={`btn ${alertsEnabled ? "secondary" : ""}`} onClick={() => void toggleAlerts()} disabled={alertBusy || !notificationsSupported()}>
          {alertBusy ? "Updating…" : alertsEnabled ? "Disable alerts" : "Enable alerts"}
        </button>
      </section>
      {error ? <p className="error">Could not load notices: {error}</p> : loading ? <p className="loading">Loading notices&hellip;</p> : notices.length === 0 ? <div className="empty-state">No notices yet.</div> : (
        <ul className="item-list">
          {notices.map((notice) => <li key={notice.id} className="item-card"><h2 className="item-title"><a href={notice.url} target="_blank" rel="noreferrer">{notice.title}</a></h2><div className="item-tags"><span className="badge">{notice.category ?? "general"}</span><span className="badge warm">{notice.published_at ?? "date unknown"}</span></div></li>)}
        </ul>
      )}
    </main>
  );
}
