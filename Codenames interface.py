%%python 
# without this tkinter craskes kernel

"""
Created on Tue Feb 19 14:58 2019

@author: Matthew Hutson
"""

'''
There are lots of parameters in some of these functions to avoid global variables.
I found through trial and error that I couldn't avoid certain global variables.
It's still not clear to me why some should be global and others not.
'''

print("opened")
from tkinter import *
from tkinter import ttk  
from tkinter import messagebox
import random
import time
from Codenames import combos, load_files, prep_lists_and_dict, give_clue, clue_for_num_targets, computer_guesses
#print("imported")

global root
global leftframe
global cardframe
global canvas
global first_card   # when you delete 25 cards from canvas and 25, it starts counting at 26
first_card = 0


root = Tk()
root.title("Codenames")
  
cardsize = 150
root_width = cardsize * 5 +310
root_height = cardsize * 5 +5
root_size = str(root_width)+'x'+str(root_height)+'+0+0'
root.geometry(root_size)  

leftframe = ttk.Frame(root, padding="3 3 3 3", width=300)
leftframe.grid()
leftframe.columnconfigure(0, minsize = 300) 

cardframe = ttk.Frame(root, padding="3 3 3 3")
cardframe.grid(column=1, row=0, sticky=E)
canvas = Canvas(cardframe, width=cardsize*5, height=cardsize*5)
canvas.pack()



def end_game(game):
    if messagebox.askyesno(message="Are you sure you want to end the game?", title="End Game?", icon="question"):  
        for child in leftframe.winfo_children(): child.destroy()        # clears buttons
        for child in cardframe.winfo_children()[1:]: child.destroy()    # clears card labels
        canvas.delete("all")                                            # clears rectangles
        welcome()
       
    
def their_turn_to_guess(root, message, guess_message, clue_shown, score_message, game, board_dis_dict_dict, all_our_words, all_their_words, neutral_words, avoid_word, all_board_words, shuffled_board_words, ml): 
    global num_targets
    global clickable
    clickable = False
    clue_shown.set("")
    global opp_prev_clue
    global first_card
    others = all_our_words + neutral_words + [avoid_word]
    message.set("It's your opponent's turn to guess.")
    ml.config(foreground="blue")
    guess_message.set("Preparing a clue...")
    root.update()
    clue, num_targets, _ = give_clue(all_their_words, others, vocab, board_dis_dict_dict, all_our_words, neutral_words, avoid_word)
    guess_message.set("Clue:")
    clue_shown.set(clue + ", " + str(num_targets))
    root.update()
    if clue:
        guesses = computer_guesses(clue, num_targets, all_board_words, board_dis_dict_dict, len(all_our_words), opp_prev_clue)
    else:       
        our_turn_to_guess(root, board_dis_dict_dict, all_our_words, all_their_words, neutral_words, avoid_word, message, guess_message, clue_shown, clickable, ml)
    for guess in guesses:
        time.sleep(3)
        guessed = "Your opponent guessed: " + guess
        message.set(guessed)
        root.update()
        time.sleep(3)
        for label in cardframe.winfo_children()[1:]: # Labels
            if guess == label.cget("text"):
                card = shuffled_board_words.index(guess) + 1
                their_label = label
                print(guess)     
        if guess == avoid_word:
            message.set("Bomb. Your opponent loses.")
            canvas.itemconfig(card, fill='black')
#            their_label.destroy()
            their_label.config(foreground='white', background='black')
            game = False                   
        elif guess in all_our_words:
            all_our_words.remove(guess)
            all_board_words.remove(guess)
            message.set("That's one of your words. Your turn.")
            canvas.itemconfig(card, fill='red')
#            their_label.destroy()
            their_label.config(foreground='white', background='red')
            opp_prev_clue = clue
        elif guess in neutral_words:
            neutral_words.remove(guess)
            all_board_words.remove(guess)
            message.set("That's a neutral word. Your turn.")
            canvas.itemconfig(card, fill='gray')
