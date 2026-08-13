---
title: "Repository-owned GitHub profile stats assets prevent third-party card failures"
date: "2026-08-13"
category: integration-issues
module: github-profile-readme
problem_type: integration_issue
component: tooling
symptoms:
  - "README cards returned HTTP 200 error SVGs instead of statistics."
  - "The SVG body reported Maximum retries exceeded and requested PAT_1."
  - "Immediate screenshots appeared empty before the generated SVG animation completed."
root_cause: missing_tooling
resolution_type: tooling_addition
severity: low
related_components:
  - development_workflow
  - documentation
tags:
  - github
  - profile-readme
  - github-actions
  - svg-assets
  - readme-stats
  - third-party-dependency
  - scheduled-workflow
---

# Repository-owned GitHub profile stats assets prevent third-party card failures

## Problem

The profile README embedded two cards from `github-readme-stats-sigma-five.vercel.app`. Both requests returned HTTP 200, but the body was an SVG error card containing `Maximum retries exceeded` and `PAT_1`, so a transport-success check did not prove the image was usable. The original project's public endpoint was also paused and was not a reliable fallback.

## Symptoms

- GitHub displayed error panels instead of activity and language metrics.
- HTTP status checks passed because the service encoded its failure inside a valid SVG response.
- An immediate screenshot could show headings and frames without metric text because the SVG elements animate into view.

## What Didn't Work

- Keeping the sigma-five Vercel URLs left rendering dependent on that deployment's token and availability.
- Switching to another public endpoint preserved the same visitor-time dependency; the original public endpoint was unavailable during investigation.
- Treating HTTP 200 as card health missed application-level errors inside the SVG.
- Treating an immediate screenshot as final evidence produced a false visual failure; the live card needed time to finish its entrance animation.

## Solution

Generate and commit four theme-specific SVG files with GitHub Actions before changing the README:

```yaml
on:
  schedule:
    - cron: "17 0 * * *"
  workflow_dispatch:

permissions:
  contents: write

- uses: stats-organization/github-readme-stats-action@e856fc8de9d7729b463c468911e232cfbdc3d55e # v2
  with:
    card: stats
    path: profile/stats-light.svg
    token: ${{ secrets.GITHUB_TOKEN }}
    fail_on_error: true
```

The workflow creates:

- `profile/stats-light.svg`
- `profile/stats-dark.svg`
- `profile/top-langs-light.svg`
- `profile/top-langs-dark.svg`

After a successful seed run, use `<picture>` to select the matching repository-owned asset:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./profile/stats-dark.svg" />
  <source media="(prefers-color-scheme: light), (prefers-color-scheme: no-preference)" srcset="./profile/stats-light.svg" />
  <img height="170" alt="Jin's GitHub stats" src="./profile/stats-light.svg" />
</picture>
```

Pin third-party actions to commit SHAs, scope workflow permissions to `contents: write`, serialize refreshes with a concurrency group, and set a bounded job timeout.

## Why This Works

Profile visits load committed SVG files from the repository instead of calling a card-rendering service at request time. GitHub's built-in `GITHUB_TOKEN` is sufficient for public statistics, so no long-lived PAT is introduced. `fail_on_error: true` fails the refresh before the commit step, preserving the last healthy assets instead of overwriting them with error cards.

Separate light and dark output files retain the profile's GitHub-native styling without runtime theme detection.

## Prevention

- Validate SVG content rather than relying on HTTP status alone:

  ```bash
  for asset in profile/*.svg; do
    rg -q '<svg' "$asset"
  done
  ! rg -n 'Something went wrong|Maximum retries exceeded|PAT_1' profile/*.svg
  ```

- Seed and verify every asset before switching README paths so the rollout cannot create broken images.
- Verify raw asset URLs and the published README after deployment.
- Wait for animated SVG content before capturing visual evidence; the live light and dark cards were verified after a 2.5-second delay.
- Keep `fail_on_error`, the timeout, and concurrency control enabled when changing the refresh workflow.

## Related Issues

- [Common Error Codes](https://github.com/anuraghazra/github-readme-stats/issues/1772)
- [Public deployment paused](https://github.com/anuraghazra/github-readme-stats/issues/3851)
- [Card throws “maximum retries exceeded”](https://github.com/anuraghazra/github-readme-stats/issues/1471)
