# Basic Network Scanning with Nmap

## What is Nmap?

Nmap (Network Mapper) is an open-source tool for network discovery and security auditing. It can identify reachable hosts, open/closed/filtered ports, services and (with suitable probes) service versions and likely operating systems. See the [official Nmap documentation](https://nmap.org/book/man.html).

## Why scan?

An authorized scan helps inventory services that are listening, check whether they are expected, and prioritize firewall, configuration, and patching reviews. An open port is not automatically a vulnerability; it identifies a listening service whose exposure and configuration should be reviewed.

## Ethical scope

**This project scanned only `127.0.0.1`, the loopback address of this Windows machine.** No other machine, VM, external IP address, or network range was scanned. Scan only systems you own or have explicit written permission to assess. Use a local VM for broader practice, and agree on scope and timing before scanning shared systems. Do not use results to access services or data without authorization.

## Install Nmap on Windows

Nmap was installed using Windows Package Manager:

```powershell
winget install --id Insecure.Nmap --exact --accept-source-agreements --accept-package-agreements
```

The installed executable was `C:\Program Files (x86)\Nmap\nmap.exe`, version **7.80**. The command was not automatically added to this PowerShell session's `PATH`, so invoke it by full path or add the install folder to `PATH`. The Winget package available in this environment was older than the current official release. For a current build, download the Windows self-installer from the [official Nmap download page](https://nmap.org/download.html) and follow the [official Windows installation guide](https://nmap.org/book/inst-windows.html). The official installer includes Npcap, which supports local loopback scanning on Windows.

Verify installation:

```powershell
& 'C:\Program Files (x86)\Nmap\nmap.exe' --version
```

## Scans performed

All commands below target loopback only:

```powershell
& 'C:\Program Files (x86)\Nmap\nmap.exe' 127.0.0.1
& 'C:\Program Files (x86)\Nmap\nmap.exe' -sV --version-light 127.0.0.1
& 'C:\Program Files (x86)\Nmap\nmap.exe' -O 127.0.0.1
```

- The basic scan checks Nmap's default 1,000 TCP ports.
- `-sV` probes open ports to identify services and versions. `--version-light` limits probe intensity.
- `-O` attempts operating-system fingerprinting; results can be inconclusive, especially on loopback.

## Findings

The scan found four open TCP ports on the local machine: **100, 135, 445, and 3306**. Local process inspection associated them with SamsungFindWindowsService, Windows RPC, Windows SMB/System, and `mysqld.exe`. Nmap's service labels for ports 100, 445, and 3306 were tentative. The MySQL response contained an 8.0.46 protocol banner, but Nmap 7.80 did not produce a definitive version match. OS detection did not produce an exact fingerprint.

Read [nmap_scan_results.txt](./nmap_scan_results.txt) for the structured results and service-by-service risk notes. Raw command output is retained in [scan_output/](./scan_output/).

An open loopback port confirms a local listener responded; it does **not** establish that the port is reachable from another computer. Firewall policy, interface binding, and network configuration were not tested from an external vantage point. Review the listener, firewall rules, service configuration, and software ownership before making changes.

## Screenshot evidence

The raw Nmap output files are the authoritative scan evidence. If genuine desktop screenshots are needed in a GitHub submission, run each documented command in a visible PowerShell window, capture that terminal output with the operating system's screenshot tool, and save the images under `screenshots/`. Do not present generated or edited text renderings as unaltered terminal screenshots.
