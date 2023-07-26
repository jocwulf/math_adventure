# Math Adventure with Streamlit and OpenAI

This Python script uses Streamlit, a popular open-source app framework, and OpenAI's GPT model to create an interactive math adventure for children. The application generates a series of riddles and stories that the child can solve and follow along, respectively.

![Alt text](./images/home.png?raw=true "Title")

## Features

1. **Story Generation**: The script generates a continuation story. The users can choose the story they want to hear and the topic of the story. Each episode of the story consists of a configurable number sentences and ends with a math problem. The math problem is integrated into the narration of the episode.

2. **Riddle Generation**: The script generates a series of math riddles for the child to solve. The number of riddles is determined by the user at the start of the session. The user can choose the number of math problems, the calculation type (addition, subtraction, multiplication, division), and the number range (1 digit or 2 digits).

3. **User Interaction**: The script allows the child to input their answers to the math problems. If the answer is correct, the next episode of the story is generated. If the answer is incorrect, the child is prompted to try again. (Note: In this example I used GPT 3.5. GPT 4 is much better in producing correct math problems.)

![Alt text](./images/story.png?raw=true "Title")   

5. **Environment Variables**: The script uses the `dotenv` package to securely load the OpenAI API key from an environment file.

## Requirements

- Python 3.6 or later
- Streamlit
- OpenAI Python
- numpy
- python-dotenv
- Pillow

## Usage

1. Clone the repository.
2. Install the required packages.
3. Set your OpenAI API key in a `.env` file.
4. Run the script using Streamlit.

## Note

This script uses the OpenAI ChatCompletion API, which requires an API key. Make sure to keep your API key secure and do not expose it in your code or version control system.
