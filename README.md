## 🍃 minty-maintenance

![Bash](https://img.shields.io/badge/Bash-4EAA25?logo=gnu-bash&logoColor=white)
![Linux Mint](https://img.shields.io/badge/Linux%20Mint-87CF3E?logo=linuxmint&logoColor=white)
![Ubuntu Base](https://img.shields.io/badge/Ubuntu%2024.04%20base-E95420?logo=ubuntu&logoColor=white)
![Made with ❤️](https://img.shields.io/badge/Made%20with-%E2%9D%A4-red)

A Bash script that keeps my Linux Mint 22 setup updated, tidy, and healthy — and writes a friendly, plain‑English report every time it runs. It’s practical, transparent, and a little fun.

### Why I built this
- **Peace of mind**: I wanted updates that explain themselves, not a black box.
- **Trustworthy automation**: Each chapter checks first, narrates actions, and errs on the side of safety.
- **Time-saver**: One command, a full system pass, and a clean summary at the end.

### What it solves for me
- **Predictability**: I can dry‑run to preview actions and impact.
- **Safety**: The most recent Timeshift snapshot is annotated as the last one before maintenance begins.
- **Clarity**: A single TXT report tells me what changed and how much space moved.

### What I learned (and care about)
- Build automation for humans — explanation beats mystery.
- Safety nets (snapshots, checks, gates) build confidence.
- Small tools, big leverage: clear UX makes infra feel effortless.

---

### Key features
- **Narrated report** explaining what’s happening and why it matters.
- **Safety-first flow** where every chapter checks state and handles errors gracefully.
- **Timeshift annotation**: marks the latest snapshot as the pre‑maintenance checkpoint.
- **Dry‑run mode** to preview changes and space impact before committing.
- **Space tracking** per step and overall, with a final summary.

---

### Correct Table of Contents (Chapters)
These are the actual chapters produced by `update_all_improved.sh` (the earlier list you saw elsewhere was incorrect):

1) Create a Safety Checkpoint (Timeshift)
2) Updating Command‑Line Tools (Homebrew)
3) Updating Your Core System Software (APT)
4) Checking for Package Issues
5) Updating Desktop Applications (Flatpak)
6) Updating Snap Applications
7) Updating Python Tools
8) Checking Standalone Applications (AppImage)
9) Checking Device Firmware Updates
10) Cleaning Up System Log Files
11) Removing Old System Kernels
12) Checking Hard Drive Health
13) Updating Desktop Extensions (GNOME)
14) Cleaning Up Docker Containers
15) Refreshing File Search Database
16) Deep Cleaning Temporary Files (BleachBit)
17) Optimizing SSD Performance (fstrim)
18) Checking Overall System Health
19) Checking Graphics Card (NVIDIA)
20) Verifying Automatic Security Updates
21) Final Summary

Every chapter runs with safety in mind and logs clearly to the TXT report.

---

### Usage
```bash
# Full maintenance run (writes a narrated report next to the script)
bash update_all_improved.sh

# Dry‑run (no changes) — preview what would happen and current state
bash update_all_improved.sh dry-run
```

---

### Example: Chapter 10 looks like this in the report
Short context, action, result — with space impact where relevant:

```text
------------------------------------------------------------------------
Chapter 10: Cleaning Up System Log Files
------------------------------------------------------------------------
📚 Your system keeps detailed logs of everything it does. Over time,
these can take up quite a bit of space.

🔧 Now I'm going to: clean up old system logs (keep 2 weeks)
Current log storage: 470.6M
   ✅ Done! Everything completed successfully.
Log storage after cleanup: 362.4M
```

---

### Timeshift: safety checkpoint (important)
- If Timeshift is available and not using the BTRFS backend, the script finds the most recent snapshot and adds a note to its `info.json` that it’s the "Maintenance checkpoint — last snapshot before updates & cleanup".
- If Timeshift isn’t installed (or BTRFS is used), the report explains the situation and next steps — still safely.

---

### Final Summary at the end
The report closes with a compact table and a space summary. Here’s an example where a single run freed up a whopping ~27 GB:

```text
🎉 All done! Here's what happened today:

Task                          | Status             | Notes
------------------------------|--------------------|------------------------------
Safety Checkpoint             | ✅ Success          | Checkpoint marked successfully
Homebrew Tools                | ✅ Success          | Tools updated
System Updates                | ✅ Success          | Updated successfully
Package Cleanup               | ✅ Success          | Cleaned 22 orphans
Flatpak Apps                  | ✅ Success          | 9 apps updated
Snap Apps                     | ✅ Success          | Old versions cleaned
Python Tools                  | ✅ Success          | Updated packages
AppImage Check                | ✅ Success          | None found
Firmware Updates              | ⚠️ Needs Attention  | Restart needed
Log Cleanup                   | ✅ Success          | Cleaned to 362.4M
Kernel Cleanup                | ✅ Success          | Old kernels removed
Disk Health                   | ✅ Success          | All drives healthy
GNOME Extensions              | ✅ Success          | Extensions updated
Docker Cleanup                | ✅ Success          | Cleaned unused containers
Search Database               | ✅ Success          | Database refreshed
Deep Clean                    | ✅ Success          | Deep cleaned
SSD Optimization              | ✅ Success          | SSDs optimized
System Health                 | ✅ Success          | All services healthy
Graphics Card                 | ✅ Success          | GPU healthy, driver OK
Auto Updates                  | ✅ Success          | Auto-updates enabled

📊 Space Summary:
   🎉 Freed up approximately 27648MB!
   Available space: 529G
```

---

### Keep the GitHub formatting crisp
- Write normal paragraphs as plain Markdown.
- Put examples/demos inside fenced code blocks (triple backticks) so they render as clean “boxes”.
- Use `---` for dividers between sections.
- Keep headings at `##` / `###` for skimmability.

---

### Cool, simple, done
This is my kind of tooling: safe by default, clear in results, and chill to use. One command, one report, and on a good day… 27 GB back.
