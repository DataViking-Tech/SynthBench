import type { Meta, StoryObj } from "@storybook-astro/framework";

import LeaderboardTable from "./LeaderboardTable.astro";

const meta: Meta<typeof LeaderboardTable> = {
  title: "Leaderboard/LeaderboardTable",
  component: LeaderboardTable,
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;

type Story = StoryObj<typeof LeaderboardTable>;

export const Default: Story = {};
