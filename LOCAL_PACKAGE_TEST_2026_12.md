# Local package test — 2026.12.0

Test date: 30 September 2026.

- Both manifests declare version `2026.12.0` and identical interface metadata.
- The publisher-supplied `assets/AID.png` decodes as a 1024×1024 PNG and is byte-identical to the supplied image.
- Website, support, privacy and terms URLs are included.
- All 33 built-in audit-validator fixture tests passed.
- A valid 2026.12 fixture passes; a fixture declaring 2026.11 is rejected without migration.
- Relative Markdown references and manifest asset paths resolve.
- The 11-file upload ZIP passed integrity and content checks. Its single top-level directory is `assessment-item-designer/`.

The ZIP contains `plugin.json`, `.codex-plugin/plugin.json`, `LICENSE`, `assets/AID.png`, and the skill with its license, four references and audit validator. Previous artwork, repository documentation, examples, caches and Git files are excluded.

The assessment workflow is unchanged apart from release/schema declarations. A full prompt-based workflow test of 2026.12.0 has not been run. Historical prompt tests in `LOCAL_PACKAGE_TEST_2026_11.md` apply to that earlier package. No OpenAI portal upload, validation, review or publication has been performed.
