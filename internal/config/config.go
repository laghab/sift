package config

type Config struct {
	Directory string
	Lang      string
	Threshold int
	Workers   int
	Search    string
	Video     bool
	JSON      bool
	Copy      bool
	DryRun    bool
}

func (c *Config) Mode() string {
	if c.DryRun {
		return "preview"
	}
	if c.Copy {
		return "copy"
	}
	return "move"
}
