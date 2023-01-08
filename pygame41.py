from cgitb import grey
from re import X
from threading import Timer
from numpy import zeros
import pygame, sys, threading
import random
import time
import socket as sok
pygame.init()
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
servAddr = '127.0.0.1'
s = sok.socket(sok.AF_INET, sok.SOCK_STREAM)
connect = s.connect((servAddr, 18000))
xp = 200
yp = 200
st=0
start = 0
p_is_right = False
p_is_left  = False
p_is_up    = False
p_is_down  = False
shooted = 0
pack = []
cooldown = 0
b = ''
pnum = 'NaN'
da = 0
timeleft = 360
def recv(s):
    global xp, yp,st,p_is_right,p_is_left,p_is_up,p_is_down, start, pnum, timeleft
    while True:
        data = str(s.recv(20), 'UTF-8')
        data = data.replace('|', '')
        xy = data.split(';')
        if xy[0] =='start' and start == 0:
            start = 1
            print(start)
            pnum = int(xy[1])
            print(pnum)
        elif start == 1 and xy[0]!='start':
            if xy[0]=='timeleft':
                timeleft = int(xy[1])
                print(timeleft)
            elif xy[0]!='timeleft':
                xp = int(xy[0])
                yp = int(xy[1])
                st = int(xy[2])
                p_is_right = int(xy[3])
                p_is_left  = int(xy[4])
                p_is_up    = int(xy[5])
                p_is_down  = int(xy[6])
        print(data,st, xy)


        
th=threading.Thread(target=recv, args=[s])
th.start()


WIDTH = 1920
HEIGHT = 1000
FPS = 60

def draw_text(surf, text, size, x, y, color):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)
# Задаем цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (34, 120, 50)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
font_name = pygame.font.match_font('arial')
FONT = pygame.font.Font(None, 32)

# Создаем игру и окно
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tanks")
clock = pygame.time.Clock()
counter = 0
class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
            
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)

class Player(pygame.sprite.Sprite):
    def __init__(self, path_img,x,y,n,color):
        pygame.sprite.Sprite.__init__(self)
        ##self.image = pygame.Surface((50, 40))
        self.image = pygame.image.load(path_img)
        self.const = self.image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.n=n
        self.speedx = 0
        self.speedy = 0
        self.is_left = False # повернут ли танк влево?
        self.is_right = False
        self.is_down = False
        self.is_up = True
        self.xspeed = 5
        self.yspeed = 5
        self.allows = []
        self.score = 0
        self.color = color
    def shoot(self):
        if self.is_down or self.is_up:
            bul = Bullet(self.rect.centerx, self.rect.top, self)
        elif self.is_left or self.is_right:
            bul = Bullet(self.rect.centerx, self.rect.top-17, self)
        all_bullet.add(bul)
        bul.update()
        # if self.n == 2:
        #     bul2 = Bullet2(self.rect.centerx, self.rect.top)
        #     all_bullet.add(bul2)
        #     bul2.update()
    def draw_text(self, surf, text, size, x, y):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, self.color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        surf.blit(text_surface, text_rect)
    def update(self):
        global pack, shooted, p_is_right,p_is_left,p_is_up,p_is_down, b
        # car_surf = self.image.convert()
        car_surf = self.image
        self.speedx  = 0
        self.speedy  = 0
        self.keystate = pygame.key.get_pressed()
        if (self.keystate[pygame.K_LEFT] and self.n==1) or (p_is_left and self.n==2):
            if (self.is_left):
                car_left = car_surf
            elif (self.is_right):
                car_left = pygame.transform.rotate(car_surf, 180)
                self.is_left = True
                self.is_right = False
            elif (self.is_up):
                car_left = pygame.transform.rotate(car_surf, 90)
                self.is_left = True
                self.is_up = False
            elif (self.is_down):
                car_left = pygame.transform.rotate(car_surf, -90)
                self.is_left = True
                self.is_down = False
            self.image=car_left
            self.speedx = -1*self.xspeed
            if self.rect.x<0:
                self.rect=0
        elif (self.keystate[pygame.K_RIGHT] and self.n==1) or (p_is_right and self.n==2):
            if (self.is_right):
                car_right = car_surf
            elif (self.is_left):
                car_right = pygame.transform.rotate(car_surf, -180)
                self.is_right = True
                self.is_left = False
            elif (self.is_up):
                car_right = pygame.transform.rotate(car_surf, -90)
                self.is_right = True
                self.is_up = False
            elif (self.is_down):
                car_right = pygame.transform.rotate(car_surf, 90)
                self.is_right = True
                self.is_down = False
            self.image=car_right
            self.speedx = self.xspeed
            if self.rect.x<0:
                self.rect.x=0
        elif (self.keystate[pygame.K_UP] and self.n==1) or (p_is_up and self.n==2):
            if(self.is_up):
                car_up = self.const
            elif (self.is_right):
                car_up = pygame.transform.rotate(car_surf, 90)
                self.is_up = True
                self.is_right = False
            elif(self.is_left):
                car_up = pygame.transform.rotate(car_surf, -90)
                self.is_up = True
                self.is_left = False
            elif(self.is_down):
                car_up = pygame.transform.rotate(car_surf, 180)
                self.is_up = True
                self.is_down = False
            self.image = car_up
            self.speedy = -1 *self.yspeed
            if self.rect.y <0:
                self.rect = 0
        elif (self.keystate[pygame.K_DOWN] and self.n==1) or (p_is_down and self.n==2):
            if(self.is_down):
                car_down = car_surf
            elif (self.is_right):
                car_down = pygame.transform.rotate(car_surf, -90)
                self.is_down = True
                self.is_right = False
            elif(self.is_left):
                car_down = pygame.transform.rotate(car_surf, 90)
                self.is_down = True
                self.is_left = False
            elif(self.is_up):
                car_down = pygame.transform.rotate(car_surf, 180)
                self.is_down = True
                self.is_up = False
            self.image = car_down
            self.speedy = self.yspeed
            if self.rect.y <0:
                self.rect = 0
        a = str(player.rect.x) + ';' + str(player.rect.y)+ ';'+ str(shooted) + ';' +str(int(player.is_right))+ ';' +str(int(player.is_left))+ ';' +str(int(player.is_up))+';' +str(int(player.is_down))
        while len(a)<20:
            a+='|'
        if a!=b:
            s.send(bytes(a, encoding ='UTF-8'))
        b = a
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        self.rectx = self.rect.x
        self.recty = self.rect.y
        self.rect = self.image.get_rect()
        self.rect.x = self.rectx
        self.rect.y = self.recty
        
        count = len(pygame.sprite.spritecollide(self, all_walls, False))
        if count>0:
            self.rect.x -= self.speedx
            self.rect.y -= self.speedy

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom >  HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0
            
