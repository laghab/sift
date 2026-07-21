package output

import (
	"encoding/json"
	"fmt"
	"os"
	"time"
)

type JSONResult struct {
	Scanned       int      `json:"scanned"`
	Matched       int      `json:"matched"`
	Skipped       int      `json:"skipped"`
	ElapsedSecs   float64  `json:"elapsed_seconds"`
	Mode          string   `json:"mode"`
	Action        string   `json:"action"`
	FilesMatched  []string `json:"files_matched"`
	FilesSkipped  []string `json:"files_skipped"`
}

func PrintJSON(total, matched, skipped int, elapsed time.Duration, mode, action string, matchedPaths, skippedPaths []string) {
	r := JSONResult{
		Scanned:      total,
		Matched:      matched,
		Skipped:      skipped,
		ElapsedSecs:  elapsed.Seconds(),
		Mode:         mode,
		Action:       action,
		FilesMatched: matchedPaths,
		FilesSkipped: skippedPaths,
	}
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	if err := enc.Encode(r); err != nil {
		fmt.Fprintf(os.Stderr, "Error encoding JSON: %v\n", err)
	}
}
