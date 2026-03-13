# Installa le dipendenze con uv
install:
	uv sync

# Esegue lo script su un file specifico (es: make run FILE=miofile.md)
run:
	uv run md2 $(FILE)

# Esegue tutti i test
test:
	uv run pytest

# Esegue solo i test unitari
test-unit:
	uv run pytest tests/unit/

# Esegue solo i test live (end-to-end)
test-live:
	uv run pytest tests/live/

# Pulisce l'ambiente virtuale
clean:
	rm -rf .venv
