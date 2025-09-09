## 🍃 minty-maintenance

![Bash](https://img.shields.io/badge/Bash-4EAA25?logo=gnu-bash&logoColor=white)
![Linux Mint](https://img.shields.io/badge/Linux%20Mint-87CF3E?logo=linuxmint&logoColor=white)
![Ubuntu Base](https://img.shields.io/badge/Ubuntu%2024.04%20base-E95420?logo=ubuntu&logoColor=white)
![Made with ❤️](https://img.shields.io/badge/Made%20with-%E2%9D%A4-red)

A Bash script that keeps my Linux Mint 22 setup updated, tidy, and healthy — and writes a friendly, plain‑English report every time it runs. It’s practical, transparent, and a little fun.

### Why I built this
- **Peace of mind**: I wanted updates that explain themselves.
- **Trustworthy automation**: Each chapter checks first, narrates actions, and errs on the side of safety.
- **Time-saver**: One command, a full system pass, and a clean summary at the end.

### What it solves for me
- **Predictability**: I can dry‑run to preview actions and impact.
- **Safety**: The most recent Timeshift snapshot is annotated as the last one before maintenance begins.
- **Clarity**: A single TXT report tells me what changed and how much space moved.

### What I learned (and care about)
- Build automation that I personally need.
- Safety nets (snapshots, checks, gates) build confidence.
- Small tools, big leverage: clear UX makes infra feel effortless.

---

### Key features
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
### Final Summary at the end

```text
------------------------------------------------------------
Chapter 21 — Maintenance Complete!
------------------------------------------------------------


🎉 All done! Here's what happened today:


Task                           | Status               | Notes                         
------------------------------ | -------------------- | ------------------------------
Safety Checkpoint              | ⚠️ Needs Attention   | No data                       
Homebrew Tools                 | ✅ Success           | Not installed (optional)      
System Updates                 | ⚠️ Needs Attention   | Updated successfully          
Package Cleanup                | ✅ Success           | Cleaned 22 orphans            
Flatpak Apps                   | ✅ Success           | 9 apps updated                
Snap Apps                      | ✅ Success           | Updated & cleaned old versions
Python Tools                   | ✅ Success           | Pipx apps checked             
AppImage Check                 | ✅ Success           | Found 6 AppImages, 8 /opt apps
Firmware Updates               | ⚠️ Needs Attention   | Updates installed - restart needed
Log Cleanup                    | ✅ Success           | Cleaned to 362.4M             
Kernel Cleanup                 | ⚠️ Needs Attention   | Cleaned old kernels           
Disk Health                    | ✅ Success           | All drives healthy            
GNOME Extensions               | ⚠️ Needs Attention   | 8 extensions updated          
Docker Cleanup                 | ✅ Success           | No data                       
Search Database                | ⚠️ Needs Attention   | Installed and initialized     
Deep Clean                     | ✅ Success           | Deep cleaned                  
SSD Optimization               | ⚠️ Needs Attention   | SSDs optimized                
System Health                  | ⚠️ Needs Attention   | Some service issues           
Graphics Card                  | ✅ Success           | GPU healthy, driver 550.163.01
Auto Updates                   | ⚠️ Needs Attention   | Not installed                 

📊 Space Summary:
   🎉 Freed up approximately 27648MB!
   Available space: 529G
Script encountered an error but continuing to summary...

📋 Overall Assessment:
   ⚠️ Several items need your attention.
   Review the orange items above for details.

💾 This report has been saved
```

---

