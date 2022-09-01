import asyncio
import pygame as pg
import random
import sys

pg.init()

pg.mixer.init()
screen = pg.display.set_mode((800,600))
clock = pg.time.Clock()
font = pg.font.SysFont("Courier New", 20, 1)

# load images and sprites
background = []
rain = []
tree = []
droplets = []
darker = []
for i in range(4):
    background.append(pg.image.load('bg'+str(i)+'.png').convert())
    rain.append(pg.image.load('rain'+str(i)+'.png').convert_alpha())
    tree.append(pg.image.load('tree'+str(i)+'.png').convert_alpha())
    droplets.append(pg.image.load('droplets'+str(i)+'.png').convert_alpha())
    darker.append(pg.image.load('darker.png').convert_alpha())

window = pg.image.load('window.png').convert_alpha()
slider_bg = pg.image.load('slider_bg.png')
slider_handle = pg.image.load('slider_handle.png')
options_img = [pg.image.load('options.png'), pg.image.load('close.png')]
for i in range(3):
    darker[i+1].blit(darker[i], (0,0))

# load sounds
sounds = {}

keys = ['brown', 'pink', 'flow', 'wind', 'drops']
for key in keys:
    sounds[key] = [pg.mixer.Sound(key +'.ogg')]
    # sounds[key][0].set_volume(0)
    # sounds[key][0].play(-1)

sounds['thunder'] = [[], [20], [50]] # samples, frequency, volume
for i in range(3):
    sounds['thunder'][0].append(pg.mixer.Sound('thunder'+str(i)+'.ogg'))
    sounds['thunder'][0][i].set_volume(0.5)

async def main():
    if sys.platform == 'emscripten':
        lock_fps = False
    else:
        lock_fps = True

    running = 1
    timer = delay = 0
    mouse_pos = [0, 0]
    clicked = 0
    options = 0
    options_rect = pg.Rect(760, 0, 40, 40)

    frame  = window.copy()
    
    while 1:
        clock.tick(30)
        pg.event.get()
        if pg.mouse.get_pressed()[0]:
            break
        screen.blit(frame, (0,0))
        screen.blit(font.render("Click to start", 0, [255, 255, 255]), [400,400])
        pg.display.update()
        await asyncio.sleep(0)
        
    for key in keys:
        sounds[key][0].set_volume(0)
        sounds[key][0].play(-1)
    
    tree_sprite = 0
    bg_sprite = 0
    rain_sprite = 0
    droplets_sprite = 0
    thunder_sprite = 4

    while True:
        if lock_fps:
            elapsed_time = 1
            clock.tick(60)/1000
        else:
            elapsed_time = clock.tick()/1000
        
        timer += 60*elapsed_time
        fps = 60/(elapsed_time+1e-6)

        if options and (int(timer)%3 == 1 or fps > 30):
            frame.blit(window, (0,0))

        if int(timer)%3 == 1 or fps > 30:
            frame.blit(background[bg_sprite], (151,46))
            frame.blit(rain[rain_sprite], (151,46))
        
        if int(timer)%3 == 2 or fps > 30:
            frame.blit(tree[tree_sprite], (151,46))
            frame.blit(droplets[droplets_sprite], (151,46))
        
            if thunder_sprite > 0:
                frame.blit(darker[thunder_sprite-1], (151,46))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = 0
        
        if timer < 250:
            for key in keys:
                sounds[key][0].set_volume(timer*0.001)
        
        if int(timer)%59 == 0:
            bg_sprite = (bg_sprite + 1)%4
        if int(timer)%27 == 0:
            rain_sprite = (rain_sprite + 1)%4
        if int(timer)%43 == 0:
            droplets_sprite = (droplets_sprite + 1)%4
        if int(timer)%77 == 0:
            tree_sprite = (tree_sprite + 1)%3
        if thunder_sprite < 4 and int(timer)%11 == 0:
            thunder_sprite +=1
        if int(timer)%83 == 0 and thunder_sprite == 4:
            if random.randint(0,100) < sounds['thunder'][1][0]:
                thunder_sprite = 0
                sample = random.randint(0,len(sounds['thunder'][0]) - 1)
                sounds['thunder'][0][sample].set_volume(sounds['thunder'][2][0]*0.01)
                sounds['thunder'][0][sample].play()
        
        if pg.mouse.get_pressed()[0]:
            if not clicked:
                mouse_pos = list(pg.mouse.get_pos())
                clicked = 1
            else:
                mouse_pos[1] = pg.mouse.get_pos()[1]
                
        else:
            clicked = 0
        
        if clicked and options_rect.collidepoint(mouse_pos) and timer > delay:
            options = not(options)
            frame.blit(window, (0,0))
            delay = timer + 600

        if options:
            if int(timer)%3 == 2  or fps > 30:
                # frame.blit(window, (0,0))
                frame.blit(font.render('Adjust sound volumes and thunder strike frequency.', 0, (255, 255, 255)), ((250, 575)))
                frame.blit(font.render('thunder', 0, (255, 255, 255)), ((570, 25)))
                frame.blit(font.render('strikes', 0, (255, 255, 255)), ((670, 25)))

            
            if int(timer)%3 == 0  or fps > 30:
                for i in range(len(sounds)-1):
                    frame.blit(font.render(keys[i], 0, (255, 255, 255)), ((75+i*100, 25)))
                    slider((75+i*100, 50), slider_bg, slider_handle, frame, mouse_pos, clicked, sounds[keys[i]][0])
                    
                slider((575, 50), slider_bg, slider_handle, frame, mouse_pos, clicked, sounds['thunder'][2])
                slider((675, 50), slider_bg, slider_handle, frame, mouse_pos, clicked, sounds['thunder'][1])

        if int(timer)%3 == 0  or fps > 30:
            frame.blit(options_img[options], (765, 10))
            # frame.blit(font.render(str(fps), 0, [255, 255, 255]), [400,400])
            screen.blit(frame, (0,0))

        pg.display.update()
        
        await asyncio.sleep(0)  # very important, and keep it 0

        if not running:
            pg.quit()
            return

def slider(coords, background, handle, frame, mouse_pos, clicked, sound):

    frame.blit(background, coords)
    size = list(background.get_size())
    size[1] = size[1] - handle.get_size()[1]

    rect = pg.Rect(coords[0], coords[1], size[0], size[1])

    if type(sound) == list:
        position = sound[0]*0.01
    else:
        position = sound.get_volume()
    if clicked and rect.collidepoint(mouse_pos[0], mouse_pos[1]-handle.get_size()[1]/2):
        position = 1 - (mouse_pos[1]-coords[1]-handle.get_size()[1]/2)/size[1]
        if type(sound) == list:
            sound[0] = int(position*100)
        else:
            sound.set_volume(position)

    frame.blit(handle, (coords[0], coords[1] + size[1]*(1-position)))


asyncio.run( main() )

# do not add anything from here
# asyncio.run is non block on pg-wasm
