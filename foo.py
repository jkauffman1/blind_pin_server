from bar import x, set_x
set_x(1)
print(x)

import bar
print(bar.x)
print(x)
print(bar.x)
print(x is bar.x)
