PYTHON ?= python3

.PHONY: verify

verify:
	$(PYTHON) scripts/check_public_companion_skeleton.py
	@echo "NEKPRESS_JAMOVI_COMPANION_SKELETON_VERIFY_OK"
