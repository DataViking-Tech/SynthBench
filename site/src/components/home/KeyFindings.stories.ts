import type { Meta, StoryObj } from "@storybook-astro/framework";

import KeyFindings from "./KeyFindings.astro";

const meta: Meta<typeof KeyFindings> = {
  title: "Home/KeyFindings",
  component: KeyFindings,
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;

type Story = StoryObj<typeof KeyFindings>;

export const Default: Story = {};
