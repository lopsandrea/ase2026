.PHONY: help install build smoke rq1 rq2 rq3 ablation cost tables clean docker

help:
	@echo "Doc2Test reproduction targets:"
	@echo "  install   - install Python deps (pip install -e .[dev])"
	@echo "  build     - build Docker image and accessory apps"
	@echo "  smoke     - run smoke test against CodeBites"
	@echo "  rq1       - reproduce Table 1 (90 runs, generation validity)"
	@echo "  rq2       - reproduce Table 2 (180 mutants, oracle capability)"
	@echo "  rq3       - reproduce Table 3 (4 baselines comparative)"
	@echo "  ablation  - reproduce Table 4 (topology + leave-one-out)"
	@echo "  cost      - reproduce Table 5 (per-phase cost breakdown)"
	@echo "  tables    - regenerate all .tex tables in evaluation/out/"
	@echo "  clean     - remove caches, traces output, build artifacts"

install:
	pip install -e .[dev]

build:
	docker compose build

smoke:
	doc2test run --uat uats/codebites_form_crud.pdf --url http://localhost:3001

rq1:
	python -m evaluation.rq1_runner --out traces/rq1
	python -m evaluation.plot_tables --rq 1 --out evaluation/out/table1.tex

rq2:
	python -m evaluation.rq2_mutation --out traces/rq2
	python -m evaluation.plot_tables --rq 2 --out evaluation/out/table2.tex

rq3:
	python -m evaluation.rq3_compare --out traces/rq3
	python -m evaluation.plot_tables --rq 3 --out evaluation/out/table3.tex

ablation:
	python -m evaluation.ablation.topology_3agents --out traces/ablation
	python -m evaluation.ablation.topology_12agents --out traces/ablation
	python -m evaluation.ablation.leave_one_out --out traces/ablation
	python -m evaluation.plot_tables --rq ablation --out evaluation/out/table4.tex

cost:
	python -m evaluation.plot_tables --rq cost --out evaluation/out/table5.tex

tables: rq1 rq2 rq3 ablation cost

clean:
	rm -rf traces/*/*.json evaluation/out/*.tex
	find . -type d -name __pycache__ -exec rm -rf {} +
