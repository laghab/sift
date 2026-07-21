package fileop

import (
	"fmt"
	"io"
	"os"
	"path/filepath"
)

const DocDirName = "SIFT_docs"

type Mode string

const (
	ModeMove    Mode = "move"
	ModeCopy    Mode = "copy"
	ModePreview Mode = "preview"
)

func UniqueDest(dir string, stem string, ext string) string {
	dest := filepath.Join(dir, stem+ext)
	if _, err := os.Stat(dest); os.IsNotExist(err) {
		return dest
	}
	for i := 2; ; i++ {
		dest = filepath.Join(dir, fmt.Sprintf("%s_sifted%d%s", stem, i, ext))
		if _, err := os.Stat(dest); os.IsNotExist(err) {
			return dest
		}
	}
}

func DocDir(base string, filePath string) string {
	rel, err := filepath.Rel(base, filepath.Dir(filePath))
	if err != nil || rel == "." {
		return filepath.Join(base, DocDirName)
	}
	return filepath.Join(base, DocDirName, rel)
}

func Do(src string, dest string, mode Mode) error {
	switch mode {
	case ModePreview:
		return nil
	case ModeCopy:
		return copyFile(src, dest)
	case ModeMove:
		return os.Rename(src, dest)
	default:
		return fmt.Errorf("unknown mode: %s", mode)
	}
}

func copyFile(src, dst string) error {
	s, err := os.Open(src)
	if err != nil {
		return fmt.Errorf("open source: %w", err)
	}
	defer s.Close()

	if err := os.MkdirAll(filepath.Dir(dst), 0755); err != nil {
		return fmt.Errorf("create dest dir: %w", err)
	}

	d, err := os.Create(dst)
	if err != nil {
		return fmt.Errorf("create dest: %w", err)
	}
	defer d.Close()

	if _, err := io.Copy(d, s); err != nil {
		return fmt.Errorf("copy data: %w", err)
	}
	return nil
}
