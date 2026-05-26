.PHONY: docs

test:
	uv run pytest --junitxml=report.xml tests/

ruff:
	uv run ruff check .

cov:
	uv run --group test pytest --cov=gnmi tests/

# publish:
# 	pip3 install 'twine>=1.5.0'
# 	python3 setup.py sdist bdist_wheel
# 	twine upload dist/*
# 	rm -fr build dist .egg gnmi-py.egg-info

proto:
	uv run --group dev sh scripts/genprotos.sh

docs:
	cd docs && uv run make html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at docs/_build/html/index.html.\n\033[0m"

bump-patch: ## Bump the patch version (x.y.Z), commit, and tag
	@$(MAKE) _bump PART=patch

bump-minor: ## Bump the minor version (x.Y.0), commit, and tag
	@$(MAKE) _bump PART=minor

bump-major: ## Bump the major version (X.0.0), commit, and tag
	@$(MAKE) _bump PART=major

push: ## Push it
	git push && git push --tags

VERSION = $$(uv version --short)

.PHONY: _bump

_bump:
	@echo "Bumping version..."
	uv version --bump $(PART)
	
	@echo "Syncing uv.lock..."
	uv sync
	
	@echo "Committing and tagging... v$(VERSION)"
	git add pyproject.toml uv.lock
	git commit -m "bump version to v$(VERSION)"
	git tag v$(VERSION)
	
	@echo "Done! Run 'git push && git push --tags' to publish."