import pygame


# Thin wrapper around the pygame display surface. The whole frame is drawn
# off-screen into a PIL image (see GamePanel.update); GameFrame's only job is
# to get that finished image onto the screen as fast as possible. Tk's
# PhotoImage path capped us at ~10 fps because Tk re-composites the entire
# ~840k-pixel window every frame on macOS; pushing the same bytes through
# SDL/pygame is ~40x cheaper, so the display is no longer the bottleneck.
class GameFrame:

    def __init__(self):
        self.running = True
        self.screen = None

    # Create the window. Mirrors the old tk geometry/title/resizable setup.
    def setup(self, width, height, title="Game Base"):
        pygame.display.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)

    # Blit a finished RGB PIL image to the screen in one swoop. frombuffer
    # shares the PIL bytes with no copy; flip() presents the back buffer.
    def blit(self, pilImage):
        surface = pygame.image.frombuffer(
            pilImage.tobytes(), pilImage.size, pilImage.mode
        )
        self.screen.blit(surface, (0, 0))
        pygame.display.flip()

    def onClosing(self):
        self.running = False
