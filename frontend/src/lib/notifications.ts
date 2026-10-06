// Opt-in helpers for AMU notice Web Push. No permission is requested until the
// student explicitly presses the enable button.

import { requestJson } from "@/lib/api";

interface VapidResponse { enabled: boolean; public_key: string | null }

function urlBase64ToArrayBuffer(value: string): ArrayBuffer {
  const padding = "=".repeat((4 - (value.length % 4)) % 4);
  const base64 = (value + padding).replace(/-/g, "+").replace(/_/g, "/");
  const raw = window.atob(base64);
  const bytes = new Uint8Array(raw.length);
  for (let index = 0; index < raw.length; index += 1) bytes[index] = raw.charCodeAt(index);
  return bytes.buffer;
}

/**
 * Whether this browser can show Web Push notifications.
 *
 * Must be safe to call while rendering on the server: `navigator` does not
 * exist during prerendering, so an unguarded check crashes the build with
 * "ReferenceError: navigator is not defined". It also returns false on the
 * server so the first client render matches the server HTML.
 */
export function notificationsSupported(): boolean {
  if (typeof window === "undefined" || typeof navigator === "undefined") {
    return false;
  }
  return "serviceWorker" in navigator && "PushManager" in window && "Notification" in window;
}

export async function getVapidConfiguration(): Promise<VapidResponse> {
  const config = await requestJson<VapidResponse>(
    "/api/notifications/vapid-public-key",
    undefined,
    "Loading notification settings"
  );
  if (typeof config?.enabled !== "boolean") {
    throw new Error("Notification settings are unavailable.");
  }
  return config;
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
  await requestJson<unknown>(
    "/api/notifications/subscriptions",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(subscription.toJSON()),
    },
    "Saving the notification subscription"
  );
}

export async function disableNotifications(): Promise<void> {
  const registration = await navigator.serviceWorker.ready;
  const subscription = await registration.pushManager.getSubscription();
  if (!subscription) return;
  await subscription.unsubscribe();
  // The server may already have expired this endpoint; local opt-out still succeeds.
  const endpoint = encodeURIComponent(subscription.endpoint);
  try {
    await requestJson<unknown>(
      `/api/notifications/subscriptions/by-endpoint?endpoint=${endpoint}`,
      { method: "DELETE" },
      "Disabling server notifications"
    );
  } catch (error) {
    if (error instanceof Error && "status" in error && (error as { status: number }).status === 404) return;
    throw error;
  }
}