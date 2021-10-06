import re
import pynvim
from pynvim.api import Buffer
from typing import Tuple, cast, List
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class Position:
    row: int
    col: int


class BufferLimitException(Exception):
    pass


@pynvim.plugin
class IndentPlugin(object):
    def __init__(self, vim: pynvim.Nvim):
        self.vim = vim

    @pynvim.command("Info")
    def info_handler(self, args: Tuple[int, int] = (1, 1)):
        pass

    def current_buffer(self) -> List[str]:
        buf: Buffer = self.vim.current.buffer
        lines: List[str] = self.vim.api.buf_get_lines(buf.handle, 0, -1, True)
        return lines

    #  slow as shit
    @pynvim.function("MoveToIndent")
    def move_to_indent_handler(self, args: Tuple[int, int] = (1, 1)):
        times, direction = args
        #  if no count is supplied, v:count  defaults to 0
        #  in this case reset it to 1
        times = times or 1

        pos = Position(*self.vim.current.window.cursor)
        logger.info(f"pos={pos}")
        buffer = self.current_buffer()

        #  save current location to jumplist
        self.vim.command('normal m`')

        try:
            #  find first line with content
            while self._empty_line(pos, buffer):
                pos.row += direction

            leading_spaces = self._num_leading_spaces(pos, buffer)

            #  climb to specified indent level
            for c in range(times):
                while True:
                    pos.row += direction
                    if pos.row == 1 or pos.row == len(buffer):
                        raise BufferLimitException()
                    if self._empty_line(pos, buffer):
                        continue
                    leading_space_current_line = self._num_leading_spaces(pos, buffer)
                    if leading_space_current_line < leading_spaces:
                        leading_spaces = leading_space_current_line
                        break
                if leading_space_current_line == 0:
                    break

        except BufferLimitException as e:
            pass

        logger.info(f"newpos={pos}")
        self.vim.current.window.cursor = [pos.row, pos.col]

    def _empty_line(self, pos: Position, buffer: List[str]):
        return re.search(r"^\s*$", buffer[pos.row - 1]) is not None

    def _num_leading_spaces(self, pos: Position, buffer: List[str]):
        line = buffer[pos.row - 1]
        match = cast(re.Match, re.search(r"^(\s*)", line))
        return len(match.group(0))
