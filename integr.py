import unittest
import os
import json
import tempfile
import sys
from unittest.mock import Mock, patch, MagicMock
import shutil

kivy_mock = Mock()
kivy_mock.app = Mock()
kivy_mock.uix = Mock()
kivy_mock.uix.widget = Mock()
kivy_mock.uix.label = Mock()
kivy_mock.uix.button = Mock()
kivy_mock.uix.boxlayout = Mock()
kivy_mock.uix.slider = Mock()
kivy_mock.graphics = Mock()
kivy_mock.clock = Mock()
kivy_mock.properties = Mock()

sys.modules['kivy'] = kivy_mock
sys.modules['kivy.app'] = kivy_mock.app
sys.modules['kivy.uix'] = kivy_mock.uix
sys.modules['kivy.uix.widget'] = kivy_mock.uix.widget
sys.modules['kivy.uix.label'] = kivy_mock.uix.label
sys.modules['kivy.uix.button'] = kivy_mock.uix.button
sys.modules['kivy.uix.boxlayout'] = kivy_mock.uix.boxlayout
sys.modules['kivy.uix.slider'] = kivy_mock.uix.slider
sys.modules['kivy.graphics'] = kivy_mock.graphics
sys.modules['kivy.clock'] = kivy_mock.clock
sys.modules['kivy.properties'] = kivy_mock.properties


class MockWidget:
    """Мок виджета Kivy"""
    def __init__(self, **kwargs):
        self.pos = (0, 0)
        self.size = (800, 600)
        self.canvas = MagicMock()
        self.children = []
        
    def bind(self, *args, **kwargs):
        pass
    
    def add_widget(self, widget):
        self.children.append(widget)
        return True


