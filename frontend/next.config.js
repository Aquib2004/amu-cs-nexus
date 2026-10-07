/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Static export, so the deployed site can be served by FastAPI from the same
  // origin as the API (Render's Python runtime has no Node and cannot run
  // `next build`). Same origin means browser CORS never applies. The export is
  // written to `out/` and committed to the repo.
  output: "export",
  // Emit `<route>/index.html` so a plain file server resolves /chat/ itself.
  trailingSlash: true,
  images: {
    // `next/image` optimisation needs a Node server, which the export has none.
    unoptimized: true,
  },
};

module.exports = nextConfig;
