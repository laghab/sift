package ocr

import (
	"fmt"
	"os/exec"
	"strings"
	"sync"
)

type OCR struct {
	lang string
	mu   sync.Mutex
}

func New(lang string) (*OCR, error) {
	if _, err := exec.LookPath("tesseract"); err != nil {
		return nil, fmt.Errorf("tesseract not found on PATH: %w", err)
	}
	return &OCR{lang: lang}, nil
}

func (o *OCR) Text(path string) (string, error) {
	o.mu.Lock()
	defer o.mu.Unlock()
	cmd := exec.Command("tesseract", path, "stdout", "--psm", "3", "-l", o.lang)
	out, err := cmd.Output()
	if err != nil {
		if ee, ok := err.(*exec.ExitError); ok {
			return "", fmt.Errorf("tesseract %q: %s", path, strings.TrimSpace(string(ee.Stderr)))
		}
		return "", fmt.Errorf("tesseract %q: %w", path, err)
	}
	return strings.TrimSpace(string(out)), nil
}

func (o *OCR) Close() {}
