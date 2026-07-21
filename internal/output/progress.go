package output

import (
	"fmt"
	"os"
	"strings"
	"sync"
	"time"

	"golang.org/x/term"
)

const barWidth = 30

type Progress struct {
	mu         sync.Mutex
	Total      int
	Current    int
	Label      string
	StatusText string
	StartTime  time.Time
}

func (p *Progress) Update(n int, status string) {
	p.mu.Lock()
	defer p.mu.Unlock()
	p.Current += n
	if status != "" {
		p.StatusText = status
	}
	p.renderLocked()
}

func (p *Progress) renderLocked() {
	if p.Total == 0 {
		return
	}
	width, _, err := term.GetSize(int(os.Stderr.Fd()))
	if err != nil {
		width = 80
	}

	filled := p.Current * barWidth / p.Total
	if filled > barWidth {
		filled = barWidth
	}
	empty := barWidth - filled

	bar := strings.Repeat("█", filled) + strings.Repeat("╸", empty)

	elapsed := time.Since(p.StartTime).Truncate(time.Second)
	elapsedStr := fmt.Sprintf("%02d:%02d", int(elapsed.Minutes()), int(elapsed.Seconds())%60)

	line := fmt.Sprintf("  %s  %5.1f%%  [%d/%d %s]  ⏱ %s",
		bar, float64(p.Current)/float64(p.Total)*100, p.Current, p.Total, p.Label, elapsedStr)

	if p.StatusText != "" {
		suffix := "  " + p.StatusText
		if len(line)+len(suffix) < width {
			line += suffix
		}
	}

	padding := width - len(line)
	if padding < 0 {
		padding = 0
	}
	fmt.Fprintf(os.Stderr, "\r%s%s", line, strings.Repeat(" ", padding))
}

func (p *Progress) Done() {
	p.mu.Lock()
	defer p.mu.Unlock()
	fmt.Fprintln(os.Stderr)
}
