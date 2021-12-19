from dataclasses import dataclass
from enum import Flag, auto
from typing import List, Tuple, Optional, Union, Generator
from itertools import combinations

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

    def positions(self) -> Generator[Position, None, None]:
        for row in range(self.grid_size):
            for column in range(self.grid_size):
                yield Position(row, column)

    def solve(self) -> Optional[Solution]:
        clauses = (
            must_not_flow_outside(self)
            + must_have_a_direction(self)
            + must_have_a_colour(self)
            + must_not_have_two_directions(self)
            + must_not_have_two_colours(self)
            + only_endpoints_flow_one_way(self)
            + endpoints_must_have_their_initial_colour(self)
            + tiles_flowing_into_each_other_match(self)
        )
        solver = Minisat22(bootstrap_with=clauses)
        if not solver.solve():
            return None
        true_variables: List[Union[TileFlowDirection, TileColour]] = [
            self.id_pool.obj(variable)
            for variable in solver.get_model()
            if variable > 0
        ]
        solution: List[Tuple[Tile, ...]] = []
        for i in range(self.grid_size):
            row: List[Tile] = []
            for j in range(self.grid_size):
                tile_variables = [
                    variable
                    for variable in true_variables
                    if variable.position == Position(i, j)
                ]
                flow_direction = next(
                    variable.flow_direction
                    for variable in tile_variables
                    if isinstance(variable, TileFlowDirection)
                )
                colour = next(
                    variable.colour
                    for variable in tile_variables
                    if isinstance(variable, TileColour)
                )
                row.append(Tile(flow_direction, colour))
            solution.append(tuple(row))
        return tuple(solution)


def must_have_a_direction(puzzle: Puzzle) -> List[Clause]:
    return [
        [
            puzzle.id_pool.id(TileFlowDirection(position, flow_direction))
            for flow_direction in FlowDirection
        ]
        for position in puzzle.positions()
    ]


def must_have_a_colour(puzzle: Puzzle) -> List[Clause]:
    return [
        [
            puzzle.id_pool.id(TileColour(position, colour))
            for colour in range(puzzle.number_of_colours)
        ]
        for position in puzzle.positions()
    ]


def must_not_have_two_directions(puzzle: Puzzle) -> List[Clause]:
    return [
        [
            -puzzle.id_pool.id(TileFlowDirection(position, fst_direction)),
            -puzzle.id_pool.id(TileFlowDirection(position, snd_direction)),
        ]
        for fst_direction, snd_direction in combinations(FlowDirection, 2)
        for position in puzzle.positions()
    ]


def must_not_have_two_colours(puzzle: Puzzle) -> List[Clause]:
    return [
        [
            -puzzle.id_pool.id(TileColour(position, fst_colour)),
            -puzzle.id_pool.id(TileColour(position, snd_colour)),
        ]
        for fst_colour, snd_colour in combinations(
            range(puzzle.number_of_colours), 2
        )
        for position in puzzle.positions()
    ]


def must_not_flow_outside(puzzle: Puzzle) -> List[Clause]:
    clauses: List[Clause] = []

    def tile_must_not_flow_outside(
        position: Position, outside: FlowDirection
    ) -> None:
        nonlocal clauses
        clauses += [
            [-puzzle.id_pool.id(TileFlowDirection(position, flow_direction))]
            for flow_direction in FlowDirection
            if flow_direction & outside
        ]

    for i in range(puzzle.grid_size):
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


def only_endpoints_flow_one_way(puzzle: Puzzle) -> List[Clause]:
    clauses: List[Clause] = []
    endpoints: Tuple[Position, ...] = sum(puzzle.endpoints, tuple())
    for position in puzzle.positions():
        if position in endpoints:
            clauses += [
                [
                    puzzle.id_pool.id(
                        TileFlowDirection(position, flow_direction)
                    )
                    for flow_direction in (
                        FlowDirection.UP,
                        FlowDirection.LEFT,
                        FlowDirection.DOWN,
                        FlowDirection.RIGHT,
                    )
                ]
            ]
        else:
            clauses += [
                [
                    puzzle.id_pool.id(
                        TileFlowDirection(position, flow_direction)
                    )
                    for flow_direction in (
                        FlowDirection.UP_LEFT,
                        FlowDirection.UP_DOWN,
                        FlowDirection.UP_RIGHT,
                        FlowDirection.LEFT_DOWN,
                        FlowDirection.LEFT_RIGHT,
                        FlowDirection.DOWN_RIGHT,
                    )
                ]
            ]
    return clauses


def endpoints_must_have_their_initial_colour(puzzle: Puzzle) -> List[Clause]:
    return [
        [puzzle.id_pool.id(TileColour(endpoint, colour))]
        for colour, endpoint_pair in enumerate(puzzle.endpoints)
        for endpoint in endpoint_pair
    ]


def tiles_flowing_into_each_other_match(puzzle: Puzzle) -> List[Clause]:
    clauses: List[Clause] = []

    def neighbour_matches(
        position: Position,
        match_flow: FlowDirection,
        neighbour_position: Position,
        neighbour_match_flow: FlowDirection,
    ) -> None:
        nonlocal clauses
        for flow_direction in FlowDirection:
            if flow_direction & match_flow:
                # The position flowing in the specified direction implies that
                # the neighbour has a matching direction.
                clauses += [
                    [
                        -puzzle.id_pool.id(
                            TileFlowDirection(position, flow_direction)
                        )
                    ]
                    + [
                        puzzle.id_pool.id(
                            TileFlowDirection(
                                neighbour_position,
                                neighbour_flow_direction,
                            )
                        )
                        for neighbour_flow_direction in FlowDirection
                        if neighbour_flow_direction & neighbour_match_flow
                    ]
                ]
                # The position flowing in the specified direction implies that
                # the colour of the current position determines the colour of
                # the neighbour.
                clauses += [
                    [
                        -puzzle.id_pool.id(
                            TileFlowDirection(
                                position,
                                flow_direction,
                            )
                        ),
                        -puzzle.id_pool.id(
                            TileColour(
                                position,
                                colour,
                            )
                        ),
                        puzzle.id_pool.id(
                            TileColour(
                                neighbour_position,
                                colour,
                            )
                        ),
                    ]
                    for colour in range(puzzle.number_of_colours)
                ]

    for position in puzzle.positions():
        if position.row > 0:
            neighbour_position = Position(position.row - 1, position.column)
            neighbour_matches(
                position,
                FlowDirection.UP,
                neighbour_position,
                FlowDirection.DOWN,
            )
        if position.column > 0:
            neighbour_position = Position(position.row, position.column - 1)
            neighbour_matches(
                position,
                FlowDirection.LEFT,
                neighbour_position,
                FlowDirection.RIGHT,
            )
        if position.row < puzzle.grid_size - 1:
            neighbour_position = Position(position.row + 1, position.column)
            neighbour_matches(
                position,
                FlowDirection.DOWN,
                neighbour_position,
                FlowDirection.UP,
            )
        if position.column < puzzle.grid_size - 1:
            neighbour_position = Position(position.row, position.column + 1)
            neighbour_matches(
                position,
                FlowDirection.RIGHT,
                neighbour_position,
                FlowDirection.LEFT,
            )
    return clauses
