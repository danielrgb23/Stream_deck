"""Entry point standalone para empacotamento (PyInstaller — ver README.md).

`xeeta_streamer_app/app.py` usa imports relativos (faz parte do pacote), o
que não funciona se o PyInstaller apontar direto pra ele como script
principal — por isso este wrapper, fora do pacote, chama `main()` através
de um import absoluto.
"""

from xeeta_streamer_app.app import main

if __name__ == "__main__":
    main()
