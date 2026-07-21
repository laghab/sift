package ocr

import (
	"fmt"
	"os"
	"path/filepath"
	"sync"

	"github.com/otiai10/gosseract/v2"
)

type OCR struct {
	mu     sync.Mutex
	client *gosseract.Client
}

func New(lang string) (*OCR, error) {
	client := gosseract.NewClient()
	if err := client.SetLanguage(lang); err != nil {
		client.Close()
		return nil, fmt.Errorf("set language %q: %w", lang, err)
	}
	client.SetPageSegMode(3)
	return &OCR{client: client}, nil
}

func (o *OCR) Text(path string) (string, error) {
	o.mu.Lock()
	defer o.mu.Unlock()
	if err := o.client.SetImage(path); err != nil {
		return "", fmt.Errorf("set image %q: %w", path, err)
	}
	text, err := o.client.Text()
	if err != nil {
		return "", fmt.Errorf("ocr %q: %w", path, err)
	}
	return text, nil
}

func (o *OCR) Close() {
	o.mu.Lock()
	defer o.mu.Unlock()
	o.client.Close()
}

func TessdataDir() string {
	if d := os.Getenv("TESSDATA_PREFIX"); d != "" {
		return d
	}
	for _, p := range []string{
		"/usr/share/tessdata",
		"/usr/local/share/tessdata",
		"/opt/homebrew/share/tessdata",
	} {
		if info, err := os.Stat(p); err == nil && info.IsDir() {
			return p
		}
	}
	cacheDir, err := os.UserCacheDir()
	if err != nil {
		return ""
	}
	return filepath.Join(cacheDir, "sift", "tessdata")
}

func EnsureTessdata(targetDir string) error {
	if targetDir == "" {
		return nil
	}
	if _, err := os.Stat(targetDir); err == nil {
		files, _ := os.ReadDir(targetDir)
		for _, f := range files {
			if filepath.Ext(f.Name()) == ".traineddata" {
				return nil
			}
		}
	}
	if err := os.MkdirAll(targetDir, 0755); err != nil {
		return fmt.Errorf("create tessdata dir: %w", err)
	}
	entries, err := TessdataFS.ReadDir("tessdata")
	if err != nil {
		return fmt.Errorf("read embedded tessdata: %w", err)
	}
	for _, e := range entries {
		if e.IsDir() {
			continue
		}
		data, err := TessdataFS.ReadFile(filepath.Join("tessdata", e.Name()))
		if err != nil {
			return fmt.Errorf("read %s: %w", e.Name(), err)
		}
		dst := filepath.Join(targetDir, e.Name())
		if err := os.WriteFile(dst, data, 0644); err != nil {
			return fmt.Errorf("write %s: %w", e.Name(), err)
		}
	}
	return nil
}
