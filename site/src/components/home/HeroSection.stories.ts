import type { Meta, StoryObj } from "@storybook-astro/framework";

import HeroSection from "./HeroSection.astro";

const meta: Meta<typeof HeroSection> = {
  title: "Home/HeroSection",
  component: HeroSection,
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;

type Story = StoryObj<typeof HeroSection>;

export const Default: Story = {};
