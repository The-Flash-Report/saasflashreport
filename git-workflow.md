# Git Workflow SOP for AI Flash Report

## Purpose
This document describes the standard operating procedure (SOP) for working with Git in the AI Flash Report project. Follow these steps to ensure smooth collaboration and avoid overwriting daily updates.

---

## 1. Always Pull the Latest Version
- **Before making any changes, always pull the latest version from GitHub.**
- The site updates automatically once per day when the script runs, so your local copy may be out of date.
- Run:
  ```sh
  git pull origin main
  ```

## 2. Make and Test Changes Locally
- Make your changes in your local working directory.
- Test your changes locally:
  - Run the script: `python3 aggregator.py`
  - Preview the site: `python3 -m http.server 8000` and visit `http://localhost:8000/`

## 3. Commit Your Changes
- Write clear, descriptive commit messages.
- Example:
  ```sh
  git add .
  git commit -m "Describe your change here"
  ```

## 4. Rebase or Merge if Needed
- If others have pushed changes since you started, rebase or merge to resolve conflicts:
  ```sh
  git pull --rebase origin main
  # or
  git merge origin/main
  ```

## 5. Push to GitHub
- Push your changes to the main branch (or a feature branch if using one):
  ```sh
  git push origin main
  ```
- The deployment will be triggered automatically after pushing to GitHub.

## 6. Special Note on Daily Updates
- If you are working near the time of the daily script run, **pull again** before your final push to avoid overwriting new content.

## 7. Troubleshooting Push Rejections
- If you try to push and see an error like:
  > Updates were rejected because the remote contains work that you do not have locally.
- This means someone else has pushed changes since your last pull.
- To fix:
  1. Run:
     ```sh
     git pull --rebase origin main
     ```
  2. Resolve any conflicts if prompted.
  3. Then push again:
     ```sh
     git push origin main
     ```
- This will safely integrate your changes with the latest remote updates.

---

**Summary:**
> Always pull before you start, test locally, commit clearly, and push when ready. This keeps the site and your work in sync with daily updates. 