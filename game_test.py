from nntplib import GroupInfo
import sys, pygame, random
from tkinter import BOTTOM

#Image and Font
BIRDIMG = [pygame.image.load('yellowbird-midflap.png')]
PIPEIMG = pygame.image.load('pipe-green.png')
PIPEIMGPROCESSED = pygame.transform.scale(PIPEIMG, (PIPEIMG.get_width()+10, PIPEIMG.get_height()+200))
GROUNDPATH = pygame.image.load('base.png')
BACKGROUND = pygame.image.load('background-night.png')
BACKGROUNDIMG = pygame.transform.scale(BACKGROUND, (500, 700))

pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 48)


class Bird(pygame.sprite.Sprite):
    MAX_ROT = 25
    ROT_VEL = 25

    def __init__(self, img, pos_x, pos_y):
        super().__init__()
        self.y = pos_y
        self.x = pos_x
        bird = img[0]
        self.velocity = 0
        self.tick_count = 0
        self.tilt = 0
        self.img_count = 0
        self.image = pygame.transform.scale(bird, [48,32])
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
    
    def jump(self):
        self.velocity = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        displacement = (self.velocity*self.tick_count +  1.5* self.tick_count**2)
        if displacement >= 16:
            displacement = 16
        if displacement < 0:
            displacement -= 2
        self.y = self.y + displacement
        if displacement < 0 or self.y < self.height + 32:
            if self.tilt < self.MAX_ROT:
                self.tilt = self.MAX_ROT
        else:
            if self.tilt > -70:
                self.tilt -= self.ROT_VEL

    def rotateImg(self, window):
        rot_image = pygame.transform.rotate(self.image, self.tilt)
        new_rect = rot_image.get_rect(center=self.image.get_rect(topleft=(self.x, self.y)).center)
        window.blit(rot_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)

class selfMovingObjects(pygame.sprite.Sprite):
    def __init__(self, img, size, pos_x, pos_y):
        super().__init__()
        self.x = pos_x
        self.y = pos_y
        self.image = pygame.transform.scale(img, (size))
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.passed = False
    
    def shiftScreen(self):
        self.rect.center = (self.x, self.y)

class Pipe():
    GAP = 125
    VEL = 5


    def __init__(self, x):
        self.x = x
        self.height = 0

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPEIMGPROCESSED, False, True)
        self.PIPE_BOTTOM = PIPEIMGPROCESSED

        self.passed = False

        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        # draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird, win):

        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True

        return False


#General Setup
pygame.init()
clock = pygame.time.Clock()

#Window Setup
size = width, height = 500, 700
WIN = pygame.display.set_mode(size, pygame.RESIZABLE)
pygame.display.set_caption("Flappy Bird Evolution")

#Color
WHITE = (255,255,255)       
BLACK = (0,0,0)

#Constants
FPS = 60
FLOORSIZE = (500, 90)
FLOORHEIGHT = 655

floor1 = selfMovingObjects(GROUNDPATH, FLOORSIZE, 0,  FLOORHEIGHT)
floor2 = selfMovingObjects(GROUNDPATH, FLOORSIZE,  500, FLOORHEIGHT)

ground = pygame.sprite.Group()
ground.add(floor1, floor2)


def drawing(window, birb, points, pipes):
    for pipe in pipes:
        pipe.draw(WIN)

    text = STAT_FONT.render("Score: " + str(points), 1, (WHITE))
    WIN.blit(text, (width - 10 - text.get_width(), 10))

    birb.rotateImg(WIN)
    ground.draw(WIN)

def main():
    #Instanitated Objects + Handling
    birb = Bird(BIRDIMG, 100, 100)
    pipesArr = [Pipe(700)]
    birb.jump() #game handling

    #The While variable
    run = True

    #Checker Variables
    top = 1
    everyOther = 0
  

    #Game Variables
    score = 0


    while run:
        WIN.blit(BACKGROUNDIMG, (0,0))
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False
            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_SPACE: birb.jump()
        
        
        birb.move()
        if birb.y + (birb.image.get_height()/2) > FLOORHEIGHT:
            #print("loss ")
            pass


        for piece in ground:
            if (piece.x <= -250):
                piece.x = 750
            piece.x -= 2
            piece.shiftScreen()
        
        add_pipe = False  
        rem = []
        for pipe in pipesArr:
            pipe.move()
            if pipe.collide(birb, WIN):
                pass
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < birb.x:
                pipe.passed = True
                add_pipe = True

            if add_pipe:
                score += 1
                pipesArr.append(Pipe(width))
                add_pipe = False
            
            for r in rem:
                pipesArr.remove(r)

        
        drawing(WIN, birb, score, pipesArr)
        pygame.display.update()

if __name__ == "__main__":
    main()