class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, player):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.speed = -10 / 10
        self.directionx = False
        self.directiony = False
        self.directionx2 = False
        self.directiony2 = False
        self.myplayer = player

        if self.myplayer.is_up == True:
            self.directiony = True
            self.speed = -10
            self.rect.bottom = y
            self.rect.centerx = x
        elif self.myplayer.is_down == True:
            self.directiony = True
            self.speed = 10
            self.rect.bottom = y+100
            self.rect.centerx = x
        elif self.myplayer.is_right == True:
            self.directionx = True
            self.speed = 10
            self.rect.right = x +  50
            self.rect.centery = y+50
        elif self.myplayer.is_left == True:
            self.directionx = True
            self.speed = -10
            self.rect.left = x-50
            self.rect.centery = y+50

        
        

    def update(self):
        if self.directiony:
            self.rect.y += self.speed
        elif self.directionx:
            self.rect.x += self.speed

        # if player.is_up or player.is_down: 
        #     self.rect.y += self.speedy
        # elif player.is_left or player.is_right:
        #     self.rect.x +=self.speedx 
        # убить, если он заходит за верхнюю часть экрана

        wall_cr = pygame.sprite.spritecollide(self, all_walls, False)

        for wall in wall_cr:
            wall.hp_down()
            
        if self.rect.bottom < 0 or self.rect.bottom >1080 or self.rect.right >1920 or self.rect.left <0 or len(wall_cr):
            self.kill()
            print('xxx')

