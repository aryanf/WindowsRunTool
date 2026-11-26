You are auditing a local clone of the **WindowsRunTool** repository on this Windows laptop. The repo is pushed to a **public** GitHub repository. Some command files are also synced between laptops with Syncthing. The goal is to find private data that is (or could become) public, and to record how this laptop is set up so it can be compared with other laptops.
 
## Rules
 
- **Read-only.** Do not edit, delete, move, commit, push, untrack or reconfigure anything. Do not change `.gitignore` or Syncthing settings. Only write the report file described at the end.
- **Never print a secret value.** When you find a credential, token, password, key, email, account ID or similar, show the file, line number, the kind of value, and at most the first 3 characters followed by `***`.
- Do not send any file content to an outside service.
- If a step fails (tool missing, path not found), note it in the report and continue.
 
## Step 1: Locate the repo
 
1. Find the clone. It is usually `C:\Code\WindowsRunTool`; if not there, search for a folder that contains `default_runner.ahk` and `python\run.py`.
2. Record: repo path, computer name (`$env:COMPUTERNAME`), current branch, latest commit (`git log -1 --oneline`), the `origin` remote URL, and whether the branch is ahead or behind `origin` (`git fetch` then `git status -sb`; fetching is allowed, pulling is not).
 
## Step 2: `.gitignore` and ignored-but-tracked files
 
1. Print the full `.gitignore`.
2. List files that match an ignore rule but are **still tracked** (they get pushed anyway):
 `git ls-files -ci --exclude-standard`
 Give the total count, and group by top-level folder with counts.
3. From that list, call out files that hold user data rather than program files: screenshots and images under app data folders, `session.xml`, `config.xml`, `*Config*.json`, `History*`, `*.db`, logs, backups, favourites/bookmarks (`*.qdr`), recent-file lists.
4. List the output of `git status --short` so local modifications to tracked files are visible.
 
## Step 3: Private data in tracked files
 
Scan every tracked file (`git ls-files`), skipping binary files. Report each finding as `file:line — type — masked sample`. Look for:
 
- Credentials: AWS keys (`AKIA…`, `ASIA…`), `aws_secret_access_key`, GitHub tokens (`ghp_`, `github_pat_`), OpenAI/Anthropic keys (`sk-…`), Slack tokens (`xox…`), private keys (`-----BEGIN … PRIVATE KEY-----`), and lines where `password`, `passwd`, `secret`, `token`, `api_key`, `apikey` or `client_secret` are assigned a literal value.
- Personal data: email addresses, phone numbers, real names, Windows user paths (`C:\Users\<name>\…`), 12-digit AWS account IDs, IP addresses that are not `127.0.0.1` or `0.0.0.0`.
- Work data: company or internal hostnames, internal URLs with IDs, Jira/Confluence/Atlassian links, SSO start URLs, ARNs containing real account IDs (ignore placeholders like `acct` or `region`).
 
Ignore obvious public URLs (github.com, microsoft.com, python.org, stackoverflow.com, w3.org and similar), placeholders, and code that only reads credentials at runtime. For each finding, say whether it looks real or like a template/example.
 
Also check the git **history** for the same patterns and for files that were deleted but are still in old commits:
`git log --all --diff-filter=D --name-only --format=` (deleted files)
`git log --all -p -G "<pattern>"` for the credential patterns above (report commit hash, file, type, masked sample).
 
## Step 4: Command folders
 
The runner loads commands from `python\<letter>\*.py` (and `urls.json` / info files). For every folder directly under `python\` that is not `__pycache__`:
 
1. Number of files on disk, number tracked by git (`git ls-files python\<x>`), number untracked (`git ls-files -o --exclude-standard python\<x>`), and number ignored.
2. Whether it contains a `.stignore` file.
3. A table of every file in it with: name, size, last-modified date, SHA-256 (first 12 hex chars), and tracked/untracked. This table is used to compare laptops, so include every file.
 
## Step 5: Syncthing
 
1. Is Syncthing running? List `syncthing*` processes (`Get-Process syncthing*`), and check whether it is running inside WSL (`wsl -e pgrep -a syncthing`, skip if WSL is not installed).
2. Find every Syncthing config that exists:
 - `%LOCALAPPDATA%\Syncthing\config.xml`
 - `%APPDATA%\Syncthing\config.xml`
 - any `config.xml` next to a portable `syncthing.exe` (search the repo's `portable_open_source_apps` and `C:\Program Files*`)
 - inside WSL: `~/.local/state/syncthing/config.xml` and `~/.config/syncthing/config.xml`
3. For each config, list:
 - Every folder: label, id, path, type (sendreceive/sendonly/receiveonly), and the **names** of the devices it is shared with.
 - Every device: name and the first 7 characters of its ID only.
 - Folders with an empty id or path (broken entries).
 - For each folder path, whether it is inside the repo and whether git tracks the files in it (overlap between git and Syncthing).
4. Do not open or print `key.pem`, `https-key.pem` or other key files.
 
## Step 6: Machine-specific config
 
1. `user_configuration.json` at the repo root: is it tracked by git? List its top-level keys and, for each string value, show only whether it is empty or set (do not print values, except `env` and browser `app_name` entries, which are not sensitive).
2. Check whether these AutoHotkey files contain personal paths, names, emails or work hostnames: `default_runner.ahk` and any other `*.ahk` in the repo (masked samples only).
 
## Step 7: Write the report
 
Write the report to `audit_<COMPUTERNAME>_<YYYY-MM-DD>.md` in the user's **Downloads** folder (not inside the repo, so it is never committed). Use exactly these sections so reports from different laptops can be compared side by side:
 
1. **Summary**: 3–6 bullet points with the most important findings, worst first.
2. **Machine**: computer name, repo path, branch, latest commit, ahead/behind origin.
3. **.gitignore**: full contents, then ignored-but-tracked files (count, grouped list, user-data files called out).
4. **Private data in tracked files**: table with columns File, Line, Type, Masked sample, Real or template, Severity (High / Medium / Low).
5. **Private data in git history**: same table plus Commit column.
6. **Command folders**: summary table per folder, then the per-file table from Step 4.
7. **Syncthing**: running instances, configs found, folders table, devices table, broken entries, git/Syncthing overlaps.
8. **Machine-specific config**: results of Step 6.
9. **Errors and skipped steps**.
10. **Recommendations**: concrete suggestions, but do not apply any of them.
 
When done, reply with the report's full path and the Summary section.
 