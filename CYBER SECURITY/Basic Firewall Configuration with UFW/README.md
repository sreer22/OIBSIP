# Basic Firewall Configuration with UFW

## What a firewall does

A host firewall filters network traffic according to rules. UFW (Uncomplicated Firewall) is a command-line frontend for managing Linux firewall rules. This configuration uses a default-deny inbound policy, explicitly permits the required management/web traffic, and blocks two services that should not be exposed in this lab.

## Scope and safety

This project creates a runnable Linux script and instructions only. **It has not been run and has not changed this Windows machine's firewall.** Run it only inside an Ubuntu, Debian, or Kali Linux VM that you own or are authorized to administer.

Enabling a firewall can disrupt existing connections. The script:

- Requires root privileges and asks the operator to type `APPLY`.
- Displays current numbered rules and requires a second `APPLY RULES` confirmation before changing policies or adding rules.
- Adds an explicit TCP/22 SSH allow rule before enabling UFW.
- Refuses to continue when it detects a remote SSH session on a nonstandard local port.
- Does not reset or delete existing rules, but it does change the default incoming and outgoing policies.

Use the VM's local console for the first activation. Confirm that SSH really listens on TCP/22; adapt the rule and safety check before using a nonstandard SSH port. Review the displayed existing numbered rules: UFW rule order matters, and an existing broad allow rule can affect the requested deny behavior. Do not proceed until existing rules are understood. Keep VM console access available. Do not run the script on a production or remote system without a reviewed rollback and recovery plan.

## Rules and rationale

| Rule | Effect | Why chosen |
|---|---|---|
| `default deny incoming` | Blocks inbound connections unless an allow rule matches. | Least-privilege starting policy for a basic host firewall. |
| `default allow outgoing` | Allows the VM to initiate outbound connections. | Preserves normal package installation, updates, and browsing for this learning setup. |
| `allow 22/tcp` | Permits inbound SSH on the standard TCP port. | Required for remote administration; allow it before enabling the firewall to reduce lockout risk. |
| `deny 80/tcp` | Explicitly blocks inbound unencrypted HTTP. | The assignment requires a deny rule; use HTTPS instead for web access. |
| `allow 443/tcp` | Permits inbound HTTPS. | Additional example rule for encrypted web service traffic. |
| `deny 3306/tcp` | Blocks inbound MySQL. | Database ports generally should not be directly reachable by arbitrary clients; access should be limited to a trusted application or network. |

The default-deny policy applies to other unsolicited incoming traffic as well. The explicit HTTP and MySQL denies make those intended restrictions visible in the status output. This script does not change IPv6 settings, router firewall policy, or cloud network rules.

## Install and run in a Linux VM

Copy this folder into the VM, then run:

```bash
chmod +x ufw_configuration.sh
sudo ./ufw_configuration.sh
```

If UFW is missing, the script runs `apt-get update` and installs it with `apt-get install -y ufw`. Type `APPLY` to permit setup to continue. Review the current numbered rules; if the requested policy is safe for this VM, type `APPLY RULES` to make firewall changes. Otherwise, enter anything else to exit without applying firewall rules. The script prints `ufw status verbose` after activation.

To inspect rules later:

```bash
sudo ufw status verbose
sudo ufw status numbered
```

To disable UFW from the VM console if necessary:

```bash
sudo ufw disable
```

## Verify that HTTP is blocked

Test across an isolated host-only VM network using a second VM that you control. Do not infer remote filtering from a test to `127.0.0.1`; loopback traffic is not a valid test of inbound filtering from another host.

1. On the target VM, find its lab IP with `ip -brief address`.
2. Start a temporary HTTP server on TCP/80 from the target VM console (only in the isolated lab):

   ```bash
   sudo python3 -m http.server 80 --bind 0.0.0.0
   ```

3. From the authorized client VM, test the target lab IP:

   ```bash
   nc -vz -w 3 TARGET_VM_IP 80
   ```

   With UFW active and the deny rule applied, the connection should fail or time out. The server must be running for this test to be meaningful. Stop it with `Ctrl+C` on the target VM.

4. Verify the active policy on the target:

   ```bash
   sudo ufw status verbose
   ```

   Expect `Status: active`, default incoming `deny`, and the SSH/HTTP/HTTPS/MySQL rules. A remote test can also be affected by VM network mode, routing, or another firewall, so record the client and target VM network details with the result.

## Screenshot evidence

No Linux VM was available in this workspace, so no live UFW status or screenshot was produced. After running the script in your VM, capture the actual terminal output of `sudo ufw status verbose` and save it as `screenshots/ufw_status.png`. Do not use a mock terminal image as evidence of a real firewall state.

## References

- [Ubuntu UFW guide](https://help.ubuntu.com/community/UFW)
- [UFW manual page](https://manpages.ubuntu.com/manpages/jammy/en/man8/ufw.8.html)
