PYTHON ?= python3

.PHONY: verify metadata release clean

verify:
	$(PYTHON) scripts/build_errata.py --check
	$(PYTHON) scripts/check_public_companion_release.py
	@echo "NEKPRESS_JAMOVI_COMPANION_RELEASE_OK"

metadata:
	$(PYTHON) scripts/update_release_metadata.py

release: verify
	$(PYTHON) scripts/build_release_bundle.py

clean:
	rm -rf -- build dist
