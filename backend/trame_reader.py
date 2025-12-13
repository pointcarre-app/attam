from pathlib import Path
from trame import Trame, TrameBuilder


# trame = TrameBuilder.from_string(origin="test", markdown_content=markdown_content)


def read_trame(path: Path) -> Trame:
    return TrameBuilder.from_file(path=path)


if __name__ == "__main__":
    trame = read_trame(path=Path("trames/alidade/nav_et_trigo.md"))
    print(trame)
