ifeq ("$(IMDIR)","")
	_IMDIR = .
else
	_IMDIR = $(IMDIR)
endif

INDICES ?= 00 01
STEM ?= s-%.tiff

VAL_THRESH ?= 0.5

DEPS = $(foreach idx,$(INDICES),deps-$(idx).pickle)

all: RESULT $(foreach idx,$(INDICES),c-$(idx).tiff) 

CENTER: $(DEPS) mk_center.py
	python mk_center.py $(DEPS) $@

rot-%.tiff: deps-%.pickle CENTER mk_rot.py
	python mk_rot.py $< --center "$$(cat CENTER)" $@

labels-%.pickle: $(_IMDIR)/$(STEM) mk_labels.py
	python mk_labels.py --val-thresh $(VAL_THRESH) $< $@

lines-%.pickle: labels-%.pickle mk_lines.py
	python mk_lines.py $< $@

deps-%.pickle: lines-%.pickle mk_deps.py
	python mk_deps.py $< $@

labels2-%.pickle: rot-%.tiff mk_labels.py
	python mk_labels.py --val-thresh $(VAL_THRESH) $< $@

lines2-%.pickle: labels2-%.pickle rot-%.tiff CENTER mk_lines.py
	python mk_lines.py $< --center "$$(cat CENTER)" $@

deps2-%.pickle: lines2-%.pickle rot-%.tiff mk_deps.py
	python mk_deps.py $< $@

DEPS2 = $(foreach idx,$(INDICES),deps2-$(idx).pickle)
IMGS2 = $(foreach idx,$(INDICES),rot-$(idx).tiff)
datapoints.pickle: $(DEPS2) $(IMGS2) mk_datapoints.py
	python mk_datapoints.py $(DEPS2) $@

RESULT: datapoints.pickle mk_solution.py
	python mk_solution.py $< $@

c-%.tiff: $(_IMDIR)/$(STEM) RESULT
	convert $< -distort barrel "$$(cat RESULT | tr ',' ' ') $$(cat CENTER)" $@ 

ila-%: labels-%.pickle
	python inspect_labels.py $<

ili-%: lines-%.pickle
	python inspect_lines.py $<

ide-%: deps-%.pickle
	python inspect_deps.py $<

ipo: datapoints.pickle
	python inspect_datapoints.py $<

ila2-%: labels2-%.pickle
	python inspect_labels.py $<

ili2-%: lines2-%.pickle
	python inspect_lines.py $<

ide2-%: deps2-%.pickle
	python inspect_deps.py $<

clean:
	$(RM) *.pickle RESULT CENTER
	$(RM) f-0*.tiff rot-*.tiff

.PHONY: clean ila-% ili-% ide-% ipo ili2-% ide2-% all
