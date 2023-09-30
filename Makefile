VERSION = $(shell ./get_version.py)
OUTPUT_DIR = plugin.video.movistarplus-$(VERSION)
OUTPUT_FILE = $(OUTPUT_DIR).zip

install:
	-install -d $(OUTPUT_DIR)/resources/lib/
	install -m 644 default.py service.py $(OUTPUT_DIR)/
	install -m 644 resources/lib/*.py $(OUTPUT_DIR)/resources/lib/
	install -m 644 resources/*.py $(OUTPUT_DIR)/resources/
	install -m 644 resources/*.jpg $(OUTPUT_DIR)/resources/
	install -m 644 resources/fanart.png $(OUTPUT_DIR)/resources/
	install -m 644 addon.xml $(OUTPUT_DIR)/
	install -m 644 *.png $(OUTPUT_DIR)/

	-install -d $(OUTPUT_DIR)/resources/icons/
	install -m 644 resources/icons/*.png $(OUTPUT_DIR)/resources/icons/

	install -m 644 resources/settings.xml $(OUTPUT_DIR)/resources/
	-install -d $(OUTPUT_DIR)/resources/language/resource.language.en_gb/
	-install -d $(OUTPUT_DIR)/resources/language/resource.language.es_es/
	install -m 644 resources/language/resource.language.en_gb/strings.po $(OUTPUT_DIR)/resources/language/resource.language.en_gb/strings.po
	install -m 644 resources/language/resource.language.es_es/strings.po $(OUTPUT_DIR)/resources/language/resource.language.es_es/strings.po

	-install -d $(OUTPUT_DIR)/resources/skins/default/1080i/
	-install -d $(OUTPUT_DIR)/resources/skins/default/media/
	install -m 644 resources/skins/default/1080i/*.xml $(OUTPUT_DIR)/resources/skins/default/1080i/
	install -m 644 resources/skins/default/media/*.png $(OUTPUT_DIR)/resources/skins/default/media/
	#install -m 644 resources/skins/default/media/*.jpg $(OUTPUT_DIR)/resources/skins/default/media/

	zip -9 -r $(OUTPUT_FILE) $(OUTPUT_DIR)/
	- ln -s $(OUTPUT_DIR)/ plugin.video.movistarplus-latest

clean:
	-rm -rf $(OUTPUT_DIR)/
	-rm $(OUTPUT_FILE)
	-rm *.pyo *.pyc
	-rm resources/lib/*.pyo resources/lib/*.pyc
	-rm plugin.video.movistarplus-latest
