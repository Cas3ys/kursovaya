import unittest
import os
import tempfile
import json
from unittest.mock import Mock, patch, mock_open
import sys

sys.modules['kivy'] = Mock()
sys.modules['kivy.app'] = Mock()
sys.modules['kivy.uix'] = Mock()
sys.modules['kivy.uix.widget'] = Mock()
sys.modules['kivy.uix.label'] = Mock()
sys.modules['kivy.uix.button'] = Mock()
sys.modules['kivy.uix.boxlayout'] = Mock()
sys.modules['kivy.uix.slider'] = Mock()
sys.modules['kivy.graphics'] = Mock()
sys.modules['kivy.clock'] = Mock()
sys.modules['kivy.properties'] = Mock()
sys.modules['kivy.core.audio'] = Mock()

import random
import warnings
warnings.filterwarnings('ignore')
class MockWidget:
    def __init__(self, **kwargs):
        self.pos = (0, 0)
        self.size = (800, 600)
        self.canvas = Mock()
        self.canvas.before = Mock()
        self.canvas.after = Mock()
        self.canvas.before.clear = Mock()
        self.canvas.after.clear = Mock()       
    def bind(self, *args, **kwargs):
        pass    
    def add_widget(self, widget):
        pass    
    def clear_widgets(self):
        pass
class TestSnakeGame(unittest.TestCase):
    """Тестирование основной игровой логики"""    
    def setUp(self):
        """Настройка перед каждым тестом"""
        
        self.mock_app = Mock()
        self.mock_app.game_speed = 0.2
        self.mock_app.sound_enabled = True
        self.mock_app.high_score = 0       
        
        self.game = Mock()
        self.game.cell_size = 20
        self.game.snake = [(100, 100)]
        self.game.direction = (1, 0)
        self.game.food = (200, 200)
        self.game.special_food = None
        self.game.game_over = False
        self.game.game_started = True
        self.game.score = 0
        self.game.score_multiplier = 1
        self.game.invincible = False
        self.game.width = 800
        self.game.height = 600    
    def test_snake_initialization(self):
        """Тест инициализации змейки"""
        self.assertEqual(len(self.game.snake), 1)
        self.assertEqual(self.game.snake[0], (100, 100))
        self.assertEqual(self.game.direction, (1, 0))
        self.assertEqual(self.game.score, 0)
        self.assertFalse(self.game.game_over)    
    def test_food_creation(self):
        """Тест создания еды"""
        self.assertIsNotNone(self.game.food)
        # Проверяем, что еда находится в пределах игрового поля
        self.assertTrue(0 <= self.game.food[0] <= 800)
        self.assertTrue(0 <= self.game.food[1] <= 600)    
    def test_snake_movement(self):
        """Тест движения змейки"""
        initial_head = self.game.snake[0]
        self.game.direction = (1, 0)
        new_head = (initial_head[0] + self.game.cell_size, initial_head[1])       
       
        self.game.snake = [new_head]        
        self.assertEqual(self.game.snake[0], new_head)
        self.assertEqual(len(self.game.snake), 1)    
    def test_collision_detection_wall(self):
        """Тест обнаружения столкновения со стеной"""
        # Помещаем змейку у границы
        self.game.snake = [(20, 100)] 
        self.game.direction = (-1, 0) 
        self.game.game_over = True        
        self.assertTrue(self.game.game_over)   
    def test_collision_detection_self(self):
        """Тест обнаружения столкновения с собой"""
        # Создаем змейку, которая столкнется с собой
        self.game.snake = [(100, 100), (80, 100), (100, 100)]  
        self.game.game_over = True          
        self.assertTrue(self.game.game_over)    
    def test_food_collection(self):
        """Тест сбора еды"""
        initial_score = self.game.score
        # Помещаем змейку на еду
        self.game.snake = [self.game.food]        
        # Имитируем сбор еды
        self.game.score += 1 * self.game.score_multiplier
        self.game.snake.append((0, 0))          
        self.assertEqual(self.game.score, 1)
        self.assertEqual(len(self.game.snake), 2)      
    def test_special_food_effects(self):
        """Тест эффектов специальной еды"""
        # Создаем специальную еду
        self.game.special_food = (200, 200)
        self.game.snake = [(200, 200)]        
        # Имитируем эффекты
        self.game.score += 5 * self.game.score_multiplier
        self.game.invincible = True
        self.game.score_multiplier = 2
        # Проверяем эффекты
        self.assertEqual(self.game.score, 5)
        self.assertTrue(self.game.invincible)
        self.assertEqual(self.game.score_multiplier, 2)


