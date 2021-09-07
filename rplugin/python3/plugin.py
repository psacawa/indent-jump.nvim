import re
import pynvim
from typing import Tuple, cast


class BufferLimitException(Exception):
    pass


@pynvim.plugin
class Limit(object):
    def __init__(self, vim: pynvim.Nvim):
        self.vim = vim

    #  slow as shit
    @pynvim.function("MoveToIndent")
    def move_to_indent_handler(self, args: Tuple[int, int] = (1, 1)):
        try:
            times, direction = args
            #  find first line with content
            while self._empty_line():
                self._go_in_dir(direction)

            leading_spaces = self._num_leading_spaces()

            #  climb to specified indent level
            for c in range(times):
                while True:
                    self._go_in_dir(direction)
                    if self._empty_line():
                        continue
                    num_leading_space_in_current_line = self._num_leading_spaces()
                    if num_leading_space_in_current_line < leading_spaces:
                        leading_spaces = num_leading_space_in_current_line
                        break

        except pynvim.NvimError:
            return

    def _empty_line(self):
        return re.search(r"^\s*$", self.vim.current.line) is not None

    def _go_in_dir(self, direction: int):
        pos = self.vim.current.window.cursor
        pos[0] += direction
        self.vim.current.window.cursor = pos

    def _num_leading_spaces(self):
        line = self.vim.current.line
        match = cast(re.Match, re.search(r"^(\s*)", line))
        return len(match.group(0))

    def _setpos(self, row=None, col=None):
        buf_num = self.vim.current.buffer.number
        #  self.vim.command('setpos', buf_num, row)
        self.vim.setpos(buf_num, row, col)
