# Reader-Assets Release

The versioned reader bundle contains the exact files recorded in `RELEASE_MANIFEST.json`.

Build it from a clean checkout:

```bash
make verify
make release
```

The resulting archive is `dist/nekpress-jamovi-companion-reader-assets-v1.0.3.zip`. The build is deterministic: identical source files produce identical member order, timestamps, permissions, and bytes.

The prior `reader-assets-v1`, `reader-assets-v1.0.1`, and `reader-assets-v1.0.2` archives and GitHub Releases remain immutable. The Study 09 effect-size definition correction is published as the separate `reader-assets-v1.0.3` patch release.

Before attaching an archive to a GitHub Release, verify the release commit, run CI, download the archive once, and run the checker again against a clean extraction.