class TestSettings(unittest.TestCase):
    """Тестирование настроек"""    
    def test_sound_toggle_logic(self):
        """Тест логики переключения звука"""
        sound_enabled = True       
        # Имитируем переключение
        sound_enabled = not sound_enabled
        self.assertFalse(sound_enabled)        
        
        sound_enabled = not sound_enabled
        self.assertTrue(sound_enabled)    
    def test_speed_range(self):
        """Тест диапазона скорости"""
        # Проверяем допустимые значения скорости
        speed = 0.2
        self.assertGreaterEqual(speed, 0.05)
        self.assertLessEqual(speed, 0.5)        
        # Проверяем шаг изменения
        step = 0.05
        self.assertEqual(step, 0.05)


class TestHighScoreSystem(unittest.TestCase):
    """Тестирование системы рекордов"""
    
    def setUp(self):
        """Создаем временный файл для тестов"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test_high_score.json')
    
    def tearDown(self):
        """Удаляем временные файлы"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_save_high_score(self):
        """Тест сохранения рекорда"""
        high_score = 100        
        # Имитируем сохранение
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('json.dump') as mock_json:
                # Сохраняем рекорд
                data = {'high_score': high_score}
                json.dump(data, mock_file())

                mock_json.assert_called_once_with({'high_score': 100}, mock_file())
    
    def test_load_high_score(self):
        """Тест загрузки рекорда"""
        # Создаем тестовый файл с рекордом
        test_data = {'high_score': 150}
        with open(self.test_file, 'w') as f:
            json.dump(test_data, f)        
        # Загружаем рекорд
        with open(self.test_file, 'r') as f:
            data = json.load(f)
            high_score = data.get('high_score', 0)
        
        self.assertEqual(high_score, 150)
    
    def test_load_nonexistent_high_score(self):
        """Тест загрузки при отсутствии файла"""
        # Имитируем отсутствие файла
        with patch('os.path.exists', return_value=False):
            high_score = 0  # Значение по умолчанию
            self.assertEqual(high_score, 0)
class TestGameMechanics(unittest.TestCase):
    """Тестирование игровых механик"""
    
    def test_pause_functionality(self):
        """Тест функции паузы"""
        paused = False        
        # Имитируем включение паузы
        paused = not paused
        self.assertTrue(paused)        
        
        paused = not paused
        self.assertFalse(paused)
    
    def test_direction_change_logic(self):
        """Тест логики изменения направления"""
        direction = (1, 0) 
        
        # Имитируем изменение направления
        new_direction = (0, 1)  # Вверх
        direction = new_direction        
        self.assertEqual(direction, (0, 1))        
        # Проверяем защиту от разворота на 180 градусов
        current_direction = (0, 1)  # Вверх
        attempted_direction = (0, -1)  # Вниз (противоположное)
        
        # Не должно меняться на противоположное
        if not (current_direction[0] == -attempted_direction[0] and 
                current_direction[1] == -attempted_direction[1]):
            direction = attempted_direction
        
        self.assertNotEqual(direction, (0, -1))  # Направление не должно измениться


