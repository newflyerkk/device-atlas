# Device Atlas maintenance

The user has authorized keeping this project synchronized to GitHub and deploying updates through GitHub Pages.

After a requested website or dataset update:
1. Run `python3 work/device-library/build.py`.
2. Run `node work/device-library/test.mjs` (use the available Node runtime).
3. Review the diff; stage only relevant project files and generated HTML.
4. Commit with a descriptive message and push `main` to `origin`.
5. Check the GitHub Actions deployment and report its result. Never claim deployment success before verification.

Do not invent missing device specifications, sale dates, shipment counts, or Android density values. Retain provenance and unknown fields.
