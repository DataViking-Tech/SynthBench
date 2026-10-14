// Routing topic taxonomy (version 1). The source of truth is
// src/synthbench/topics.py; publish.py keys topic_metrics, topic_scores and
// per-question `topic` by these ids. tests/test_topics.py checks that the ids
// and labels here match the Python definition.

export const TOPICS = [
  { id: "politics", label: "Politics and policy" },
  { id: "economy", label: "Economy and work" },
  { id: "technology", label: "Technology and media" },
  { id: "science-health", label: "Science and health" },
  { id: "identity", label: "Identity and values" },
  { id: "society", label: "Family, community and safety" },
  { id: "global", label: "Global affairs" },
] as const;

export type TopicId = (typeof TOPICS)[number]["id"];

export const TOPIC_IDS: readonly TopicId[] = TOPICS.map((t) => t.id);

const LABELS: Record<string, string> = Object.fromEntries(TOPICS.map((t) => [t.id, t.label]));

/** Display label for a topic id. Unknown values (older artifacts) pass through. */
export function topicLabel(id: string | null | undefined): string {
  if (!id) return "";
  return LABELS[id] ?? id;
}