class Wall(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('pixil-frame-0(3).png')
        self.rect = self.image.get_rect()
        self.rect.centerx = 0
        self.rect.centery = 0
        self.hp = 3

    def hp_down(self):
        self.hp -= 1

        if (self.hp == 0):
            self.kill()

    def update(self):
        pass
class superwall(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('pixil-frame-0.png')
        self.rect = self.image.get_rect()
        self.rect.centerx = 0
        self.rect.centery = 0
    def hp_down(self):
        pass
    def update(self):
        pass
inputbox = InputBox(WIDTH/2-200, 400,140,32)
all_sprites = pygame.sprite.Group()
all_bullet = pygame.sprite.Group()
all_walls = pygame.sprite.Group()
#for i in range(stenki):
#    wall = Wall()
#    wall.rect.centerx= random.randint(0,1920)
#    wall.rect.centery = random.randint(0, 1080)
#    all_walls.add(wall)
a = zeros([HEIGHT,WIDTH])
for i in range(HEIGHT):
    for j in range(WIDTH):
        if (j%50 == 49 or j ==0) and i%50==49 and j!=1749 and j!=1799 and j!= 1699 and i!=899 and i!=949 and i!= 849 and j!=199 and j!=249 and j!= 149 and i!=199 and i!=249 and i!= 149:
            a[i,j] = 1
        if (i>398 and i<749 and j>398 and j<1599) or (j>=0 and j<49) or (j>1929 and j<1979):
            a[i, j] =0
        if ((i==349 or i==399 or i==699 or i==749) and (j==349 or j ==399 or j==1599 or j==1549)) or ((i==499 or i==549) and (j==949 or j==999)):
            a[i,j] =2
        if a[i,j] == 1:
            wall=Wall()
            wall.rect.x = j+1
            wall.rect.y = i+1
            all_walls.add(wall)
        if a[i,j] == 2:
            swall=superwall()
            swall.rect.x = j+1
            swall.rect.y = i+1
            all_walls.add(swall)

print(a)
# Цикл игры
running = True
# cadr = 0
# sec = 0
# endtime = 360
while running:
    if start==0:
        for event in pygame.event.get():
            inputbox.handle_event(event)
        inputbox.update()
        screen.fill((40, 40, 40))
        inputbox.draw(screen)
        draw_text(screen, 'WAITING FOR SECOND PLAYER', 50, WIDTH/2, 500, WHITE)
        

    elif start==1:
        endtime = timeleft
        if pnum == 1:
            player1posx = 1750
            player1posy = 900
            player1pic = 'pixil-layer-Background(1).png'
            player1color = BLUE
            player1colorstr = 'BLUE'
            player1tabx = 1800
            player1taby = 920
            player2posx = 200
            player2posy = 200
            player2pic = 'pixil-layer-Background(2).png'
            player2color = RED
            player2colorstr = 'RED'
            player2taby = 10
            player2tabx = 200
            da+=1
            pnum = 0
        elif pnum == 2:
            player2posx = 1750
            player2posy = 900
            player2pic = 'pixil-layer-Background(1).png'
            player2color = BLUE
            player2colorstr = 'BLUE'
            player2tabx = 1800
            player2taby = 920
            player1posx = 200
            player1posy = 200
            player1pic = 'pixil-layer-Background(2).png'
            player1color = RED
            player1colorstr = 'RED'
            player1taby = 10
            player1tabx = 200
            da+=1
            pnum=0
        if da==1:
            player = Player(player1pic , player1posx, player1posy,1, player1color)
            player2= Player(player2pic , player2posx, player2posy,2, player2color)
            all_sprites.add(player)
            all_sprites.add(player2)
            da+=1
        #Срем в код 
        # cadr += 1
        # if cadr % 60 == 0:
        #     endtime -= 1
        #     cadr = 0
        #     #sec += 1
        # Ввод процесса (события)
        for event in pygame.event.get():
            # проверка для закрытия окна
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP_ENTER:
                    if cooldown==0:
                        cooldown = endtime
                    if cooldown-1>endtime:
                        player.shoot()
                        shooted=1
                        cooldown =endtime
        # Обновление
        all_sprites.update()
        all_bullet.update()
        all_walls.update()
        player2.rect.x = xp
        player2.rect.y = yp
        shooted=0
        if st==1:
            player2.shoot()
            st=0
        # Рендеринг
        screen.fill(GREEN)
        all_sprites.draw(screen)
        all_bullet.draw(screen)
        all_walls.draw(screen)
        player.draw_text(screen, 'score:'+str(player.score), 50, player1tabx, player1taby)
        player2.draw_text(screen, 'score:'+str(player2.score), 50, player2tabx, player2taby)
        draw_text(screen, 'Time left:'+str(endtime), 50, WIDTH/2, 100, WHITE)
        if endtime == 0:
            if player.score > player2.score:
                draw_text(screen, player1colorstr+' win', 200, WIDTH/2, 400, player1color)
            elif player.score < player2.score:
                draw_text(screen, player2colorstr+' win', 200, WIDTH/2, 400 , player2color)
            else:
                draw_text(screen, 'DRAW', 200, WIDTH/2, 500, WHITE)
        if endtime <0:
            pygame.time.delay(2000)
            pygame.quit()
        # После отрисовки всего, переrворачиваем экран
        
        f = player.rect.colliderect(player2.rect)
        if f == True:
            player.rect.centery -= player.speedy
            player.rect.centerx -= player.speedx
            player2.rect.centery -= player2.speedy
            player2.rect.centerx -= player2.speedx
            print('1')
        if len(pygame.sprite.spritecollide(player2, all_bullet, True))>0:
            player2.rect.centery = player2posy
            player2.rect.centerx = player2posx
            player.score +=1
            print('p1')
        if len(pygame.sprite.spritecollide(player, all_bullet, True))>0:
            player.rect.centery = player1posy
            player.rect.centerx = player1posx
            player2.score +=1
            print('p2')
        #print(all_walls)
        #print(len(pygame.sprite.spritecollide(player2, all_bullet, True)))
        #print('Убито')
        #print(len(pygame.sprite.spritecollide(player2, all_walls, False)))
        #print(player.rect.height, player.rect.width)
        #print(player.recvd)
        #print(xp,yp)
    pygame.display.flip()
    # Держим цикл на правильной скорости
    clock.tick(FPS)
pygame.quit()