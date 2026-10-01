const FEATURES: { title: string; href: string; blurb: string }[] = [
  {
    title: "YouRobo",
    href: "/chat",
    blurb: "Ask questions about the department; answers come with numbered sources.",
  },
  {
    title: "Search",
    href: "/search",
    blurb: "Keyword and semantic search across notices, documents and pages.",
  },
  {
    title: "Notices",
    href: "/notices",
    blurb: "Department notices and announcements.",
  },
  {
    title: "Documents",
    href: "/documents",
    blurb: "Indexed documents with links to the official source pages.",
  },
  {
    title: "Faculty",
    href: "/faculty",
    blurb: "Faculty directory for the Department of Computer Science.",
  },
  {
    title: "Programmes",
    href: "/programs",
    blurb: "Degrees offered by the department (ug, postgraduate, PhD).",
  },
  {
    title: "Laboratories",
    href: "/laboratories",
    blurb: "Teaching and research laboratories of the department.",
  },
  {
    title: "Research",
    href: "/research",
    blurb: "Research projects with funding agencies and investigators.",
  },
  {
    title: "Staff",
    href: "/staff",
    blurb: "Non-teaching staff directory.",
  },
  {
    title: "Exams",
    href: "/exams",
    blurb: "Official Controller of Examinations portals and NEP cell.",
  },
];

export default function Home() {
  return (
    <main>
      <section className="hero">
        <h1>AMUCS Nexus</h1>
        <p>
          Knowledge, search, and a source-grounded AI assistant for the AMU
          Department of Computer Science. Ask YouRobo, search the indexed
          content, or browse notices, documents, faculty and research directly.
        </p>
        <div className="field-row">
          <a className="btn" href="/chat">
            Ask YouRobo
          </a>
          <a className="btn secondary" href="/search">
            Search content
          </a>
        </div>
      </section>

      <section className="card-grid">
        {FEATURES.map((f) => (
          <a key={f.title} className="feature-card" href={f.href}>
            <span className="feature-title">{f.title}</span>
            <p>{f.blurb}</p>
          </a>
        ))}
      </section>

    </main>
  );
}