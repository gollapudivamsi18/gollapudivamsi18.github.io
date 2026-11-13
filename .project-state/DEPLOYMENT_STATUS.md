# Deployment status

- Live URL: https://gollapudivamsi18.github.io
- Source: GitHub Pages, branch `main`, root folder, `.nojekyll`.
- Live commit: b7ad5e3 (merge of PR #1, 13 Nov 2026). Previous live commit c9c35e2 stays in history.
- Verified live in the browser after the Pages build: index, projects.html, resume.html, assistant
  data and scripts, three diagrams, sitemap.xml and robots.txt all return 200; skill order
  01 Azure DevOps and SRE, 02 Azure cloud infrastructure, 03 Windows Server, 04 Linux; the assistant
  answered a Kubernetes question on the live page.
- CI on the merged head (5dab2d1): Validate demos (python-tests, helm, terraform, scripts,
  prometheus, public-site) and DevSecOps demo (lint, test, sast, secrets, dependencies, container)
  all green. `deploy-example` is skipped by design (it only runs with Azure OIDC configured).
- Profile README: https://github.com/gollapudivamsi18 (repository `gollapudivamsi18`, public).
