# Reliable GitHub Stats Cards Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the broken runtime Vercel embeds with attractive, theme-aware SVG cards generated and stored by the profile repository.

**Architecture:** A scheduled GitHub Actions workflow renders separate light and dark activity and language cards using the repository's built-in token. The workflow commits only successful SVG output, after which README `<picture>` elements select the correct local asset for the viewer's GitHub theme.

**Tech Stack:** GitHub Actions, `stats-organization/github-readme-stats-action` v2 pinned by commit SHA, repository-relative SVG assets, HTML `<picture>` elements in Markdown

---

## File Map

- Create `.github/workflows/stats.yml`: generate, validate, and commit four theme-aware SVG cards.
- Generate `profile/stats-dark.svg`, `profile/stats-light.svg`, `profile/top-langs-dark.svg`, and `profile/top-langs-light.svg`: repository-owned card output produced by the workflow.
- Modify `README.md`: replace the two broken Vercel images with accessible local `<picture>` elements.
- Preserve `.github/workflows/arcade.yml` and every non-stats section in `README.md` unchanged.

### Task 1: Add the fail-safe card-generation workflow

**Files:**
- Create: `.github/workflows/stats.yml`

- [ ] **Step 1: Confirm the workflow does not exist yet**

Run:

```bash
test ! -e .github/workflows/stats.yml
```

Expected: exit status `0`.

- [ ] **Step 2: Create the workflow**

Create `.github/workflows/stats.yml` with exactly:

```yaml
name: Update GitHub stats cards

on:
  schedule:
    - cron: "17 0 * * *"
  workflow_dispatch:

permissions:
  contents: write

concurrency:
  group: profile-stats
  cancel-in-progress: true

jobs:
  generate:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - name: Check out profile repository
        uses: actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803 # v6

      - name: Generate dark stats card
        uses: stats-organization/github-readme-stats-action@e856fc8de9d7729b463c468911e232cfbdc3d55e # v2
        with:
          card: stats
          options: username=${{ github.repository_owner }}&show_icons=true&bg_color=0D1117&title_color=58A6FF&text_color=C9D1D9&icon_color=58A6FF&border_color=30363D
          path: profile/stats-dark.svg
          token: ${{ secrets.GITHUB_TOKEN }}
          fail_on_error: true

      - name: Generate light stats card
        uses: stats-organization/github-readme-stats-action@e856fc8de9d7729b463c468911e232cfbdc3d55e # v2
        with:
          card: stats
          options: username=${{ github.repository_owner }}&show_icons=true&bg_color=FFFFFF&title_color=2F80ED&text_color=24292F&icon_color=2F80ED&border_color=D0D7DE
          path: profile/stats-light.svg
          token: ${{ secrets.GITHUB_TOKEN }}
          fail_on_error: true

      - name: Generate dark languages card
        uses: stats-organization/github-readme-stats-action@e856fc8de9d7729b463c468911e232cfbdc3d55e # v2
        with:
          card: top-langs
          options: username=${{ github.repository_owner }}&layout=compact&langs_count=6&bg_color=0D1117&title_color=58A6FF&text_color=C9D1D9&border_color=30363D
          path: profile/top-langs-dark.svg
          token: ${{ secrets.GITHUB_TOKEN }}
          fail_on_error: true

      - name: Generate light languages card
        uses: stats-organization/github-readme-stats-action@e856fc8de9d7729b463c468911e232cfbdc3d55e # v2
        with:
          card: top-langs
          options: username=${{ github.repository_owner }}&layout=compact&langs_count=6&bg_color=FFFFFF&title_color=2F80ED&text_color=24292F&border_color=D0D7DE
          path: profile/top-langs-light.svg
          token: ${{ secrets.GITHUB_TOKEN }}
          fail_on_error: true

      - name: Commit refreshed cards
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add profile/*.svg
          git diff --cached --quiet && exit 0
          git commit \
            -m "Keep profile visitors current without runtime dependencies" \
            -m "Refresh repository-owned stats cards after a successful GitHub API render." \
            -m "Constraint: Public GitHub statistics only
          Confidence: high
          Scope-risk: narrow
          Tested: All card generators completed with fail_on_error enabled"
          git push
```

