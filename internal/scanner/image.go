package scanner

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"github.com/laghab/sift/internal/fileop"
	"github.com/laghab/sift/internal/ocr"
	"github.com/laghab/sift/internal/output"
)

var imgExts = []string{".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif", ".heic", ".gif"}

type imgWorker struct {
	path         string
	matchedPaths *[]string
	skippedPaths *[]string
	matched      *int
	skipped      *int
	mu           *sync.Mutex
}

func ScanImages(ctx context.Context, dir string, o *ocr.OCR, threshold int, mode fileop.Mode, search string, workers int, prog *output.Progress) (total int, matched int, skipped int, matchedPaths, skippedPaths []string) {
	files := collectFiles(dir, imgExts)
	total = len(files)

	if prog != nil {
		prog.Total = total
		prog.Label = "images"
		prog.StartTime = time.Now()
	}

	var mu sync.Mutex
	sem := make(chan struct{}, workers)
	var wg sync.WaitGroup

	for _, f := range files {
		if ctx.Err() != nil {
			break
		}
		sem <- struct{}{}
		wg.Add(1)
	go func(path string) {
		defer wg.Done()
		defer func() { <-sem }()
		defer func() {
			if r := recover(); r != nil {
				fmt.Fprintf(os.Stderr, "panic processing %s: %v\n", path, r)
			}
		}()
		processOneImage(ctx, path, dir, o, threshold, mode, search, prog, &mu, &matchedPaths, &skippedPaths, &matched, &skipped)
	}(f)
	}
	wg.Wait()

	return
}

func processOneImage(ctx context.Context, path, dir string, o *ocr.OCR, threshold int, mode fileop.Mode, search string, prog *output.Progress,
	mu *sync.Mutex, matchedPaths, skippedPaths *[]string, matched, skipped *int) {

	if ctx.Err() != nil {
		return
	}

	if prog != nil {
		prog.Update(1, "Scanning: "+filepath.Base(path))
	}

	text, err := o.Text(path)
	if err != nil {
		recordSkipped(path, mu, skippedPaths, skipped)
		return
	}

	wc := ocr.CountMeaningfulWords(text)
	if search != "" && !strings.Contains(strings.ToLower(text), strings.ToLower(search)) {
		recordSkipped(path, mu, skippedPaths, skipped)
		return
	}
	if wc < threshold {
		recordSkipped(path, mu, skippedPaths, skipped)
		return
	}

	destDir := fileop.DocDir(dir, path)
	if err := os.MkdirAll(destDir, 0755); err != nil {
		recordSkipped(path, mu, skippedPaths, skipped)
		return
	}

	stem := strings.TrimSuffix(filepath.Base(path), filepath.Ext(path))
	dest := fileop.UniqueDest(destDir, stem, filepath.Ext(path))
	if err := fileop.Do(path, dest, mode); err != nil {
		recordSkipped(path, mu, skippedPaths, skipped)
		return
	}

	mu.Lock()
	*matched++
	*matchedPaths = append(*matchedPaths, path)
	mu.Unlock()
}

func recordSkipped(path string, mu *sync.Mutex, skippedPaths *[]string, skipped *int) {
	mu.Lock()
	*skipped++
	*skippedPaths = append(*skippedPaths, path)
	mu.Unlock()
}

func collectFiles(dir string, exts []string) []string {
	extSet := make(map[string]bool, len(exts))
	for _, e := range exts {
		extSet[strings.ToLower(e)] = true
	}

	var files []string
	filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return nil
		}
		if info.IsDir() {
			if info.Name() == fileop.DocDirName {
				return filepath.SkipDir
			}
			return nil
		}
		if extSet[strings.ToLower(filepath.Ext(path))] {
			files = append(files, path)
		}
		return nil
	})
	return files
}
