import streamlit as st
import random
import string

# --- Configuration ---
st.set_page_config(page_title="Streamlit Wordle", page_icon="📝", layout="centered")

# --- Level Definitions ---
LEVELS = {
    1: "SMOKE",
    2: "HOUSE"
}

# --- Game State Initialization ---
def setup_level(level_num):
    """Sets up or resets the game state for a specific level."""
    st.session_state.level = level_num
    st.session_state.solution = LEVELS.get(level_num, "HOUSE") # Default to last word if level invalid
    st.session_state.guesses = []
    st.session_state.results = []
    st.session_state.game_over = False
    st.session_state.win = False
    st.session_state.keyboard_colors = {letter: 'lightgray' for letter in string.ascii_uppercase}

# Initialize the game at the very start of the session
if 'level' not in st.session_state:
    setup_level(1)

# --- Styling ---
# Inject custom CSS to style the game board, keyboard, and overall theme to match the NYT Wordle.
st.markdown("""
<style>
    .title {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        text-align: center;
        font-weight: bold;
        font-size: 36px;
        letter-spacing: 0.1em;
        margin-bottom: 20px;
    }
    .grid-container {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 5px;
        width: 300px;
        margin: 0 auto;
    }
    .grid-item {
        width: 50px;
        height: 50px;
        border: 2px solid #d3d6da;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 2rem;
        font-weight: bold;
        text-transform: uppercase;
        color: black;
    }
    .grid-item.correct { background-color: #6aaa64; color: white; border-color: #6aaa64; }
    .grid-item.present { background-color: #c9b458; color: white; border-color: #c9b458; }
    .grid-item.absent { background-color: #787c7e; color: white; border-color: #787c7e; }

    .keyboard-row {
        display: flex;
        justify-content: center;
        margin: 5px 0;
    }
    .key {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: bold;
        padding: 15px 10px;
        margin: 2px;
        border-radius: 4px;
        text-transform: uppercase;
        cursor: default;
        color: black;
        min-width: 40px;
        text-align: center;
    }
    .key-correct { background-color: #6aaa64; color: white; }
    .key-present { background-color: #c9b458; color: white; }
    .key-absent { background-color: #787c7e; color: white; }
    .key-lightgray { background-color: #d3d6da; }
</style>
""", unsafe_allow_html=True)


# --- Game Logic ---
def check_guess(guess, solution):
    """
    Compares the user's guess to the solution and returns the color-coded results.
    Also updates the keyboard colors based on the guess.
    """
    results = ['absent'] * 5
    solution_letters = list(solution)
    guess_letters = list(guess)
    keyboard_colors = st.session_state.keyboard_colors.copy()

    # First pass for correct letters (green)
    for i in range(5):
        if guess_letters[i] == solution_letters[i]:
            results[i] = 'correct'
            solution_letters[i] = None  # Mark as used
            keyboard_colors[guess_letters[i]] = 'key-correct'

    # Second pass for present letters (yellow)
    for i in range(5):
        if results[i] != 'correct' and guess_letters[i] in solution_letters:
            results[i] = 'present'
            solution_letters[solution_letters.index(guess_letters[i])] = None # Mark as used
            if keyboard_colors[guess_letters[i]] != 'key-correct':
                keyboard_colors[guess_letters[i]] = 'key-present'

    # Update absent letters on the keyboard
    for letter in guess:
        if letter.upper() in keyboard_colors and keyboard_colors[letter.upper()] == 'lightgray':
             keyboard_colors[letter.upper()] = 'key-absent'

    return results, keyboard_colors

# --- UI Rendering ---

st.markdown("<div class='title'>ARUSH'S WORDLE</div>", unsafe_allow_html=True)
st.header(f"Level {st.session_state.level}")

# Button to reset the entire game
if st.button("Reset Game to Level 1"):
    setup_level(1)
    st.rerun()

st.write("") # Spacer

# Main game interface
# Game Over Message and Level Progression/Retry
if st.session_state.get('game_over', False):
    if st.session_state.win:
        st.success(f"Correct! The word was {st.session_state.solution}.")

        next_level = st.session_state.level + 1
        if next_level in LEVELS:
            if st.button("Next Level"):
                setup_level(next_level)
                st.rerun()
        else:
            st.balloons()
            st.success("Congratulations! You have completed all levels!")
    else:
        st.error(f"Game over! The word was {st.session_state.solution}.")
        if st.button("Try Again"):
            setup_level(st.session_state.level) # Re-setup the same level
            st.rerun()

# Game Board
board_html = ['<div class="grid-container">']
for i in range(6):
    if i < len(st.session_state.get('guesses', [])):
        guess = st.session_state.guesses[i]
        result = st.session_state.results[i]
        for j in range(5):
            board_html.append(f'<div class="grid-item {result[j]}">{guess[j]}</div>')
    else:
        for _ in range(5):
            board_html.append('<div class="grid-item"></div>')
board_html.append('</div>')
st.markdown("".join(board_html), unsafe_allow_html=True)

st.write("") # Spacer

# On-screen Keyboard
keyboard_html = []
keyboard_layout = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
for row in keyboard_layout:
    keyboard_html.append('<div class="keyboard-row">')
    for letter in row:
        color_class = st.session_state.get('keyboard_colors', {}).get(letter, 'lightgray')
        if color_class not in ['key-correct', 'key-present', 'key-absent']:
            color_class = 'key-lightgray'
        keyboard_html.append(f'<div class="key {color_class}">{letter}</div>')
    keyboard_html.append('</div>')
st.markdown("".join(keyboard_html), unsafe_allow_html=True)

# Input Form
if not st.session_state.get('game_over', False):
    with st.form(key="guess_form", clear_on_submit=True):
        user_guess = st.text_input("Enter your guess:", max_chars=5, key="guess_input").upper()
        submit_button = st.form_submit_button(label='Enter')

        if submit_button and user_guess:
            if len(user_guess) != 5 or not user_guess.isalpha():
                st.warning("Guess must be 5 letters long.")
            else:
                # Process the valid guess
                result, new_keyboard_colors = check_guess(user_guess, st.session_state.solution)
                st.session_state.guesses.append(user_guess)
                st.session_state.results.append(result)
                st.session_state.keyboard_colors = new_keyboard_colors

                # Check for win/loss conditions
                if user_guess == st.session_state.solution:
                    st.session_state.game_over = True
                    st.session_state.win = True
                elif len(st.session_state.guesses) == 6:
                    st.session_state.game_over = True
                    st.session_state.win = False

                st.rerun() # Rerun to update the UI immediately

