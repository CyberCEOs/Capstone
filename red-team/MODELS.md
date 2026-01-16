Project models and large binaries
================================

This repo includes references to very large model files (GGUF) which must not be stored in Git history or pushed to GitHub directly because of repository size limits.

Recommended workflow
- Keep model binaries out of Git. Either:
  - Upload large models to a release or storage service (GitHub Releases, S3, or an internal file server), and add a small download helper script in this folder.
  - Use Git LFS for model files if you have the quota and want them versioned.

Where to place models for local development
- Place local model files in `red-team/memory/` (this folder is ignored by `.gitignore` for `*.gguf`).

How to add a model for collaborators
1. Upload the model file to GitHub Releases or cloud storage.
2. Add a short note in this file with the download link and checksum.
3. Do NOT commit the model into git history.

Quick helper (example):
```bash
# Download into local memory folder (example)
mkdir -p red-team/memory
curl -L -o red-team/memory/baronllm.gguf "<release-url>"
sha256sum red-team/memory/baronllm.gguf
```

If you need help moving the large file out of history, follow the instructions in the repo root README or ask me and I will generate the exact git-filter-repo commands.
