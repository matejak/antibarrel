labels-%.pickle: s-%.tiff mk_label.py
	python mk_label.py $< $@

lines-%.pickle: labels-%.pickle mk_lines.py
	python mk_lines.py $< $@

deps-%.pickle: lines-%.pickle mk_deps.py
	python mk_deps.py $< $@

DEPS = 01 02

CENTER: $(foreach idx,deps-$(idx).pickle,$(INDICES)) mk_center.py
	python mk_center.py $(DEPS) $@

rot-%.tiff: deps-%.pickle s-%.tiff CENTER mk_rot.py
	python mk_rot.py $< --center "$$(cat CENTER)" $@

labels2-%.pickle: rot-%.tiff mk_label.py
	python mk_label.py $< $@

lines2-%.pickle: labels2-%.pickle CENTER mk_lines.py
	python mk_lines.py $< --center "$$(cat CENTER)" $@

deps2-%.pickle: lines2-%.pickle mk_deps.py
	python mk_deps.py $< $@

datapoints.pickle: $(foreach idx,deps2-$(idx).pickle,$(INDICES))
	python mk_datapoints.py $^ $@

RESULT2: datapoints.pickle
	python mk_solution.py $< $@


data.pickle: summary.pickle
	python do2.py $< $@ $(if $(PLOT),--plot)

summary.pickle: output-01.pickle output-02.pickle
	python conclude.py $^ $@

output-%.pickle: s-%.tiff
	python do.py $< $@ $(if $(PLOT),--plot)

RESULT: data.pickle
	python problem.py $(if $(PLOT),--plot) $< > $@

f-%.tiff: s-%.tiff RESULT
	convert $< -distort barrel "$$(cat RESULT)" $@ 

show: _show-01 _show-02

_show-%: f-%.tiff
	python do.py $< --plot

clean:
	$(RM) *.pickle RESULT
	$(RM) f-0*.tiff