#            their_label.destroy()
            their_label.config(foreground='white', background='grey')
            opp_prev_clue = clue
        else:
            all_their_words.remove(guess)
            all_board_words.remove(guess)
            message.set("Your opponent got one.")
            canvas.itemconfig(card+first_card, fill='blue')
#            their_label.destroy()
            their_label.config(foreground='white', background='blue')
            score_message.set("You have "+str(len(all_our_words))+" words left. \nYour opponent has "+str(len(all_their_words))+" words left.")
            opp_prev_clue = ''
            if len(all_their_words) == 0:
                message.set("Your opponent wins :-(")
                score_message.set("")
                game = False
        root.update()
        time.sleep(2)
    if game:
        our_turn_to_guess(root, board_dis_dict_dict, all_our_words, all_their_words, neutral_words, avoid_word, message, guess_message, clue_shown, ml)
    

def end_turn(turn, root, message, guess_message, clue_shown, score_message, game, board_dis_dict_dict, all_our_words, all_their_words, neutral_words, avoid_word, all_board_words, shuffled_board_words, ml):
    if turn == 1:
        print("Turn over.")
    message.set("It's your opponent's turn to guess.")
    guess_message.set("")
    clue_shown.set("")
    their_turn_to_guess(root, message, guess_message, clue_shown, score_message, game, board_dis_dict_dict, all_our_words, all_their_words, neutral_words, avoid_word, all_board_words, shuffled_board_words, ml)

          
def card_click(root, game, card, word, label, message, guess_message, score_message, turn, board_dis_dict_dict, all_our_words, all_their_words, all_board_words, neutral_words, avoid_word, clue_shown, shuffled_board_words, ml):
    '''int, string, Label'''
    global clickable
    global cards_clicked
    global num_targets
    if game and clickable and canvas.itemcget(card, "fill") == "white":     
        if word == avoid_word:
            canvas.itemconfig(card, fill='black')
#            label.destroy()
            label.config(foreground='white', background='black')
            message.set("BOMB. You lose.")
            game = False 
            root.update()
        elif word in all_their_words:
            all_their_words.remove(word)
            all_board_words.remove(word)
            message.set("That's your opponent's word. Turn over.")
            time.sleep(3)
            message.set("It's your opponent's turn to guess.")
            ml.config(foreground="blue")
            guess_message.set("Clue:")
            canvas.itemconfig(card, fill='blue')
#            label.destroy()
            label.config(foreground='white', background='blue')
            score_message.set("You have "+str(len(all_our_words))+" words left. \nYour opponent has "+str(len(all_their_words))+" words left.")
            if len(all_their_words) == 0:
                guess_message.set("YOU LOSE.")
                game = False
            root.update()
            their_turn_to_guess(root, message, guess_message, clue_shown, score_message, game, board_dis_dict_dict, all_our_words, all_their_words, neutral_words, avoid_word, all_board_words, shuffled_board_words, ml)
        elif word in neutral_words:
            neutral_words.remove(word)
            all_board_words.remove(word)
            message.set("That's a neutral word. Turn over.")
            canvas.itemconfig(card, fill='grey')
#            label.destroy()  
            label.config(foreground='white', background='grey')
            root.update()
            their_turn_to_guess(root, message, guess_message, clue_shown, score_message, game, board_dis_dict_dict, all_our_words, all_their_words, neutral_words, avoid_word, all_board_words, shuffled_board_words, ml)
        elif word in all_our_words:  
            all_our_words.remove(word)
            all_board_words.remove(word)
            message.set("You got one!")
            canvas.itemconfig(card, fill='red')
#            label.destroy()
            label.config(foreground='white', background='red')
            score_message.set("You have "+str(len(all_our_words))+" words left. \nYour opponent has "+str(len(all_their_words))+" words left.")
            cards_clicked += 1
            root.update()
            if len(all_our_words) == 0:
                message.set("You win!")
                root.update()
                game = False
            if cards_clicked == num_targets + 1: 
                message.set("No more guesses.")
                root.update()
                their_turn_to_guess(root, message, guess_message, clue_shown, score_message, game, board_dis_dict_dict, all_our_words, all_their_words, neutral_words, avoid_word, all_board_words, shuffled_board_words, ml)                                
    
    
