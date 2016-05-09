data.pickle: summary.pickle
	python do2.py $< $@ $(if $(PLOT),--plot)

# summary.pickle: output-01.pickle output-02.pickle
summary.pickle: output-01.pickle output-02.pickle
	python conclude.py $^ $@

# output-%.pickle: sinus-%.tiff
output-%.pickle: s-%.tiff
	python do.py $< $@ $(if $(PLOT),--plot)

clean:
	$(RM) *.pickle
