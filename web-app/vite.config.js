import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'
 // import { VitePWA } from 'vite-plugin-pwa'
import viteCompression from 'vite-plugin-compression'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    visualizer({
      filename: 'dist/stats.html',
      open: false,
      gzipSize: true,
      brotliSize: true
    }),
     // Temporarily disabled PWA due to build issues
     // VitePWA({
     //   registerType: 'autoUpdate',
     //   includeAssets: ['favicon.svg', 'apple-touch-icon.png', 'mask-icon.svg'],
     //   manifest: {
     //     name: 'ICE Facility Heatmap - Immigration Detention Centers',
     //     short_name: 'ICE Heatmap',
     //     description: 'Interactive heatmap of ICE detention facilities with real-time population data',
     //     theme_color: '#1e40af',
     //     background_color: '#ffffff',
     //     display: 'standalone',
     //     orientation: 'portrait',
     //     scope: '/',
     //     start_url: '/',
     //     icons: [
     //       {
     //         src: 'favicon.svg',
     //         sizes: 'any',
     //         type: 'image/svg+xml',
     //         purpose: 'any maskable'
     //       }
     //     ]
     //   },
     //   workbox: {
     //     globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
     //     runtimeCaching: [
     //       {
     //         urlPattern: /^https:\/\/basemaps\.cartocdn\.com\/.*/i,
     //         handler: 'CacheFirst',
     //         options: {
     //           cacheName: 'carto-basemaps',
     //           expiration: {
     //             maxEntries: 10,
     //             maxAgeSeconds: 60 * 60 * 24 * 365 // 1 year
     //           },
     //           cacheKeyWillBeUsed: async ({ request }) => {
     //             return `${request.url}?${Date.now()}`;
     //           }
     //         }
     //       }
     //     ]
     //   }
     // }),
    viteCompression({
      algorithm: 'gzip',
      ext: '.gz',
    }),
    viteCompression({
      algorithm: 'brotliCompress',
      ext: '.br',
    })
  ],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Separate vendor chunks for better caching
          'react-vendor': ['react', 'react-dom'],
          'map-vendor': ['maplibre-gl', 'mapbox-gl', '@deck.gl/core', '@deck.gl/react', '@deck.gl/mapbox'],
          'deckgl-vendor': ['@deck.gl/layers', '@deck.gl/aggregation-layers'],
          'ui-vendor': ['leaflet', 'react-leaflet']
        }
      }
    },
    // Optimize chunk size
    chunkSizeWarningLimit: 1000,
    // Enable source maps for better debugging
    sourcemap: false,
    // Optimize assets
    assetsInlineLimit: 4096,
    // Minify for production
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    }
  },
  // Optimize dependencies
  optimizeDeps: {
    include: ['react', 'react-dom', 'maplibre-gl']
  },
  // Performance optimizations
  server: {
    fs: {
      // Allow serving files from one level up to the project root
      allow: ['..']
    }
  }
})