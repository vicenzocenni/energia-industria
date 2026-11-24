import logging
import subprocess
import sys
from Config import BASE_DIR
import subprocess

RAIZ = BASE_DIR
SRC = RAIZ / "src"

def configurar_log():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.FileHandler(RAIZ / "pipeline.log"),
            logging.StreamHandler()
        ]
    )


def executar_script(nome):
    subprocess.run(
        [sys.executable, str(SRC / nome)],
        cwd=RAIZ,
        check=True
    )


def transformar_todas():
    executar_script("formatar_producao_industria.py")
    executar_script("transformar.py")


def enriquecer():
    executar_script("juncao.py")

def etapa_carga():
    import carga
    carga.main()

def etapa_modelagem():
    subprocess.run(
        ["dbt", "run"],
        cwd=RAIZ / "ecox14",
        check=True,
    )


ETAPAS = [
    ("transformacao", transformar_todas),
    ("enriquecimento", enriquecer),
    ("carga", etapa_carga),
    ("modelagem", etapa_modelagem)
]


def executar(nome, funcao):
    logging.info("etapa %s: inicio", nome)
    try:
        funcao()
    except Exception:
        logging.exception("etapa %s falhou", nome)
        raise
    logging.info("etapa %s: fim", nome)


def main(a_partir_de=None):
    configurar_log()
    nomes_etapas = [nome for nome, _ in ETAPAS]
    if a_partir_de is not None and a_partir_de not in nomes_etapas:
        raise ValueError(
            f"Etapa desconhecida: {a_partir_de}. "
            f"Etapas disponíveis: {', '.join(nomes_etapas)}"
        )

    comecou = a_partir_de is None
    for nome, funcao in ETAPAS:
        if nome == a_partir_de:
            comecou = True
        if not comecou:
            logging.info("etapa %s: ignorada", nome)
            continue
        executar(nome, funcao)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)