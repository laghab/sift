package main

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"runtime"
	"time"

	"github.com/spf13/cobra"

	"github.com/laghab/sift/internal/config"
	"github.com/laghab/sift/internal/fileop"
	"github.com/laghab/sift/internal/ocr"
	"github.com/laghab/sift/internal/output"
	"github.com/laghab/sift/internal/scanner"
)

var version = "v1.1.0"

func main() {
	for _, a := range os.Args[1:] {
		if a == "--version" || a == "-V" {
			fmt.Printf("Sift %s\n", version)
			os.Exit(0)
		}
	}

	cfg := &config.Config{}
	rootCmd := buildRoot(cfg)

	if err := rootCmd.Execute(); err != nil {
		os.Exit(1)
	}

	if cfg.Directory == "" {
		rootCmd.Help()
		fmt.Println()
		fmt.Println("  Example: sift ~/WhatsAppBackup")
		fmt.Println("           sift ~/WhatsAppBackup --video")
		fmt.Println("           sift ~/WhatsAppBackup --copy --search invoice")
		fmt.Println()
		os.Exit(0)
	}

	info, err := os.Stat(cfg.Directory)
	if err != nil || !info.IsDir() {
		fmt.Fprintf(os.Stderr, "  Error: '%s' is not a valid directory.\n", cfg.Directory)
		os.Exit(1)
	}

	workers := cfg.Workers
	if workers <= 0 {
		workers = max(1, int(float64(runtime.NumCPU())*0.7))
	}

	mode := fileop.Mode(cfg.Mode())
	actionLabel := map[fileop.Mode]string{
		fileop.ModeMove:    "moved",
		fileop.ModeCopy:    "copied",
		fileop.ModePreview: "identified",
	}[mode]

	if !cfg.JSON {
		fmt.Fprintf(os.Stderr, "  Target:    %s\n", cfg.Directory)
		fmt.Fprintf(os.Stderr, "  Workers:   %d\n", workers)
		modeStr := "Image"
		if cfg.Video {
			modeStr = "Video"
		}
		fmt.Fprintf(os.Stderr, "  Mode:      %s scan\n", modeStr)
		fmt.Fprintf(os.Stderr, "  Action:    %s\n", string(mode))
		if cfg.Search != "" {
			fmt.Fprintf(os.Stderr, "  Search:    %s\n", cfg.Search)
		}
		fmt.Fprintf(os.Stderr, "  Threshold: %d+ words\n", cfg.Threshold)
		fmt.Fprintln(os.Stderr)
	}

	o, err := ocr.New(cfg.Lang)
	if err != nil {
		fmt.Fprintf(os.Stderr, "  Error initializing OCR: %v\n", err)
		os.Exit(1)
	}
	defer o.Close()

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, os.Interrupt)
	go func() {
		<-sigCh
		cancel()
	}()

	var prog *output.Progress
	if !cfg.JSON {
		prog = &output.Progress{}
	}

	start := time.Now()
	var total, matched, skipped int
	var matchedPaths, skippedPaths []string

	if cfg.Video {
		total, matched, skipped, matchedPaths, skippedPaths = scanner.ScanVideos(
			ctx, cfg.Directory, o, cfg.Threshold, mode, cfg.Search, workers, prog)
	} else {
		total, matched, skipped, matchedPaths, skippedPaths = scanner.ScanImages(
			ctx, cfg.Directory, o, cfg.Threshold, mode, cfg.Search, workers, prog)
	}
	elapsed := time.Since(start)

	if ctx.Err() != nil {
		if !cfg.JSON {
			fmt.Fprintln(os.Stderr, "\n  Interrupted by user.")
		}
		os.Exit(130)
	}

	if prog != nil {
		prog.Done()
	}

	label := "images"
	if cfg.Video {
		label = "videos"
	}

	if cfg.JSON {
		modeStr := "image"
		if cfg.Video {
			modeStr = "video"
		}
		output.PrintJSON(total, matched, skipped, elapsed, modeStr, string(mode), matchedPaths, skippedPaths)
	} else {
		output.PrintSummary(output.ScanResult{
			Total:   total,
			Matched: matched,
			Skipped: skipped,
			Elapsed: elapsed,
			Label:   label,
			Action:  actionLabel,
		})
	}
}

func buildRoot(cfg *config.Config) *cobra.Command {
	root := &cobra.Command{
		Use:   "sift [directory]",
		Short: "Sift — Digital Document Sifter",
		Long: `Sift finds images and videos containing text using OCR,
and moves/copies them into a SIFT_docs/ folder.

Examples:
  sift ~/WhatsAppBackup
  sift ~/WhatsAppBackup --video
  sift ~/WhatsAppBackup --copy --search invoice
  sift ~/WhatsAppBackup --json`,
		Args: cobra.MaximumNArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			if len(args) > 0 {
				cfg.Directory = args[0]
			}
			return nil
		},
	}

	root.Flags().BoolVarP(&cfg.Video, "video", "v", false, "Scan videos instead of images (requires ffmpeg)")
	root.Flags().IntVarP(&cfg.Workers, "workers", "w", 0, "Number of parallel workers (default: 70% of CPU)")
	root.Flags().StringVarP(&cfg.Lang, "lang", "l", "eng", "Tesseract language (default: eng)")
	root.Flags().IntVarP(&cfg.Threshold, "threshold", "t", 2, "Minimum meaningful words to consider as document (default: 2)")
	root.Flags().BoolVar(&cfg.Copy, "copy", false, "Copy files to SIFT_docs instead of moving them")
	root.Flags().BoolVar(&cfg.DryRun, "dry-run", false, "Show which files would be processed without performing file operations")
	root.Flags().StringVar(&cfg.Search, "search", "", "Only process files containing this text (case-insensitive)")
	root.Flags().BoolVar(&cfg.JSON, "json", false, "Output results as JSON to stdout")

	root.CompletionOptions.DisableDefaultCmd = true
	root.SilenceErrors = true

	return root
}
