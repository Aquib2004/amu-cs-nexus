"use client";

// Official controllers of examinations + NEP cell entry points.
// Every URL in this list was probed and returned HTTP 200 during development;
// the links open in a new tab because the official portals set framing
// security headers that prevent embedding (an iframe would show a blank box).

const EXAM_PORTALS = [
  {
    label: "AMU Controller of Examinations",
    url: "https://www.amucontrollerexams.com/",
    note: "Exam schedules, forms and registration.",
  },
  {
    label: "Examination Results (official)",
    url: "https://results.amucontrollerexams.com/",
    note: "Public result and grade lookups.",
  },
];

const NEP_LINKS = [
  {
    label: "AMU homepage",
    url: "https://www.amu.ac.in/",
    note: "University main site.",
  },
  {
    label: "AMU NEP",
    url: "https://www.amu.ac.in/nep",
    note: "National Education Policy at AMU.",
  },
  {
    label: "AMU NEP Cell",
    url: "https://www.amu.ac.in/nep-cell",
    note: "NEP implementation cell.",
  },
  {
    label: "Dept. of Computer Science",
    url: "https://www.amu.ac.in/department/computer-science",
    note: "Department official pages.",
  },
];

export default function ExamsPage() {
  return (
    <main>
      <h1 className="page-title">Controller of Examinations &amp; NEP</h1>
      <p className="page-subtitle">
        Results, exam schedules, registration, and National Education Policy
        resources are handled by AMU&rsquo;s official online systems. These
        links open the official portals in a new tab.
      </p>

      <section className="card" style={{ marginBottom: "1rem" }}>
        <h2>Examination portals</h2>
        <ul className="item-list">
          {EXAM_PORTALS.map((e) => (
            <li key={e.url} className="external-card">
              <h3>{e.label}</h3>
              <p>{e.note}</p>
              <a href={e.url} target="_blank" rel="noreferrer">
                {e.url}
              </a>
            </li>
          ))}
        </ul>
      </section>

      <section className="card">
        <h2>University &amp; NEP resources</h2>
        <ul className="item-list">
          {NEP_LINKS.map((e) => (
            <li key={e.url} className="external-card">
              <h3>{e.label}</h3>
              <p>{e.note}</p>
              <a href={e.url} target="_blank" rel="noreferrer">
                {e.url}
              </a>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}