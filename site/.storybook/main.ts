import type { StorybookConfig } from "@storybook-astro/framework";

const config: StorybookConfig = {
  stories: ["../src/**/*.stories.@(js|jsx|ts|tsx)"],
  addons: ["@storybook/addon-a11y", "@storybook/addon-themes"],
  framework: {
    name: "@storybook-astro/framework",
    options: {
      // Prerender Astro stories into static HTML at build time. Avoids the
      // need for a running Astro render server during CI/VRT (server mode
      // default requires a sidecar on port 3000). Tradeoff: no storyRules
      // dynamic mocking — all stories must be deterministic.
      renderMode: "static",
    },
  },
  docs: {
    defaultName: "Docs",
  },
};

export default config;
