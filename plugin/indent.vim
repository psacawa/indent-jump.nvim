if exists("g:loaded_indent_object")
  finish
endif

nnoremap <silent> [i  :<c-u>call MoveToIndent(v:count,-1)<cr>
nnoremap <silent> ]i  :<c-u>call MoveToIndent(v:count,1)<cr>

let g:loaded_indent_object = 1
