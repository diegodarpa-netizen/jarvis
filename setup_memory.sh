#!/bin/bash
# setup_memory.sh — Vincula la memoria de Jarvis con Claude Code
# Ejecutar una vez en cada máquina nueva donde se clone el repo

JARVIS_DIR="$(cd "$(dirname "$0")" && pwd)"
MEMORY_SOURCE="$JARVIS_DIR/memory"

# Detectar el path codificado del proyecto para Claude
ENCODED_PATH=$(echo "$JARVIS_DIR" | sed 's|/|-|g' | sed 's|^-||')
CLAUDE_PROJECT_DIR="$HOME/.claude/projects/$ENCODED_PATH"

echo "📁 Jarvis: $JARVIS_DIR"
echo "🧠 Claude project dir: $CLAUDE_PROJECT_DIR"

# Crear directorio si no existe
mkdir -p "$CLAUDE_PROJECT_DIR"

# Si ya existe un directorio memory, hacer backup
if [ -d "$CLAUDE_PROJECT_DIR/memory" ] && [ ! -L "$CLAUDE_PROJECT_DIR/memory" ]; then
    echo "⚠️  Haciendo backup de memory existente..."
    mv "$CLAUDE_PROJECT_DIR/memory" "$CLAUDE_PROJECT_DIR/memory.backup.$(date +%Y%m%d%H%M%S)"
fi

# Crear symlink
ln -sfn "$MEMORY_SOURCE" "$CLAUDE_PROJECT_DIR/memory"

echo "✅ Symlink creado: $CLAUDE_PROJECT_DIR/memory → $MEMORY_SOURCE"
echo "🎉 Memoria de Jarvis sincronizada. Podés abrir Claude Code."
