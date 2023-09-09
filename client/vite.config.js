import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import { VitePWA } from "vite-plugin-pwa";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        react(),
        VitePWA({
            // add this to cache all the imports
            workbox: {
                globPatterns: ["**/*"],
            },
            // add this to cache all the
            // static assets in the public folder
            includeAssets: ["**/*"],
            manifest: {
                short_name: "Jetpack AI",
                name: "Jetpack AI",
                icons: [
                    {
                        src: "icons/manifest-icon-192.maskable.png",
                        sizes: "192x192",
                        type: "image/png",
                        purpose: "any",
                    },
                    {
                        src: "icons/manifest-icon-192.maskable.png",
                        sizes: "192x192",
                        type: "image/png",
                        purpose: "maskable",
                    },
                    {
                        src: "icons/manifest-icon-512.maskable.png",
                        sizes: "512x512",
                        type: "image/png",
                        purpose: "any",
                    },
                    {
                        src: "icons/manifest-icon-512.maskable.png",
                        sizes: "512x512",
                        type: "image/png",
                        purpose: "maskable",
                    },
                ],
                start_url: ".",
                display: "standalone",
                theme_color: "#5e35b1",
                background_color: "#fefefe",
            },
        }),
    ],
});
