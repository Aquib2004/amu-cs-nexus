"use client";

import { useState } from "react";

const EXAM_PORTS = [
  {
    label: "AMU Controller of Examinations (official portal)",
    url: "https://ccae.amucontrollerexams.com/result_display/loginmodalresultdisplaybyfacno.php",
  },
  {
    label: "AMU Online - Current Students",
    url: "https://amuonline.ac.in/",
  },
  {
    label: "Examination Schedule / Scheme",
    url: "https://www.results.amucontrollerexams.com/display/scheme",
  },
];

export default function ExamsPage() {
  const [embedded, setEmbedded] = useState(false);

  return (
    <main>
      <h1>Controller of Examinations</h1>
      <p className="chat-hint">
        Results, exam schedules, and registration are handled by AMU&apos;s
        official Controller of Examinations systems.
      </p>
      <p className="chat-hint">
        Note: the official portal may refuse to render inside an embedded frame
        (its security headers control framing). If you do not see the panel
        below, please open the link directly in a new tab.
      </p>

      <section className="status-card">
        <h2>Official portals</h2>
        <ul className="directory-list">
          {EXAM_PORTS.map((e) => (
            <li key={e.url} className="directory-item">
              <a href={e.url} target="_blank" rel="noreferrer">
                {e.label}
              </a>
            </li>
          ))}
        </ul>
        <button type="button" onClick={() => setEmbedded(true)}>
          Try embedded view
        </button>
        {embedded && (
          <div className="exam-frame-wrap">
            <iframe
              title="AMU Controller of Examinations"
              src={EXAM_PORTS[0].url}
              sandbox="allow-forms allow-scripts"
            />
            <p className="notice-meta">
              If this is blank, the site blocked embedding. Use the direct links
              above or the official site.
            </p>
          </div>
        )}
      </section>
    </main>
  );
}