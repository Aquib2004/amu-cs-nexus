// Local PostCSS configuration for the AMUCS Nexus frontend.
//
// Next.js + PostCSS search parent directories for the nearest postcss
// config. Without this file, PostCSS would pick up the config in the user's
// home directory (C:\Users\<user>\postcss.config.js), which is not valid JS
// and breaks every build on this machine. This project uses no PostCSS
// plugins, so the config is intentionally empty.
module.exports = {
  plugins: {},
};