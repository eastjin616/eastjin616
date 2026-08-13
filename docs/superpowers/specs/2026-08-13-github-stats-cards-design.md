# Reliable GitHub Stats Cards Design

## Goal

Replace the broken third-party GitHub Stats embeds with repository-owned SVG cards that match the existing profile, adapt to GitHub's light and dark themes, and continue showing the last healthy result when a refresh fails.

## Scope

Only the `GitHub Stats` section changes. The header, Contact Me, Best Friends, hidden Tech Stack, Pac-Man Contributions, and quote card remain unchanged.

## Visual Design

The section keeps its existing centered `GitHub Stats` heading and two-card composition:

- The activity card appears first and shows public GitHub activity with icons.
- The compact languages card appears second and shows the six most-used public languages.
- Dark-mode cards use the GitHub dark panel treatment with `#58A6FF` for titles and icons.
- Light-mode cards use the GitHub default light treatment with the existing `#2F80ED` accent.
- Standard GitHub-style borders and corner radii keep the cards visually restrained.
- Both cards use the same displayed height. GitHub's normal inline wrapping lets them sit side by side when space permits and stack on narrow screens.

Each card is embedded through a `<picture>` element with a `prefers-color-scheme` source and an accessible fallback image. The fallback uses the light card and includes descriptive alt text.

## Architecture

A dedicated `.github/workflows/stats.yml` workflow generates four repository-owned assets:

- `profile/stats-dark.svg`
- `profile/stats-light.svg`
- `profile/top-langs-dark.svg`
- `profile/top-langs-light.svg`

The workflow uses the maintained GitHub Readme Stats Action and GitHub's built-in `GITHUB_TOKEN`. Public statistics are sufficient, so no long-lived personal access token is introduced.

Third-party actions are pinned to verified commit SHAs, matching the repository's existing workflow security pattern. The workflow receives only `contents: write`, which is required to commit refreshed SVG files.

## Data Flow

1. A daily schedule or manual dispatch starts the workflow.
2. The workflow checks out the profile repository.
3. The action fetches public statistics through the GitHub API using `GITHUB_TOKEN`.
4. Separate light and dark options render the four SVG files.
5. A commit step stages only `profile/*.svg` and pushes only when generated content changed.
6. The profile README renders the local SVG files without making a runtime request to a public card server.

## Failure Handling

Each card-generation step enables `fail_on_error`. If GitHub API access or rendering fails, the workflow fails before the commit step and does not replace healthy assets with an error card.

The workflow has a bounded timeout and a concurrency group so overlapping scheduled or manual runs do not race. Existing SVG files remain available while a failed refresh is investigated.

## Rollout

The workflow is published before the README is changed. A manual run must successfully generate and commit all four SVG assets. Only after the assets are verified does the README switch from the broken Vercel URLs to repository-relative paths. This prevents a transient broken-image state during deployment.

## Verification

Implementation is complete only when all of the following hold:

- The workflow YAML parses successfully.
- Every third-party action reference resolves to the intended upstream commit.
- A manual workflow dispatch completes successfully.
- All four SVG files exist and contain SVG markup.
- No generated asset contains `Something went wrong`, `Maximum retries exceeded`, or `PAT_1`.
- Raw GitHub URLs for all four assets return successfully.
- The live profile renders the light/dark card pair without changing the surrounding sections.
- The repository contains no PAT or newly introduced secret.

## Non-goals

- Redesigning other profile sections
- Displaying private-repository statistics
- Operating a personal Vercel deployment
- Adding custom card-rendering code
