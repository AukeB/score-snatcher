ruff:
	uv run ruff check src --fix
	uv run ruff format src
	@rm -rf .python-version .ruff_cache src/__pycache__

clean:
	find . -type d -name '__pycache__' -exec rm -r {} + 2>/dev/null
	find . -type d -name '.ruff_cache' -exec rm -r {} + 2>/dev/null

git:
	git add -A
	git commit -m "Updated"
	git push

all:
	make ruff
	make clean
	make git
