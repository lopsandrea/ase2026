# Record & Replay baseline (paper §4.5, Tab. 4)

A traditional manual baseline representing classic Selenium IDE-style
automation: scripts are *recorded* by a human walking through the
successful user journey and exported as a Selenium IDE `.side` file, then
replayed against the mutated environments.

To regenerate the recordings:

1. Open Selenium IDE in Chrome.
2. Click **Record a new test in a new project** and set the base URL to
   the configured app (e.g., `http://localhost:3001` for CodeBites).
3. Manually execute the UAT scenario step-by-step.
4. Stop recording, save the project under this directory as
   `<subject>.side`.
5. Export to Python via *Export* → *Python pytest* and place the file
   under `<subject>.py`.

We provide pre-recorded `.side` projects and Python exports for each of
the nine evaluation scenarios. Note that the R&R baseline by definition
fails as soon as any locator changes — the 18% mutation-survival figure
in Tab. 4 quantifies this fragility.
