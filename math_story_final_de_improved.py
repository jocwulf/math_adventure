import os
import numpy as np
import streamlit as st
import openai
from dotenv import load_dotenv
from streamlit_chat import message

# Konstanten
SENTENCES_PER_EPISODE = 5
RIDDLE_MIN = 2
RIDDLE_MAX = 10

# OpenAI-Schlüssel aus .env-Datei laden
load_dotenv(".env")
openai.api_key = os.getenv("OPENAI_KEY")

def generate_riddle():
    """Generiert ein Multiplikationsrätsel und gibt die Frage und Antwort zurück."""
    multiplicand = np.random.randint(RIDDLE_MIN, RIDDLE_MAX)
    multiplier = np.random.randint(RIDDLE_MIN, RIDDLE_MAX)
    product = multiplicand * multiplier
    question = "{} : {}".format(str(product), str(multiplier))
    return question, multiplicand

def generate_story(messages):
    """Generiert eine Story-Episode mit der OpenAI-API und gibt die Story zurück."""
    story = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        temperature=0.5,
    )
    return story['choices'][0]['message']['content']

def generate_challenge():
    """Generiert eine Reihe von Rätseln und Geschichten, die das Kind lösen kann."""
    st.session_state['right_answer'] = [] # Liste der richtigen Antworten
    st.session_state['question'] = [] # Liste der Fragen
    st.session_state['story'] = [] # Liste der Episoden  
    st.session_state['num_riddles'] = st.session_state['riddle_count'] # Anzahl der Rätsel in der Session-Status
    messages = [] # Liste der Nachrichten für OpenAI-Anfragen

    # Systemnachricht für OpenAI-Anfragen
    sys_message = """Erzähle einem siebenjährigen Kind eine Fortsetzungsgeschichte. Jede Episode besteht aus genau {0} Sätzen. Die Geschichte handelt vom Schultag von {1}. Eine Episode der Geschichte besteht aus genau {0} Sätzen und nicht mehr. Beginnen Sie direkt mit der Erzählung. Beenden Sie jede Episode mit einem Mathematikproblem, das immer zuvor von [role: user] gestellt wird. Integrieren Sie das Mathematikproblem in die Erzählung der Episode. Stellen Sie sicher, dass das Mathematikproblem korrekt formuliert ist. Geben Sie die Lösung nicht an. Durch die Lösung dieses Problems kann das Kind {1} helfen. Fahren Sie in der neuen Episode mit bereits erzählten Episoden fort, ohne auf die Lösung einzugehen. Stellen Sie ein neues Mathematikproblem. BITTE BEACHTEN SIE: Geben Sie die Lösung zum Mathematikproblem nicht an. Verwenden Sie nur {0} Sätze. Beenden Sie das Ende mit dem Mathematikproblem.""".format(SENTENCES_PER_EPISODE, st.session_state['person'])
    
    messages.append({"role": "system", "content": sys_message})

    for _ in range(st.session_state['riddle_count']): # Rätsel und Geschichten generieren
        # Rätsel generieren
        question, answer = generate_riddle()
        messages.append({"role": "user", "content": question})

        # Geschichte generieren
        story = generate_story(messages)
        messages.append({"role": "assistant", "content": story})
        
        # Rätsel und Geschichte im Session-Status speichern
        st.session_state.right_answer.append(answer)
        st.session_state.question.append(question)
        st.session_state.story.append(story)

    # Finale Episode erstellen
    messages.pop(0) # Erstes Element in der Nachrichtenliste entfernen (Systemnachricht)
    messages.append({"role": "user", "content": "Beenden Sie die Geschichte in fünf Sätzen. Fügen Sie kein Mathematikproblem hinzu."})
    story = generate_story(messages)
    st.session_state.story.append(story)   
    
    st.session_state['current_task'] = 0 # Verfolgt die aktuelle Episode
    return st.session_state['story'][0] # Gibt die erste Episode zurück

def on_input_change():
    """Verarbeitet die Eingabe des Kindes und überprüft, ob sie korrekt ist."""
    user_input = st.session_state["user_input"+str(st.session_state['current_task'])] # Benutzereingabe abrufen
    st.session_state['past'].append(user_input) # Benutzereingabe im Session-Status speichern
    if user_input == st.session_state.right_answer[st.session_state['current_task']]: # Benutzereingabe ist korrekt
        st.success("Richtige Antwort! Hier ist der nächste Teil der Geschichte.")
        # Überprüfen, ob alle Aufgaben erledigt sind
        if st.session_state['current_task'] == st.session_state['num_riddles']-1: # Alle Aufgaben sind erledigt
            st.session_state['generated'].append(st.session_state['story'][st.session_state['current_task']+1]) # Finale Episode generieren
            st.session_state['finished'] = True # Fertig-Flag setzen
        else: # Nicht alle Aufgaben sind erledigt
            st.session_state['current_task']+=1 # Aufgabenzähler erhöhen
            st.session_state['generated'].append(st.session_state['story'][st.session_state['current_task']]) # Nächste Episode für die Ausgabe anhängen
    else: # Benutzereingabe ist falsch
        st.session_state.generated.append("Nicht ganz richtig. Versuchen Sie es erneut! " + st.session_state.question[st.session_state['current_task'] ])  # Falsche Nachricht zur Ausgabe hinzufügen

if 'input_done' not in st.session_state:
    st.session_state['input_done'] = False

st.title("༼ ͡ಠ ͜ʖ ͡ಠ ༽ Dein Mathe-Abenteuer")

if st.session_state['input_done'] == False:
    with st.sidebar:
        st.selectbox("Wie viele Matheprobleme möchtest du lösen?", [3, 5, 7, 10], key="riddle_count", index=0)
        st.selectbox("Welche Geschichte möchtest du hören?", ["Die Kinder aus Bullerbü", "Pippi Langstrumpf", "Michel aus Lönneberga"], key="person", index=0)
        if st.button("Starte die Geschichte", key="start_btn"):
            st.session_state['input_done'] = True

if st.session_state['input_done']:
    if 'past' not in st.session_state:
        st.session_state['past']=['Hier werden deine Antworten angezeigt.']
    if 'generated' not in st.session_state:
        st.session_state['generated'] = [generate_challenge()]
    if 'finished' not in st.session_state:
        st.session_state['finished'] = False
    chat_placeholder = st.empty()
    with chat_placeholder.container():    
        # st.write(st.session_state.story) # Zum Debuggen
        for i in range(len(st.session_state['generated'])):  
                           
            message(str(st.session_state['past'][i]), is_user=True, key=str(i) + '_user')
            message(
                st.session_state['generated'][i],
                key=str(i)
            )

    with st.container():
        st.number_input("Deine Lösung:", min_value=0, max_value=9, 
                        value=1, step=1, on_change=on_input_change, 
                        key="user_input"+str(st.session_state['current_task']),
                        disabled=st.session_state['finished'])
