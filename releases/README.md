# Reader-Assets Release

The versioned reader bundle contains the exact files recorded in `RELEASE_MANIFEST.json`.

Build it from a clean checkout:

```bash
make verify
make release
```

The resulting archive is `dist/nekpress-jamovi-companion-reader-assets-v1.0.1.zip`. The build is deterministic: identical source files produce identical member order, timestamps, permissions, and bytes.

The prior `reader-assets-v1` archive and GitHub Release remain immutable. Platform-metadata corrections are published as the separate `reader-assets-v1.0.1` patch release.

Before attaching an archive to a GitHub Release, verify the release commit, run CI, download the archive once, and run the checker again against a clean extraction.