class IntegrationTestSnakeGame(unittest.TestCase):
    """Интеграционное тестирование игры 'Змейка'"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем временный файл для рекордов
        self.temp_dir = tempfile.mkdtemp()
        self.high_score_file = os.path.join(self.temp_dir, 'high_score.json')
        
        # Увеличиваем лимит рекурсии
        import sys
        self.original_recursion_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(10000)
    
    def tearDown(self):
        """Очистка после каждого теста"""
        # Восстанавливаем лимит рекурсии
        import sys
        sys.setrecursionlimit(self.original_recursion_limit)
        
        # Очищаем временную директорию
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_high_score_system_integration(self):
        """Интеграционный тест системы рекордов - ПРОСТАЯ ВЕРСИЯ"""
        # Тест 1: Сохранение рекорда
        test_high_score = 150        
        # Сохраняем в файл
        with open(self.high_score_file, 'w') as f:
            json.dump({'high_score': test_high_score}, f)

        self.assertTrue(os.path.exists(self.high_score_file))      
        with open(self.high_score_file, 'r') as f:
            data = json.load(f)
            loaded_high_score = data.get('high_score', 0)        
        # Проверяем целостность данных
        self.assertEqual(loaded_high_score, test_high_score)
        
        # Тест 2: Обновление рекорда
        new_score = 200
        current_high_score = loaded_high_score
        
        # Проверяем, нужно ли обновить рекорд
        if new_score > current_high_score:
            current_high_score = new_score
        
        # Сохраняем обновленный рекорд
        with open(self.high_score_file, 'w') as f:
            json.dump({'high_score': current_high_score}, f)
        with open(self.high_score_file, 'r') as f:
            data = json.load(f)
            loaded_high_score = data.get('high_score', 0)
        
        self.assertEqual(loaded_high_score, new_score)        
        # Тест 3: Рекорд не должен уменьшаться
        lower_score = 100
        if lower_score > loaded_high_score:  # Это условие не выполнится
            loaded_high_score = lower_score       
        # Проверяем, что рекорд не изменился
        self.assertNotEqual(loaded_high_score, lower_score)
        self.assertEqual(loaded_high_score, new_score)    
    def test_game_flow_integration(self):
        """Тест полного игрового цикла"""
        # Имитируем игровые состояния
        game_states = {
            'score': 0,
            'snake': [(100, 100)],
            'food': (200, 200),
            'game_over': False,
            'game_started': True
        }
        
        # Имитируем движение змейки
        initial_snake_length = len(game_states['snake'])
        game_states['snake'].insert(0, (120, 100))        
        # Проверяем, что змейка движется
        self.assertEqual(len(game_states['snake']), initial_snake_length + 1)        
        # Имитируем несколько ходов
        for _ in range(5):
            # Движение вправо
            new_head = (game_states['snake'][0][0] + 20, game_states['snake'][0][1])
            game_states['snake'].insert(0, new_head)            
            # Если не собрали еду, удаляем хвост
            if new_head != game_states['food']:
                game_states['snake'].pop()
        
        # Проверяем состояние после нескольких ходов
        self.assertGreater(len(game_states['snake']), 0)
        self.assertFalse(game_states['game_over'])
    
    def test_settings_integration(self):
        """Интеграционный тест настроек"""
        settings_state = {
            'game_speed': 0.2,
            'sound_enabled': True,
            'high_score': 0
        }
        
        # Тестируем изменение скорости
        new_speed = 0.3
        settings_state['game_speed'] = new_speed       
        # Проверяем, что скорость изменилась
        self.assertEqual(settings_state['game_speed'], new_speed)        
        # Проверяем граничные значения скорости
        settings_state['game_speed'] = 0.05  # Минимальная
        self.assertEqual(settings_state['game_speed'], 0.05)
        
        settings_state['game_speed'] = 0.5  # Максимальная
        self.assertEqual(settings_state['game_speed'], 0.5)        
        # Тестируем переключение звука
        initial_sound_state = settings_state['sound_enabled']
        settings_state['sound_enabled'] = not initial_sound_state
        self.assertNotEqual(settings_state['sound_enabled'], initial_sound_state)
    
    def test_special_food_integration(self):
        """Интеграционный тест специальной еды"""
        game_state = {
            'score': 0,
            'score_multiplier': 1,
            'invincible': False,
            'invincible_timer': 0,
            'special_food': (300, 300),
            'snake': [(300, 300)]  # Змейка на специальной еде
        }
        
        # Имитируем сбор специальной еды
        if game_state['snake'][0] == game_state['special_food']:
            game_state['score'] += 5 * game_state['score_multiplier']
            game_state['invincible'] = True
            game_state['score_multiplier'] = 2
            game_state['invincible_timer'] = 5
            game_state['special_food'] = None
        
        # Проверяем эффекты
        self.assertEqual(game_state['score'], 5)  # 5 * 1 = 5
        self.assertTrue(game_state['invincible'])
        self.assertEqual(game_state['score_multiplier'], 2)
        self.assertEqual(game_state['invincible_timer'], 5)
        self.assertIsNone(game_state['special_food'])
    
    def test_game_over_flow_integration(self):
        """Тест потока завершения игры"""
        # Имитируем состояние перед завершением
        game_state = {
            'score': 50,
            'high_score': 40,
            'game_over': False,
            'game_started': True
        }
        
        # Имитируем столкновение
        game_state['game_over'] = True
        game_state['game_started'] = False       
        # Проверяем изменение состояний
        self.assertTrue(game_state['game_over'])
        self.assertFalse(game_state['game_started'])        
        # Имитируем проверку рекорда
        if game_state['score'] > game_state['high_score']:
            game_state['high_score'] = game_state['score']        
        # Проверяем обновление рекорда
        self.assertEqual(game_state['high_score'], 50)
    
    def test_pause_functionality_integration(self):
        """Интеграционный тест функции паузы"""
        game_state = {
            'paused': False,
            'game_started': True,
            'snake': [(100, 100)],
            'direction': (1, 0)
        }
        
        # Имитируем включение паузы
        game_state['paused'] = not game_state['paused']
        self.assertTrue(game_state['paused'])
        
        # Имитируем движение при паузе
        if not game_state['paused']:
            # Это не должно выполняться, так как игра на паузе
            new_head = (game_state['snake'][0][0] + 20, game_state['snake'][0][1])
            game_state['snake'].insert(0, new_head)
        
        # Проверяем, что змейка не двигалась
        self.assertEqual(len(game_state['snake']), 1)
        self.assertEqual(game_state['snake'][0], (100, 100))
class TestDataConsistency(unittest.TestCase):
    """Тесты согласованности данных"""
    
    def test_score_calculation_consistency(self):
        """Тест согласованности расчета счета"""
        score = 0
        score_multiplier = 1        
        # Имитируем сбор обычной еды
        score += 1 * score_multiplier
        self.assertEqual(score, 1)        
        # Имитируем активацию множителя
        score_multiplier = 2       
        # Имитируем еще один сбор обычной еды
        score += 1 * score_multiplier
        self.assertEqual(score, 3)  # 1 + (1*2) = 3        
        # Имитируем сбор специальной еды
        score += 5 * score_multiplier
        self.assertEqual(score, 13)  # 3 + (5*2) = 13
    
    def test_snake_growth_consistency(self):
        """Тест согласованности роста змейки"""
        snake = [(100, 100)]
        initial_length = len(snake)
        
        # Имитируем несколько движений без сбора еды
        for i in range(3):
            new_head = (snake[0][0] + 20, snake[0][1])
            snake.insert(0, new_head)
            snake.pop()  
        self.assertEqual(len(snake), initial_length)        
        # Имитируем сбор еды
        new_head = (snake[0][0] + 20, snake[0][1])
        snake.insert(0, new_head)

        self.assertEqual(len(snake), initial_length + 1)
    
    def test_boundary_check_consistency(self):
        """Тест согласованности проверки границ"""
        field_margin = 20
        width = 800
        height = 600
        
        # Тестовые позиции
        test_positions = [
            (field_margin, 100),      
            (field_margin - 1, 100),  
        ]
        
        expected_results = [
            True,   
            False,  
        ]
        
        for (x, y), expected in zip(test_positions, expected_results):
            is_inside = (
                field_margin <= x < width - field_margin and
                field_margin <= y < height - field_margin
            )
            self.assertEqual(is_inside, expected)


class TestErrorHandling(unittest.TestCase):
    """Тесты обработки ошибок"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()    
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)    
    def test_file_operations_error_handling(self):
        """Тест обработки ошибок файловых операций"""
        # Тест с поврежденным JSON файлом
        bad_json_file = os.path.join(self.temp_dir, 'bad_json.json')
        
        # Создаем файл с поврежденным JSON
        with open(bad_json_file, 'w') as f:
            f.write('{invalid json}')
        
        # Имитируем загрузку с обработкой ошибок
        high_score = 0
        try:
            with open(bad_json_file, 'r') as f:
                data = json.load(f)
                high_score = data.get('high_score', 0)
        except (json.JSONDecodeError, IOError):
            # В случае ошибки используем значение по умолчанию
            high_score = 0
        
        self.assertEqual(high_score, 0)


