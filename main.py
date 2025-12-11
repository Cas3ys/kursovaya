from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty
from kivy.core.audio import SoundLoader
import random
import json
import os

class SettingsMenu(BoxLayout):
    def __init__(self, back_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 30
        self.spacing = 20
        
        self.back_callback = back_callback
        
        title = Label(text='НАСТРОЙКИ', font_size='30sp', color=(0, 1, 1, 1))
        self.add_widget(title)
        
        # Регулятор скорости
        speed_label = Label(text='СКОРОСТЬ:', font_size='20sp')
        self.add_widget(speed_label)
        
        self.speed_slider = Slider(min=0.05, max=0.5, value=0.2, step=0.05)
        self.add_widget(self.speed_slider)
        
        # Переключатель звука
        self.sound_btn = Button(
            text='ЗВУК: ВКЛ',
            size_hint=(None, None),
            size=(150, 40)
        )
        self.sound_btn.bind(on_press=self.toggle_sound)
        self.add_widget(self.sound_btn)
        
        # Кнопка назад
        back_btn = Button(
            text='НАЗАД',
            size_hint=(None, None),
            size=(120, 40)
        )
        back_btn.bind(on_press=self.go_back)
        self.add_widget(back_btn)
    
    def toggle_sound(self, instance):
        app = App.get_running_app()
        app.sound_enabled = not app.sound_enabled
        instance.text = 'ЗВУК: ВКЛ' if app.sound_enabled else 'ЗВУК: ВЫКЛ'
    
    def go_back(self, instance):
        self.back_callback()

class MainMenu(BoxLayout):
    def __init__(self, start_callback, settings_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 50
        self.spacing = 30
        
        self.start_callback = start_callback
        self.settings_callback = settings_callback
        
        # Анимация
        self.title = Label(
            text='ЗМЕЙКА',
            font_size='40sp',
            color=(0, 1, 0, 1)
        )
        self.add_widget(self.title)
        
        # Кнопка старта
        start_btn = Button(
            text='НАЧАТЬ ИГРУ',
            size_hint=(None, None),
            size=(200, 60),
            font_size='20sp',
            background_color=(0, 0.7, 0, 1)
        )
        start_btn.bind(on_press=self.start_game)
        self.add_widget(start_btn)
        
        # Кнопка настроек
        settings_btn = Button(
            text='НАСТРОЙКИ',
            size_hint=(None, None),
            size=(150, 50),
            font_size='16sp',
            background_color=(0.2, 0.5, 0.8, 1)
        )
        settings_btn.bind(on_press=self.open_settings)
        self.add_widget(settings_btn)
        
        Clock.schedule_interval(self.animate_title, 0.5)
    
    def animate_title(self, dt):
        colors = [(0, 1, 0, 1), (1, 1, 0, 1), (0, 1, 1, 1), (1, 0, 1, 1)]
        current_color = random.choice(colors)
        self.title.color = current_color
    
    def start_game(self, instance):
        self.start_callback()
    
    def open_settings(self, instance):
        self.settings_callback()

class GameOverScreen(BoxLayout):
    def __init__(self, score, high_score, restart_callback, menu_callback, **kwargs):
        super().__init__(**kwargs)
        
        self.orientation = 'vertical'
        self.padding = 50
        self.spacing = 20
        
        self.restart_callback = restart_callback
        self.menu_callback = menu_callback
        
        # Заголовок
        title = Label(
            text='ИГРА ОКОНЧЕНА',
            font_size='30sp',
            color=(1, 0, 0, 1)
        )
        self.add_widget(title)
        
        # Счет
        score_label = Label(
            text=f'Счет: {score}',
            font_size='25sp',
            color=(1, 1, 1, 1)
        )
        self.add_widget(score_label)
        
        # Рекорд
        high_score_label = Label(
            text=f'Рекорд: {high_score}',
            font_size='20sp',
            color=(1, 0.5, 0, 1)
        )
        self.add_widget(high_score_label)
        
        # Сообщение о новом рекорде
        if score == high_score and score > 0:
            record_label = Label(
                text='НОВЫЙ РЕКОРД!',
                font_size='20sp',
                color=(1, 1, 0, 1)
            )
            self.add_widget(record_label)
        
        # Кнопка рестарта
        restart_btn = Button(
            text='ИГРАТЬ СНОВА',
            size_hint=(None, None),
            size=(200, 50),
            font_size='18sp',
            background_color=(0.8, 0.2, 0, 1)
        )
        restart_btn.bind(on_press=self.restart_game)
        self.add_widget(restart_btn)
        
        # Кнопка меню
        menu_btn = Button(
            text='В МЕНЮ',
            size_hint=(None, None),
            size=(150, 40),
            font_size='16sp',
            background_color=(0.2, 0.2, 0.8, 1)
        )
        menu_btn.bind(on_press=self.go_to_menu)
        self.add_widget(menu_btn)
    
    def restart_game(self, instance):
        self.restart_callback()
    
    def go_to_menu(self, instance):
        self.menu_callback()

class SnakeGame(Widget):
    score = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Игровые переменные
        self.cell_size = 20
        self.snake = []
        self.direction = (1, 0)
        self.food = None
        self.special_food = None
        self.special_food_timer = 0
        self.game_over = False
        self.game_started = False
        self.speed = 0.2
        self.paused = False
        
        # Эффекты
        self.invincible = False
        self.invincible_timer = 0
        self.score_multiplier = 1

        self.eat_sound = None
        self.game_over_sound = None
        self.load_sounds()

        self.create_background_and_border()

        self.score_label = Label(
            text='Счет: 0',
            size_hint=(None, None),
            pos=(10, self.height - 40),
            color=(1, 1, 1, 1)
        )
        self.add_widget(self.score_label)
        
        self.multiplier_label = Label(
            text='',
            size_hint=(None, None),
            pos=(10, self.height - 70),
            color=(1, 1, 0, 1)
        )
        self.add_widget(self.multiplier_label)
        
        self.bind(size=self._update, pos=self._update)
    
    def create_background_and_border(self):
        self.canvas.before.clear()
        
        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            Rectangle(pos=self.pos, size=self.size)

            Color(0.15, 0.15, 0.15, 1)
            field_margin = 20
            field_pos = (field_margin, field_margin)
            field_size = (self.width - 2*field_margin, self.height - 2*field_margin)
            Rectangle(pos=field_pos, size=field_size)      
            # Внешняя рамка (толстая)
            Color(0.3, 0.5, 0.8, 1)
            Line(rectangle=(
                field_pos[0] - 3, 
                field_pos[1] - 3, 
                field_size[0] + 6, 
                field_size[1] + 6
            ), width=3)    
            # Внутренняя рамка (тонкая)
            Color(0.5, 0.7, 1.0, 1)
            Line(rectangle=(
                field_pos[0] - 1, 
                field_pos[1] - 1, 
                field_size[0] + 2, 
                field_size[1] + 2
            ), width=1)
            # Декоративные уголки
            corner_size = 15

            Line(points=[
                field_pos[0], field_pos[1] + corner_size,
                field_pos[0], field_pos[1],
                field_pos[0] + corner_size, field_pos[1]
            ], width=2)
            
            Line(points=[
                field_pos[0] + field_size[0] - corner_size, field_pos[1],
                field_pos[0] + field_size[0], field_pos[1],
                field_pos[0] + field_size[0], field_pos[1] + corner_size
            ], width=2)
            
            Line(points=[
                field_pos[0], field_pos[1] + field_size[1] - corner_size,
                field_pos[0], field_pos[1] + field_size[1],
                field_pos[0] + corner_size, field_pos[1] + field_size[1]
            ], width=2)
            
            Line(points=[
                field_pos[0] + field_size[0] - corner_size, field_pos[1] + field_size[1],
                field_pos[0] + field_size[0], field_pos[1] + field_size[1],
                field_pos[0] + field_size[0], field_pos[1] + field_size[1] - corner_size
            ], width=2)
    
    def load_sounds(self):
        try:
            self.eat_sound = SoundLoader.load('eat.wav')
            self.game_over_sound = SoundLoader.load('game_over.wav')
        except:
            print("Звуковые файлы не найдены")  
    def play_sound(self, sound):
        app = App.get_running_app()
        if app.sound_enabled and sound:
            sound.play() 
    def _update(self, *args):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size
        
        self.score_label.pos = (10, self.height - 40)
        self.multiplier_label.pos = (10, self.height - 70)  
        # Обновляем рамку при изменении размера
        self.create_background_and_border()  
    def start_game(self):
        self.snake = [(100, 100)]
        self.direction = (1, 0)
        self.score = 0
        self.game_over = False
        self.game_started = True
        self.paused = False
        self.invincible = False
        self.score_multiplier = 1
        
        self.speed = App.get_running_app().game_speed
        
        self.create_food()
        Clock.unschedule(self.update)
        Clock.schedule_interval(self.update, self.speed)
        
        self.draw_snake()
        self.draw_food()
    
    def create_food(self):
        if not self.game_started:
            return          
        # Учитываем отступы рамки при создании еды
        field_margin = 20
        max_x = int((self.width - 2 * field_margin) // self.cell_size) - 1
        max_y = int((self.height - 2 * field_margin) // self.cell_size) - 1
        
        while True:
            x = random.randint(0, max_x) * self.cell_size + field_margin
            y = random.randint(0, max_y) * self.cell_size + field_margin
            
            if (x, y) not in self.snake:
                self.food = (x, y)
                break     
        # Случайно создаем специальную еду
        if random.random() < 0.3:  # 30% шанс
            while True:
                x = random.randint(0, max_x) * self.cell_size + field_margin
                y = random.randint(0, max_y) * self.cell_size + field_margin
                
                if (x, y) not in self.snake and (x, y) != self.food:
                    self.special_food = (x, y)
                    self.special_food_timer = 10  # 10 секунд
                    break
    
    def draw_snake(self):
        self.canvas.after.clear()   
        with self.canvas.after:
            # Рисуем специальную еду
            if self.special_food:
                Color(1, 0.5, 0, 1)  # Оранжевый
                x, y = self.special_food
                Ellipse(pos=(x, y), size=(self.cell_size, self.cell_size))        
            # Рисуем обычную еду
            if self.food:
                Color(1, 0, 0, 1)
                x, y = self.food
                Rectangle(pos=(x, y), size=(self.cell_size, self.cell_size))         
            # Рисуем змейку
            for i, (x, y) in enumerate(self.snake):
                if self.invincible and i == 0:
                    Color(1, 1, 1, 1) if int(self.invincible_timer * 10) % 2 else Color(0, 1, 0, 1)
                elif i == 0:
                    Color(0, 1, 0, 1)
                else:
                    Color(0, 0.8, 0, 1)
                Rectangle(pos=(x, y), size=(self.cell_size, self.cell_size))         
                # Рисуем глаза только на голове змейки
                if i == 0:
                    # Определяем положение глаз в зависимости от направления
                    dx, dy = self.direction
                    eye_size = self.cell_size // 5
                    eye_offset = eye_size  # Отступ от края
                    
                    # Глаза черного цвета
                    Color(0, 0, 0, 1)                    
                    if dx == 1:  # Движение вправо
                        # Правый глаз (правый верхний угол)
                        Ellipse(pos=(x + self.cell_size - eye_size - eye_offset//2, 
                                   y + self.cell_size - eye_size*2), 
                               size=(eye_size, eye_size))
                        # Левый глаз (правый нижний угол)
                        Ellipse(pos=(x + self.cell_size - eye_size - eye_offset//2, 
                                   y + eye_offset//2), 
                               size=(eye_size, eye_size))                    
                    elif dx == -1:  # Движение влево
                        # Правый глаз (левый верхний угол)
                        Ellipse(pos=(x + eye_offset//2, 
                                   y + self.cell_size - eye_size*2), 
                               size=(eye_size, eye_size))
                        # Левый глаз (левый нижний угол)
                        Ellipse(pos=(x + eye_offset//2, 
                                   y + eye_offset//2), 
                               size=(eye_size, eye_size))                 
                    elif dy == 1:  # Движение вверх
                        # Правый глаз (правый верхний угол)
                        Ellipse(pos=(x + self.cell_size - eye_size*2, 
                                   y + self.cell_size - eye_size - eye_offset//2), 
                               size=(eye_size, eye_size))
                        # Левый глаз (левый верхний угол)
                        Ellipse(pos=(x + eye_offset//2, 
                                   y + self.cell_size - eye_size - eye_offset//2), 
                               size=(eye_size, eye_size))                
                    elif dy == -1:  # Движение вниз
                        # Правый глаз (правый нижний угол)
                        Ellipse(pos=(x + self.cell_size - eye_size*2, 
                                   y + eye_offset//2), 
                               size=(eye_size, eye_size))
                        # Левый глаз (левый нижний угол)
                        Ellipse(pos=(x + eye_offset//2, 
                                   y + eye_offset//2), 
                               size=(eye_size, eye_size))
    
    def draw_food(self):
        pass   
    def update(self, dt):
        if self.game_over or not self.game_started or self.paused:
            return    
        # Обновляем таймеры
        if self.special_food:
            self.special_food_timer -= dt
            if self.special_food_timer <= 0:
                self.special_food = None
        
        if self.invincible:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False
                self.multiplier_label.text = ''    
        # Двигаем змейку
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx * self.cell_size, head_y + dy * self.cell_size)       
        # Проверяем столкновения с учетом рамки
        field_margin = 20
        if not self.invincible:
            if (new_head[0] < field_margin or new_head[0] >= self.width - field_margin or 
                new_head[1] < field_margin or new_head[1] >= self.height - field_margin):
                self.end_game()
                return
            
            if new_head in self.snake:
                self.end_game()
                return      
        self.snake.insert(0, new_head)       
        # Проверяем сбор еды
        points_earned = 0
        
        if new_head == self.food:
            points_earned = 1 * self.score_multiplier
            self.score += points_earned
            self.play_sound(self.eat_sound)
            self.create_food()
        elif self.special_food and new_head == self.special_food:
            points_earned = 5 * self.score_multiplier
            self.score += points_earned
            self.invincible = True
            self.invincible_timer = 5  # 5 секунд неуязвимости
            self.score_multiplier = 2
            self.multiplier_label.text = f'x{self.score_multiplier}'
            self.special_food = None
            self.play_sound(self.eat_sound)
        else:
            self.snake.pop()
        
        self.score_label.text = f'Счет: {self.score}'
        self.draw_snake()
    
    def end_game(self):
        self.game_over = True
        self.game_started = False
        Clock.unschedule(self.update)
        self.play_sound(self.game_over_sound)
        
        # Сохраняем рекорд
        app = App.get_running_app()
        if self.score > app.high_score:
            app.high_score = self.score
            app.save_high_score()
        
        App.get_running_app().show_game_over(self.score)
    
    def on_touch_down(self, touch):
        if not self.game_started or self.game_over:
            return
        
        # Пауза по двойному нажатию
        if touch.is_double_tap:
            self.paused = not self.paused
            return
        
        if self.paused:
            return
        
        head_x, head_y = self.snake[0]
        touch_x, touch_y = touch.pos
        
        dx = touch_x - head_x
        dy = touch_y - head_y
        
        if abs(dx) > abs(dy):
            new_direction = (1 if dx > 0 else -1, 0)
        else:
            new_direction = (0, 1 if dy > 0 else -1)
        
        current_dx, current_dy = self.direction
        new_dx, new_dy = new_direction
        
        if not (current_dx == -new_dx and current_dy == -new_dy):
            self.direction = new_direction

class SnakeApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.high_score = 0
        self.game_speed = 0.2
        self.sound_enabled = True
        self.load_high_score()
    
    def build(self):
        self.root = BoxLayout(orientation='vertical')
        self.show_menu()
        return self.root
    
    def load_high_score(self):
        try:
            if os.path.exists('high_score.json'):
                with open('high_score.json', 'r') as f:
                    data = json.load(f)
                    self.high_score = data.get('high_score', 0)
        except:
            self.high_score = 0    
    def save_high_score(self):
        try:
            with open('high_score.json', 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass    
    def show_menu(self):
        self.root.clear_widgets()
        menu = MainMenu(
            start_callback=self.start_game,
            settings_callback=self.show_settings
        )
        self.root.add_widget(menu)    
    def show_settings(self):
        self.root.clear_widgets()
        settings = SettingsMenu(back_callback=self.show_menu)
        settings.speed_slider.value = self.game_speed
        settings.sound_btn.text = 'ЗВУК: ВКЛ' if self.sound_enabled else 'ЗВУК: ВЫКЛ'
        self.root.add_widget(settings)        
        # Сохраняем настройки при изменении
        def on_speed_change(instance, value):
            self.game_speed = value
        settings.speed_slider.bind(value=on_speed_change)    
    def start_game(self):
        self.root.clear_widgets()
        game = SnakeGame()
        game.start_game()
        self.root.add_widget(game)    
    def show_game_over(self, score):
        self.root.clear_widgets()
        game_over = GameOverScreen(
            score=score,
            high_score=self.high_score,
            restart_callback=self.start_game,
            menu_callback=self.show_menu
        )
        self.root.add_widget(game_over)
if __name__ == '__main__':
    SnakeApp().run()
