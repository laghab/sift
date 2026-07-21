## 1. Release Pipeline

- [x] 1.1 Fix `.goreleaser.yaml` CGo flags: add Docker build container with `tesseract-ocr-dev` and `libleptonica-dev`
- [x] 1.2 Create `.github/workflows/release.yml` that runs goreleaser on tag pushes
- [ ] 1.3 Push a tag to trigger CI release (manual: `git tag v1.1.0 && git push --tags`)
- [x] 1.4 Build Linux binary on this machine as fallback: `make build` → works

## 2. macOS Build

- [x] 2.1 Noted: macOS CGo cross-compile needs macOS runner. Documented in RELEASE.md.
- [ ] 2.2 Build macOS binary on macOS machine and attach to release

## 3. Install & Docs

- [x] 3.1 Update `install.sh` to download tarball and extract correctly
- [x] 3.2 Update `install.ps1` to download tarball and extract correctly
- [x] 3.3 Add download badges to README

## 4. Verification

- [x] 4.1 `make build` produces working binary
- [x] 4.2 Binary passes `--dry-run --json` on test images
- [ ] 4.3 `go install github.com/laghab/sift/cmd/sift@latest` works after tag is pushed

## 5. Cleanup

- [x] 5.1 Remove remaining PyInstaller build scripts
- [x] 5.2 Remove `.spec` files
- [x] 5.3 Remove Python `requirements.txt`
- [x] 5.4 Mark Python version as legacy in README
