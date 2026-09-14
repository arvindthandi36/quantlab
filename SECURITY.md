# Local security scope

QuantLab is local educational software. It binds to 127.0.0.1 and uses Host/origin checks and a
per-process request token for commands. These controls do not turn it into an authenticated
internet service. Do not expose it through a public proxy or bind it to a public interface.

Import only journals and data you intend to inspect. Strict JSON and replay verification reject
many malformed inputs, but this is not a guarantee against resource exhaustion or a hostile
local process. Complete journals contain privileged post-session simulation evidence.

Keep personal runs, progress, original datasets and credentials out of public issues. For a suspected
security defect, prepare a minimal synthetic reproduction. No private security contact or response
SLA is configured; coordinate a private channel with the repository owner before disclosing secrets
or a sensitive exploit. Never invent contact details.

Repository secret scanning is a useful check, not a formal audit. [Limitations](docs/LIMITATIONS.md).
