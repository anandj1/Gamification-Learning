import pygame
import random
import datetime
import MySQLdb
from sklearn.tree import DecisionTreeClassifier

# Database connection
db = MySQLdb.connect("localhost", "root", "Radhey9922", "gamification")
con = db.cursor()

# Authentication
uname = input('Enter your username: ')
upass = input('Enter your password: ')

con.execute(f"SELECT * FROM profiles WHERE username = '{uname}' AND password = '{upass}'")
get_profile = con.fetchone()

if get_profile:
    profile_id = get_profile[0]
    con.execute(f"SELECT * FROM students WHERE profile_id = '{profile_id}'")
    get_student = con.fetchone()
    student_id = get_student[0]
    con.execute(f"SELECT coin FROM student_coins WHERE profile_id = '{profile_id}'")
    get_coins = con.fetchone()
    all_coins = get_coins[0]

    # AI Difficulty Manager
    class AIDifficultyManager:
        def __init__(self):
            self.difficulty = 2  # Start with medium
            self.history = []
            
        def update_difficulty(self, correct):
            self.history.append(correct)
            if len(self.history) > 5:
                self.history.pop(0)
                
            success_rate = sum(self.history)/len(self.history) if self.history else 0.5
            if success_rate > 0.7:
                self.difficulty = min(3, self.difficulty + 1)
            elif success_rate < 0.3:
                self.difficulty = max(1, self.difficulty - 1)
            return self.difficulty

    # Pygame initialization
    pygame.init()
    WIDTH, HEIGHT = 1000, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Code Master: AI Coding Challenge")
    clock = pygame.time.Clock()

    # UI Constants
    COLORS = {
        'background': (245, 245, 245),
        'header': (70, 130, 180),
        'text': (40, 40, 40),
        'correct': (50, 205, 50),
        'wrong': (220, 20, 60),
        'button': (100, 149, 237),
        'button_hover': (65, 105, 225)
    }

    FONT_REGULAR = pygame.font.Font(None, 32)
    FONT_HEADER = pygame.font.Font(None, 40)
    FONT_BUTTON = pygame.font.Font(None, 28)

    # Layout Dimensions
    HEADER_HEIGHT = 80
    QUESTION_HEIGHT = 180
    OPTION_HEIGHT = 80
    OPTION_SPACING = 15
    OPTION_WIDTH = WIDTH - 100
    MAX_VISIBLE_OPTIONS = 4

    def draw_wrapped_text(surface, text, color, rect, font):
        words = text.split(' ')
        lines = []
        current_line = []
        width = 0
        
        for word in words:
            word_surface = font.render(word, True, color)
            word_width = word_surface.get_width()
            
            if width + word_width < rect.width:
                current_line.append(word)
                width += word_width + font.size(' ')[0]
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                width = word_width
                
        lines.append(' '.join(current_line))
        y = rect.top
        
        for line in lines:
            text_surface = font.render(line, True, color)
            surface.blit(text_surface, (rect.left, y))
            y += font.get_linesize()

    def draw_header(elapsed):
        pygame.draw.rect(screen, COLORS['header'], (0, 0, WIDTH, HEADER_HEIGHT))
        score_text = FONT_HEADER.render(f"Score: {score}", True, COLORS['text'])
        screen.blit(score_text, (20, (HEADER_HEIGHT - score_text.get_height())//2))
        time_text = FONT_HEADER.render(f"Time: {max(0, game_time_limit - elapsed)}s", True, COLORS['text'])
        screen.blit(time_text, (WIDTH - time_text.get_width() - 20, (HEADER_HEIGHT - time_text.get_height())//2))

    def draw_question(question):
        question_rect = pygame.Rect(30, HEADER_HEIGHT + 20, WIDTH-60, QUESTION_HEIGHT)
        pygame.draw.rect(screen, (255, 255, 255), question_rect, 0, 10)
        draw_wrapped_text(screen, question['question'], COLORS['text'], question_rect.inflate(-30, -30), FONT_REGULAR)

    def draw_options(options, mouse_pos):
        option_rects = []
        start_y = HEADER_HEIGHT + QUESTION_HEIGHT + 30 - scroll_offset
        
        for i, option in enumerate(options):
            rect = pygame.Rect(50, start_y + i*(OPTION_HEIGHT + OPTION_SPACING), OPTION_WIDTH, OPTION_HEIGHT)
            color = COLORS['button_hover'] if rect.collidepoint(mouse_pos) else COLORS['button']
            pygame.draw.rect(screen, color, rect, 0, 10)
            draw_wrapped_text(screen, option, COLORS['text'], rect.inflate(-30, -30), FONT_BUTTON)
            option_rects.append(rect)
            
        # Scrollbar
        if len(options) > MAX_VISIBLE_OPTIONS:
            scroll_area_height = HEIGHT - HEADER_HEIGHT - QUESTION_HEIGHT - 60
            scrollbar_height = scroll_area_height * (MAX_VISIBLE_OPTIONS / len(options))
            scroll_pos = (scroll_offset / ((len(options) - MAX_VISIBLE_OPTIONS) * (OPTION_HEIGHT + OPTION_SPACING))) * (scroll_area_height - scrollbar_height)
            
            pygame.draw.rect(screen, COLORS['button'], (WIDTH-20, HEADER_HEIGHT + QUESTION_HEIGHT + 30, 10, scroll_area_height))
            pygame.draw.rect(screen, COLORS['button_hover'], (WIDTH-20, HEADER_HEIGHT + QUESTION_HEIGHT + 30 + scroll_pos, 10, scrollbar_height))
            
        return option_rects

    # Game state initialization
    ai_manager = AIDifficultyManager()
    game_time_limit = 60
    start_time = datetime.datetime.now()
    motivation_messages = ["Keep trying!", "You're learning!", "Almost there!", "Try again!"]
    asked_questions = {1: [], 2: [], 3: []}
    score = 0
    scroll_offset = 0

    # All original questions
    mcq_questions = [
    {
        "difficulty": 1,
        "question": "Which is the correct for loop syntax in Python?",
        "options": [
            "loop i in 10",
            "for i in range(10)",
            "for (i=0; i<10; i++)",
            "for i in range(10):"
        ],
        "correct": 3,
        "hint": "Remember, Python uses a colon ':' at the end of the for loop statement."
    },
    {
        "difficulty": 1,
        "question": "How do you print text to the console in Python?",
        "options": [
            "echo 'Hello'",
            "System.out.print('Hello')",
            "console.log('Hello')",
            "print('Hello')"
        ],
        "correct": 3,
        "hint": "Python uses the print() function."
    },
    {
        "difficulty": 1,
        "question": "How do you write a single-line comment in Python?",
        "options": [
            "/* This is a comment */",
            "// This is a comment",
            "# This is a comment",
            "<!-- This is a comment -->"
        ],
        "correct": 2,
        "hint": "Python uses the '#' symbol for single-line comments."
    },
    {
        "difficulty": 1,
        "question": "Which symbol is used for assignment in Python?",
        "options": [
            "==",
            "=>",
            "=",
            ":="
        ],
        "correct": 2,
        "hint": "Assignment in Python uses the '=' symbol."
    },
    {
        "difficulty": 1,
        "question": "Which operator is used for exponentiation in Python?",
        "options": [
            "*^",
            "**",
            "%",
            "^"
        ],
        "correct": 1,
        "hint": "Exponentiation in Python uses '**'."
    },
    {
        "difficulty": 1,
        "question": "How do you create a list in Python?",
        "options": [
            "{1, 2, 3}",
            "<1, 2, 3>",
            "[1, 2, 3]",
            "(1, 2, 3)"
        ],
        "correct": 2,
        "hint": "Lists in Python are denoted by square brackets []."
    },
    {
        "difficulty": 1,
        "question": "How do you create a tuple in Python?",
        "options": [
            "<1, 2, 3>",
            "[1, 2, 3]",
            "{1, 2, 3}",
            "(1, 2, 3)"
        ],
        "correct": 3,
        "hint": "Tuples in Python are created using parentheses."
    },
    {
        "difficulty": 1,
        "question": "Which keyword is used to begin a conditional statement in Python?",
        "options": [
            "cond",
            "when",
            "if",
            "switch"
        ],
        "correct": 2,
        "hint": "Python uses 'if' to start a conditional block."
    },
    {
        "difficulty": 2,
        "question": "How do you read a file in Python?",
        "options": [
            "read_file('file.txt')",
            "file.open('r')",
            "with open('file.txt', 'r') as f:",
            "open('file.txt', 'read')"
        ],
        "correct": 2,
        "hint": "Using the 'with' statement is the recommended way to read files in Python."
    },
    {
        "difficulty": 2,
        "question": "Which method is used to add an item to the end of a list in Python?",
        "options": [
            "push()",
            "insert()",
            "append()",
            "add()"
        ],
        "correct": 2,
        "hint": "The list method append() adds an item at the end."
    },
    {
        "difficulty": 2,
        "question": "How do you handle exceptions in Python?",
        "options": [
            "do/catch",
            "try/catch",
            "try/except",
            "if/else"
        ],
        "correct": 2,
        "hint": "Python uses try/except blocks to handle exceptions."
    },
    {
        "difficulty": 2,
        "question": "Which keyword is used to define a function in Python?",
        "options": [
            "def",
            "lambda",
            "function",
            "func"
        ],
        "correct": 0,
        "hint": "Python uses 'def' to define a function."
    },
    {
        "difficulty": 2,
        "question": "Which method is used to remove an item from a list by value?",
        "options": [
            "discard()",
            "remove()",
            "delete()",
            "pop()"
        ],
        "correct": 1,
        "hint": "Use remove() to eliminate an item by its value."
    },
    {
        "difficulty": 2,
        "question": "How do you convert the string '123' into an integer?",
        "options": [
            "eval('123')",
            "float('123')",
            "int('123')",
            "str('123')"
        ],
        "correct": 2,
        "hint": "The int() function converts a string to an integer."
    },
    {
        "difficulty": 2,
        "question": "What is the output of len('hello')?",
        "options": [
            "Error",
            "4",
            "5",
            "6"
        ],
        "correct": 2,
        "hint": "len() returns the number of characters in a string."
    },
    {
        "difficulty": 2,
        "question": "How do you slice a list to get its first three elements?",
        "options": [
            "list[:3]",
            "None of the above",
            "Both are correct",
            "list[0:3]"
        ],
        "correct": 2,
        "hint": "Both list[:3] and list[0:3] yield the first three elements."
    },
    {
        "difficulty": 3,
        "question": "What is a decorator in Python?",
        "options": [
            "A comment that describes a function",
            "A loop structure for iterating over data",
            "A function that modifies another function's behavior using the '@' symbol",
            "A built-in method for sorting lists"
        ],
        "correct": 2,
        "hint": "Decorators are used to modify the behavior of functions via the '@' symbol."
    },
    {
        "difficulty": 3,
        "question": "Which of the following best describes the purpose of Python's context managers?",
        "options": [
            "They optimize memory usage through garbage collection.",
            "They automatically manage resources, ensuring proper acquisition and release.",
            "They help in multi-threading by managing locks.",
            "They are used for creating decorators."
        ],
        "correct": 1,
        "hint": "Context managers automatically manage resources (like file streams)."
    },
    {
        "difficulty": 3,
        "question": "What is the main difference between a shallow copy and a deep copy in Python?",
        "options": [
            "A shallow copy is used for immutable objects, while a deep copy is for mutable objects.",
            "A shallow copy recursively copies all objects, while a deep copy only copies references.",
            "A shallow copy copies object references, while a deep copy recursively copies all objects.",
            "There is no difference between shallow and deep copies."
        ],
        "correct": 2,
        "hint": "A shallow copy copies references; a deep copy creates new copies of nested objects."
    },
    {
        "difficulty": 3,
        "question": "Which built-in module in Python is used for regular expressions?",
        "options": [
            "re",
            "regexp",
            "regex",
            "pyregex"
        ],
        "correct": 0,
        "hint": "The 're' module is used for regular expressions in Python."
    },
    {
        "difficulty": 3,
        "question": "What does the 'yield' keyword do in a Python function?",
        "options": [
            "Starts a coroutine",
            "Creates a generator",
            "Returns a value and exits",
            "Terminates a loop"
        ],
        "correct": 1,
        "hint": "The 'yield' keyword turns a function into a generator."
    },
    {
        "difficulty": 3,
        "question": "What is the output of the list comprehension [x**2 for x in range(5)]?",
        "options": [
            "[0, 1, 4, 9, 16]",
            "[0, 2, 4, 6, 8]",
            "[1, 4, 9, 16, 25]",
            "[0, 1, 2, 3, 4]"
        ],
        "correct": 0,
        "hint": "Each element is squared: 0², 1², 2², 3², and 4²."
    },
    {
        "difficulty": 3,
        "question": "What do *args and **kwargs allow in a Python function?",
        "options": [
            "None of the above",
            "Automatic type conversion",
            "Passing a variable number of positional and keyword arguments",
            "Specifying fixed parameters only"
        ],
        "correct": 2,
        "hint": "They allow the function to accept any number of positional and keyword arguments."
    },
    {
        "difficulty": 3,
        "question": "Which statement about Python's Global Interpreter Lock (GIL) is true?",
        "options": [
            "It allows parallel execution of Python threads.",
            "It is responsible for memory management in Python.",
            "It prevents multiple native threads from executing Python bytecodes simultaneously.",
            "It has been removed in Python 3.x."
        ],
        "correct": 2,
        "hint": "The GIL prevents multiple threads from executing Python bytecode at once."
    }
]
   

    def get_question(difficulty):
        available = [q for q in mcq_questions if q['difficulty'] == difficulty and q not in asked_questions[difficulty]]
        if not available:
            asked_questions[difficulty].clear()
            available = [q for q in mcq_questions if q['difficulty'] == difficulty]
        return random.choice(available)

    # Initialize first question
    current_question = get_question(ai_manager.difficulty)
    running = True
    feedback = ""
    feedback_timer = 0

    # Main game loop
    while running:
        screen.fill(COLORS['background'])
        mouse_pos = pygame.mouse.get_pos()
        elapsed = (datetime.datetime.now() - start_time).seconds

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (4, 5):  # Mouse wheel
                    max_offset = (len(current_question['options']) - MAX_VISIBLE_OPTIONS) * (OPTION_HEIGHT + OPTION_SPACING)
                    if event.button == 4:  # Wheel up
                        scroll_offset = max(0, scroll_offset - 30)
                    else:  # Wheel down
                        scroll_offset = min(max_offset, scroll_offset + 30)
                else:
                    x, y = event.pos
                    for i, rect in enumerate(option_rects):
                        adj_y = rect.y + scroll_offset
                        if HEADER_HEIGHT + QUESTION_HEIGHT + 30 <= adj_y <= HEIGHT - 50:
                            if rect.x <= x <= rect.x + rect.width and adj_y <= y <= adj_y + rect.height:
                                if i == current_question['correct']:
                                    score += 10 * current_question['difficulty']
                                    feedback = f"Correct! +{10 * current_question['difficulty']}"
                                    correct = True
                                else:
                                    feedback = random.choice(motivation_messages)
                                    correct = False
                                ai_manager.difficulty = ai_manager.update_difficulty(correct)
                                current_question = get_question(ai_manager.difficulty)
                                feedback_timer = pygame.time.get_ticks()
                                scroll_offset = 0

        # Draw elements
        draw_header(elapsed)
        draw_question(current_question)
        option_rects = draw_options(current_question['options'], mouse_pos)

        # Feedback message
        if pygame.time.get_ticks() - feedback_timer < 1500:
            color = COLORS['correct'] if "Correct" in feedback else COLORS['wrong']
            feedback_surf = FONT_HEADER.render(feedback, True, color)
            screen.blit(feedback_surf, (WIDTH//2 - feedback_surf.get_width()//2, HEIGHT - 80))

        # Time check
        if elapsed >= game_time_limit:
            running = False

        pygame.display.flip()
        clock.tick(30)

    # Database update
    end_time = datetime.datetime.now()
    total_seconds = (end_time - start_time).total_seconds()
    
    try:
        con.execute(f"""
            INSERT INTO games_played (game, coins, profile_id, student_id, date, start_time, end_time, seconds)
            VALUES ('Code Master', {score}, {profile_id}, {student_id}, 
            '{datetime.date.today()}', '{start_time}', '{end_time}', {total_seconds})
        """)
        con.execute(f"UPDATE student_coins SET coin = {all_coins + score} WHERE profile_id = {profile_id}")
        db.commit()
    except Exception as e:
        print(f"Database error: {e}")
        db.rollback()

    pygame.quit()
    print(f"Game Over! Final Score: {score} | Total Coins: {all_coins + score}")

else:
    print("Invalid credentials")