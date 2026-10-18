// Colours for a question's answer options in stacked distribution bars and
// their legends (question, run and compare pages), one module so the same
// option gets the same colour everywhere.
//
// - Substantive options take ten distinct categorical hues in a fixed order
//   (--sb-opt-1..10 in sb.css, stepped separately for light and dark mode and
//   checked for colour-blind separation between neighbours, which is what
//   matters in a stacked bar). Option 11 on gets a lighter tint of the hue
//   ten slots back rather than repeating it outright.
// - Non-answers ("Don't know", "Refused", "No answer"...) are neutral grey
//   (--sb-opt-none) and don't use up a hue.
// - Ordered scales (agree → disagree), when the caller knows the options are
//   ordinal, use a one-hue ramp from --sb-ord-lo to --sb-ord-hi instead. The
//   question payloads carry no ordinal flag yet, so every page currently
//   passes the default (categorical).

const HUES = 10;

/**
 * Answers that are a non-answer rather than a position on the question. The
 * whole label must be one (a trailing note in brackets is allowed), so a
 * substantive option that merely starts with "don't know" (GSS_GOD's
 * agnostic "don't know, no way to find out") keeps its hue.
 */
const NON_ANSWER =
  /^\s*(?:(?:i\s+)?don['’]?t know|do not know|dk|not sure|unsure|refused|no answer|no opinion|prefer not to (?:say|answer)|declined?(?: to answer)?|skipped|not asked)\s*(?:\(.*\))?\s*\.?\s*$/i;
export const isNonAnswer = (option: string): boolean => NON_ANSWER.test(option);

export interface PaletteOpts {
  /** The options are an ordered scale: colour them along a single-hue ramp. */
  ordered?: boolean;
}

/** One CSS colour per option, in the order given. */
export function optionColors(options: string[], o: PaletteOpts = {}): string[] {
  const substantive = options.filter((k) => !isNonAnswer(k));
  const n = substantive.length;
  let slot = 0;
  return options.map((k) => {
    if (isNonAnswer(k)) return "var(--sb-opt-none)";
    const i = slot++;
    if (o.ordered) {
      const t = n > 1 ? Math.round((i / (n - 1)) * 100) : 100;
      return `color-mix(in oklab, var(--sb-ord-hi) ${t}%, var(--sb-ord-lo))`;
    }
    const hue = `var(--sb-opt-${(i % HUES) + 1})`;
    return i < HUES ? hue : `color-mix(in oklab, ${hue} 55%, var(--sb-panel))`;
  });
}

const cache = new Map<string, string[]>();
/** Colour of option `i` of `options` (memoised per option list). */
export function optionColor(options: string[], i: number, o: PaletteOpts = {}): string {
  const key = `${o.ordered ? 1 : 0}\u0000${options.join("\u0000")}`;
  let colors = cache.get(key);
  if (!colors) {
    colors = optionColors(options, o);
    cache.set(key, colors);
  }
  return colors[i] ?? "var(--sb-opt-none)";
}
