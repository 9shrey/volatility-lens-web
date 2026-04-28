# Vercel infra notes

This folder documents the bits of Vercel configuration that live *outside* the
codebase (project settings, env vars, Blob bindings). The `vercel.json` at the
repo root is the only config consumed at build time.

See [`env.example.md`](env.example.md) for the env-var contract and
[`docs/deployment.md`](../../docs/deployment.md) for one-time setup.
