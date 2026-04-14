import type { Meta, StoryObj } from "@storybook-astro/framework";

import Chart from "./Chart.astro";

const meta: Meta<typeof Chart> = {
  title: "Shared/Chart",
  component: Chart,
  parameters: {
    layout: "padded",
  },
  argTypes: {
    height: { control: "text" },
    theme: { control: "select", options: ["auto", "light", "dark"] },
    renderer: { control: "select", options: ["svg", "canvas"] },
  },
};

export default meta;

type Story = StoryObj<typeof Chart>;

const sampleBarOption = {
  tooltip: { trigger: "axis" },
  xAxis: {
    type: "category",
    data: ["GPT-4o", "Claude Haiku", "Gemini Flash", "Ensemble"],
  },
  yAxis: { type: "value", name: "SPS" },
  series: [
    {
      type: "bar",
      data: [0.72, 0.68, 0.65, 0.81],
      itemStyle: { color: "var(--color-primary)" },
    },
  ],
};

const sampleLineOption = {
  tooltip: { trigger: "axis" },
  legend: { data: ["Model A", "Model B"] },
  xAxis: {
    type: "category",
    data: ["N=100", "N=500", "N=1000", "N=5000"],
  },
  yAxis: { type: "value", name: "SPS" },
  series: [
    {
      name: "Model A",
      type: "line",
      data: [0.55, 0.62, 0.68, 0.72],
    },
    {
      name: "Model B",
      type: "line",
      data: [0.48, 0.58, 0.63, 0.67],
    },
  ],
};

export const Bar: Story = {
  args: {
    option: sampleBarOption,
    height: "400px",
    theme: "auto",
    renderer: "svg",
  },
};

export const Line: Story = {
  args: {
    option: sampleLineOption,
    height: "400px",
    theme: "auto",
    renderer: "svg",
  },
};

export const ShortHeight: Story = {
  args: {
    option: sampleBarOption,
    height: "250px",
    theme: "auto",
    renderer: "svg",
  },
};
