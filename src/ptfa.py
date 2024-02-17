from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Callable

from code_analysis import CFG

PatternCheck = Callable[[CFG, int], bool]


class DefinitelyPTFA(ABC):
    def __init__(self, check_pattern: PatternCheck):
        self.check_pattern = check_pattern

        self.cfg: CFG
        self.visited: set[int]
        self.worklist: list[int]
        self.in_dict: dict[int, bool]
        self.out_dict: dict[int, bool]

    @abstractmethod
    def pre_loop_init(self) -> Iterable[None]:
        ...

    @abstractmethod
    def check_node(self, nid: int) -> None:
        ...

    @abstractmethod
    def next_nodes(self, nid: int) -> Iterable[int]:
        ...

    @abstractmethod
    def can_propagate(self, nid: int, next_nid: int) -> bool:
        ...

    @abstractmethod
    def propagate(self, nid: int, next_nid: int):
        ...

    def __call__(self, cfg: CFG) -> tuple[dict[int, bool], dict[int, bool]]:
        self.cfg = cfg

        self.visited = set()
        self.worklist = []

        node_ids: list[int] = self.cfg.get_node_ids()
        self.in_dict = {k: True for k in node_ids}
        self.out_dict = {k: True for k in node_ids}

        for _ in self.pre_loop_init():
            while self.worklist:
                nid = self.worklist.pop()
                self.check_node(nid)
                for next_nid in self.next_nodes(nid):
                    if (
                        self.can_propagate(nid, next_nid)
                        or next_nid not in self.visited
                    ):
                        self.propagate(nid, next_nid)
                        self.worklist.append(next_nid)
                        self.visited.add(next_nid)

        return self.in_dict, self.out_dict


class DefinitelyReachablePTFA(DefinitelyPTFA):
    def get_exit_node(self) -> Iterable[int]:
        node_ids = self.cfg.get_node_ids()
        for nid in node_ids:
            if self.cfg.get_type(nid) == "Exit":
                yield nid

    def pre_loop_init(self) -> Iterable[None]:
        for exit_nid in self.get_exit_node():
            self.out_dict[exit_nid] = False
            self.visited.add(exit_nid)
            self.worklist.append(exit_nid)
            yield

    def check_node(self, nid: int) -> None:
        self.in_dict[nid] = self.out_dict[nid] or self.check_pattern(self.cfg, nid)

    def next_nodes(self, nid: int) -> Iterable[int]:
        return self.cfg.get_any_parents(nid)

    def can_propagate(self, nid: int, next_nid: int) -> bool:
        return self.in_dict[nid] < self.out_dict[next_nid]

    def propagate(self, nid: int, next_nid: int) -> None:
        self.out_dict[next_nid] = self.in_dict[nid]


class DefinitelyReachingPTFA(DefinitelyPTFA):
    def get_entry_node(self) -> Iterable[int]:
        node_ids = self.cfg.get_node_ids()
        for nid in node_ids:
            if self.cfg.get_type(nid) == "Entry":
                yield nid

    def pre_loop_init(self) -> Iterable[None]:
        for entry_nid in self.get_entry_node():
            self.in_dict[entry_nid] = False
            self.visited.add(entry_nid)
            self.worklist.append(entry_nid)
            yield

    def check_node(self, nid: int) -> None:
        self.out_dict[nid] = self.in_dict[nid] or self.check_pattern(self.cfg, nid)

    def next_nodes(self, nid: int) -> Iterable[int]:
        return self.cfg.get_any_children(nid)

    def can_propagate(self, nid: int, next_nid: int) -> bool:
        return self.out_dict[nid] < self.in_dict[next_nid]

    def propagate(self, nid: int, next_nid: int) -> None:
        self.in_dict[next_nid] = self.out_dict[nid]
