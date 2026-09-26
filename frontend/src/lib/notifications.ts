// Opt-in helpers for AMU notice Web Push. No permission is requested until the
// student explicitly presses the enable button.

import { API_BASE_URL } from "@/lib/api";

interface VapidResponse { enabled: boolean; public_key: string | null }

function urlBase64ToArrayBuffer(value: string): ArrayBuffer {
  const padding = "=".repeat((4 - (value.length % 4)) % 4);
  const base64 = (value + padding).replace(/-/g, "+").replace(/_/g, "/");
  const raw = window.atob(base64);
  const bytes = new Uint8Array(raw.length);
  for (let index = 0; index < raw.length; index += 1) bytes[index] = raw.charCodeAt(index);
  return bytes.buffer;
}

export function notificationsSupported(): boolean {
  return "serviceWorker" in navigator && "PushManager" in window && "Notification" in window;
}

export async function getVapidConfiguration(): Promise<VapidResponse> {
  const response = await fetch(`${API_BASE_URL}/api/notifications/vapid-public-key`);
  if (!response.ok) throw new Error("Notification settings are unavailable.");
  return (await response.json()) as VapidResponse;
}

export async function enableNotifications(): Promise<void> {
  if (!notificationsSupported()) throw new Error("This browser does not support notifications.");
  const permission = await Notification.requestPermission();
  if (permission !== "granted") throw new Error("Notification permission was not granted.");
  const config = await getVapidConfiguration();
  if (!config.enabled || !config.public_key) throw new Error("Notifications are not configured on the server.");

  const registration = await navigator.serviceWorker.register("/sw.js", { scope: "/" });
  const subscription = await registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToArrayBuffer(config.public_key),
  });
  const response = await fetch(`${API_BASE_URL}/api/notifications/subscriptions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(subscription.toJSON()),
  });
  if (!response.ok) throw new Error("Could not save the notification subscription.");
}

export async function disableNotifications(): Promise<void> {
  const registration = await navigator.serviceWorker.ready;
  const subscription = await registration.pushManager.getSubscription();
  if (!subscription) return;
  await subscription.unsubscribe();
  // The server may already have expired this endpoint; local opt-out still succeeds.
  const response = await fetch(`${API_BASE_URL}/api/notifications/subscriptions/by-endpoint?endpoint=${encodeURIComponent(subscription.endpoint)}`, {
    method: "DELETE",
  });
  if (!response.ok && response.status !== 404) throw new Error("Could not disable server notifications.");
}
