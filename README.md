# Toqie Public Release

<video src="demo.mp4" width="100%" autoplay loop muted playsinline></video>


This folder contains the public/stateless Toqie Kernel package.

## Included

- deploy_toqie.py
- release/kernel_runner.py
- release/kernel_parser.py
- release/kernel_http.py
- release/kernel_secret_guard.py

## Not Included

The proprietary Hippocampus layer is intentionally excluded:

- private/kernel_hippocampus.py
- private/kernel_memory_runner.py
- private/memory_index.json

## Run

```bash
python deploy_toqie.py
```

Expected public mode:

```text
PUBLIC TRACK / STATELESS
```

If a private/ folder is manually supplied later, the same gatekeeper can detect it and unlock Architect mode.