def card_lambda(root, game, row, col, cardlist, message, guess_message, score_message, turn, board_dis_dict_dict, all_our_words, all_their_words, all_board_words, neutral_words, avoid_word, clue_shown, shuffled_board_words, ml):
    return lambda x: card_click(root, game, cardlist[row][col][0], cardlist[row][col][1], cardlist[row][col][2], message, guess_message, score_message, turn, board_dis_dict_dict, all_our_words, all_their_words, all_board_words, neutral_words, avoid_word, clue_shown, shuffled_board_words, ml)


def our_turn_to_guess(root, board_dis_dict_dict, all_our_words, all_their_words, neutral_words, avoid_word, message, guess_message, clue_shown, ml):     
    global num_targets
    global cards_clicked
    global clickable
    cards_clicked = 0
    others = all_their_words + neutral_words + [avoid_word]
    message.set("It's your turn to guess.")
    ml.config(foreground="red")
    guess_message.set("Preparing a clue...")
    clue_shown.set("")
    root.update()
    clue, num_targets, targets = give_clue(all_our_words, others, vocab, board_dis_dict_dict, all_their_words, neutral_words, avoid_word) #
#    print(targets) # for testing
    clue_shown.set(clue + ", " + str(num_targets))
    guess_message.set("Clue:")
    root.update()
    clickable = True          


def place_cards(role, root, game, message, guess_message, score_message, turn, board_dis_dict_dict, all_our_words, all_their_words, all_board_words, neutral_words, avoid_word, clue_shown, shuffled_board_words, ml):
    global first_card
    cardlist = []
    bwi = 0 # board words index
    first_card += 25
    for row in range(5):
        cardrow = []
        for col in range(5):
            card = canvas.create_rectangle((col*cardsize+10, row*cardsize+10, col*cardsize+cardsize-10, row*cardsize+cardsize-10), fill="white", outline="black")
            word = shuffled_board_words[bwi]
            bwi += 1
            label = Label(cardframe, text=word, bg='white') 
            label.place(x=(col*cardsize + cardsize/2 - 45), y=(row*cardsize + cardsize/2 - 10))
            cardtup = (card, word, label)
            cardrow.append(cardtup)
        cardlist.append(cardrow)
    if role == 1:   # guesser
        for row in range(5):
            for col in range(5):
                canvas.tag_bind(cardlist[row][col][0], "<Button-1>", card_lambda(root, game, row, col, cardlist, message, guess_message, score_message, turn, board_dis_dict_dict, all_our_words, all_their_words, all_board_words, neutral_words, avoid_word, clue_shown, shuffled_board_words, ml))
                cardlist[row][col][2].bind("<Button-1>", card_lambda(root, game, row, col, cardlist, message, guess_message, score_message, turn, board_dis_dict_dict, all_our_words, all_their_words, all_board_words, neutral_words, avoid_word, clue_shown, shuffled_board_words, ml))           
    else:           # giver
        return cardlist   
    
    
def cover_card(color, guess, shuffled_board_words, cardlist):
    ''' str, str, list, list of list of tuples(int, str, label) '''
    global first_card
    card = shuffled_board_words.index(guess) 
    canvas.itemconfig(card + 26, fill=color)
    canvas.itemconfig(card + first_card + 1, fill=color)
    
#    labels_left = []
#    for i in cardframe.winfo_children()[1:]:
#        labels_left.append(i.cget("text"))
#    ll_index = labels_left.index(guess)
#    cardframe.winfo_children()[ll_index + 1].destroy()
  
    '''find indices of word in cardlist. make its label white'''
    for i,row in enumerate(cardlist):
        for j,tup in enumerate(row):
            if tup[1] == guess:
                loc = (i, j)
    label = cardlist [loc[0]] [loc[1]] [2]
    label.config(foreground='white', background=color)
         
    root.update()

    
