PYTHON ?= python3

.PHONY: verify audit audit-volume2 metadata release clean

verify:
	$(PYTHON) scripts/build_errata.py --check
	$(PYTHON) scripts/check_public_companion_release.py
	$(PYTHON) scripts/check_open_materials.py
	$(PYTHON) scripts/check_open_materials_volume2.py
	$(PYTHON) scripts/verify_resource_numbers.py
	$(PYTHON) scripts/verify_volume2_numbers.py
	@echo "NEKPRESS_JAMOVI_COMPANION_RELEASE_OK"

audit:
	$(PYTHON) scripts/verify_resource_numbers.py

audit-volume2:
	$(PYTHON) scripts/verify_volume2_numbers.py

metadata:
	$(PYTHON) scripts/update_release_metadata.py

release: verify
	$(PYTHON) scripts/build_release_bundle.py

clean:
	rm -rf -- build dist
