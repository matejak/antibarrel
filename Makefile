ifeq ("$(IMDIR)","")
	_IMDIR = .
else
	_IMDIR = $(IMDIR)
endif

INDICES ?= 01 02
STEM ?= s-%.tiff

VAL_THRESH ?= 0.5

DEPS = $(foreach idx,$(INDICES),deps-$(idx).pickle)

all: RESULT $(foreach idx,$(INDICES),c-$(idx).tiff) 

UP2DATE:
	touch $@

CENTER: $(DEPS) UP2DATE
	abar-center $(DEPS) $@

rot-%.tiff: deps-%.pickle CENTER UP2DATE
	abar-rot $< --center "$$(cat CENTER)" $@

labels-%.pickle: $(_IMDIR)/$(STEM) UP2DATE
	abar-labels --val-thresh $(VAL_THRESH) $< $@

lines-%.pickle: labels-%.pickle UP2DATE
	abar-lines $< $@

deps-%.pickle: lines-%.pickle UP2DATE
	abar-deps $< $@

labels2-%.pickle: rot-%.tiff UP2DATE
	abar-labels --val-thresh $(VAL_THRESH) $< $@

lines2-%.pickle: labels2-%.pickle rot-%.tiff CENTER UP2DATE
	abar-lines $< --center "$$(cat CENTER)" $@

deps2-%.pickle: lines2-%.pickle rot-%.tiff UP2DATE
	abar-deps $< $@

DEPS2 = $(foreach idx,$(INDICES),deps2-$(idx).pickle)
IMGS2 = $(foreach idx,$(INDICES),rot-$(idx).tiff)
datapoints.pickle: $(DEPS2) $(IMGS2) UP2DATE
	abar-datapoints $(DEPS2) $@

RESULT: datapoints.pickle UP2DATE
	abar-solution $< $@

c-%.tiff: $(_IMDIR)/$(STEM) RESULT
	convert $< -distort barrel "$$(cat RESULT | tr ',' ' ') $$(cat CENTER)" $@ 

ila-%: labels-%.pickle
	abari-labels $<

ili-%: lines-%.pickle
	abari-lines $<

ide-%: deps-%.pickle
	abari-deps $<

ipo: datapoints.pickle
	abari-datapoints $<

ila2-%: labels2-%.pickle
	abari-labels $<

ili2-%: lines2-%.pickle
	abari-lines $<

ide2-%: deps2-%.pickle
	abari-deps $<

clean:
	$(RM) *.pickle RESULT CENTER UP2DATE
	$(RM) f-0*.tiff rot-*.tiff

.PHONY: clean ila-% ili-% ide-% ipo ili2-% ide2-% all
