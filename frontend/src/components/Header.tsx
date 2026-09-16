// Top navigation bar showing the planned AMUCS Nexus areas.

export const NAV_AREAS = [
  "Chat",
  "Search",
  "Notices",
  "Documents",
  "Faculty",
  "Research",
] as const;

export default function Header() {
  return (
    <header className="site-header">
      <a className="brand" href="#top">
        AMUCS Nexus
      </a>
      <nav aria-label="Main navigation">
        <ul>
          {NAV_AREAS.map((area) => (
            <li key={area}>
              {/* Becomes a real link when each page is built. */}
              <span className="nav-pending">{area}</span>
            </li>
          ))}
        </ul>
      </nav>
    </header>
  );
}