- [ ] **Step 3: Parse and structurally validate the workflow**

Run:

```bash
ruby -e 'require "yaml"; YAML.load_file(".github/workflows/stats.yml")'
rg -n 'contents: write|fail_on_error: true|profile/(stats|top-langs)-(dark|light)\.svg' .github/workflows/stats.yml
```

Expected: Ruby exits `0`; the search shows one scoped permission, four fail-safe settings, and all four asset paths.

- [ ] **Step 4: Verify pinned action commits still resolve upstream**

Run:

```bash
test "$(git ls-remote https://github.com/actions/checkout.git refs/tags/v6 | cut -f1)" = "d23441a48e516b6c34aea4fa41551a30e30af803"
test "$(git ls-remote https://github.com/stats-organization/github-readme-stats-action.git 'refs/tags/v2^{}' | cut -f1)" = "e856fc8de9d7729b463c468911e232cfbdc3d55e"
```

Expected: both assertions exit `0`, proving that the pinned commits are still the commits behind the documented major-version tags.

- [ ] **Step 5: Commit the workflow**

Run:

```bash
git add .github/workflows/stats.yml
git commit -m "Keep profile statistics available without a public runtime" \
  -m "Generate light and dark cards inside the profile repository so a third-party Vercel outage cannot replace the section with an error image." \
  -m "Constraint: Public statistics only; no personal access token is introduced
Rejected: Another public card endpoint | repeats the same runtime dependency
Confidence: high
Scope-risk: narrow
Directive: Keep fail_on_error enabled so failed refreshes cannot overwrite healthy SVGs
Tested: YAML parse, structural assertions, and pinned action reference resolution
Not-tested: Live Actions execution before publication"
```

Expected: one commit containing only `.github/workflows/stats.yml`.

### Task 2: Publish the workflow and seed verified assets

**Files:**
- Generate: `profile/stats-dark.svg`
- Generate: `profile/stats-light.svg`
- Generate: `profile/top-langs-dark.svg`
- Generate: `profile/top-langs-light.svg`

- [ ] **Step 1: Publish the design, plan, and workflow commits**

Run:

```bash
git push origin main
```

Expected: the remote `main` branch advances successfully.

- [ ] **Step 2: Dispatch the new workflow**

Run:

```bash
gh workflow run stats.yml --repo eastjin616/eastjin616 --ref main
```

Expected: GitHub accepts the dispatch without an error.

- [ ] **Step 3: Watch the dispatched run to completion**

Run:

```bash
run_id="$(gh run list --repo eastjin616/eastjin616 --workflow stats.yml --event workflow_dispatch --limit 1 --json databaseId --jq '.[0].databaseId')"
gh run watch "$run_id" --repo eastjin616/eastjin616 --exit-status
```

Expected: the `generate` job and all card-generation steps succeed.

- [ ] **Step 4: Fast-forward to the workflow's asset commit**

Run:

```bash
git pull --ff-only origin main
```

Expected: the four `profile/*.svg` files appear locally without a merge commit.

- [ ] **Step 5: Validate the generated assets before changing README**

Run:

```bash
test -s profile/stats-dark.svg
test -s profile/stats-light.svg
test -s profile/top-langs-dark.svg
test -s profile/top-langs-light.svg
for asset in profile/*.svg; do
  rg -q '<svg' "$asset"
done
! rg -n 'Something went wrong|Maximum retries exceeded|PAT_1' profile/*.svg
```

Expected: all files are non-empty and contain SVG markup; no error-card text is found.

### Task 3: Switch the README only after healthy assets exist

**Files:**
- Modify: `README.md` in the `GitHub Stats` section

- [ ] **Step 1: Confirm the broken host is still the current source**

