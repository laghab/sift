BINARY=dist/sift
VERSION=$(shell git describe --tags --always 2>/dev/null || echo "dev")
LDFLAGS=-ldflags="-X main.version=$(VERSION)"
CGO_ENABLED=1

.PHONY: build clean test lint run

build:
	mkdir -p dist
	CGO_ENABLED=$(CGO_ENABLED) go build $(LDFLAGS) -o $(BINARY) ./cmd/sift/

build-static:
	mkdir -p dist
	CGO_ENABLED=$(CGO_ENABLED) go build $(LDFLAGS) \
		-tags static \
		-ldflags="-X main.version=$(VERSION) -extldflags '-static'" \
		-o $(BINARY) ./cmd/sift/

clean:
	rm -rf dist/

test:
	go test ./internal/...

lint:
	go vet ./internal/...
	staticcheck ./internal/... 2>/dev/null || true

run: build
	./$(BINARY) $(ARGS)
