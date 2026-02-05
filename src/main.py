from src.cli import run_repl
from src.service import TodoService
from src.store import TodoStore


def main() -> None:
    store = TodoStore()
    service = TodoService(store)
    run_repl(service)


if __name__ == "__main__":
    main()
