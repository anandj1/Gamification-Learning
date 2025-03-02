import pygame
import random
import sys
import time
from pygame.locals import *

# Game Configuration
WIDTH, HEIGHT = 1200, 800
FPS = 60
COLORS = {
    'background': (20, 25, 50),
    'text': (255, 255, 255),
    'correct': (50, 205, 50),
    'wrong': (220, 20, 60),
    'button': (30, 40, 120),
    'streak': (255, 215, 0),
    'powerup': (0, 255, 255),
    'nebula': (90, 40, 150),
    'shield': (0, 150, 255)
}

class AIDifficultyManager:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.history = []
        self.difficulty = 1
        self.streak_factor = 1.0
        self.response_times = []
        
    def update_difficulty(self, correct, response_time):
        self.history.append(correct)
        self.response_times.append(response_time)
        
        if len(self.history) > 5:
            self.history.pop(0)
            self.response_times.pop(0)
            
        success_rate = sum(self.history) / len(self.history) if self.history else 0.5
        avg_response = sum(self.response_times) / len(self.response_times) if self.response_times else 10
        time_factor = max(0, 1 - (avg_response / 15))
        
        adjustment = (success_rate - 0.5) + (time_factor * 0.5)
        self.difficulty = min(3, max(1, round(self.difficulty + adjustment)))
        return self.difficulty

class GameState:
    def __init__(self, quiz_game):
        self.quiz_game = quiz_game
        self.reset()
        
    def reset(self):
        self.score = 0
        self.lives = 3
        self.streak = 0
        self.multiplier = 1
        self.shields = 0
        self.active_powerups = {}
        self.questions_answered = 0
        self.difficulty_manager = AIDifficultyManager()
        self.game_active = True
        self.current_question = self.quiz_game.get_question()
        self.question_start_time = time.time()

