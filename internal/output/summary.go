package output

import (
	"fmt"
	"os"
	"time"
)

type ScanResult struct {
	Total   int
	Matched int
	Skipped int
	Elapsed time.Duration
	Label   string
	Action  string
}

func supportsColor() bool {
	file, _ := os.Stderr.Stat()
	return (file.Mode() & os.ModeCharDevice) != 0
}

func cyan(s string) string {
	if supportsColor() {
		return "\033[96m" + s + "\033[0m"
	}
	return s
}

func green(s string) string {
	if supportsColor() {
		return "\033[92m" + s + "\033[0m"
	}
	return s
}

func PrintSummary(r ScanResult) {
	pct := 0.0
	if r.Total > 0 {
		pct = float64(r.Matched) / float64(r.Total) * 100
	}
	elapsed := r.Elapsed.Truncate(time.Second)
	elapsedStr := fmt.Sprintf("%02d:%02d", int(elapsed.Minutes()), int(elapsed.Seconds())%60)

	fmt.Fprintln(os.Stderr)
	fmt.Fprintln(os.Stderr, cyan("  ─────────────────────────────────────"))
	fmt.Fprintln(os.Stderr, green("  SIFT COMPLETE"))
	fmt.Fprintln(os.Stderr, cyan("  ─────────────────────────────────────"))
	fmt.Fprintf(os.Stderr, "  %s scanned:  %d\n", r.Label, r.Total)
	fmt.Fprintf(os.Stderr, "  Text found → %s: %s (%0.1f%%)\n", r.Action, green(fmt.Sprint(r.Matched)), pct)
	fmt.Fprintf(os.Stderr, "  No text (left):    %d\n", r.Skipped)
	fmt.Fprintf(os.Stderr, "  Time taken:        %s\n", elapsedStr)
	fmt.Fprintln(os.Stderr, cyan("  ─────────────────────────────────────"))
	fmt.Fprintln(os.Stderr)
}