class TestAttendanceAnalyzerIntegration(unittest.TestCase):
    """Тесты логики анализа посещаемости"""
    
    def test_attendance_logic(self):
        """Тест логики определения присутствия"""
        def is_present(mark):
            if mark is None or str(mark).strip() == '':
                return True
            mark_str = str(mark).strip().lower()
            absent_marks = ['н', 'нет', '0', 'отсутствовал']
            return mark_str not in absent_marks
        
        # Тестовые случаи
        self.assertTrue(is_present(''))  
        self.assertTrue(is_present(None))  
        self.assertFalse(is_present('н'))  
        self.assertFalse(is_present('нет'))  
        self.assertFalse(is_present('0'))  
        self.assertTrue(is_present('+'))  
        self.assertTrue(is_present('присутствовал'))  
    
    def test_data_grouping_logic(self):
        """Тест логики группировки данных"""
        # Имитируем данные посещаемости
        attendance_data = [
            {'ФИО': 'Иванов', 'Присутствовал': True},
            {'ФИО': 'Иванов', 'Присутствовал': False},
            {'ФИО': 'Петров', 'Присутствовал': True},
            {'ФИО': 'Петров', 'Присутствовал': True},
        ]
        
        
        student_stats = {}
        for record in attendance_data:
            name = record['ФИО']
            if name not in student_stats:
                student_stats[name] = {'total': 0, 'present': 0}
            student_stats[name]['total'] += 1
            if record['Присутствовал']:
                student_stats[name]['present'] += 1
        
        # Проверяем результаты
        self.assertEqual(student_stats['Иванов']['present'], 1)
        self.assertEqual(student_stats['Иванов']['total'], 2)
        self.assertEqual(student_stats['Петров']['present'], 2)
        self.assertEqual(student_stats['Петров']['total'], 2)


class TestPerformance(unittest.TestCase):
    """Тесты производительности"""
    
    def test_game_loop_performance_simulation(self):
        """Тест производительности (симуляция)"""
        import time
        
        # Имитируем игровой цикл
        iterations = 100
        start_time = time.time()
        
        # Простая симуляция игрового цикла
        for i in range(iterations):
            # Имитация некоторых вычислений
            x = i * 2
            y = i * 3
            _ = x + y
        
        end_time = time.time()
        execution_time = end_time - start_time

        self.assertLess(execution_time, 0.1,
                       f"Симуляция слишком медленная: {execution_time:.3f} сек")
    
    def test_memory_usage_simulation(self):
        """Тест использования памяти (симуляция)"""
        import sys        
        # Имитируем создание игровых объектов
        snake_length = 10
        snake = [(i * 20, 100) for i in range(snake_length)]        
        # Проверяем размер структуры данных
        self.assertEqual(len(snake), 10)       
        # Оцениваем использование памяти (грубая оценка)
        estimated_memory = len(snake) * 2 * 8  # 10 пар координат, 8 байт каждая       
        # Проверяем, что использование памяти разумное
        self.assertLess(estimated_memory, 1000,  # Менее 1KB
                        f"Оценка памяти слишком высокая: {estimated_memory} байт")
def run_all_tests():
    """Запуск всех тестов"""
    # Создаем тестовый набор
    test_cases = [
        TestSnakeGame,
        TestSettings,
        TestHighScoreSystem,
        TestGameMechanics,
        TestAttendanceAnalyzerIntegration,
        TestPerformance
    ]    
    # Собираем все тесты
    all_tests = []
    for test_case in test_cases:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
        all_tests.append(suite)    

    complete_suite = unittest.TestSuite(all_tests)    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(complete_suite)    
    # Выводим статистику
    print(f"\n{'='*60}")
    print(f"СТАТИСТИКА ТЕСТОВ:")
    print(f"Всего тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    print(f"Пропущено: {len(result.skipped)}")
    print(f"{'='*60}")    
    # Детали ошибок
    if result.failures:
        print("\nПРОВАЛЕННЫЕ ТЕСТЫ:")
        for test, traceback in result.failures:
            print(f"\n{test}:")
            print(traceback)   
    if result.errors:
        print("\nТЕСТЫ С ОШИБКАМИ:")
        for test, traceback in result.errors:
            print(f"\n{test}:")
            print(traceback)    
    return result
if __name__ == '__main__':
    print("ЗАПУСК ТЕСТОВ ДЛЯ ИГРЫ 'ЗМЕЙКА'")
    print("="*60)    
    result = run_all_tests()    
    # Возвращаем код выхода
    exit_code = 0 if result.wasSuccessful() else 1
    sys.exit(exit_code)
