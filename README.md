## All homework assignments base-code for Java Programming UChicago MPCS 51036

This project contains all the base code you will need for your homework (called projects) in Java Programming 51036 -- but not the answers :(
There are also some simple examples in this project. Each package (e.g. _01control) contains a file called _instructions.txt which contains instructions for each project.

## The master branch

You may create however many branches you like, but be sure to merge those changes back to master as master is the only branch that the graders will evaluate.

If you don't know how to merge, stay on master...or ask me during office hours and I will show you how to merge.


## Design Patterns annotated in the base code
Ten patterns are annotated in the `_08final` project with `TODO PATTERN n of 10` comments (search for `TODO PATTERN`).
Three earlier labels were retired because the code does not match the pattern; a `NOTE` comment at each spot
explains why (the team lists are not Composite, `Movable` is not a Facade, the `Falcon` enums are not the State pattern).

| # | Pattern | Java (`src/java/_08final`) | Python (`src/python/_08final`) |
|---|---|---|---|
| 1 | Singleton | `CommandCenter` | `CommandCenter`, `ImageLoader` (`__new__` idiom) |
| 2 | Model-View-Controller | the three packages; `Game` | the three packages; `Game` |
| 3 | Command | `GameOp`, `GameOpsQueue`, `Game.processGameOpsQueue()` | same |
| 4 | Observer | `Game implements KeyListener` (Swing callbacks) | not present: pygame *polls* events (see `Game.main`) |
| 5 | Game Loop | `Game.run()` | `Game.main()` |
| 6 | Template Method | `Sprite.move()`, abstract `draw()`, lifecycle hooks | `Sprite(ABC)`, `@abstractmethod draw()`, hooks |
| 7 | Pipeline | `Sprite.renderVector()`, `Asteroid.generateVertices()` | `Sprite.renderVector()` (`seq().map()` chain) |
| 8 | Facade | `SoundLoader`, `ImageLoader` | `SoundLoader`, `ImageLoader` |
| 9 | Flyweight | `ImageLoader.IMAGE_MAP` shared `BufferedImage`s | `ImageLoader.IMAGES` shared PIL images |
| 10 | Double Buffer | `GamePanel.update()` | `GamePanel.update()` |
| 10 | Adapter | — | `view/Graphics.py` (PIL behind the `java.awt.Graphics` API) |

Both languages carry ten: Java has Observer and no Adapter; Python has Adapter and no Observer.
Chapters 43 and 44 of *Advanced Programming in Python and Java* treat each pattern with fresh examples.

## Python Game Base translation
The final project base code has been translated into python. To run it from IntelliJ Ultimate, you will create a new 
run configuration with the following settings:

Use specified interpreter: uv
script: src/python/_08final/mvc/controller/Game.py
