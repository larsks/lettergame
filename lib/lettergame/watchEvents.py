import pygame

def main():
  pygame.init()
  screen = pygame.display.set_mode((200,200))

  while True:
    for event in pygame.event.get():
      print event

      if event.type == pygame.QUIT:
        sys.exit()

if __name__ == '__main__': main()