def clue_button(game, cardlist, clue, num_tar, cml, clue_message, score_message, all_board_words, board_dis_dict_dict, all_our_words, all_their_words, neutral_words, avoid_word, shuffled_board_words, cb, clue_entry, number_entry):  
    global my_prev_clue
    global opp_prev_clue
    clue = clue.get().upper()   # StringVar into str
    num_tar = num_tar.get()   
    
    clue_message.set("Thinking...")
    cml.config(foreground="red") 
    root.update()
            
    turn = True          
    if game and turn:
        known = clue in vocab
        if not known : 
            clue_message.set("I don't know that word. Try again.")
            root.update()
        unique = True
        for w in all_board_words:
            if clue[:3] in w or w[:3] in clue:
                unique = False
                clue_message.set("Too similar to a shown word. Try again.")
                root.update()       

        if known and unique:          
            guesses = computer_guesses(clue, num_tar, all_board_words, board_dis_dict_dict, len(all_our_words), my_prev_clue)
            for guess in guesses:
                if turn and game:
                    clue_message.set("I guess: " + guess)
                    root.update()
                    time.sleep(3)
                    if guess == avoid_word:
                        clue_message.set("Bomb. You lose.")
                        cover_card("black", guess, shuffled_board_words, cardlist)
                        game = False
                    elif guess in all_their_words:
                        all_their_words.remove(guess)
                        all_board_words.remove(guess)
                        clue_message.set("That's your opponent's word. Turn over.")
                        cover_card("blue", guess, shuffled_board_words, cardlist)
                        turn = False
                        my_prev_clue = clue[:]
                        time.sleep(3)
                    elif guess in neutral_words:
                        neutral_words.remove(guess)
                        all_board_words.remove(guess)
                        clue_message.set("That's a neutral word. Turn over.")
                        cover_card("gray", guess, shuffled_board_words, cardlist)
                        turn = False
                        my_prev_clue = clue[:]
                        time.sleep(3)
                    else:
                        all_our_words.remove(guess)
                        all_board_words.remove(guess)
                        clue_message.set("I got one!")
#                        score_message.set("You have "+str(len(all_our_words))+" words left. \nYour opponent has "+str(len(all_their_words))+" words left.") # too long
                        score_message.set("Red has "+str(len(all_our_words))+" words left. Blue has "+str(len(all_their_words))+" words left.")
                        cover_card("red", guess, shuffled_board_words, cardlist)
                        time.sleep(3)
                        if len(all_our_words) == 0:
                            clue_message.set("You win!")
                            game = False
                            root.update()
            cb.config(state="DISABLED")   
            clue_entry.delete(0, END)
            number_entry.delete(0, END)
            root.update()            
            turn = False        
    
        while game and not turn: # opponent's turn to give clue
            others = all_our_words + neutral_words + [avoid_word]
            clue_message.set("Your opponent is thinking of a clue.")
            cml.config(foreground="blue")
            root.update()
            clue, num_targets, _ = give_clue(all_their_words, others, vocab, board_dis_dict_dict, all_our_words, neutral_words, avoid_word)
            if clue:
#                clue_message.set("Your opponent's clue is " + clue + ", targeting " + str(num_targets) + " words.") #too long
                clue_message.set("Your opponent's clue is " + clue + ", " + str(num_targets)) 
                guesses = computer_guesses(clue, num_targets, all_board_words, board_dis_dict_dict, len(all_our_words), opp_prev_clue)
                root.update()
                time.sleep(3)
            else:
                clue_message.set("Your opponent passes. Your turn.")
                root.update()
                time.sleep(3)
                turn = True
                break
            for guess in guesses:
                if game and not turn:                    
                    clue_message.set("I guess: " + guess)
                    root.update()
                    time.sleep(3)
                    if guess == avoid_word:
                        clue_message.set("Bomb. Your opponent loses.")
                        cover_card(black, guess, shuffled_board_words, cardlist)
                        game = False
                    elif guess in all_our_words:
                        all_our_words.remove(guess)
                        all_board_words.remove(guess)
                        clue_message.set("That's one of your words. Your turn.")
                        cover_card("red", guess, shuffled_board_words, cardlist)
                        time.sleep(3)
                        turn = True
                        opp_prev_clue = clue[:]
                    elif guess in neutral_words:
                        neutral_words.remove(guess)
                        all_board_words.remove(guess)
                        clue_message.set("That's a neutral word. Your turn.")
                        cover_card("gray", guess, shuffled_board_words, cardlist)
                        time.sleep(3)
                        turn = True
                        opp_prev_clue = clue[:]
                    else:
                        all_their_words.remove(guess)
                        all_board_words.remove(guess)
                        clue_message.set("I got one.")
