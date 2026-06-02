import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  base: process.env.VITE_BASE_PATH ?? "/",
  server: {
    host: "0.0.0.0",
    port: 5173,
    allowedHosts: ["caucasian-broom-overlook.ngrok-free.dev"],
    proxy: {
      "/api": {
        target: "http://backend:8000",
        changeOrigin: true
      }
    }
  }
});
