import os
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()


def create_quiz_gemini(topic, num_questions=10):
    """
    Creates a quiz using the Gemini API.

    Args:
        topic: The topic for the quiz.
        num_questions: The number of questions to generate (max 20).

    Returns:
        A list of dictionaries, where each dictionary represents a question
        and its options, or an error message.
    """

    if not topic:
        return "Invalid topic."

    if num_questions > 20:
        num_questions = 20

    genai.configure(api_key=os.environ.get("GEMINI_API_KEY")) # Replace with your actual API key

    # List available models and select one
    try:
        available_models = genai.list_models()
        model_name = None
        for model in available_models:
            if "generateContent" in model.supported_generation_methods and "gemini-1.5-flash" in model.name.lower():
                model_name = model.name #find the 1.5 flash model
                break
        if not model_name:
          for model in available_models:
            if "generateContent" in model.supported_generation_methods and "gemini-pro" in model.name.lower():
              model_name = model.name #fallback to gemini-pro if 1.5 flash is not found.
              break

        if not model_name:
            return "Error: No suitable model found that supports generateContent. Check available models."

        model = genai.GenerativeModel(model_name)

        prompt = f"""
        Create a multiple-choice quiz about {topic} with {num_questions} questions.
        Each question should have 4 options (A, B, C, D).
        Provide the answer key at the end.
        Example format:
        1. What is the capital of France?
        A. London
        B. Paris
        C. Berlin
        D. Rome

        2. ...

        Answer Key:
        1. B
        2. ...
        """

        response = model.generate_content(prompt)
        quiz_text = response.text

        questions = []
        question_lines = quiz_text.split('\n')
        current_question = {}
        answer_key = {}
        parsing_answers = False

        for line in question_lines:
            line = line.strip()
            if line.startswith("Answer Key:"):
                parsing_answers = True
                continue

            if parsing_answers:
                if line:
                    try:
                        question_number = int(line.split(".")[0].strip())
                        correct_answer = line.split(".")[1].strip()
                        answer_key[question_number] = correct_answer
                    except (ValueError, IndexError):
                        pass # Handle malformed answer key lines.
                continue

            if line.startswith(tuple(str(i) + "." for i in range(1, num_questions + 1))):
                if current_question:
                    questions.append(current_question)
                current_question = {"options": []}
                current_question["question"] = line.split(".")[1].strip()

            elif line.startswith(("A.", "B.", "C.", "D.")):
                current_question["options"].append(line.split(".")[1].strip())

        if current_question:
            questions.append(current_question)

        for i, question in enumerate(questions):
            correct_option_index = ord(answer_key.get(i + 1, 'Z')) - ord('A')
            if 0 <= correct_option_index < len(question["options"]):
                question["correct_answer"] = question["options"][correct_option_index]
            else:
                question["correct_answer"] = "Answer not found"

        return questions

    except Exception as e:
        return f"Error: {e}"

def run_quiz(questions):
    """
    Runs the quiz, displays questions, provides real-time answers, and explanations.
    """
    if isinstance(questions, str):
        print(questions)
        return
    if not questions:
        print("No questions to display.")
        return

    score = 0
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY")) # Replace with your API key
    model = genai.GenerativeModel('gemini-1.5-flash') # or gemini-1.5-flash, or your selected model.

    for i, question_data in enumerate(questions):
        print(f"\nQuestion {i + 1}: {question_data['question']}")
        for j, option in enumerate(question_data["options"]):
            print(f"{chr(ord('A') + j)}. {option}")

        while True:
            user_answer = input("Your answer (A, B, C, or D): ").upper()
            if user_answer in ["A", "B", "C", "D"]:
                break
            else:
                print("Invalid input. Please enter A, B, C, or D.")

        selected_option = question_data["options"][ord(user_answer) - ord('A')]
        correct_answer = question_data["correct_answer"]

        if selected_option == correct_answer:
            print("Correct!")
            score += 1
            # Real-time answer (can be customized)
            print(f"The answer is: {correct_answer}")

        else:
            print(f"Incorrect. The correct answer is: {correct_answer}")
            print(f"You selected: {selected_option}")

            # Explanation using Gemini API
            try:
                explanation_prompt = f"""
                Explain the following question and answer in detail:
                Question: {question_data['question']}
                Correct Answer: {correct_answer}
                Selected Answer: {selected_option}
                Explain why the correct answer is correct, and why the selected answer is incorrect.
                """
                explanation_response = model.generate_content(explanation_prompt)
                print("\nExplanation:")
                print(explanation_response.text)
            except Exception as e:
                print(f"Could not generate explanation: {e}")

    print(f"\nYour final score: {score}/{len(questions)}")

if __name__ == "__main__":
    topic = input("Enter a quiz topic: ")
    num_questions = int(input("Enter the number of questions (up to 20): "))
    quiz_questions = create_quiz_gemini(topic, num_questions)
    run_quiz(quiz_questions)