Run:

```bash
rg -n 'github-readme-stats-sigma-five\.vercel\.app' README.md
```

Expected: two matches in the `GitHub Stats` section.

- [ ] **Step 2: Replace only the two card images**

The complete resulting section must be:

```html
<div align="center">
  <h2>GitHub Stats</h2>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./profile/stats-dark.svg" />
    <source media="(prefers-color-scheme: light), (prefers-color-scheme: no-preference)" srcset="./profile/stats-light.svg" />
    <img height="170" alt="Jin's GitHub stats" src="./profile/stats-light.svg" />
  </picture>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./profile/top-langs-dark.svg" />
    <source media="(prefers-color-scheme: light), (prefers-color-scheme: no-preference)" srcset="./profile/top-langs-light.svg" />
    <img height="170" alt="Jin's most used languages" src="./profile/top-langs-light.svg" />
  </picture>
</div>
```

- [ ] **Step 3: Verify scope and references**

Run:

```bash
! rg -n 'github-readme-stats-sigma-five\.vercel\.app|github-readme-stats\.vercel\.app' README.md
rg -n 'profile/(stats|top-langs)-(dark|light)\.svg|alt="Jin' README.md
git diff --check
git diff -- README.md
```

Expected: no public stats host remains; four local paths and two alt texts are present; the diff changes only the old image lines inside `GitHub Stats`.

- [ ] **Step 4: Commit the README transition**

Run:

```bash
git add README.md
git commit -m "Keep profile visitors clear of third-party card failures" \
  -m "Render verified repository-owned light and dark SVGs while preserving the surrounding profile layout and blue visual accent." \
  -m "Constraint: Contact, Best Friends, Pac-Man, and quote sections remain unchanged
Rejected: Switch to the official public endpoint | it is currently paused and remains a runtime dependency
Confidence: high
Scope-risk: narrow
Reversibility: clean
Directive: Do not restore runtime card URLs without proving their availability model
Tested: Asset existence, error-text scan, README reference assertions, and whitespace check
Not-tested: Live GitHub rendering before publication"
```

Expected: one commit containing only `README.md`.

### Task 4: Publish and visually verify the live profile

**Files:**
- Verify: `README.md`
- Verify: `profile/*.svg`

- [ ] **Step 1: Publish the README transition**

Run:

```bash
git push origin main
```

Expected: remote `main` advances successfully.

- [ ] **Step 2: Verify all raw assets are publicly reachable**

Run:

```bash
for asset in stats-dark stats-light top-langs-dark top-langs-light; do
  curl --fail --silent --show-error "https://raw.githubusercontent.com/eastjin616/eastjin616/main/profile/${asset}.svg" | rg -q '<svg'
done
```

Expected: all four requests exit `0` and contain SVG markup.

- [ ] **Step 3: Verify the published README no longer references the failed service**

Run:

```bash
published_readme="$(curl --fail --silent --show-error https://raw.githubusercontent.com/eastjin616/eastjin616/main/README.md)"
! printf '%s' "$published_readme" | rg -n 'github-readme-stats-sigma-five\.vercel\.app|Maximum retries exceeded|PAT_1'
printf '%s' "$published_readme" | rg -n 'profile/(stats|top-langs)-(dark|light)\.svg'
```

Expected: the broken service and error text are absent; all four local paths are present.

- [ ] **Step 4: Capture and inspect the live profile**

Run:

```bash
playwright screenshot --full-page https://github.com/eastjin616 /tmp/eastjin616-profile-live.png
```

Expected: the screenshot shows the two GitHub-native cards between Best Friends and Pac-Man, with no error panels or broken images. Inspect the image at full resolution before continuing.

- [ ] **Step 5: Run final repository checks**

Run:

```bash
git fetch origin main
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
git diff --check origin/main
git status --short --untracked-files=no
```

Expected: local and remote `main` match, no whitespace errors exist, and no tracked changes remain.
