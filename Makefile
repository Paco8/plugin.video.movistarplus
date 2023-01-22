VERSION = $(shell ./get_version.py)
OUTPUT_DIR = plugin.video.movistarplus-$(VERSION)
OUTPUT_FILE = $(OUTPUT_DIR).zip

install:
	-install -d $(OUTPUT_DIR)/resources/lib/
	install -m 644 default.py service.py $(OUTPUT_DIR)/
	install -m 644 resources/lib/*.py $(OUTPUT_DIR)/resources/lib/
	install -m 644 resources/*.py $(OUTPUT_DIR)/resources/
	install -m 644 addon.xml $(OUTPUT_DIR)/
	install -m 644 *.png $(OUTPUT_DIR)/

	install -m 644 resources/settings.xml $(OUTPUT_DIR)/resources/
	-install -d $(OUTPUT_DIR)/resources/language/resource.language.en_gb/
	-install -d $(OUTPUT_DIR)/resources/language/resource.language.es_es/
	install -m 644 resources/language/resource.language.en_gb/strings.po $(OUTPUT_DIR)/resources/language/resource.language.en_gb/strings.po
	install -m 644 resources/language/resource.language.es_es/strings.po $(OUTPUT_DIR)/resources/language/resource.language.es_es/strings.po

	zip -9 -r $(OUTPUT_FILE) $(OUTPUT_DIR)/

clean:
	-rm -rf $(OUTPUT_DIR)/
	-rm $(OUTPUT_FILE)
	-rm *.pyo *.pyc
	-rm resources/lib/*.pyo resources/lib/*.pyc