#                        score_message.set("You have " + str(len(all_our_words)) + " words left. Your opponent has " + str(len(all_their_words)) + " words left.") # too long
                        score_message.set("Red has " + str(len(all_our_words)) + " words left. Blue has " + str(len(all_their_words)) + " words left.")
                        cover_card("blue", guess, shuffled_board_words, cardlist)
                        opp_prev_clue = ''
                        if len(all_their_words) == 0:
                            clue_message.set("Your opponent wins :-(")
                            game = False
                        root.update()
                        time.sleep(3)
            if game:
                cb.config(state="NORMAL")
                clue_message.set("Enter a clue and number of targets:")
                cml.config(foreground="red")
                root.update()
                turn = True
        
    
def play_game(root, role):
    game = True
    global clickable # needs to be global
    clickable = False
    global turn # needs to be global
    turn = True
    global num_targets
    global my_prev_clue
    global opp_prev_clue
    my_prev_clue = ""
    opp_prev_clue = ""
    global vocab # needs to be global
    vocab, dis_matrix, CNwordlist = load_files()    
    all_board_words, all_our_words, all_their_words, neutral_words, avoid_word, board_dis_dict_dict \
        = prep_lists_and_dict(vocab, dis_matrix, CNwordlist)    
    shuffled_board_words = all_board_words[:] # for assigning to cards
    random.shuffle(shuffled_board_words)   
        
    if role == 1: # human is guesser
    
        message = StringVar()
        message.set("It's your turn to guess.")
        ml = ttk.Label(leftframe, textvariable=message) # message label
        ml.grid(column=0, row=0, sticky=N) # sticky=N doesn't do anything 
        ml.config(foreground="red")
        
        guess_message = StringVar()
        guess_message.set("")
        ttk.Label(leftframe, textvariable=guess_message).grid(column=0, row=1, sticky=N)
        
        clue_shown = StringVar()
        ttk.Label(leftframe, textvariable=clue_shown).grid(column=0, row=2, sticky=N)        

        end_turn_button = ttk.Button(leftframe, text="End Turn", command = lambda: end_turn(turn, root, message, guess_message, clue_shown, score_message, game, board_dis_dict_dict, all_our_words, all_their_words, neutral_words, avoid_word, all_board_words, shuffled_board_words, ml))
        end_turn_button.grid(column=0, row=3)
        
        score_message = StringVar()
        score_message.set("You have 9 words left. \nYour opponent has 8 words left.")
        ttk.Label(leftframe, textvariable=score_message).grid(column=0, row=4)
        
        ttk.Label(leftframe, text="––––––––––––––––––––––––––––––––––––––––").grid(column=0, row=5)
        end_game_button = ttk.Button(leftframe, text="End Game", command = lambda: end_game(game))
        end_game_button.grid(column=0, row=6)
        
        for child in leftframe.winfo_children(): child.grid_configure(padx=5, pady=5)        
        
        place_cards(role, root, game, message, guess_message, score_message, turn, board_dis_dict_dict, all_our_words, all_their_words, all_board_words, neutral_words, avoid_word, clue_shown, shuffled_board_words, ml)
        our_turn_to_guess(root, board_dis_dict_dict, all_our_words, all_their_words, neutral_words, avoid_word, message, guess_message, clue_shown, ml)       

    
    if role == 2: # human is clue giver

        clue_message = StringVar()
        clue_message.set("Enter a clue and number of targets:")
        cml = ttk.Label(leftframe, textvariable=clue_message)
        cml.grid(column=0, row=0)
        cml.config(foreground="red")
                  
        clue = StringVar()
        num_tar = IntVar()
        clue_entry = ttk.Entry(leftframe, width=15, textvariable=clue)
        number_entry = ttk.Entry(leftframe, width=2, textvariable=num_tar)
        clue_entry.grid(column=0, row=1)
        number_entry.grid(column=0, row=1, sticky=(E))
        number_entry.delete(0, END)

        score_message = StringVar()
        score_message.set("You have 9 words left. \nYour opponent has 8 words left.")
        ttk.Label(leftframe, textvariable=score_message).grid(column=0, row=4)
        
        message, guess_message, clue_shown, ml = None, None, None, None 
        cardlist = place_cards(role, root, game, message, guess_message, score_message, turn, board_dis_dict_dict, all_our_words, all_their_words, all_board_words, neutral_words, avoid_word, clue_shown, shuffled_board_words, ml) # list of list of tuples of (card/int, word/str, label/Label)
        for row in cardlist:
            for card in row:
                if card[1] in all_our_words:
                    card[2].config(foreground="red")
                if card[1] in all_their_words:
                    card[2].config(foreground="blue")
                if card[1] in neutral_words:
                    card[2].config(foreground="grey")
                if card[1] in avoid_word:
                    card[2].config(foreground="black")
