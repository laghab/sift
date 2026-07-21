# Release Process

Sift uses GoReleaser for automated cross-platform builds.

## Trigger a release

Push a version tag:

```bash
git tag v1.1.0
git push origin v1.1.0
```

GitHub Actions will:
1. Build for linux/amd64, linux/arm64, windows/amd64
2. Create tarballs with LICENSE and README
3. Generate checksums
4. Attach everything to a GitHub release

## macOS builds

The CI runs on Linux and can't cross-compile CGo for macOS.
Build macOS binaries on a macOS machine:

```bash
go build -o sift ./cmd/sift/
tar czf sift_darwin_amd64.tar.gz sift LICENSE README.md
# For ARM Macs:
GOARCH=arm64 go build -o sift ./cmd/sift/
tar czf sift_darwin_arm64.tar.gz sift LICENSE README.md
```

Then upload the tarballs to the release manually.

## Manual build

```bash
make build
```

## Binary naming

Archives produced by GoReleaser:
- `sift_linux_amd64.tar.gz`
- `sift_linux_arm64.tar.gz`  
- `sift_windows_amd64.tar.gz`

macOS archives (manual):
- `sift_darwin_amd64.tar.gz`
- `sift_darwin_arm64.tar.gz`

Each archive contains the binary, LICENSE, and README.
