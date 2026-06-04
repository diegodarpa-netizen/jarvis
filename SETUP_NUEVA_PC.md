# Setup Jarvis en nueva computadora

## Requisitos previos
- Tener Python 3 instalado
- Tener Git instalado
- Tener Claude Code instalado

## Pasos

### 1. Clonar el repo
```bash
git clone https://github.com/diegodarpa-netizen/jarvis.git ~/Desktop/Jarvis
cd ~/Desktop/Jarvis
```

### 2. Instalar dependencias Python
```bash
pip3 install -r requirements.txt
```

### 3. Vincular la memoria con Claude Code
```bash
bash setup_memory.sh
```

### 4. Crear el archivo de API keys
```bash
cp Jarvis/.env.example Jarvis/.env
```
Abrí el archivo `Jarvis/.env` y completá con tus API keys.

---

## Sincronización diaria

**Subir cambios (desde cualquier PC):**
```bash
git add .
git commit -m "actualización"
git push
```

**Bajar cambios (en la otra PC):**
```bash
git pull
```

---

## Repo
https://github.com/diegodarpa-netizen/jarvis (privado)
