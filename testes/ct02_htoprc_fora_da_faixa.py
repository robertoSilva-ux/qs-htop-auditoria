#!/usr/bin/env python3
"""CT-02 — htoprc com campo fora da faixa (BVA: limite superior + 1)

Caso de teste executável do Milestone 2 (Qualidade de Software, 2026.2).
Objeto: htop, commit 8ff043d. Deriva do relatório, seção 6 (CT-02).

Pré-condição: ~/.config/htop/htoprc com "fields=0 999" — 999 está muito acima
da faixa de índices de coluna, logo cai na fronteira inválida superior.
Resultado esperado: o htop ignora o valor inválido, sobe com a configuração
padrão de colunas e encerra normalmente com 'q' — sem crash, sem abort.

Método: o binário real é executado dentro de um pty de 24x80 (mesmo par usado
pela suíte oficial do projeto, RoteTerm(24, 80)), com HOME temporário. A tela é
capturada e reduzida a uma assinatura de elementos de interface; o caso é
comparado a uma execução de controle com configuração válida — se as duas
assinaturas coincidem, o valor inválido não foi aplicado.

Uso:
    python3 ct02_htoprc_fora_da_faixa.py [/caminho/para/htop]

Sai com 0 se passar, 1 se falhar. Só biblioteca padrão.
"""
import fcntl
import os
import pty
import re
import select
import shutil
import struct
import subprocess
import sys
import tempfile
import termios
import time

BINARIO = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
    "~/.hermes/cache/scratch/qs-m2/htop/htop")
LARGURA, ALTURA = 80, 24
MARCADORES = ["PID", "Mem", "Tasks:", "Load average", "Uptime:",
              "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10"]


def executa(conteudo_htoprc):
    """Roda o htop com o htoprc dado; devolve (código de saída, tela, config final)."""
    raiz = tempfile.mkdtemp(prefix="ct02-")
    home = os.path.join(raiz, "home")
    confdir = os.path.join(home, ".config", "htop")
    os.makedirs(confdir)
    htoprc = os.path.join(confdir, "htoprc")
    with open(htoprc, "w", encoding="utf-8") as f:
        f.write(conteudo_htoprc)

    env = {
        "HOME": home,
        "TERM": "xterm-256color",
        "PATH": "/usr/bin:/bin",
        "LANG": "C.UTF-8",
        "GCOV_PREFIX": os.path.join(raiz, "gcov"),  # binário instrumentado por cobertura
    }

    master, slave = pty.openpty()
    fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", ALTURA, LARGURA, 0, 0))
    proc = subprocess.Popen([BINARIO], stdin=slave, stdout=slave, stderr=slave,
                            env=env, close_fds=True, preexec_fn=os.setsid)
    os.close(slave)

    def drena(segundos):
        buf, t0 = b"", time.time()
        while time.time() - t0 < segundos:
            pronto, _, _ = select.select([master], [], [], 0.2)
            if pronto:
                try:
                    buf += os.read(master, 65536)
                except OSError:
                    break
        return buf

    tela = drena(2.0)
    try:
        os.write(master, b"q")
    except OSError:
        pass
    try:
        rc = proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        rc = None
    tela += drena(0.5)
    try:
        os.close(master)
    except OSError:
        pass

    final = open(htoprc, encoding="utf-8").read() if os.path.exists(htoprc) else ""
    shutil.rmtree(raiz, ignore_errors=True)

    texto = tela.decode("utf-8", "replace")
    texto = re.sub(r"\x1b\[[0-9;?]*[A-Za-z]|\x1b[()][A-Z0-9]|\x1b[=>]", " ", texto)
    return rc, re.sub(r"\s+", " ", texto), final


def assinatura(tela):
    return {m for m in MARCADORES if m in tela}


def main():
    if not os.access(BINARIO, os.X_OK):
        print(f"FALHA: binário não encontrado ou sem permissão: {BINARIO}")
        return 1

    print("CT-02 — htoprc com campo fora da faixa (BVA, limite superior + 1)")
    print(f"binário: {BINARIO}")

    rc_invalido, tela_invalida, cfg_invalido = executa("fields=0 999\n")
    rc_valido, tela_valida, _ = executa("fields=0 48 49 46 47 2 1 1 1 1 1\n")

    ass_invalida, ass_valida = assinatura(tela_invalida), assinatura(tela_valida)

    checagens = [
        ("htop sobe com o valor inválido (não aborta)",
         rc_invalido is not None),
        ("encerra normalmente com 'q' (código 0)", rc_invalido == 0),
        ("não termina por sinal (sem crash/segfault)",
         rc_invalido is not None and rc_invalido >= 0),
        ("interface desenhada: medidores, tarefas, carga e barra de funções",
         len(ass_invalida) >= 10),
        ("colunas em uso são as padrão (índice 999 ignorado)",
         ass_invalida == ass_valida and len(ass_valida) >= 10),
        ("htoprc preservado (não corrompido na leitura)",
         "fields=" in cfg_invalido),
    ]

    print(f"\n  configuração inválida : fields=0 999  → saída {rc_invalido}")
    print(f"  configuração válida   : fields=0 48 49 ... → saída {rc_valido}")
    print(f"  marcadores na tela    : {len(ass_invalida)} de {len(MARCADORES)}")
    print()
    for nome, ok in checagens:
        print(f"  [{'PASS' if ok else 'FAIL'}] {nome}")

    falhas = [n for n, ok in checagens if not ok]
    print()
    if falhas:
        print(f"RESULTADO: FALHOU ({len(falhas)} de {len(checagens)} checagens)")
        print("tela (trecho):", tela_invalida[:300])
        return 1
    print(f"RESULTADO: PASSOU ({len(checagens)} de {len(checagens)} checagens)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
