// Top navigation bar for AMUCS Nexus.
// The AMU mark is served from `frontend/public/amu-logo.png`, downloaded from
// the official AMU site (assets/images/final-logo-2.png). It is the
// University's trademark: we use it only to identify the institution this
// student project is about, not to imply official endorsement. See
// docs/decisions/ADR-002-branding-and-logo.md.

export const NAV_AREAS: { label: string; href: string; title: string }[] = [
  { label: "YouRobo", href: "/chat", title: "Ask the AI college assistant" },
  { label: "Search", href: "/search", title: "Search indexed content" },
  { label: "Notices", href: "/notices", title: "Department notices" },
  { label: "Documents", href: "/documents", title: "Document library" },
  { label: "Faculty", href: "/faculty", title: "Faculty directory" },
  { label: "Research", href: "/research", title: "Research and publications" },
  { label: "Exams", href: "/exams", title: "Controller of Examinations" },
];

export default function Header() {
  return (
    <header className="site-header">
      <a className="brand" href="/" aria-label="AMUCS Nexus - home">
        <img
          className="brand-logo"
          src="/amu-logo.png"
          alt="Aligarh Muslim University"
          width={38}
          height={38}
        />
        <span className="brand-text">
          AMUCS Nexus
          <span className="brand-tagline">YouRobo AI Assistant</span>
        </span>
      </a>
      <nav aria-label="Main navigation">
        <ul>
          {NAV_AREAS.map((item) => (
            <li key={item.label}>
              <a className="nav-link" href={item.href} title={item.title}>
                {item.label}
              </a>
            </li>
          ))}
        </ul>
      </nav>
    </header>
  );
}