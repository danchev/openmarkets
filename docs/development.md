# Development

## Dependency security

Audit the committed lockfile with uv's native OSV integration:

```bash
uv audit --locked
```

CI also enables uv's preview malware check during a locked sync. This check is
opt-in and requires a current uv release:

```bash
UV_MALWARE_CHECK=1 uv --preview-features malware-check sync --locked --all-groups --all-extras
```
