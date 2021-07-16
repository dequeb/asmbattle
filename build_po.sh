
###### phase 1

cp locale/assembler.pot     locale/assembler.pot.old
cp locale/cpu.pot           locale/cpu.pot.old
cp locale/memory.pot        locale/memory.pot.old
cp locale/ui_controller.pot locale/ui_controller.pot.old
cp locale/ui_view.pot       locale/ui_view.pot.old

# cp locale/fr_CA/LC_MESSAGES/assembler.po     locale/fr_CA/LC_MESSAGES/assembler.po.old
# cp locale/fr_CA/LC_MESSAGES/cpu.po           locale/fr_CA/LC_MESSAGES/cpu.po.old
# cp locale/fr_CA/LC_MESSAGES/memory.po        locale/fr_CA/LC_MESSAGES/memory.po.old
# cp locale/fr_CA/LC_MESSAGES/ui_controller.po locale/fr_CA/LC_MESSAGES/ui_controller.po.old
# cp locale/fr_CA/LC_MESSAGES/ui_view.po       locale/fr_CA/LC_MESSAGES/ui_view.po.old

# cp locale/en_US/LC_MESSAGES/assembler.po     locale/en_US/LC_MESSAGES/assembler.po.old
# cp locale/en_US/LC_MESSAGES/cpu.po           locale/en_US/LC_MESSAGES/cpu.po.old
# cp locale/en_US/LC_MESSAGES/memory.po        locale/en_US/LC_MESSAGES/memory.po.old
# cp locale/en_US/LC_MESSAGES/ui_controller.po locale/en_US/LC_MESSAGES/ui_controller.po.old
# cp locale/en_US/LC_MESSAGES/ui_view.po       locale/en_US/LC_MESSAGES/ui_view.po.old

xgettext -d assembler       -o locale/assembler.pot     asmbattle/assembler.py
xgettext -d cpu             -o locale/cpu.pot           asmbattle/cpu.py
xgettext -d memory          -o locale/memory.pot        asmbattle/memory.py
xgettext -d ui_controller   -o locale/ui_controller.pot asmbattle/ui_controller.py
xgettext -d ui_view         -o locale/ui_view.pot       asmbattle/ui_view.py

# cp locale/assembler.pot     locale/fr_CA/LC_MESSAGES/assembler.po
# cp locale/cpu.pot           locale/fr_CA/LC_MESSAGES/cpu.po
# cp locale/memory.pot        locale/fr_CA/LC_MESSAGES/memory.po
# cp locale/ui_controller.pot locale/fr_CA/LC_MESSAGES/ui_controller.po
# cp locale/ui_view.pot       locale/fr_CA/LC_MESSAGES/ui_view.po

# cp locale/assembler.pot     locale/en_US/LC_MESSAGES/assembler.po
# cp locale/cpu.pot           locale/en_US/LC_MESSAGES/cpu.po
# cp locale/memory.pot        locale/en_US/LC_MESSAGES/memory.po
# cp locale/ui_controller.pot locale/en_US/LC_MESSAGES/ui_controller.po
# cp locale/ui_view.pot       locale/en_US/LC_MESSAGES/ui_view.po
