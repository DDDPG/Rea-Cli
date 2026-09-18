# Security policy

reacli runs local Python and REAPER scripts with the permissions of the invoking
user. Generated scripts, custom ReaScripts and REAPER plugins are executable
code. Resource-directory isolation separates preferences and worker state; it
does not sandbox scripts or restrict their access to files and the network.

Use trusted scripts and disposable project copies. REAPER may resolve project
media and plugin paths outside the project directory. Run untrusted material in
an appropriately isolated operating-system environment, not in your normal
editing session. A successful proof reports script execution, not a security
assessment of that script or a guarantee of the intended audio result.

## Reporting a vulnerability

Use **Security → Report a vulnerability** on the hosting GitHub repository when
private vulnerability reporting is enabled. If that option is unavailable,
open an issue asking the maintainers for a private reporting channel; omit
exploit details, credentials and private project files from the public issue.

Provide the affected version or commit, platform, minimal reproduction and
expected impact through the private channel. Redact sensitive paths and audio
material. Ordinary correctness bugs belong in the bug-report issue template.

The project is currently alpha. Security fixes target the latest development
revision; no long-term support branches or guaranteed response times are
promised. Repository administrators should enable GitHub private vulnerability
reporting before accepting public users.