#                    print(card[0], card[1], card[2]) # 37 POUND .!frame2.!label37
#                    print(type(card[2]))   # <class 'tkinter.Label'>                
        
        cb = ttk.Button(leftframe, text="Give Clue", command = lambda: clue_button(game, cardlist, clue, num_tar, cml, clue_message, score_message, all_board_words, board_dis_dict_dict, all_our_words, all_their_words, neutral_words, avoid_word, shuffled_board_words, cb, clue_entry, number_entry))
        cb.grid(column=0, row=2)
        root.bind('<Return>', lambda x: clue_button(game, cardlist, clue, num_tar, cml, clue_message, score_message, all_board_words, board_dis_dict_dict, all_our_words, all_their_words, neutral_words, avoid_word, shuffled_board_words, cb, clue_entry, number_entry))     
        
        ttk.Label(leftframe, text="––––––––––––––––––––––––––––––––––––––––").grid(column=0, row=5)
        end_game_button = ttk.Button(leftframe, text="End Game", command = lambda: end_game(game))
        end_game_button.grid(column=0, row=6)
                
        root.update()
  

def play_guesser():
#    global canvas
    for child in leftframe.winfo_children(): child.destroy()        # clears buttons
    for child in cardframe.winfo_children()[1:]: child.destroy()    # clears card labels
    canvas.delete("all")                                            # clears rectangles
    play_game(root, 1) 
    
    
def play_giver():
    for child in leftframe.winfo_children(): child.destroy()        # clears buttons
    for child in cardframe.winfo_children()[1:]: child.destroy()    # clears card labels
    canvas.delete("all")                                            # clears rectangles
    global my_prev_clue     # yes?
    global opp_prev_clue    # yes?
    my_prev_clue = ""       # yes?
    opp_prev_clue = ""      # yes?                                   
    play_game(root, 2)


def welcome():
    global first_card
    if first_card > 1:
        first_card += 25
    for row in range(5):
        for col in range(5):
            card = canvas.create_rectangle((col*cardsize+10, row*cardsize+10, col*cardsize+cardsize-10, row*cardsize+cardsize-10), fill="white", outline="black")
            label = Label(cardframe, text="CODENAMES", background="white")
            label.place(x=(col*cardsize + cardsize/2 - 50), y=(row*cardsize + cardsize/2 - 10))
                                          
    ttk.Label(leftframe, text="Welcome to Codenames.").grid(column=0, row=0, sticky=N)
    guesser_button = ttk.Button(leftframe, text="Play as guesser.", command=play_guesser)
    giver_button = ttk.Button(leftframe, text="Play as clue giver.", command=play_giver)       
    guesser_button.grid() 
    giver_button.grid()
    root.mainloop()
    
welcome()
         
#canvas created. welcome called, creating cards. 
#welcome calls play_giver, which deletes cards and calls play_game, which calls place_cards, which creates cards.
#end_game deletes cards, calls welcome.
 