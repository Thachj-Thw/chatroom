# from network import Network
import pygame
import sys
import asyncio
import websockets

uri = "ws://localhost:5000"
error = False
try:
    websockets.connect(uri)
except:
    error = True

width = 300
hight = 500
pygame.init()
display = pygame.display.set_mode((width, hight), pygame.RESIZABLE)
pygame.display.set_caption('World Chat')
clock = pygame.time.Clock()
color = pygame.Color('lightskyblue3')
fps = 60
font_size = 25
font = pygame.font.SysFont('consolas', font_size - 5)
# n = Network()
data_send = ''
data_get = 'ị'


def resize(e):
    globals()['width'] = e.w
    globals()['hight'] = e.h
    globals()['display'] = pygame.display.set_mode((width, hight), pygame.RESIZABLE)


def get_name():
    if error:
        in_text = 'Can not connect to server'
    else:
        in_text = 'Your name'
    in_rect = pygame.Rect(0, (hight // 3) - 5, 1, font_size)
    while True:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                resize(event)
                in_rect = pygame.Rect(0, (hight // 3) - 5, 1, font_size)
            if event.type == pygame.KEYDOWN:
                if error:
                    pygame.quit()
                    sys.exit()
                if in_text == 'Your name' or in_text == 'Try another name':
                    in_text = ''
                if event.key == pygame.K_BACKSPACE:
                    in_text = in_text[:-1]
                elif event.key == 13:
                    if in_text == '':
                        in_text = 'Try another name'
                    else:
                        websockets.connect(uri).send(data_send)
                        globals()['data_send'] = f'{in_text}ịọJoined'
                        return in_text
                else:
                    in_text += event.unicode

        display.fill((255, 255, 255))
        pygame.draw.rect(display, color, in_rect)
        text = font.render(in_text, True, (0, 0, 0))
        display.blit(text, (width // 2 - text.get_width() // 2, hight // 3))
        in_rect.x = (width // 2 - text.get_width() // 2) - 5
        in_rect.w = text.get_width() + 10
        pygame.display.update()
        pygame.display.flip()


class Mess:
    def __init__(self, data, name):
        self.data = data
        self.name = name
        self.rect = pygame.Rect(0, 0, 1, font_size)

    def draw(self):
        h = hight - font_size * 3
        for m in self.data:
            if m[1] == 'ọJoined' or m[1] == 'ọDisconnected':
                t = font.render(m[1][1:], True, (255, 0, 0))
            else:
                t = font.render(m[1], True, (0, 0, 0))
            na = font.render(m[0], True, (0, 0, 255))
            if m[0] == self.name:
                display.blit(t, (width - 10 - t.get_width(), h))
                self.rect.x = width - 10 - t.get_width() - 5
                self.rect.y = h - 5
                self.rect.w = t.get_width() + 10
            else:
                display.blit(na, (5, h))
                display.blit(t, (na.get_width() + 15, h))
                self.rect.x = na.get_width() + 10
                self.rect.y = h - 5
                self.rect.w = t.get_width() + 10
            pygame.draw.rect(display, color, self.rect, 2)
            h -= (font_size * 2)


class InputBox:
    def __init__(self):
        self.t = ''
        self.rect = pygame.Rect(0, hight - font_size - 10, width, hight - (hight - font_size - 10))
        self.s = ''

    def draw(self):
        pygame.draw.rect(display, color, self.rect)
        text = font.render(self.t, True, (0, 0, 0))
        display.blit(text, (width - 10 - text.get_width(), hight - font_size))

    def resize(self):
        self.rect = pygame.Rect(0, hight - font_size - 10, width, hight - (hight - font_size - 10))

    def update(self, event):
        self.s = ''
        if event.key == pygame.K_BACKSPACE:
            self.t = self.t[:-1]
        elif event.key == 13:
            self.s = self.t
            self.t = ''
        else:
            self.t += event.unicode
        return self.s


async def run(n):
    all_data = []
    mess = Mess(all_data, n)
    input_box = InputBox()
    loop = True
    while loop:
        clock.tick(fps)
        send_text = ''
        display.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                globals()['data_send'] = f'{n}ịọDisconnected'
                loop = False
                # pygame.quit()
                # sys.exit()
            if event.type == pygame.VIDEORESIZE:
                resize(event)
                input_box.resize()
            if event.type == pygame.KEYDOWN:
                send_text = input_box.update(event)
        display.fill((255, 255, 255))
        input_box.draw()
        mess.draw()
        if send_text != '':
            globals()['data_send'] = f'{n}ị{send_text}'
        data = data_get.split('ị')
        globals()['data_get'] = 'ị'
        if data[0] != '':
            all_data.insert(0, (data[0], data[1]))

        pygame.display.update()
        pygame.display.flip()
        await asyncio.sleep(.01)


async def send(websocket, n):
    while True:
        if data_send != f'{n}ị':
            await websocket.send(data_send)
            # print('send:', data_send)
            if data_send == f'{n}ịọDisconnected':
                pygame.quit()
                sys.exit()
            globals()['data_send'] = f'{n}ị'
        await asyncio.sleep(0)


async def get(websocket):
    while True:
        greeting = await websocket.recv()
        globals()['data_get'] = greeting
        # print(f"get: {greeting}")
        await asyncio.sleep(0)


async def main():
    name = get_name()
    async with websockets.connect(uri) as websocket:
        await asyncio.gather(
            send(websocket, name),
            get(websocket),
            run(name)
        )
#
# if __name__ == '__main__':
#     asyncio.run(main())
