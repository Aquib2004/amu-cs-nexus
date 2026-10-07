/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Static export, so the deployed site can be served by FastAPI from the same
  // origin as the API (Render's Python runtime has no Node and cannot run
  // `next build`). Same origin means browser CORS never applies. The export is
  // written to `out/` and committed to the repo.
  output: "export",
  // MUST stay false. Vercel's trailing-slash rule fires before rewrites, so
  // `true` turned every /api request into a 308 to /api/.../ and the proxy
  // never ran. The trade-off is that routes export as <route>.html instead of
  // <route>/index.html, which app/main.py handles with its ".html" fallback.
  trailingSlash: false,
  images: {
    // `next/image` optimisation needs a Node server, which the export has none.
    unoptimized: true,
  },
};

module.exports = nextConfig;
