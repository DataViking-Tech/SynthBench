import type { Meta, StoryObj } from "@storybook-astro/framework";

import ConvergenceLine from "./ConvergenceLine.astro";

const meta: Meta<typeof ConvergenceLine> = {
  title: "Findings/ConvergenceLine",
  component: ConvergenceLine,
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;

type Story = StoryObj<typeof ConvergenceLine>;

export const Default: Story = {};
