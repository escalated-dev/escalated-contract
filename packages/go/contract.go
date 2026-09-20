// Package contract reads the published Escalated contract.
//
// A port should not keep its own copy of the manifest. Each of the eleven
// ports used to vendor escalated-pages.json into its own testdata and refresh
// it by hand; two drifted and their parity tests stayed green, because each
// port was comparing itself against its own stale copy.
//
// The contract files are embedded, so a consumer needs nothing on disk.
package contract

import (
	"embed"
	"encoding/json"
	"fmt"
	"io/fs"
	"sync"
)

//go:embed contract
var files embed.FS

// PageProps is what a single page component reads.
type PageProps struct {
	// Props the component reads.
	Props []string `json:"props"`
	// Props it cannot render without.
	Required []string `json:"required"`
}

// Manifest is the published page contract.
type Manifest struct {
	// Version is the @escalated-dev/escalated release this came from.
	Version string `json:"version"`
	// Pages is every page name the shared frontend resolves.
	Pages []string `json:"pages"`
	// Props is keyed by page name.
	Props map[string]PageProps `json:"props"`
}

var (
	once   sync.Once
	loaded Manifest
	loadIn error
)

func load() (Manifest, error) {
	once.Do(func() {
		raw, err := files.ReadFile("contract/pages.json")
		if err != nil {
			loadIn = fmt.Errorf("reading embedded page manifest: %w", err)
			return
		}
		if err := json.Unmarshal(raw, &loaded); err != nil {
			loadIn = fmt.Errorf("parsing embedded page manifest: %w", err)
		}
	})
	return loaded, loadIn
}

// Pages returns every page name the shared frontend resolves.
//
// A name a backend renders that is not here is not a runtime error. Inertia
// returns 200, the resolver returns undefined, and the panel comes up blank.
func Pages() ([]string, error) {
	m, err := load()
	if err != nil {
		return nil, err
	}
	return m.Pages, nil
}

// PropsFor returns the props a page reads.
func PropsFor(page string) (PageProps, error) {
	m, err := load()
	if err != nil {
		return PageProps{}, err
	}
	p, ok := m.Props[page]
	if !ok {
		return PageProps{}, fmt.Errorf(
			"no props recorded for page %q: either the name is wrong, or the frontend has not released it yet", page)
	}
	return p, nil
}

// RendersPage reports whether the shared frontend has a component for a name.
func RendersPage(page string) (bool, error) {
	m, err := load()
	if err != nil {
		return false, err
	}
	for _, p := range m.Pages {
		if p == page {
			return true, nil
		}
	}
	return false, nil
}

// FrontendVersion returns the frontend release this manifest came from.
func FrontendVersion() (string, error) {
	m, err := load()
	if err != nil {
		return "", err
	}
	return m.Version, nil
}

// Conformance returns the embedded conformance fixtures, for a runner to walk.
func Conformance() (fs.FS, error) {
	return fs.Sub(files, "contract/conformance")
}
