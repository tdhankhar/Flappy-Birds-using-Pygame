import random
import os
import sys #to exit the game
import pygame
from pygame.locals import * #basic py game imports

#global variables for the game
FPS = 32
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH,SCREENHEIGHT))
GROUNDY = SCREENHEIGHT*0.8
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'gallery/sprites/bird.png'
BACKGROUND = 'gallery/sprites/background.png'
BASE = 'gallery/sprites/base.png'
PIPE = 'gallery/sprites/pipe.png'

def welcomeScreen(highscore):
    '''
    Shows Welcome image on screen
    '''
    playerx = int(SCREENWIDTH/5)
    playery = int(SCREENHEIGHT - GAME_SPRITES['player'].get_height())/2
    basex = 0
    while True:
        for event in pygame.event.get():
            #if cross then close
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return
            
            else:
                SCREEN.blit(GAME_SPRITES['background'],(0, 0))
                SCREEN.blit(GAME_SPRITES['player'],(playerx, playery))
                SCREEN.blit(GAME_SPRITES['base'],(basex, GROUNDY))
                myDigits = [int(x) for x in list(str(highscore))]
                width =0
                for digit in myDigits:
                    width += GAME_SPRITES['numbers'][digit].get_width()
                Xoffset = (SCREENWIDTH -width)/2

                for digit in myDigits:
                    SCREEN.blit(GAME_SPRITES['numbers'][digit],(Xoffset,SCREENHEIGHT*0.12))
                    Xoffset += GAME_SPRITES['numbers'][digit].get_width()
                pygame.display.update()
                FPSCLOCK.tick(FPS)

def mainGame(highscore):
    score = 0
    playerx = int(SCREENWIDTH/5)
    playery = int(SCREENWIDTH/2)
    basex = 0

    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # my List of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH+200, 'y':newPipe1[0]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[0]['y']},
    ]
    # my List of lower pipes
    lowerPipes = [
        {'x': SCREENWIDTH+200, 'y':newPipe1[1]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[1]['y']},
    ]

    pipeValX = -4
    playerValY = -9
    playerMaxValY = 10
    playerAccY = 1

    playerFlapAccv = -8 # velocity while flapping
    playerFlapped = False

    #game loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type ==KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerValY = playerFlapAccv
                    playerFlapped = True
                    GAME_SOUNDS['wing'].play()
        
        crashTest = isCollide(playerx,playery,upperPipes,lowerPipes)
        if crashTest:
            with open("highscore.txt","w") as f:
                f.write(str(highscore))
            return

        playerMidPos = playerx + GAME_SPRITES['player'].get_width()/2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width()/2
            if pipeMidPos<= playerMidPos < pipeMidPos +4:
                score +=1
                print(f"Your score is {score}") 
                GAME_SOUNDS['point'].play()
                if score > int(highscore):
                    highscore = score
            
        if playerValY < playerMaxValY and not playerFlapped:
            playerValY +=playerAccY
        
        if playerFlapped:
            playerFlapped = False
        playerHeight = GAME_SPRITES['player'].get_height()
        playery = playery + min(playerValY, GROUNDY-playery-playerHeight)

        #move pipes to the left
        for upperPipe,lowerPipe in zip(upperPipes,lowerPipes):
            upperPipe['x']+=pipeValX
            lowerPipe['x']+=pipeValX
        
        #add a new pipe
        if 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # remove pipes
        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        #blit the sprites
        SCREEN.blit(GAME_SPRITES['background'],(0,0))
        for upperPipe,lowerPipe in zip(upperPipes,lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0],(upperPipe['x'],upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1],(lowerPipe['x'],lowerPipe['y']))
        
        SCREEN.blit(GAME_SPRITES['base'],(basex,GROUNDY))
        SCREEN.blit(GAME_SPRITES['player'],(playerx,playery))
        myDigits = [int(x) for x in list(str(score))]
        width =0
        for digit in myDigits:
            width += GAME_SPRITES['numbers'][digit].get_width()
        Xoffset = (SCREENWIDTH -width)/2

        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit],(Xoffset,SCREENHEIGHT*0.12))
            Xoffset += GAME_SPRITES['numbers'][digit].get_width()
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def isCollide(playerx,playery,upperPipes,lowerPipes):
    if playery> GROUNDY - 25  or playery<0:
        GAME_SOUNDS['hit'].play()
        return True
    
    for pipe in upperPipes:
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        if(playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width()):
            GAME_SOUNDS['hit'].play()
            return True

    for pipe in lowerPipes:
        if (playery + GAME_SPRITES['player'].get_height() > pipe['y']) and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
            GAME_SOUNDS['hit'].play()
            return True

    return False

def getRandomPipe():
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT/3
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height() - 1.2*offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
        {'x' : pipeX, 'y' : -y1}, #upper pipe
        {'x' : pipeX, 'y' : y2} #lower pipe
    ]
    return pipe

if __name__ == "__main__":
    pygame.init() #initialize all modules
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('BY TARUN')
    GAME_SPRITES['numbers'] = (
        pygame.image.load('gallery/sprites/0.png').convert_alpha(),
        pygame.image.load('gallery/sprites/1.png').convert_alpha(),
        pygame.image.load('gallery/sprites/2.png').convert_alpha(),
        pygame.image.load('gallery/sprites/3.png').convert_alpha(),
        pygame.image.load('gallery/sprites/4.png').convert_alpha(),
        pygame.image.load('gallery/sprites/5.png').convert_alpha(),
        pygame.image.load('gallery/sprites/6.png').convert_alpha(),
        pygame.image.load('gallery/sprites/7.png').convert_alpha(),
        pygame.image.load('gallery/sprites/8.png').convert_alpha(),
        pygame.image.load('gallery/sprites/9.png').convert_alpha(),
    )

    GAME_SPRITES['message'] = pygame.image.load('gallery/sprites/message.png').convert_alpha()
    GAME_SPRITES['base'] = pygame.image.load('gallery/sprites/base.png').convert_alpha()
    GAME_SPRITES['pipe'] = (
        pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180),
        pygame.image.load(PIPE).convert_alpha(),
    )
    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()

    #sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('gallery/audio/die.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')
    if not os.path.exists ("highscore.txt"):
        with open("highscore.txt","w") as f:
            f.write(str("0"))
    while True:
        with open("highscore.txt","r") as f:
            highscore = f.read()
        print(highscore)
        welcomeScreen(highscore)
        mainGame(highscore)