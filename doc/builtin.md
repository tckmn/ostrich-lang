# Ostrich builtins

Here is a list of all Ostrich instructions and what they do. They are arranged
in ASCIIbetical order (the same order as in the source code).

## `\n`, ` `

Whitespace is usually ignored in Ostrich, but be careful not to accidentally assign to it!

    >>> {`.`+}: d;`wait` `what` `huh?`
    `wait.` `what.` `huh?`

## `!`

Logical not. `0`, ` `` `, `[]`, `{}` return `1`; everything else returns `0`.

    >>> 0! ``! []! {}!
    1 1 1 1
    >>> ;;;; 1! ` `! [``]! {foo}!
    0 0 0 0

## `"`

TODO

## `#`

TODO

## `$`

TODO

## `%`

TODO

## `&`

TODO

## `'`

TODO

## `(`

TODO

## `)`

TODO

## `*`

TODO

## `+`

TODO

## `,`

TODO

## `-`

TODO

## `.`

TODO

## `/`

TODO

## `:`

TODO

## `;`

TODO

## `<`

TODO

## `=`

TODO

## `>`

TODO

## `?`

TODO

## `@`

TODO

## `[`

TODO

## `\`

TODO

## `]`

TODO

## `^`

TODO

## `` ` ``

TODO

## `f`

TODO

## `p`

TODO

## `q`

TODO

## `z`

TODO

## `{`

TODO

## `|`

TODO

## `}`

TODO

## `~`

TODO
