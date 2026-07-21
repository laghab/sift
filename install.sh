#!/usr/bin/env bash
set -euo pipefail

REPO="laghab/sift"
VERSION="${1:-latest}"
INSTALL_DIR="${SIFT_INSTALL_DIR:-$HOME/.local/bin}"

if [ "$VERSION" = "latest" ]; then
    DOWNLOAD_URL="https://github.com/$REPO/releases/latest/download"
else
    DOWNLOAD_URL="https://github.com/$REPO/releases/download/$VERSION"
fi

detect_arch() {
    local arch
    arch="$(uname -m)"
    case "$arch" in
        x86_64|amd64) echo "x86_64" ;;
        aarch64|arm64) echo "arm64" ;;
        *) echo "unsupported: $arch"; return 1 ;;
    esac
}

detect_os() {
    local os
    os="$(uname -s)"
    case "$os" in
        Linux) echo "linux" ;;
        Darwin) echo "macos" ;;
        *) echo "unsupported: $os"; return 1 ;;
    esac
}

main() {
    local os arch filename url tmpdir
    os="$(detect_os)"
    arch="$(detect_arch)"
    filename="sift_${os}_${arch}.tar.gz"

    echo "  Sift Installer"
    echo "  Detected: $os ($arch)"
    echo ""

    url="$DOWNLOAD_URL/$filename"
    echo "  Downloading $url ..."

    tmpdir="$(mktemp -d)"
    trap 'rm -rf "$tmpdir"' EXIT
    (
        cd "$tmpdir"
        if command -v curl &>/dev/null; then
            curl -fsSL "$url" -o "$filename"
        elif command -v wget &>/dev/null; then
            wget -q "$url" -O "$filename"
        else
            echo "  Error: need curl or wget"
            exit 1
        fi
        tar xzf "$filename"
    )

    mkdir -p "$INSTALL_DIR"
    cp "$tmpdir/sift" "$INSTALL_DIR/sift" 2>/dev/null || cp "$tmpdir/sift.exe" "$INSTALL_DIR/sift" 2>/dev/null
    chmod +x "$INSTALL_DIR/sift"
    echo "  Installed to: $INSTALL_DIR/sift"
    echo ""
    echo "  Make sure $INSTALL_DIR is in your PATH."
    echo "  Run 'sift --help' to get started."
}

main
