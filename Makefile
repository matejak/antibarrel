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
