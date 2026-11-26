# Syncthing

Some command folders hold private data (personal info, work notes, credentials helpers, browser URLs). They are **not** pushed to GitHub — they are listed in `.gitignore` — and are shared between laptops with [Syncthing](https://syncthing.net/) instead.

## Folders to sync

| Folder | Content |
|---|---|
| `python/l` | URL command config (`urls.json`) |
| `python/cp` | Copy-to-clipboard scripts |
| `python/i` | Info topics |
| `python/ii` | Secondary info topics (personal) |
| `python/t` | Tertiary info topics |

## Setup on a new laptop

1. Clone the repo to the same path as on the other laptops (e.g. `C:\code\WindowsRunTool`).
2. Install and start Syncthing (Windows or WSL).
3. Add the other laptops as devices.
4. For each folder above, accept the share from another device (or add it with the same folder ID) and point it at the matching path in the clone, e.g. `C:\code\WindowsRunTool\python\i` (or `/mnt/c/code/WindowsRunTool/python/i` in WSL).
5. Use folder type **Send & Receive**.

## `python/p` is not synced

`python/p` is tracked in git and is **not** shared with Syncthing. Private scripts in it are not committed, so copy them by hand to the laptops where you need them. Which ones you need depends on the working environment.

These are usually useful in every environment:

- `send.py`
- `stand.py`
- `stands.py`
- `fix.py`
- `ask.py`

Keep these private scripts out of git, for example by listing them in `.git/info/exclude`.

## Notes

- Keep these folders in `.gitignore` so private files are never committed.
- Bind the Syncthing GUI to `127.0.0.1:8384` (or enable TLS) so it is not reachable from the network.
