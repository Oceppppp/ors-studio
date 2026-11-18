# Publish ORS Studio to GitHub from Windows

The target is a new public repository: `Oceppppp/ors-studio`.

1. Extract the release source ZIP.
2. Ensure no `.env`, database dump, uploaded dataset, or local secrets exist in the project folder.
3. Install Git for Windows and GitHub CLI if they are not installed.
4. Run `PUBLISH_TO_GITHUB.bat` from the project root.
5. Sign in in the browser as `Oceppppp` if prompted and approve the `repo` and `workflow` scopes.
6. The script creates the public repository if it does not exist, verifies the target, pushes `main`, then pushes tag `v0.4.0`. It never force-pushes and never overwrites a tag that points to a different commit.
7. Open `https://github.com/Oceppppp/ors-studio/actions` and review Web CI and Windows build results.
8. After source publication, connect the repository in Render and apply `render.yaml` as a Blueprint. This step is separate from GitHub publishing.

Do not paste tokens or passwords into ChatGPT. GitHub App connection in ChatGPT and GitHub CLI authentication on Windows are separate.
