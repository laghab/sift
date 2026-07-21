package scanner

import (
	"context"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/laghab/sift/internal/fileop"
	"github.com/laghab/sift/internal/ocr"
	"github.com/laghab/sift/internal/output"
)

var vidExts = []string{".mp4", ".mkv", ".mov", ".avi", ".3gp", ".webm"}

func ScanVideos(ctx context.Context, dir string, o *ocr.OCR, minWords int, mode fileop.Mode, search string, workers int, prog *output.Progress) (total int, matched int, skipped int, matchedPaths, skippedPaths []string) {
	files := collectFiles(dir, vidExts)
	total = len(files)

	if prog != nil {
		prog.Total = total
		prog.Label = "videos"
		prog.StartTime = time.Now()
	}

	ffmpegPath, ffprobePath := findFFmpeg()
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
			processOneVideo(ctx, path, dir, o, minWords, mode, search, ffmpegPath, ffprobePath, prog, &mu, &matchedPaths, &skippedPaths, &matched, &skipped)
		}(f)
	}
	wg.Wait()

	return
}

func processOneVideo(ctx context.Context, path, dir string, o *ocr.OCR, minWords int, mode fileop.Mode, search, ffmpeg, ffprobe string,
	prog *output.Progress, mu *sync.Mutex, matchedPaths, skippedPaths *[]string, matched, skipped *int) {

	if ctx.Err() != nil {
		return
	}
	if prog != nil {
		prog.Update(1, "Scanning: "+filepath.Base(path))
	}

	duration := getDuration(ffprobe, path)
	frames, tmpdir := extractFrames(ctx, ffmpeg, path, duration)
	if tmpdir != "" {
		defer os.RemoveAll(tmpdir)
	}
	if len(frames) == 0 {
		recordSkipped(path, mu, skippedPaths, skipped)
		return
	}

	totalWords := 0
	for _, frame := range frames {
		text, err := o.Text(frame)
		if err != nil {
			continue
		}
		totalWords += ocr.CountMeaningfulWords(text)
		if search != "" && strings.Contains(strings.ToLower(text), strings.ToLower(search)) {
			totalWords = minWords
		}
		if totalWords >= minWords {
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
			return
		}
	}

	recordSkipped(path, mu, skippedPaths, skipped)
}

func getDuration(ffprobe, path string) float64 {
	cmd := exec.Command(ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path)
	out, err := cmd.Output()
	if err != nil {
		return 0
	}
	d, err := strconv.ParseFloat(strings.TrimSpace(string(out)), 64)
	if err != nil {
		return 0
	}
	return d
}

func extractFrames(ctx context.Context, ffmpeg, path string, duration float64) ([]string, string) {
	var interval int
	switch {
	case duration < 15:
		interval = 1
	case duration < 60:
		interval = 2
	default:
		interval = 5
	}

	tmpdir, err := os.MkdirTemp("", "sift_video_*")
	if err != nil {
		return nil, ""
	}

	pattern := filepath.Join(tmpdir, "frame%03d.jpg")
	cmd := exec.CommandContext(ctx, ffmpeg, "-i", path, "-vf", fmt.Sprintf("fps=1/%d", interval), "-q:v", "5", pattern, "-y")
	cmd.Env = append(os.Environ(), "OMP_THREAD_LIMIT=1")
	if err := cmd.Run(); err != nil {
		os.RemoveAll(tmpdir)
		return nil, ""
	}

	frames, err := filepath.Glob(filepath.Join(tmpdir, "*.jpg"))
	if err != nil || len(frames) == 0 {
		os.RemoveAll(tmpdir)
		return nil, ""
	}
	return frames, tmpdir
}

func findFFmpeg() (ffmpeg, ffprobe string) {
	ffmpeg = lookPath("ffmpeg")
	ffprobe = lookPath("ffprobe")
	return
}

func lookPath(name string) string {
	exe, err := os.Executable()
	if err == nil {
		dir := filepath.Dir(exe)
		candidate := filepath.Join(dir, name)
		if _, err := os.Stat(candidate); err == nil {
			return candidate
		}
		candidate = filepath.Join(dir, name+".exe")
		if _, err := os.Stat(candidate); err == nil {
			return candidate
		}
	}
	if p, err := exec.LookPath(name); err == nil {
		return p
	}
	return name
}
