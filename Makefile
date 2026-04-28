.PHONY: help install pipeline-install web-install lint test test-pipeline test-web smoke publish schemas dev clean

PY ?= python
PIPELINE_CONFIG ?= pipeline/configs/smoke.yaml
BUNDLE_OUT ?= pipeline/artifacts/smoke

help:
	@echo "Targets:"
	@echo "  install         - install pipeline (uv) and web (pnpm) deps"
	@echo "  test            - run pipeline + web tests"
	@echo "  test-pipeline   - pytest under pipeline/"
	@echo "  smoke           - run vlens publish on smoke config and validate bundle"
	@echo "  schemas         - export pydantic JSON schemas + regenerate zod"
	@echo "  dev             - run next dev against local smoke bundle"
	@echo "  publish         - run vlens publish (default config)"
	@echo "  lint            - lint both stacks"
	@echo "  clean           - remove build artifacts"

pipeline-install:
	cd pipeline && $(PY) -m pip install -e .[dev]

web-install:
	cd web && pnpm install --frozen-lockfile || cd web && pnpm install

install: pipeline-install web-install

test-pipeline:
	cd pipeline && $(PY) -m pytest -q

test-web:
	cd web && pnpm test --run

test: test-pipeline test-web

smoke:
	cd pipeline && $(PY) -m vlens.cli publish --config configs/smoke.yaml --out artifacts/smoke
	cd pipeline && $(PY) -m vlens.cli verify --bundle artifacts/smoke

publish:
	cd pipeline && $(PY) -m vlens.cli publish --config configs/default.yaml --out artifacts/default

schemas:
	cd pipeline && $(PY) -m vlens.cli schema export --out ../web/lib/artifacts/schemas.generated.json

dev:
	cd web && pnpm dev

lint:
	cd pipeline && $(PY) -m ruff check src tests
	cd web && pnpm lint

clean:
	rm -rf pipeline/artifacts/* pipeline/.pytest_cache pipeline/.ruff_cache web/.next web/out web/playwright-report
