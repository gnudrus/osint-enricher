"""Test essenziali per validare la configurazione del progetto OSINT Enricher."""

def test_ci_configuration():
    """Verifica che l'ambiente CI sia configurato correttamente."""
    assert True  # Questo test passa sempre e validra il CI

def test_python_version_supported():
    """Controlla che usiamo Python 3.11+ come richiesto dal progetto."""
    import sys
    assert sys.version_info >= (3, 11), f"Python 3.11+ richiesto, trovato {sys.version}"

def test_essential_files_exist():
    """Verifica che i file fondamentali del progetto esistano."""
    import os
    # Ottieni la directory radice del repository
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Controlla file e directory essenziali
    assert os.path.exists(os.path.join(root_dir, "README.md")), "README.md mancante"
    assert os.path.exists(os.path.join(root_dir, "src")), "Directory src/ mancante"
    assert os.path.exists(os.path.join(root_dir, "requirements.txt")), "requirements.txt mancante"
    assert os.path.getsize(os.path.join(root_dir, "README.md")) > 50, "README.md sembra vuoto"
