#!/bin/bash

# Check if the script has execute permissions
if [ ! -x "$0" ]; then
    echo "Error: This script does not have execute permissions."
    echo "Please run the following command to fix it:"
    echo "  chmod +x $0"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for uv
if ! command_exists uv; then
    echo "uv non trovato. Installazione di uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    if [ $? -ne 0 ]; then
        echo "Errore: impossibile installare uv."
        exit 1
    fi
    # Reload PATH to pick up uv
    export PATH="$HOME/.local/bin:$PATH"
fi

if command_exists md2; then
    echo "md2 trovato, aggiornamento in corso..."
    ACTION="Aggiornamento"
else
    echo "Installazione di md2 con uv..."
    ACTION="Installazione"
fi

uv tool install . --force --reinstall

# M92: sync the bundled templates to the user dir so CSS edits in
# md2/templates/ reach the renderer (md2 reads from ~/.md2/templates/
# at render time and never re-copies after the first run).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_TEMPLATES="$HOME/.md2/templates"
if [ -d "$USER_TEMPLATES" ]; then
    cp -r "$SCRIPT_DIR/md2/templates/." "$USER_TEMPLATES/"
    echo "Template utente sincronizzati in $USER_TEMPLATES."
fi

if [ $? -eq 0 ]; then
    echo "$ACTION completato! Ora puoi usare il comando 'md2'."
    echo ""
    echo "ATTENZIONE: Se ricevi l'errore 'command not found', assicurati che ~/.local/bin sia nel tuo PATH."
    echo "Puoi aggiungerlo eseguendo questo comando nel tuo terminale:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo "Per renderlo permanente, aggiungi quella riga al file ~/.bashrc o ~/.zshrc."
else
    echo "$ACTION fallito."
    exit 1
fi
