summary.pickle: output-01.pickle output-02.pickle
	python conclude.py $^ $@

output-%.pickle: sinus-%.tiff
	python do.py $< $@

data.pickle: summary.pickle
	python do2.py $< $@

clean:
	$(RM) *.pickle