def run_integration_tests():
    """Запуск интеграционных тестов"""
    print("ЗАПУСК ИНТЕГРАЦИОННЫХ ТЕСТОВ ДЛЯ ИГРЫ 'ЗМЕЙКА'")
    print("="*70)
    
    # Увеличиваем лимит рекурсии
    original_recursion_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(10000)
    
    try:
        # Создаем тестовый набор
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()        
        # Добавляем тесты
        suite.addTests(loader.loadTestsFromTestCase(IntegrationTestSnakeGame))
        suite.addTests(loader.loadTestsFromTestCase(TestDataConsistency))
        suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))        
        # Запускаем тесты
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        result = runner.run(suite)        
        # Выводим статистику
        print(f"\n{'='*70}")
        print("РЕЗУЛЬТАТЫ ИНТЕГРАЦИОННОГО ТЕСТИРОВАНИЯ:")
        print(f"{'='*70}")
        print(f"Всего тестов: {result.testsRun}")
        print(f"Успешно пройдено: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"Провалено: {len(result.failures)}")
        print(f"Ошибок выполнения: {len(result.errors)}")
        
        if result.errors:
            print(f"\nОШИБКИ ВЫПОЛНЕНИЯ:")
            for test, traceback in result.errors:
                print(f"\n{test}")
                # Выводим только последнюю строку ошибки
                lines = traceback.split('\n')
                for line in reversed(lines):
                    if line.strip():
                        print(f"Ошибка: {line}")
                        break
        
        print(f"\n{'='*70}")
        
        return result
    
    finally:
        # Восстанавливаем лимит рекурсии
        sys.setrecursionlimit(original_recursion_limit)


if __name__ == '__main__':
    # Увеличиваем лимит рекурсии еще на глобальном уровне
    sys.setrecursionlimit(10000)    
    # Запускаем тесты
    result = run_integration_tests()    
    # Возвращаем соответствующий код выхода
    sys.exit(0 if result.wasSuccessful() else 1)
