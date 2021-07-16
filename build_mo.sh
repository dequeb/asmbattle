###### phase 2

# cp locale/fr_CA/LC_MESSAGES/assembler.mo     locale/fr_CA/LC_MESSAGES/assembler.mo.old
# cp locale/fr_CA/LC_MESSAGES/cpu.mo           locale/fr_CA/LC_MESSAGES/cpu.mo.old
# cp locale/fr_CA/LC_MESSAGES/memory.mo        locale/fr_CA/LC_MESSAGES/memory.mo.old
# cp locale/fr_CA/LC_MESSAGES/ui_controller.mo locale/fr_CA/LC_MESSAGES/ui_controller.mo.old
# cp locale/fr_CA/LC_MESSAGES/ui_view.mo       locale/fr_CA/LC_MESSAGES/ui_view.mo.old

# cp locale/en_US/LC_MESSAGES/assembler.mo     locale/en_US/LC_MESSAGES/assembler.mo.old
# cp locale/en_US/LC_MESSAGES/cpu.mo           locale/en_US/LC_MESSAGES/cpu.mo.old
# cp locale/en_US/LC_MESSAGES/memory.mo        locale/en_US/LC_MESSAGES/memory.mo.old
# cp locale/en_US/LC_MESSAGES/ui_controller.mo locale/en_US/LC_MESSAGES/ui_controller.mo.old
# cp locale/en_US/LC_MESSAGES/ui_view.mo       locale/en_US/LC_MESSAGES/ui_view.mo.old

set -x #echo on

msgfmt -o locale/fr_CA/LC_MESSAGES/assembler.mo      locale/fr_CA/LC_MESSAGES/assembler.po
msgfmt -o locale/fr_CA/LC_MESSAGES/cpu.mo            locale/fr_CA/LC_MESSAGES/cpu.po
msgfmt -o locale/fr_CA/LC_MESSAGES/memory.mo         locale/fr_CA/LC_MESSAGES/memory.po
msgfmt -o locale/fr_CA/LC_MESSAGES/ui_controller.mo  locale/fr_CA/LC_MESSAGES/ui_controller.po
msgfmt -o locale/fr_CA/LC_MESSAGES/ui_view.mo        locale/fr_CA/LC_MESSAGES/ui_view.po

msgfmt -o locale/en_US/LC_MESSAGES/assembler.mo      locale/en_US/LC_MESSAGES/assembler.po
msgfmt -o locale/en_US/LC_MESSAGES/cpu.mo            locale/en_US/LC_MESSAGES/cpu.po
msgfmt -o locale/en_US/LC_MESSAGES/memory.mo         locale/en_US/LC_MESSAGES/memory.po
msgfmt -o locale/en_US/LC_MESSAGES/ui_controller.mo  locale/en_US/LC_MESSAGES/ui_controller.po
msgfmt -o locale/en_US/LC_MESSAGES/ui_view.mo        locale/en_US/LC_MESSAGES/ui_view.po
