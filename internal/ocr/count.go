package ocr

import "unicode"

func CountMeaningfulWords(text string) int {
	count := 0
	start := 0
	for i, r := range text {
		if r == ' ' || r == '\t' || r == '\n' || r == '\r' {
			if i > start {
				if wordLen(text[start:i]) >= 3 {
					count++
				}
			}
			start = i + 1
		}
	}
	if start < len(text) {
		if wordLen(text[start:]) >= 3 {
			count++
		}
	}
	return count
}

func wordLen(word string) int {
	n := 0
	for _, r := range word {
		if unicode.IsLetter(r) {
			n++
		}
	}
	return n
}
