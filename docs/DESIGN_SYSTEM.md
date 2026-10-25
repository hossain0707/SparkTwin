# SparkTwin visual design system

- Palette: deep navy `#08121f`, layered slate cards, mint `#59e2bd`, cool blue `#77a8ff` and measured amber/red for caution/error.
- Typography: system sans-serif for reliability; monospaced data labels for formula/detail blocks.
- Layout: stable left navigation on desktop, collapsible drawer on mobile; responsive KPI cards and two-column panels.
- Interaction: light 200–300 ms transitions, faint orbital art, subtle moving diagram connectors; **honor `prefers-reduced-motion`**.
- Evidence labeling: every illustrative calculation says estimate. Never create fake terminal screenshots, measured metrics or hardware badges.
- Data presentation: values carry GB/GiB/tokens/sec units and confidence; benchmark results only after imported real observations.
- Documentation: banner, animated walkthrough, implementation-faithful SVG architecture, quick start and status matrix, with no unnecessary decorative emojis.
- Assets: self-hosted SVG and plain CSS, no analytics trackers, remote images or font files.


## GitHub repository visual system — 2026-10-25

The `README.md` is the canonical public-facing product page, but it must not substitute presentation polish for verified engineering evidence. Keep the product storytelling aligned with the measured capabilities and the tagged developer-preview release.

### Versioned README assets

| Asset | Function | Motion |
| --- | --- | --- |
| `docs/sparktwin-banner.svg` | Branded hero with unified-memory chip and thesis | Two slow orbits; restrained ambient movement |
| `docs/workflow-animated.svg` | Configure → Estimate → Compare → Calibrate → Report | Sequenced status highlights |
| `docs/planning-cockpit.svg` | Illustrative interface composition, clearly labeled non-screenshot | Gentle bar breathing and local status indicator |
| `docs/architecture.svg` | Implementation-faithful loopback, local data and optional SSH boundaries | Subtle data-flow dashes |

All visuals are **self-hosted** in the repository as lightweight SVGs, use system fonts, embed no remote trackers, and have accessible `title`, `desc` or relevant `alt` attributes. CSS motion must honor `@media (prefers-reduced-motion: reduce)`. No JavaScript or off-site CDNs in the diagrams.

### Editorial and technical integrity

- README section order: introduction → download → visual product tour → capabilities → architecture → equations → quick start → verification → continuation.
- Do not use fabricated terminal captures, fake benchmark numbers, invented performance percentages, a fake device connection badge, or claim visual studies are real screenshots.
- Link to real, currently published GitHub release assets; only amend download names after verifying them.
- README should state the precise **current scope**, **what is unverified**, and exact GitHub release stage.
- Keep `START_HERE.md`, `AGENTS.md`, `docs/VERIFICATION.md`, and `docs/RELEASE.md` consistent with current README.
- New screenshots should be captured from a tested real build and labeled with model configuration, host and test date.
- Avoid excessive movement; keep animations optional, subtle and informative, with visible static fallbacks.
