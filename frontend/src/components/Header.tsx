// Top navigation bar showing the AMUCS Nexus areas.
// Areas with an href are built pages; the rest are placeholders.

export const NAV_AREAS: { label: string; href?: string }[] = [
  { label: "Chat", href: "/chat" },
  { label: "Search", href: "/search" },
  { label: "Notices", href: "/notices" },
  { label: "Documents" },
  { label: "Faculty" },
  { label: "Research" },
];

export default function Header() {
  return (
    <header className="site-header">
      <a className="brand" href="/">
        AMUCS Nexus
      </a>
      <nav aria-label="Main navigation">
        <ul>
          {NAV_AREAS.map((item) => (
            <li key={item.label}>
              {item.href ? (
                <a className="nav-link" href={item.href}>
                  {item.label}
                </a>
              ) : (
                <span className="nav-pending" title="Not built yet">
                  {item.label}
                </span>
              )}
            </li>
          ))}
        </ul>
      </nav>
    </header>
  );
}
