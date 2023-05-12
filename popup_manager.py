import json
import os
import threading
import time
from collections import deque
from tkinter import Canvas, Tk, BOTH, Label, Button, PhotoImage, NW
import pyglet
import urllib.request


class PopupManager():
    def __init__(self):
        self.queue = deque()
        self.running = True
        self.tts_on = True
        self.width = 600
        self.height = 400
        self.outline_offset = 2

        with open("config.json", "r", encoding="UTF8") as st_json:
            json_data = json.load(st_json)

        self.clova_api_id = json_data['clova_api_id']
        self.clova_api_pwd = json_data['clova_api_pwd']

        pyglet.font.add_file('price_font.ttf')
        pyglet.font.add_file('time_font.ttf')

        thread = threading.Thread(target=self.show_popup)
        thread.start()

    def move_window(self, event):  # Moving the window
        root.geometry(f'+{event.x_root}+{event.y_root}')

    def draw_shadow(self, x1, y1, x2, y2, radius=25, **kwargs):  # Creating a rounded rectangle
        x2 += 3
        y2 += 3

        colors = ['#9e9e9e', '#969696', '#8f8f8f', '#878787', '#808080',
                  '#787878', '#717171', '#696969', '#626262', '#5a5a5a',
                  '#535353', '#4b4b4b', '#444444', '#3c3c3c', '#353535',
                  '#2d2d2d', '#262626', '#1e1e1e', '#171717', '#0f0f0f']



        for i in range(20):
            points = [x1 + radius, y1,
                      x1 + radius, y1,
                      x2 - radius, y1,
                      x2 - radius, y1,
                      x2, y1,
                      x2, y1 + radius,
                      x2, y1 + radius,
                      x2, y2 - radius,
                      x2, y2 - radius,
                      x2, y2,
                      x2 - radius, y2,
                      x2 - radius, y2,
                      x1 + radius, y2,
                      x1 + radius, y2,
                      x1, y2,
                      x1, y2 - radius,
                      x1, y2 - radius,
                      x1, y1 + radius,
                      x1, y1 + radius,
                      x1, y1]

            x2 -= 0.15
            y2 -= 0.15

            canvas.create_polygon(points, **kwargs, smooth=True, fill=colors[i])



    def draw_outline(self, x1, y1, x2, y2, radius=25, **kwargs):  # Creating a rounded rectangle
        points = [x1 + radius, y1,
                  x1 + radius, y1,
                  x2 - radius, y1,
                  x2 - radius, y1,
                  x2, y1,
                  x2, y1 + radius,
                  x2, y1 + radius,
                  x2, y2 - radius,
                  x2, y2 - radius,
                  x2, y2,
                  x2 - radius, y2,
                  x2 - radius, y2,
                  x1 + radius, y2,
                  x1 + radius, y2,
                  x1, y2,
                  x1, y2 - radius,
                  x1, y2 - radius,
                  x1, y1 + radius,
                  x1, y1 + radius,
                  x1, y1]

        return canvas.create_polygon(points, **kwargs, smooth=True, fill="#4189F5")

    def round_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):  # Creating a rounded rectangle
        points = [x1 + radius, y1,
                  x1 + radius, y1,
                  x2 - radius, y1,
                  x2 - radius, y1,
                  x2, y1,
                  x2, y1 + radius,
                  x2, y1 + radius,
                  x2, y2 - radius,
                  x2, y2 - radius,
                  x2, y2,
                  x2 - radius, y2,
                  x2 - radius, y2,
                  x1 + radius, y2,
                  x1 + radius, y2,
                  x1, y2,
                  x1, y2 - radius,
                  x1, y2 - radius,
                  x1, y1 + radius,
                  x1, y1 + radius,
                  x1, y1]

        return canvas.create_polygon(points, **kwargs, smooth=True, fill="white")

    def draw_title(self, x1, y1, x2, y2, radius=25, **kwargs):  # Creating a rounded rectangle
        points = [x1 + radius, y1,
                  x1 + radius, y1,
                  x2 - radius, y1,
                  x2 - radius, y1,
                  x2, y1,
                  x2, y1 + radius,
                  x2, y1 + radius,
                  x2, y2 - 0,
                  x2, y2 - 0,
                  x2, y2,
                  x2 - 0, y2,
                  x2 - 0, y2,
                  x1 + 0, y2,
                  x1 + 0, y2,
                  x1, y2,
                  x1, y2 - 0,
                  x1, y2 - 0,
                  x1, y1 + radius,
                  x1, y1 + radius,
                  x1, y1]

        return canvas.create_polygon(points, **kwargs, smooth=True, fill="#4189F5")

    def close_window(self):
        root.destroy()

    def close_window_on_action(self, event):
        root.destroy()

    def put_data(self, price, payment_time, popup_duration):
        price = format(int(price), ',d')
        self.queue.append((price + ' 원', payment_time, int(popup_duration)))

    def stop_thread(self):
        self.running = False
        self.queue = deque()

    def tts(self, text):
        if self.tts_on:
            audio = 'speech.mp3'
            text = f'줍줍포인트 {text}이 결제되었습니다'
            encText = urllib.parse.quote(text)
            data = "speaker=nshasha&speed=-1&alpha=1&pitch=1&format=mp3&text=" + encText;
            url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
            request = urllib.request.Request(url)
            request.add_header("X-NCP-APIGW-API-KEY-ID", self.clova_api_id)
            request.add_header("X-NCP-APIGW-API-KEY", self.clova_api_pwd)
            response = urllib.request.urlopen(request, data=data.encode('utf-8'))
            rescode = response.getcode()
            if (rescode == 200):
                response_body = response.read()
                with open(audio, 'wb') as f:
                    f.write(response_body)

                sound = pyglet.media.load(audio, streaming=False)
                sound.play()
                os.remove(audio)
            else:
                print("Error Code:" + rescode)

    def tts_toggle(self):
        self.tts_on = not self.tts_on

    def show_popup(self):
        global root, canvas

        while self.running:
            if self.queue:
                price, transaction_time, duration = self.queue.popleft()
                self.tts(price)
                root = Tk()
                root.overrideredirect(1)
                root.bind("<Button-1>", self.close_window_on_action)
                root.geometry(f'{self.width}x{self.height}')
                root.config(background='grey')
                root.attributes("-transparentcolor", "grey")

                # Center the window on the screen
                root.update_idletasks()
                width = root.winfo_width()
                height = root.winfo_height()
                x = (root.winfo_screenwidth() // 2) - (width // 2)
                y = (root.winfo_screenheight() // 2) - (height // 2)
                root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

                canvas = Canvas(root, bg="grey", highlightthickness=0)
                canvas.pack(fill=BOTH, expand=1)

                self.draw_outline(0, 0, self.width, self.height, radius=70)
                self.round_rectangle(self.outline_offset, self.outline_offset, self.width-self.outline_offset, self.height-self.outline_offset, radius=70)  # Creating the rounded rectangle/window
                self.draw_title(self.outline_offset, self.outline_offset, self.width-self.outline_offset, 70, radius=70)

                logo_image = PhotoImage(file="logo.png")
                logo_label = Label(canvas, image=logo_image, borderwidth=0)
                logo_label.place(x=20, y=15)

                close_image = PhotoImage(file="close.png")  # 이미지 파일 이름을 필요에 따라 변경하세요
                close_button = Button(canvas, image=close_image, relief="flat", command=self.close_window, bg="#4189F5", activebackground="#4189F5", bd=0, borderwidth=0)
                close_button.place(x=self.width-60, y=15)

                my_label = Label(canvas, text=price, font=('더잠실 6 ExtraBold', 50), foreground='black', background='white')
                my_label.place(x=self.width//2, y=200, anchor='center')

                my_label2 = Label(canvas, text=transaction_time, font=('더잠실 2 Light', 25), foreground='black', background='white')
                my_label2.place(x=self.width//2, y=self.height-50, anchor='center')

                root.update()
                root.wm_attributes("-topmost", 1)
                root.after(duration * 1000, self.close_window)
                root.mainloop()
            time.sleep(1)

        exit(0)