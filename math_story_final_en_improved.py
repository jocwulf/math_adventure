import os
import numpy as np
import streamlit as st
import openai
from dotenv import load_dotenv
from streamlit_chat import message

# Constants
SENTENCES_PER_EPISODE = 6
RIDDLE_MIN = 2
RIDDLE_MAX = 20

# Load OpenAI key from .env file
load_dotenv(".env")
openai.api_key = os.getenv("OPENAI_KEY")

def generate_riddle():
    """Generates a multiplication riddle and returns the question and answer."""
    multiplicand = np.random.randint(RIDDLE_MIN, RIDDLE_MAX)
    multiplier = np.random.randint(RIDDLE_MIN, RIDDLE_MAX)
    product = multiplicand * multiplier
    question = "{} : {}".format(str(product), str(multiplier))
    return question, multiplicand

def generate_story(messages):
    """Generates a story episode using the OpenAI API and returns the story."""
    story = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        temperature=0.5,
    )
    return story['choices'][0]['message']['content']

def generate_challenge():
    """Generates a set of riddles and stories for the child to solve."""
    st.session_state['right_answer'] = [] # list of right answers
    st.session_state['question'] = [] # list of questions
    st.session_state['story'] = [] # list of episodes  
    st.session_state['num_riddles'] = st.session_state['riddle_count'] # number of riddles persistent in session state
    messages = [] # list of messages for openai requests

    # system message for openai requests
    sys_message = """Tell a seven-year-old child a continuation story. Each episode consists of exactly {0} sentences. The story is about the school day of {1}. An episode of the story consists of exactly {0} sentences and no more. Start directly with the narration. End each episode with a math problem, which is always posed by [role: user] beforehand. Integrate the math problem into the narration of the episode. Make sure the math problem is correctly formulated. Do not give the solution. By solving this problem, the child can help {1}. Continue in the new episode already told episodes and pose a new math problem. PLEASE NOTE: Do not give the solution to the math problem. Use only {0} sentences. End the end with the math problem.""".format(SENTENCES_PER_EPISODE, st.session_state['person'])
    
    messages.append({"role": "system", "content": sys_message})

    for _ in range(st.session_state['riddle_count']): # generate riddles and stories
        # generate riddle
        question, answer = generate_riddle()
        messages.append({"role": "user", "content": question})

        # generate story
        story = generate_story(messages)
        messages.append({"role": "assistant", "content": story})
        
        # save riddle and story to session state
        st.session_state.right_answer.append(answer)
        st.session_state.question.append(question)
        st.session_state.story.append(story)

    # create final episode
    messages.pop(0) # remove first item in messages list (system message)
    messages.append({"role": "user", "content": "Finish the story in five sentences. Do not include a math problem."})
    story = generate_story(messages)
    st.session_state.story.append(story)   
    
    st.session_state['current_task'] = 0 # keeps track of the current episode
    return st.session_state['story'][0] # return first episode

def on_input_change():
    """Handles child input and checks if it is correct."""
    user_input = st.session_state["user_input"+str(st.session_state['current_task'])] # get user input
    st.session_state['past'].append(user_input) # save user input to session state
    if user_input == st.session_state.right_answer[st.session_state['current_task']]: # user input is correct
        st.success("Correct answer! Here's the next part of the story.")
        #check if all tasks done
        if st.session_state['current_task'] == st.session_state['num_riddles']-1: # all tasks are done
            st.session_state['generated'].append(st.session_state['story'][st.session_state['current_task']+1]) # generate final episode
            st.session_state['finished'] = True # set finished flag
        else: # not all tasks are done
            st.session_state['current_task']+=1 # increase current task counter
            st.session_state['generated'].append(st.session_state['story'][st.session_state['current_task']]) # append next episode for output
    else: # user input is wrong
        st.session_state.generated.append("Not quite right. Try again! " + st.session_state.question[st.session_state['current_task'] ])  # append wrong message to output

if 'input_done' not in st.session_state:
    st.session_state['input_done'] = False

st.title("༼ ͡ಠ ͜ʖ ͡ಠ ༽ Your Math Adventure")

if st.session_state['input_done'] == False:
    with st.sidebar:
        st.selectbox("How many math problems would you like to solve?", [3, 5, 7, 10], key="riddle_count", index=0)
        st.selectbox("Which story do you want to hear?", ["The Bullerby Children", "Pippi Longstocking", "Emil of Lönneberga"], key="person", index=0)
        if st.button("Start the story", key="start_btn"):
            st.session_state['input_done'] = True

if st.session_state['input_done']:
    if 'past' not in st.session_state:
        st.session_state['past']=['Here your answers are shown.']
    if 'generated' not in st.session_state:
        st.session_state['generated'] = [generate_challenge()]
    if 'finished' not in st.session_state:
        st.session_state['finished'] = False
    chat_placeholder = st.empty()
    with chat_placeholder.container():    
        # st.write(st.session_state.story) # for debugging
        for i in range(len(st.session_state['generated'])):  
                           
            message(str(st.session_state['past'][i]), is_user=True, key=str(i) + '_user')
            message(
                st.session_state['generated'][i],
                key=str(i)
            )



    with st.container():
        st.number_input("Your solution:", min_value=0, max_value=9, 
                        value=1, step=1, on_change=on_input_change, 
                        key="user_input"+str(st.session_state['current_task']),
                        disabled=st.session_state['finished'])