class QuizGame:
    def __init__(self):
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("SQL Nebula Challenge")
            self.clock = pygame.time.Clock()
            self.font = pygame.font.Font(None, 36)
            self.title_font = pygame.font.Font(None, 72)
            self.button_font = pygame.font.Font(None, 28)
            self.questions = self.load_questions()
            self.state = None
            self.running = False
            self.option_rects = []  # Initialize the list for option buttons
        except Exception as e:
            print(f"Initialization error: {e}")
            self.quit_game()

    def load_questions(self):
        base_questions = [
            # Difficulty 1
            {
                "difficulty": 1,
                "question": "Which SQL command retrieves data?",
                "options": ["INSERT", "EXECUTE", "UPDATE", "SELECT"],
                "correct": 3
            },
            {
                "difficulty": 1,
                "question": "Default MySQL port?",
                "options": ["1433", "8080", "3306", "1521"],
                "correct": 2
            },
            {
                "difficulty": 1,
                "question": "Which clause filters results?",
                "options": ["FIND", "WHERE", "SEARCH", "FILTER"],
                "correct": 1
            },
            {
                "difficulty": 1,
                "question": "What does DML stand for?",
                "options": ["Database Management Layer", "Digital Media Layer", "Data Markup Language", "Data Manipulation Language"],
                "correct": 3
            },
            {
                "difficulty": 1,
                "question": "Which keyword is used to sort results?",
                "options": ["FILTER BY", "ORDER BY", "GROUP BY", "SORT BY"],
                "correct": 1
            },
            # Difficulty 2
            {
                "difficulty": 2,
                "question": "Which MySQL engine supports transactions?",
                "options": ["Memory", "InnoDB", "CSV", "MyISAM"],
                "correct": 1
            },
            {
                "difficulty": 2,
                "question": "Which command improves query performance?",
                "options": ["BOOST", "FAST", "QUICK", "INDEX"],
                "correct": 3
            },
            {
                "difficulty": 2,
                "question": "What does ACID stand for?",
                "options": ["Atomicity, Consistency, Isolation, Durability", "Aggregation, Constraints, Indexes, Data", "Automation, Concurrency, Isolation, Data", "Accuracy, Consistency, Integrity, Duration"],
                "correct": 0
            },
            {
                "difficulty": 2,
                "question": "Which operator checks for NULL?",
                "options": ["HAS NULL", "IS NULL", "= NULL", "EQUALS NULL"],
                "correct": 1
            },
            {
                "difficulty": 2,
                "question": "Which function counts rows?",
                "options": ["TOTAL()", "AMOUNT()", "COUNT()", "SUM()"],
                "correct": 2
            },
            # Difficulty 3
            {
                "difficulty": 3,
                "question": "Which JOIN returns all records?",
                "options": ["RIGHT JOIN", "INNER JOIN", "FULL JOIN", "LEFT JOIN"],
                "correct": 2
            },
            {
                "difficulty": 3,
                "question": "What's MySQL's query cache?",
                "options": ["Cached SELECT results", "Connection pool", "Query history", "Index cache"],
                "correct": 0
            },
            {
                "difficulty": 3,
                "question": "What does MyISAM support that InnoDB doesn't?",
                "options": ["Row-level locking", "Foreign keys", "Full-text search", "Transactions"],
                "correct": 2
            },
            {
                "difficulty": 3,
                "question": "What is a MySQL view?",
                "options": ["Backup file", "Virtual table", "Index type", "Storage engine"],
                "correct": 1
            },
            {
                "difficulty": 3,
                "question": "Which is a JSON function?",
                "options": ["GET_JSON()", "JSON_READ()", "JSON_EXTRACT()", "PARSE_JSON()"],
                "correct": 2
            },
            {
                "difficulty": 1,
                "question": "Default MySQL superuser?",
                "options": ["administrator", "root", "admin", "superuser"],
                "correct": 1
            },
            {
                "difficulty": 2,
                "question": "Purpose of ZEROFILL?",
                "options": ["Fill empty strings", "Replace NULL", "Left-pad numbers", "Fill deleted data"],
                "correct": 2
            },
            {
                "difficulty": 1,
                "question": "Create database command?",
                "options": ["NEW DATABASE", "MAKE DATABASE", "CREATE DATABASE", "BUILD DATABASE"],
                "correct": 2
            },
            {
                "difficulty": 3,
                "question": "Which is spatial data type?",
                "options": ["GEO", "COORDINATE", "POINT", "LOCATION"],
                "correct": 2
            },
            {
                "difficulty": 2,
                "question": "Which is boolean literal?",
                "options": ["VALID", "YES", "TRUE", "ON"],
                "correct": 2
            },
            {
                "difficulty": 3,
                "question": "What does GIL stand for?",
                "options": ["General Input Layer", "Global Interpreter Lock", "Graphical Interface Layer", "Generic Index Library"],
                "correct": 1
            },
            {
                "difficulty": 2,
                "question": "Which command deletes a table?",
                "options": ["ERASE TABLE", "DROP TABLE", "DELETE TABLE", "REMOVE TABLE"],
                "correct": 1
            },
            {
                "difficulty": 1,
                "question": "Which command adds a new row?",
                "options": ["ADD", "UPDATE", "INSERT", "CREATE"],
                "correct": 2
            },
            {
                "difficulty": 3,
                "question": "What is a stored procedure?",
                "options": ["A backup method", "Precompiled SQL code", "A user role", "A table type"],
                "correct": 1
            },
            {
                "difficulty": 2,
                "question": "Which command modifies a table?",
                "options": ["ALTER TABLE", "UPDATE TABLE", "CHANGE TABLE", "MODIFY TABLE"],
                "correct": 0
            }
        ]
        
        # Process questions to randomize options
        processed_questions = []
        for q in base_questions:
            options = q["options"].copy()
            # Get the correct answer text from the original list
            correct_option = q["options"][q["correct"]]
            random.shuffle(options)
            
            processed_questions.append({
                "difficulty": q["difficulty"],
                "question": q["question"],
                "options": options,
                "correct": options.index(correct_option)
            })
            
        return processed_questions

    def get_question(self):
        if not self.state: 
            return random.choice(self.questions)
        pool = [q for q in self.questions if q['difficulty'] == self.state.difficulty_manager.difficulty]
        return random.choice(pool) if pool else random.choice(self.questions)

    def draw_button(self, text, rect, color=COLORS['button']):
        pygame.draw.rect(self.screen, color, rect, border_radius=15)
        text_surf = self.button_font.render(text, True, COLORS['text'])
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
        return rect

    def check_answer(self, selected_index):
        if not self.state.game_active:
            return
            
        response_time = time.time() - self.state.question_start_time
        correct = selected_index == self.state.current_question['correct']
        
        if correct:
            self.state.score += int(10 * self.state.multiplier)
            self.state.streak += 1
            
            if self.state.streak % 5 == 0:
                self.state.shields += 1
            if self.state.streak % 3 == 0:
                self.state.multiplier += 0.5
        else:
            self.state.score = max(0, self.state.score - 5)
            if self.state.shields > 0:
                self.state.shields -= 1
            else:
                self.state.lives -= 1
                self.state.streak = 0
                self.state.multiplier = 1

        self.state.difficulty_manager.update_difficulty(correct, response_time)
        self.state.questions_answered += 1
        self.state.current_question = self.get_question()
        self.state.question_start_time = time.time()

        if self.state.lives <= 0:
            self.state.game_active = False

    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.title_font.render("GAME OVER", True, COLORS['wrong'])
        self.screen.blit(game_over_text, (WIDTH//2 - 180, HEIGHT//2 - 100))
        
        final_score = self.font.render(f"Final Score: {self.state.score}", True, COLORS['text'])
        self.screen.blit(final_score, (WIDTH//2 - 100, HEIGHT//2))
        
        retry_rect = self.draw_button("Retry", pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 50, 300, 60))
        quit_rect = self.draw_button("Quit", pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 130, 300, 60))
        return retry_rect, quit_rect

    def game_loop(self):
        self.state = GameState(self)
        self.running = True
        while self.running:
            try:
                self.clock.tick(FPS)
                self.screen.fill(COLORS['background'])
                
                # Process events
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.quit_game()
                    if event.type == MOUSEBUTTONDOWN:
                        if self.state.game_active:
                            for i, rect in enumerate(self.option_rects):
                                if rect.collidepoint(event.pos):
                                    self.check_answer(i)
                        else:
                            retry_rect, quit_rect = self.draw_game_over()
                            if retry_rect.collidepoint(event.pos):
                                self.state.reset()
                            if quit_rect.collidepoint(event.pos):
                                self.quit_game()

                if self.state.game_active:
                    # Draw background elements
                    for _ in range(3):
                        x = random.randint(0, WIDTH)
                        y = random.randint(0, HEIGHT)
                        pygame.draw.circle(self.screen, COLORS['nebula'], (x, y), random.randint(1, 3))

                    # Draw score
                    score_text = self.font.render(f"SCORE: {self.state.score}", True, COLORS['text'])
                    self.screen.blit(score_text, (20, 20))
                    
                    # Draw lives
                    for i in range(self.state.lives):
                        pos = (WIDTH - 120 + i * 40, 40)
                        pygame.draw.circle(self.screen, (255, 50, 50), pos, 15)

                    # Draw question
                    question_text = self.font.render(self.state.current_question['question'], True, COLORS['text'])
                    self.screen.blit(question_text, (100, 150))

                    # Draw options and store their rectangles
                    self.option_rects = []
                    y_offset = 300
                    for option in self.state.current_question['options']:
                        rect = self.draw_button(option, pygame.Rect(200, y_offset, WIDTH - 400, 60))
                        self.option_rects.append(rect)
                        y_offset += 80
                else:
                    self.draw_game_over()

                pygame.display.flip()
            except Exception as e:
                print(f"Error in game loop: {e}")
                self.running = False

    def main_menu(self):
        self.running = True
        while self.running:
            try:
                self.screen.fill(COLORS['background'])
                title = self.title_font.render("SQL Nebula", True, COLORS['text'])
                self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
                play_rect = self.draw_button("Start Mission", pygame.Rect(WIDTH // 2 - 150, 300, 300, 60))
                quit_rect = self.draw_button("Exit", pygame.Rect(WIDTH // 2 - 150, 400, 300, 60))
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.quit_game()
                    if event.type == MOUSEBUTTONDOWN:
                        if play_rect.collidepoint(event.pos):
                            self.game_loop()
                        if quit_rect.collidepoint(event.pos):
                            self.quit_game()
                pygame.display.flip()
            except Exception as e:
                print(f"Error in main menu: {e}")
                self.running = False

    def quit_game(self):
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = QuizGame()
    game.main_menu()