from dataclasses import dataclass
from enum import Flag, auto
from typing import List, Tuple, Optional, Union

from pysat.formula import IDPool  # type: ignore
from pysat.solvers import Minisat22  # type: ignore


@dataclass(frozen=True)
class Position:
    row: int
    column: int


class FlowDirection(Flag):
    # Directions used for the initial coloured tiles on the grid
    UP = auto()
    LEFT = auto()
    DOWN = auto()
    RIGHT = auto()
    # Directions used for the rest of the grid
    UP_LEFT = UP | LEFT
    UP_DOWN = UP | DOWN
    UP_RIGHT = UP | RIGHT
    LEFT_DOWN = LEFT | DOWN
    LEFT_RIGHT = LEFT | RIGHT
    DOWN_RIGHT = DOWN | RIGHT


@dataclass(frozen=True)
class TileFlowDirection:
    position: Position
    flow_direction: FlowDirection


@dataclass(frozen=True)
class TileColour:
    position: Position
    colour: int


@dataclass(frozen=True)
class Tile:
    flow_direction: FlowDirection
    colour: int


Solution = Tuple[Tuple[Tile, ...], ...]

Clause = List[int]


@dataclass
class Puzzle:
    grid_size: int
    # The index represents the colour
    endpoints: Tuple[Tuple[Position, Position], ...]

    def __post_init__(self):
        self.id_pool = IDPool()
        self.number_of_colours = len(self.endpoints)

    def solve(self) -> Optional[Solution]:
        clauses = must_not_flow_outside(self)
        solver = Minisat22()
        for clause in clauses:
            solver.add_clause(clause)
        if not solver.solve():
            return None
        true_variables: List[Union[TileFlowDirection, TileColour]] = [
            self.id_pool.obj(variable)
            for variable in solver.get_model()
            if variable > 0
        ]
        print(solver.get_model())
        solution: List[Tuple[Tile, ...]] = []
        for i in range(0, self.grid_size):
            row: List[Tile] = []
            for j in range(0, self.grid_size):
                tile_variables = [
                    variable
                    for variable in true_variables
                    if variable.position == Position(i, j)
                ]
                flow_direction = next(
                    variable.flow_direction  # type: ignore
                    for variable in tile_variables
                    if isinstance(tile_variables, TileFlowDirection)
                )
                colour = next(
                    variable.colour  # type: ignore
                    for variable in tile_variables
                    if isinstance(tile_variables, TileColour)
                )
                row.append(Tile(flow_direction, colour))
            solution.append(tuple(row))
        return tuple(solution)


def must_not_flow_outside(puzzle: Puzzle) -> List[Clause]:
    clauses: List[Clause] = []

    def tile_must_not_flow_outside(
        position: Position, outside: FlowDirection
    ) -> None:
        nonlocal clauses
        clauses += [
            [
                -puzzle.id_pool.id(
                    TileFlowDirection(
                        Position(row=0, column=i), flow_direction
                    )
                )
            ]
            for flow_direction in FlowDirection
            if flow_direction & outside
        ]

    for i in range(0, puzzle.grid_size):
        tile_must_not_flow_outside(Position(row=0, column=i), FlowDirection.UP)
        tile_must_not_flow_outside(
            Position(row=i, column=0), FlowDirection.LEFT
        )
        tile_must_not_flow_outside(
            Position(row=puzzle.grid_size - 1, column=i), FlowDirection.DOWN
        )
        tile_must_not_flow_outside(
            Position(row=i, column=puzzle.grid_size - 1), FlowDirection.RIGHT
        )

    return clauses
