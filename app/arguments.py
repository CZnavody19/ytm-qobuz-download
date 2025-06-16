class Arguments:
    def __init__(self, defs: list[tuple[str|None, str, str]]) -> None:
        self.defs = defs
        self.active: list[tuple[str|None, str, str]] = []

    def parse(self, args: list[str]) -> bool:
        for arg in args:
            res = None
            match arg.count("-"):
                case 1:
                    res = self._parse_short(arg[1:])
                case 2:
                    res = self._parse_long(arg[2:])
                case _:
                    raise ValueError(f"Invalid argument format: {arg}")
            if res is False:
                return False
        return True

    def has(self, arg: str) -> bool:
        return any(d[0] == arg or d[1] == arg for d in self.active)
    
    def print_help(self) -> None:
        print("Available arguments:")
        for short, long, description in self.defs:
            if short:
                print(f"-{short}, --{long}: {description}")
            else:
                print(f"--{long}: {description}")

    def _parse_short(self, arg: str) -> bool:
        if arg == "h":
            self.print_help()
            return False

        for d in self.defs:
            if d[0] == arg:
                self.active.append(d)
                return True

        raise ValueError(f"Unknown short argument: {arg}")

    def _parse_long(self, arg: str) -> bool:
        if arg == "help":
            self.print_help()
            return False

        for d in self.defs:
            if d[1] == arg:
                self.active.append(d)
                return True

        raise ValueError(f"Unknown long argument: {arg}")