.PHONY : all
all : GDP\ by\ industry.pdf GDP\ by\ industry.html

./GDP\ by\ industry.pdf : ./GDP\ by\ industry.md
	pandoc -o "$@" "$<"

./GDP\ by\ industry.html :./GDP\ by\ industry.md
	pandoc -so "$@" "$<"

./GDP\ by\ industry.md : ../data/GDP_by_industry.csv ../data/gdpconfig.json
	python pipeline.py -c ../data/gdpconfig.json ../data/GDP_by_industry.csv

.PHONY : test
test :
	python ../tests/summaries.py

.PHONY : clean
clean :
	rm *.pdf *.html *.md
