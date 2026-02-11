/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  // Disable all static optimization
  experimental: {
    appDir: true,
  },
  // Generate all pages dynamically
  generateBuildId: async () => {
    return 'build-' + Date.now()
  },
}

module.exports = nextConfig
