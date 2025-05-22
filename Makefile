SHELL := /bin/bash

# download all dependencies and build a tar archive
.PHONY: build
build:
	./build.sh

# clean the build directory
.PHONY: clean
clean:
	rm -rf build
