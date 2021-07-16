obj_files = aboutbox.mo assembler.mo cpu.mo memory.mo iu_controller.mo ui_view.mo
src_files = aboutbox.py assembler.py cpu.py memory.py iu_controller.py ui_view.py

all: $(obj_files)

$(filter %.o,$(obj_files)): %.o: %.c
    echo "target: $@ prereq: $<"
$(filter %.result,$(obj_files)): %.result: %.raw
    echo "target: $@ prereq: $<"

%.c %.raw:
    touch $@

clean:
    rm -f $(src_files)
