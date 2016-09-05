ifeq ("$(IMDIR)","")
	_IMDIR =
else
	_IMDIR = $(IMDIR)/
endif
INDICES = 01 02

DEPS = $(foreach idx,$(INDICES),deps-$(idx).pickle)
CENTER: $(DEPS) mk_center.py
	python mk_center.py $(DEPS) $@

rot-%.tiff: deps-%.pickle $(_IMDIR)s-%.tiff CENTER mk_rot.py
	python mk_rot.py $< --center "$$(cat CENTER)" $@

labels2-%.pickle: rot-%.tiff mk_labels.py
	python mk_labels.py $< $@

lines2-%.pickle: labels2-%.pickle rot-%.tiff CENTER mk_lines.py
	python mk_lines.py $< --center "$$(cat CENTER)" $@

deps2-%.pickle: lines2-%.pickle rot-%.tiff mk_deps.py
	python mk_deps.py $< $@

DEPS2 = $(foreach idx,$(INDICES),deps2-$(idx).pickle)
IMGS2 = $(foreach idx,$(INDICES),rot-$(idx).tiff)
datapoints.pickle: $(DEPS2) $(IMGS2) mk_datapoints.py
	python mk_datapoints.py $(DEPS2) $@

RESULT2: datapoints.pickle
	python mk_solution.py $< $@

c-%.tiff: s-%.tiff RESULT2
	convert $< -distort barrel "$$(cat RESULT2)" $@ 

all: RESULT2 $(foreach idx,$(INDICES),c-$(idx).tiff) 

ila-%: labels-%.pickle
	python inspect_labels.py $<

ili-%: lines-%.pickle
	python inspect_lines.py $<

ide-%: deps-%.pickle
	python inspect_deps.py $<

ipo: datapoints.pickle
	python inspect_datapoints.py $<

clean:
	$(RM) *.pickle RESULT RESULT2 CENTER
	$(RM) f-0*.tiff rot-*.tiff

.PHONY: clean ila-% ili-% ide-% ipo all

### vvv OLD STUFF vvv ###

labels-%.pickle: $(_IMDIR)s-%.tiff mk_labels.py
	python mk_labels.py $< $@

lines-%.pickle: labels-%.pickle mk_lines.py
	python mk_lines.py $< $@

deps-%.pickle: lines-%.pickle mk_deps.py
	python mk_deps.py $< $@

data.pickle: summary.pickle
	python do2.py $< $@ $(if $(PLOT),--plot)

summary.pickle: output-01.pickle output-02.pickle
	python conclude.py $^ $@

output-%.pickle: $(_IMDIR)s-%.tiff
	python do.py $< $@ $(if $(PLOT),--plot)

RESULT: data.pickle
	python problem.py $(if $(PLOT),--plot) $< > $@

f-%.tiff: $(_IMDIR)s-%.tiff RESULT
	convert $< -distort barrel "$$(cat RESULT)" $@ 

show: _show-01 _show-02

_show-%: f-%.tiff
	python do.py $< --plot
