"""
Created on Sat Jul 22 11:45 2017

@author: Matthew Hutson
"""


# to do:

import random
import itertools
import cProfile
import copy
import sys


seed = random.randint(0,1000)
# seed = 913
print('\nseed =', seed)
random.seed(seed)


def combos(wordlist, size):
    ''' list of strings, int -> list of list of strings'''
    combinations = itertools.combinations(wordlist, size)
    return list(combinations)


def load_files():
    vocab_filename = 'glove vocab 50k.txt'
    # a list of 50,000 vocabulary words the system knows
    vocab_file = open(vocab_filename, 'r')
    vocab = vocab_file.readline().split(" ") # list, 50k
    vocab_file.close()
    for i in range(len(vocab)):
        vocab[i] = vocab[i].rstrip(',').strip('\'') # remove the commas and quotes
    # vocab = set(vocab) # breaks it, and doesn't save much time (see testListVsSet())

    filename = 'glove.6B.300d.clean.dis.txt'
    # the distance from each of those 50k words to each of the 400 Codenames words
    dis_file = open(filename, encoding='utf-8', mode='r')
    dis_matrix = []
    for line in dis_file:
        line = line.rstrip().split(" ")
        dis_matrix.append(line) 
    dis_file.close()
    
    filename = 'Codenames word list.txt'
    CNwordlist_file = open(filename, encoding='utf-8', mode='r')
    CNwordlist = []
    for line in CNwordlist_file:
        CNwordlist.append(line.rstrip()) # 400 words
    CNwordlist_file.close()
    
#    filename = '/Users/mhutson/Documents/links/neural-networks/Codenames/GloVe/glove dull words.txt'
#    file = open(filename, encoding='utf-8', mode='r')
#    dull_words = [] 
#    for line in file:
#        dull_words.append(line.strip("\'").strip('\n'))
#    dull_words = tuple(dull_words)
#    file.close()
    
    return vocab, dis_matrix, CNwordlist # , dull_words


def prep_lists_and_dict(vocab, dis_matrix, CNwordlist):  
#    shuffled_CNwordlist = CNwordlist[:]    
    shuffled_CNwordlist = copy.deepcopy(CNwordlist)
    random.shuffle(shuffled_CNwordlist)
    all_board_words = shuffled_CNwordlist[:25]
    all_our_words = shuffled_CNwordlist[:9] 
    all_their_words = shuffled_CNwordlist[9:17]
    neutral_words = shuffled_CNwordlist[17:24]
    avoid_word = shuffled_CNwordlist[24]   
    
    board_dis_dict_dict = {}    # 50k items. key is word, value is dict with 25 word-dis items
    bwi_dict = {}               # indices of board words in CN list
    for bw in all_board_words:        
        bwi_dict[bw] = CNwordlist.index(bw) #25-item dict. keys are board words, values are their indices 0-399 in CNwordlist  
    i = 0
    for v in vocab:                         #50k
        v_dict = {}
        for b in all_board_words:           #25 
            dis = float( dis_matrix[i][bwi_dict[b]] ) # distance from vocab word to board word
            v_dict[b] = dis
        board_dis_dict_dict[v] = v_dict    
        i += 1                  #now I can find a dis with board_dis_dict_dict[vocab word][board word]  
    
    return all_board_words, all_our_words, all_their_words, neutral_words, avoid_word, board_dis_dict_dict
    
    
def play_game():
    print("Welcome to Codenames!")
    role = int(input("Type 1 to be the guesser and 2 to be the clue giver: "))
    if role == "q":
        sys.exit()
    while role not in [1, 2]:
        role = int(input("Try again: "))
    print("Loading...")
    vocab, dis_matrix, CNwordlist = load_files()     
    all_board_words, all_our_words, all_their_words, neutral_words, avoid_word, board_dis_dict_dict \
        = prep_lists_and_dict(vocab, dis_matrix, CNwordlist)
        
    if role == 1: # human is guesser
        game = 1
        opp_prev_clue = ''
        while game == 1: # take a turn
            print("\nAll words on the board: " + ', '.join(all_board_words))
            others = all_their_words + neutral_words + [avoid_word]
            _, num_targets, _ = give_clue(all_our_words, others, vocab, board_dis_dict_dict, all_their_words, neutral_words, avoid_word)
            turn = 1 
#            my_prev_clue = ''
#            while game == 1 and turn == 1: # your turn to guess
            for g in range(num_targets + 1):
                if game == 1 and turn == 1:
                    guess = input("Guess (type * to end your turn or q to quit): ").upper()
                    if guess == '*':
                        turn = 0
                        print("Turn over.")
                    elif guess == 'Q':
                        sys.exit()
                    else:
                        while guess not in all_board_words:
                            guess = input("That word isn't listed. Try again: ").upper()
                        if guess == avoid_word:
                            print("Bomb. You lose.")
                            game = 0
                        elif guess in all_their_words:
                            all_their_words.remove(guess)
                            all_board_words.remove(guess)
                            print("That's one of your opponent's words. Turn over.")
                            turn = 0
                            if len(all_their_words) == 0:
                                print("You lose.")
                                game = 0
                                break
                        elif guess in neutral_words:
                            neutral_words.remove(guess)
                            all_board_words.remove(guess)
                            print("That's a neutral word. Turn over.")
                            turn = 0
                        else:
                            all_our_words.remove(guess)
                            all_board_words.remove(guess)
                            print("You got one!")
                            if len(all_our_words) == 0:
                                print("You win!")
                                game = 0
                                break
                            print("You have " + str(len(all_our_words)) + " words left. Your opponent has " + str(len(all_their_words)) + " words left.")
                            if g < num_targets:
                                print("\nAll words on the board: " + ', '.join(all_board_words))
                            else:
                                print("Turn over.")
            turn = 0
            while game == 1 and turn == 0: # opponent guesses
                print("\nAll words on the board: " + ', '.join(all_board_words))
                others = all_our_words + neutral_words + [avoid_word]
                clue, num_targets, _ = give_clue(all_their_words, others, vocab, board_dis_dict_dict, all_our_words, neutral_words, avoid_word)
                if clue:
                    guesses = computer_guesses(clue, num_targets, all_board_words, board_dis_dict_dict, len(all_our_words), opp_prev_clue)
                else:
                    
                    turn == 1
                    break
                for guess in guesses:
                    if turn == 0:
                        print("Your opponent guessed: ", guess)
                        if guess == avoid_word:
                            print("Bomb. Your opponent loses.")
                            game = 0
                        elif guess in all_our_words:
                            all_our_words.remove(guess)
                            all_board_words.remove(guess)
                            print("That's one of your words. Your turn.")
                            turn = 1
                            opp_prev_clue = clue
                        elif guess in neutral_words:
                            neutral_words.remove(guess)
                            all_board_words.remove(guess)
                            print("That's a neutral word. Your turn.")
                            turn = 1
                            opp_prev_clue = clue
                        else:
                            all_their_words.remove(guess)
                            all_board_words.remove(guess)
                            print("Your opponent got one.")
                            print("You have " + str(len(all_our_words)) + " words left. Your opponent has " + str(len(all_their_words)) + " words left.")
                            opp_prev_clue = ''
    #                        print("All words: " + ', '.join(shuffled_CNwordlist))
                            if len(all_their_words) == 0:
                                print("Your opponent wins :-(")
                                game = 0
                turn = 1

    else: # ro1e = 2, human is clue giver
        game = 1
        my_prev_clue = ''
        opp_prev_clue = ''
        while game == 1:
            turn = 1 # your turn to give clue
            while game == 1 and turn == 1: # loops each turn
                print("\nYour words: " + ', '.join(all_our_words))
                print("Your opponent's words: " + ', '.join(all_their_words))
                print("Neutral words: " + ', '.join(neutral_words))
                print("Avoid word: " + avoid_word) #  + "\n")
#                others = all_their_words + neutral_words + [avoid_word] # not used?
                
                clue = input("Give a clue: ").upper()               
                unique = False # avoid overlap with words on board. 
                if clue == 'Q':
                    sys.quit()               
                while clue not in vocab or not unique: 
                    if clue not in vocab:
                        clue = input("I don't know that word. Try again: ").upper()
                    else:
                        for w in all_board_words:
                            if clue[:3] in w or w[:3] in clue:
                                unique = False
                                clue = input("Too similar to a shown word. Try again: ").upper()
                            else: unique = True                                                     
#                clue_vocab_index = vocab.index(clue)
                num_targets = int(input("How many target words? "))
                
                guesses = computer_guesses(clue, num_targets, all_board_words, board_dis_dict_dict, len(all_our_words), my_prev_clue)
                for guess in guesses:
                    if turn == 1 and game == 1:
                        print("I guess: ", guess)
                        if guess == avoid_word:
                            print("Bomb. You lose.")
                            game = 0
                        elif guess in all_their_words:
                            all_their_words.remove(guess)
                            all_board_words.remove(guess)
                            print("That's one of your opponent's words. Turn over.")
                            turn = 0
                            my_prev_clue = clue[:]
                        elif guess in neutral_words:
                            neutral_words.remove(guess)
                            all_board_words.remove(guess)
                            print("That's a neutral word. Turn over.")
                            turn = 0
                            my_prev_clue = clue[:]
                        else:
                            all_our_words.remove(guess)
                            all_board_words.remove(guess)
                            print("I got one!")
                            print("You have " + str(len(all_our_words)) + " words left. Your opponent has " + str(len(all_their_words)) + " words left.")
                            my_prev_clue = ''
   #                        print("All words: " + ', '.join(shuffled_CNwordlist))
                            if len(all_our_words) == 0:
                                print("You win!")
                                game = 0
                turn = 0
            while game == 1 and turn == 0: # opponent's turn to give clue
                print("\nYour words: " + ', '.join(all_our_words))
                print("Your opponent's words: " + ', '.join(all_their_words))
                print("Neutral words: " + ', '.join(neutral_words))
                print("Avoid word: " + avoid_word + "\n")
                others = all_our_words + neutral_words + [avoid_word]
                print("Your opponent is thinking of a clue.")
                clue, num_targets, _ = give_clue(all_their_words, others, vocab, board_dis_dict_dict, all_our_words, neutral_words, avoid_word)
#                print("Your opponent's clue is " + clue + ", targeting " + str(num_targets) + " words.")
                if clue:
                        guesses = computer_guesses(clue, num_targets, all_board_words, board_dis_dict_dict, len(all_our_words), opp_prev_clue)
                else:
                    turn = 1
                    break
                for guess in guesses:
                    if turn == 0 and game == 1:
                        print("I guess: ", guess)
                        if guess == avoid_word:
                            print("Bomb. Your opponent loses.")
                            game = 0
                        elif guess in all_our_words:
                            all_our_words.remove(guess)
                            all_board_words.remove(guess)
                            print("That's one of your words. Your turn.")
                            turn = 1
                            opp_prev_clue = clue[:]
                        elif guess in neutral_words:
                            neutral_words.remove(guess)
                            all_board_words.remove(guess)
                            print("That's a neutral word. Your turn.")
                            turn = 1
                            opp_prev_clue = clue[:]
                        else:
                            all_their_words.remove(guess)
                            all_board_words.remove(guess)
                            print("I got one.")
                            print("You have " + str(len(all_our_words)) + " words left. Your opponent has " + str(len(all_their_words)) + " words left.")
                            opp_prev_clue = ''
    #                        print("All words: " + ', '.join(shuffled_CNwordlist))
                            if len(all_their_words) == 0:
                                print("Your opponent wins :-(")
                                game = 0
                turn = 1
   

def give_clue(all_target_words, all_other_words, vocab, board_dis_dict_dict, all_their_words, neutral_words, avoid_word):  
    ''' Asks computer for a clue. '''
    ''' First create dictionaries for each category of word (targets, theirs, etc.). 
     The keys for each are the 50,000 vocab words. 
     The values are the key's distances to each word in our/other list '''
    tar_dis_dict = {}   # 50,000 keys, each with a 9-item list as its value
    other_dis_dict = {} # 50,000 keys, each with a 16-item list as its value 
    their_dis_dict = {}
    neutral_dis_dict = {}
    avoid_dis_dict = {}           
    for word in vocab:  #50,000
        
        row = []
        for w in all_target_words:           
            row.append(board_dis_dict_dict[word][w])      # KeyError: 'THE' 
        tar_dis_dict[word] = row
        
        row = []
        for w in all_other_words:           
            row.append(board_dis_dict_dict[word][w])        
        other_dis_dict[word] = row     
        
        row = []
        for w in all_their_words:           
            row.append(board_dis_dict_dict[word][w])        
        their_dis_dict[word] = row
        
        row = []
        for w in neutral_words:           
            row.append(board_dis_dict_dict[word][w])        
        neutral_dis_dict[word] = row
        
        row = []
        row.append(board_dis_dict_dict[word][avoid_word])        
        avoid_dis_dict[word] = row
    
    word_list_list = [all_target_words, all_other_words, all_their_words, neutral_words, avoid_word]
    for word_list in word_list_list:
        for word in word_list:
            if word == 'ICE CREAM':
                word = 'DESSERT'
            if word == 'LOCH NESS':
                word = 'MONSTER'
            if word == 'NEW YORK':
                word = 'CITY'
            if word == 'SCUBA DIVER':
                word = 'SCUBA'          
    
    ''' SET LIMIT TO 2 FOR SURVEY '''        
    target_limit = 9
    for num_targets in range(target_limit, -1, -1): # try 3, 2, 1      
        if num_targets == 0:
            print("* Pass *")
            closest_clue = False
            break
        elif num_targets > 1:
            print("Targeting ", str(num_targets), " words...")
        else:
            print("Targeting 1 word...")
        closest_clue, clue_combo, best_combo_distance = clue_for_num_targets(num_targets, all_target_words, all_other_words, tar_dis_dict, other_dis_dict, their_dis_dict, neutral_dis_dict, avoid_dis_dict, vocab, board_dis_dict_dict)
#        print("closest_clue, clue_combo, best_combo_distance:")
#        print(closest_clue, clue_combo, best_combo_distance)
        if len(clue_combo) > 0 and best_combo_distance < .7: # .65 is good. distance from clue to most dissimilar word in combo. higher is more liberal. 
#            '''PAUSE FOR SURVEY'''
            print("The clue is: " + closest_clue)  # PAUSE FOR SURVEY
#            print("Targeting: " + ', '.join(clue_combo))
#            print("Clue's average distance to targets:", best_combo_distance) 
            break
    return closest_clue, num_targets, clue_combo # returns clue_combo for checking
                       
            
def clue_for_num_targets(num_targets, all_our_words, all_other_words, our_dis_dict, other_dis_dict, their_dis_dict, neutral_dis_dict, avoid_dis_dict, vocab, board_dis_dict_dict):
    ''' use the two distance dictionaries to find clues '''
    our_combos = combos(all_our_words, num_targets)
#    print(len(our_combos))
    best_combo_distance = 10
    closest_clue = ""
    clue_combo = []
#    potential_clue_count = {}  # for printing most common clues during testing
#    c_loop = 1                 # for printing potential clues and targets during testing
    
    ''' potential clues need to be closer to at least one of ours than any others '''
    n_buffer, t_buffer, a_buffer = .14, .16, .18
    allowable_vocab = [] 
    for voc in vocab:
        if voc != "": # and voc not in dull_words: 
            greatest_distance_to_ours = min(our_dis_dict[voc]) # distance between word and most distant word in ours
            smallest_distance_to_theirs = min(their_dis_dict[voc])
            smallest_distance_to_neutral = min(neutral_dis_dict[voc])
            smallest_distance_to_avoid = min(avoid_dis_dict[voc]) 
            gap_t = smallest_distance_to_theirs - greatest_distance_to_ours
            gap_n = smallest_distance_to_neutral - greatest_distance_to_ours
            gap_a = smallest_distance_to_avoid - greatest_distance_to_ours
            if gap_t > t_buffer and gap_n > n_buffer and gap_a > a_buffer: 
                allowable_vocab.append(voc) # list of strings   
#        print("len(allowable_vocab) = ", len(allowable_vocab)) # ~1,000
                   
    for our_combo in our_combos:
        
        ''' assemble the combo distance matrix/dict, ~1,000 x combo size '''
        combo_dis_dict = {}
        for voc in allowable_vocab:
            row = []
            for ourw in our_combo:    # 3, 2, or 1
                row.append(board_dis_dict_dict[voc][ourw])               
            combo_dis_dict[voc] = row            
         
        ''' find clues with lower dis to all combo words than to any of others '''
#        buffer = .17
        potential_clues = [] 
        for voc in allowable_vocab:
            if voc != "":
                greatest_distance_to_ours = max(combo_dis_dict[voc]) # distance between word and most distant word in the combo
#                smallest_distance_to_others = min(other_dis_dict[voc])
                smallest_distance_to_theirs = min(their_dis_dict[voc])
                smallest_distance_to_neutral = min(neutral_dis_dict[voc])
                smallest_distance_to_avoid = min(avoid_dis_dict[voc])
#                gap = smallest_distance_to_others - greatest_distance_to_ours # should be positive   
                gap_t = smallest_distance_to_theirs - greatest_distance_to_ours
                gap_n = smallest_distance_to_neutral - greatest_distance_to_ours
                gap_a = smallest_distance_to_avoid - greatest_distance_to_ours
#                if gap > buffer: 
                if gap_t > t_buffer and gap_n > n_buffer and gap_a > a_buffer: 
                    #print("gap = " + str(gap)) # use to fine-tune window
                    potential_clues.append(voc) # list of strings   
#        if len(potential_clues) > 0: 
#            print("10 potential clues, out of ", len(potential_clues))
#            print(potential_clues[:10])
        
        ''' pick the clue that minimizes the distance to its most dissimilar word in the combo '''
        min_dis = 10
#        min_dis_index = 0
        clue = '' #added this
        for pc in potential_clues: 
            ''' get the list of distances for each target vocab word in potential clues '''
#            distances_to_targets = combo_dis_dict[pc]
#            dis = round(sum(distances_to_targets) / len(distances_to_targets), 3)
            dis = max(combo_dis_dict[pc])
            if dis < min_dis:
                unique = True # avoid overlap with words on board. 
                for w in all_our_words:
                    if pc[:3] in w or w[:3] in pc:
                        unique = False
                for w in all_other_words:
                    if pc[:3] in w or w[:3] in pc:
                        unique = False
                if unique:          
                    min_dis = dis
                    clue = pc # added this
#            clue = vocab[min_dis_index]
            for word in our_combo:
                if word == 'ICE CREAM':
                    word = 'DESSERT'
                if word == 'LOCH NESS':
                    word = 'MONSTER'
                if word == 'NEW YORK':
                    word = 'CITY'
                if word == 'SCUBA DIVER':
                    word = 'SCUBA'
#        if len(potential_clues) > 0: 
#            print("Clue for combo " + str(c_loop) + " of " + str(len(our_combos)) + " is " + clue)
#            print("Its average distance to target words is:", min_dis)
#            print("Targeting: " + ', '.join(our_combo) + "\n")
#        c_loop += 1
        if min_dis < best_combo_distance:
            best_combo_distance = min_dis
            closest_clue = clue
            clue_combo = our_combo
#    import operator
#    potential_clue_count = sorted(potential_clue_count.items(), key=operator.itemgetter(1), reverse=True)
#    print("Potential clue count: ", potential_clue_count)
    if closest_clue: # used for checking
        print("The best clue is: " + closest_clue)          
        print("Targeting: " + ', '.join(clue_combo)) 
        print("Clue's average distance to targets:", best_combo_distance) 
    return closest_clue, clue_combo, best_combo_distance


def computer_guesses(clue, num_targets, all_board_words, board_dis_dict_dict, team_score=0, prev_clue=''):
    dis_dict = {}
    prev_dis_dict = {}
    for word in all_board_words: # 25  
        dis = board_dis_dict_dict[clue][word]
        dis_dict[word] = dis
        
        ''' If not all targets for previous clue were guessed, consider that clue too: '''
        if prev_clue:          
            prev_dis = board_dis_dict_dict[prev_clue][word]            
            prev_dis_dict[word] = prev_dis
            adjustment = 2 * prev_dis / (1 + team_score)      
            print('word, raw distance, adjustment: ', word, '\n', dis, '\t', adjustment)
            dis = dis + adjustment   
            
    ''' sort the board words by distance to clue: '''      
    dis_list = list(dis_dict.items())
    dis_list.sort(key=lambda x: x[1])
    guesses = []
    for i in range(num_targets):
        guesses.append(dis_list[i][0])
    return guesses
    
# play_game()
#cProfile.run('play_game()')





""" To generate data for user study: """

def survey(rounds):
    import sys
    
    shared_words = [ [],[],[],[],[] ]       # boards, ours, theirs, neutral, avoid.
    unique_words = [ [[],[]], [[],[]] ]     # A [targets, clues], B [targets, clues].
    comp_guesses = []
    num_correct, num_targets_hit, num_ours, num_theirs, num_neutral, num_avoid = 0, 0, 0, 0, 0, 0
    my_clues = [] # for compare_clue_guessing()
    my_targets_list = []
    
    for r in range(rounds):       
        repeat = True
        while repeat:
            repeat = False
            print("Round ", r+1)
            print("Loading files.")
            
            vocab, dis_matrix, CNwordlist = load_files()          
            all_board_words, all_our_words, all_their_words, neutral_words, avoid_word, board_dis_dict_dict \
                = prep_lists_and_dict(vocab, dis_matrix, CNwordlist)            
                                  
            print("\nYour words: " + ', '.join(all_our_words))
            print("Your opponent's words: " + ', '.join(all_their_words))
            print("Neutral words: " + ', '.join(neutral_words))
            print("Avoid word: " + avoid_word) #  + "\n")
            others = all_their_words + neutral_words + [avoid_word]
            its_clue, num_targets, clue_combo = give_clue(all_our_words, others, vocab, board_dis_dict_dict, all_their_words, neutral_words, avoid_word)
            
            ''' for testing how long "give_clue" takes: '''
            return
            
            my_clue = input("Enter a clue for 2 words: ").upper()   
            while my_clue not in vocab: 
                if my_clue == "Q":
                    sys.exit()
                my_clue = input("I don't know that word. Try again: ").upper()
            
            my_targets = [input("Enter target 1: ").upper(), input("Enter target 2: ").upper()]
            print(its_clue)
            its_targets = list(clue_combo)
            print(its_targets)
            
            reply = "x"
            while reply not in ["1", "0"]:
                reply = input("Do round {} over? 1 for yes, 0 for no: ".format(r+1))
            repeat = int(reply)              
        
        random.shuffle(all_board_words)
        shared_words[0].append(all_board_words)
        shared_words[1].append(all_our_words)
        shared_words[2].append(all_their_words)
        shared_words[3].append(neutral_words)
        shared_words[4].append([avoid_word])   
        ''' on the even rounds, r%2 = 0 and group A (unique_words[0]) gets my targets and clues '''
        ''' on the odd rounds r%2 = 1 and group B (unique_words[1]) gets my targets and clues '''
        unique_words[r%2][0].append(my_targets) 
        unique_words[r%2][1].append([my_clue]) 
        ''' on the even rounds, (r+1)%2 = 1, and group B (unique_words[1]) gets its targets and clues '''
        ''' on the odd rounds, (r+1)%2 = 0, and group A (unique_words[0]) gets its targets and clues '''
        unique_words[(r+1)%2][0].append(its_targets) 
        unique_words[(r+1)%2][1].append([its_clue])
        my_clues.append(my_clue)
        my_targets_list.append(my_targets)
        
        ''' Also have computer guess from my clues: '''
        guesses = computer_guesses(my_clue, 2, all_board_words, board_dis_dict_dict)
        comp_guesses.append(guesses)
        
    
    shared_string = ">> boards = " + str(shared_words[0]) + "\n>> ours = " + str(shared_words[1]) + \
                            "\n>> theirs = " + str(shared_words[2]) + "\n>> neutral = " + str(shared_words[3]) + \
                            "\n>> avoid = " + str(shared_words[4]) 
    shared_string = ">> boards = " + str(shared_words[0]) + "\n>> ours = " + str(shared_words[1]) + \
                            "\n>> theirs = " + str(shared_words[2]) + "\n>> neutral = " + str(shared_words[3]) + \
                            "\n>> avoid = " + str(shared_words[4])                         
                            
    A_string = "\n>> targets = " + str(unique_words[0][0]) + "\n>> clues = " + str(unique_words[0][1])
    B_string = "\n>> targets = " + str(unique_words[1][0]) + "\n>> clues = " + str(unique_words[1][1])      
    shared_string, A_string, B_string = shared_string.replace("\'", "\""), A_string.replace("\'", "\""), B_string.replace("\'", "\"")    
    
    print(shared_string) 
    print("")
    print(A_string)   
    print("")
    print(B_string) 
    print("\nMy clues:")
    print(my_clues)
    print("\nMy targets:")
    print(my_targets_list)    
    
    ''' Print computer's guesses based on my clues and the results: '''
    for r in range(rounds):
        c = 0
        for g in range(2):        
            if comp_guesses[r][g] in unique_words[r%2][0][r]: # in my_targets
                num_targets_hit += 1
                c += 1              
            if comp_guesses[r][g] in shared_words[1][r]:
                num_ours += 1
            if comp_guesses[r][g] in shared_words[2][r]:
                num_theirs += 1
            if comp_guesses[r][g] in shared_words[3][r]:
                num_neutral += 1
            if comp_guesses[r][g] in shared_words[4][r]:
                num_avoid += 1
        if c == 2: num_correct += 1
    print("\nWhen the computer guessed from your clues, it got this many correct, targets, ours, theirs, neutrals, avoids: ")
    print(num_correct, num_targets_hit, num_ours, num_theirs, num_neutral, num_avoid)       
    print("Its guesses: ", comp_guesses)     
                 
#survey(10)   
#cProfile.run('survey(1)')
#survey(1)
   
 

def compare_clue_guessing(boards, ours, theirs, neutral, avoid, clues, targets, comp_guesses=[]):
    ''' takes 10 boards with my clues, and guesses 2 targets for each '''
    vocab, dis_matrix, CNwordlist = load_files()  
    num_correct, num_targets_hit, num_ours, num_theirs, num_neutral, num_avoid = 0, 0, 0, 0, 0, 0

    for board in boards:
        for word in board:
            word = word.replace("\"", "")           
    for i in range(len(clues)):
        clues[i] = clues[i][0].replace("\"", "")
        
    if comp_guesses is []:
        for c in range(len(clues)):            
            board_dis_dict_dict = {}    # 50k items. key is word, value is dict with 25 word-dis items
            bwi_dict = {}               # indices of board words in CN list
            for bw in boards[c]: 
                bwi_dict[bw] = CNwordlist.index(bw) #25-item dict. keys are board words, values are their indices 0-399 in CNwordlist  
            i = 0
            for v in vocab:                         #50k
                v_dict = {}
                for b in boards[c]:                 #25 
                    dis = float( dis_matrix[i][bwi_dict[b]] ) # distance from vocab word to board word
                    v_dict[b] = dis
                board_dis_dict_dict[v] = v_dict    
                i += 1                  #now I can find a dis with board_dis_dict_dict[vocab word][board word]  
            
            guesses = computer_guesses(clues[c], 2, boards[c], board_dis_dict_dict)
            comp_guesses.append(guesses)
                
    ''' Print computer's guesses based on my clues and the results: '''
    for r in range(len(boards)):
        cor = 0
        for g in range(2):        
            if comp_guesses[r][g] in targets[r]: # in my_targets
                num_targets_hit += 1
                cor += 1              
            if comp_guesses[r][g] in ours[r]:
                num_ours += 1
            if comp_guesses[r][g] in theirs[r]:
                num_theirs += 1
            if comp_guesses[r][g] in neutral[r]:
                num_neutral += 1
            if comp_guesses[r][g] in avoid[r]:
                num_avoid += 1
        if cor == 2: num_correct += 1
    print("\nWhen the computer guessed from your clues, it got this many correct, targets, ours, theirs, neutrals, avoids: ")
    print(num_correct, num_targets_hit, num_ours, num_theirs, num_neutral, num_avoid)       
    print("Its guesses: ", comp_guesses)         
       
#boards = [["PLAY", "ORGAN", "CHINA", "THUMB", "SUB", "HAM", "NAIL", "KNIFE", "CRANE", "HEAD", "RING", "ROCK", "FILE", "TICK", "FRANCE", "SPOT", "AUSTRALIA", "CELL", "SCIENTIST", "GLASS", "WATCH", "BEAR", "MILLIONAIRE", "DOCTOR", "TRIP"], ["CARROT", "BATTERY", "DROP", "SPELL", "WALL", "PHOENIX", "NOVEL", "CHURCH", "MAIL", "AUSTRALIA", "SPIDER", "ROBOT", "SQUARE", "SHOT", "LOG", "WAVE", "LAP", "GRACE", "TRIP", "STRIKE", "LOCH NESS", "BAR", "COPPER", "SPIKE", "PAPER"], ["CONCERT", "NET", "DWARF", "KNIGHT", "PIE", "FLUTE", "TEMPLE", "MEXICO", "GIANT", "DOG", "LONDON", "BOOT", "MATCH", "ROBOT", "KID", "BEIJING", "DRILL", "BAND", "BUTTON", "BUCK", "SERVER", "BELL", "CARROT", "HOLLYWOOD", "STATE"], ["DANCE", "HOLE", "TAG", "LEAD", "PIE", "CAP", "DINOSAUR", "LONDON", "ROCK", "PIN", "GIANT", "IRON", "ARM", "HOSPITAL", "VET", "CHURCH", "CROSS", "BOLT", "SHIP", "TABLE", "DRESS", "PLAY", "TICK", "MAMMOTH", "OLYMPUS"], ["TOOTH", "SATELLITE", "DRILL", "STADIUM", "OLIVE", "SHOP", "DECK", "SHOE", "MEXICO", "MERCURY", "HOTEL", "AMAZON", "BUGLE", "BUCK", "THUMB", "ROOT", "GLASS", "DISEASE", "LONDON", "MARCH", "HORSE", "THEATER", "BUTTON", "MOSCOW", "GIANT"], ["GRASS", "CROSS", "CIRCLE", "BOW", "GENIUS", "MOON", "LASER", "DRESS", "PIN", "CHEST", "BERMUDA", "FAN", "MODEL", "BATTERY", "GHOST", "CAPITAL", "MAIL", "STRING", "POLE", "SATELLITE", "CROWN", "SPOT", "SPELL", "PLAY", "FLY"], ["SPACE", "MATCH", "TABLE", "EYE", "WEB", "OCTOPUS", "PIE", "SUIT", "VACUUM", "MILLIONAIRE", "CLOAK", "COPPER", "SWITCH", "DINOSAUR", "BUCK", "BAT", "PASTE", "BERLIN", "CANADA", "CHINA", "CASINO", "CROSS", "EMBASSY", "MINE", "HELICOPTER"], ["STRAW", "TEACHER", "DIAMOND", "NURSE", "ORGAN", "SINK", "UNDERTAKER", "ROW", "SLIP", "LIMOUSINE", "MATCH", "LAB", "BAND", "SHOE", "THIEF", "SOLDIER", "ARM", "PLATE", "AIR", "BATTERY", "CROSS", "AFRICA", "SWING", "PUPIL", "BACK"], ["TRAIN", "ROBOT", "LEMON", "REVOLUTION", "DRAGON", "PLATYPUS", "APPLE", "CLIFF", "MASS", "GLASS", "AMBULANCE", "WAKE", "ROUND", "WHIP", "PIE", "ROSE", "BOARD", "TELESCOPE", "STICK", "SERVER", "WAR", "POUND", "BUFFALO", "BOX", "COMPOUND"], ["CHINA", "CASINO", "KEY", "THIEF", "POST", "BERRY", "COLD", "CIRCLE", "QUEEN", "MOUNT", "SHOE", "HELICOPTER", "PART", "POOL", "PASTE", "SOUL", "MICROSCOPE", "CLOAK", "FORCE", "PLOT", "STAFF", "RABBIT", "AUSTRALIA", "BAND", "DISEASE"]]
#ours = [["HEAD", "GLASS", "ROCK", "TRIP", "MILLIONAIRE", "SPOT", "KNIFE", "SCIENTIST", "RING"], ["LAP", "CHURCH", "SPELL", "SPIDER", "CARROT", "SHOT", "TRIP", "PAPER", "WALL"], ["NET", "KID", "CONCERT", "BEIJING", "DOG", "MATCH", "FLUTE", "BOOT", "DWARF"], ["DANCE", "OLYMPUS", "ROCK", "MAMMOTH", "HOSPITAL", "PIE", "IRON", "PLAY", "LONDON"], ["THEATER", "SHOE", "MOSCOW", "BUCK", "AMAZON", "HORSE", "HOTEL", "ROOT", "SATELLITE"], ["SPOT", "CIRCLE", "MOON", "DRESS", "CAPITAL", "LASER", "PIN", "SATELLITE", "PLAY"], ["VACUUM", "EMBASSY", "SWITCH", "OCTOPUS", "WEB", "PIE", "CHINA", "SPACE", "CLOAK"], ["SINK", "LIMOUSINE", "NURSE", "ARM", "DIAMOND", "BATTERY", "UNDERTAKER", "BACK", "CROSS"], ["SERVER", "GLASS", "BOARD", "STICK", "WAKE", "REVOLUTION", "PIE", "CLIFF", "POUND"], ["KEY", "THIEF", "MOUNT", "PLOT", "CIRCLE", "BAND", "HELICOPTER", "MICROSCOPE", "DISEASE"]]
#theirs = [["CRANE", "SUB", "CHINA", "FILE", "AUSTRALIA", "FRANCE", "CELL", "THUMB"], ["COPPER", "PHOENIX", "LOG", "BAR", "AUSTRALIA", "NOVEL", "ROBOT", "STRIKE"], ["DRILL", "LONDON", "BAND", "KNIGHT", "MEXICO", "GIANT", "BUTTON", "BELL"], ["DINOSAUR", "TICK", "BOLT", "PIN", "TABLE", "CROSS", "TAG", "CAP"], ["DISEASE", "SHOP", "MARCH", "GIANT", "DECK", "MEXICO", "MERCURY", "LONDON"], ["GHOST", "CROSS", "MODEL", "CROWN", "STRING", "SPELL", "FLY", "CHEST"], ["HELICOPTER", "PASTE", "CROSS", "EYE", "COPPER", "BUCK", "SUIT", "BERLIN"], ["SOLDIER", "SWING", "MATCH", "PUPIL", "THIEF", "ORGAN", "AIR", "PLATE"], ["DRAGON", "MASS", "ROSE", "APPLE", "TRAIN", "PLATYPUS", "BOX", "WAR"], ["CHINA", "STAFF", "CLOAK", "SHOE", "SOUL", "QUEEN", "CASINO", "POOL"]]
#neutral = [["DOCTOR", "HAM", "PLAY", "BEAR", "TICK", "WATCH", "NAIL"], ["MAIL", "BATTERY", "SQUARE", "GRACE", "LOCH NESS", "WAVE", "SPIKE"], ["STATE", "PIE", "ROBOT", "SERVER", "HOLLYWOOD", "TEMPLE", "CARROT"], ["SHIP", "DRESS", "ARM", "GIANT", "HOLE", "LEAD", "CHURCH"], ["GLASS", "DRILL", "BUGLE", "BUTTON", "STADIUM", "THUMB", "TOOTH"], ["POLE", "BERMUDA", "GENIUS", "BATTERY", "GRASS", "MAIL", "BOW"], ["CANADA", "MATCH", "BAT", "DINOSAUR", "TABLE", "MINE", "MILLIONAIRE"], ["ROW", "SLIP", "TEACHER", "BAND", "STRAW", "LAB", "AFRICA"], ["ROUND", "TELESCOPE", "WHIP", "LEMON", "BUFFALO", "AMBULANCE", "ROBOT"], ["PASTE", "RABBIT", "POST", "AUSTRALIA", "BERRY", "COLD", "FORCE"]]
#avoid = [["ORGAN"], ["DROP"], ["BUCK"], ["VET"], ["OLIVE"], ["FAN"], ["CASINO"], ["SHOE"], ["COMPOUND"], ["PART"]]
#clues = ['GEOLOGY', 'TICKET', 'PUPPY', 'MUSIC', 'SPUTNIK', 'ORBIT', 'APPLIANCE', 'FUNERAL', 'WINE', 'BACTERIA']
#targets = [["ROCK", "SCIENTIST"], ["TRIP", "PAPER"], ["KID", "DOG"], ["DANCE", "ROCK"], ["MOSCOW", "SATELLITE"], ["MOON", "SATELLITE"], ["VACUUM", "SWITCH"], ["UNDERTAKER", "CROSS"], ["SERVER", "GLASS"], ["MICROSCOPE", "DISEASE"]]
#guesses = [['SCIENTIST', 'ROCK'], ['TRIP', 'MAIL'], ['DOG', 'KID'], ['DANCE', 'ROCK'], ['SATELLITE', 'MOSCOW'], ['SATELLITE', 'MOON'], ['VACUUM', 'WEB'], ['SOLDIER', 'LIMOUSINE'], ['GLASS', 'APPLE'], ['DISEASE', 'MICROSCOPE']]
#compare_clue_guessing(boards, ours, theirs, neutral, avoid, clues, targets, guesses)


def guess(): 
    ''' standalone test of computer guessing from human clue '''
    vocab, dis_matrix, CNwordlist, _ = load_files()
    #    shuffled_CNwordlist = CNwordlist[:]
    shuffled_CNwordlist = copy.deepcopy(CNwordlist)
    random.shuffle(shuffled_CNwordlist)
    all_our_words = shuffled_CNwordlist[:9] 
    all_other_words = shuffled_CNwordlist[9:25]      # treat 6 neutrals and 1 bomb as others, to avoid them
    all_words = all_our_words + all_other_words
    print("Our words: " + ', '.join(all_our_words))
    print("Other words: " + ', '.join(all_other_words))
    clue = input("Give a clue (IN CAPS): ")
    while clue not in vocab: 
        clue = input("I don't know that word. Try again: ")
    clue_vocab_index = vocab.index(clue)    # 0 - 49,999?
    num_targets = int(input("How many target words? "))
    
    ''' compile the distances of all words to the clue word '''
    dis_dict = {}
    for word in all_words: # 25
        CN_index = CNwordlist.index(word) # 0-399
        dis = dis_matrix[clue_vocab_index][CN_index] # no need to float()
        dis_dict[word] = dis
       
    dis_list = list(dis_dict.items())
    dis_list.sort(key=lambda x: x[1])
    guesses = []
    for i in range(num_targets):
        guesses.append(dis_list[i][0])
    print("My guesses:", guesses)
    
#guess()
        
  
    
def vocab_near_CN_word(target, number=10):
    '''find the [number] closest vocab words to CN target'''   
    vocab, dis_matrix, CNwordlist = load_files()    
    CN_index = CNwordlist.index(target) 
    dis_dict = {}
    for word in vocab: 
        vocab_index = vocab.index(word) 
        dis = float(dis_matrix[vocab_index][CN_index])
        dis_dict[word] = dis        
    ''' sort the vocab words by distance to target: '''
    dis_list = list(dis_dict.items())
    dis_list.sort(key=lambda x: x[1])
    closest = []
    for i in range(number):
        closest.append(dis_list[i])
    print(closest)
    
    

#vocab_near_CN_word('AGENT')

### 
""" Test methods: """

def testListVsSet():
    wordlist = [''.join(random.choice(string.ascii_uppercase) for _ in range(5)) for _ in range(50000)]
    word = wordlist[25000]
    wordset = set(wordlist)
    def f1():
        print(word in wordlist)
    def f2():
        print(word in set(wordlist))
    def f3():
        print(word in wordset)
    cProfile.run('f1()') # 0.001 seconds
    cProfile.run('f2()') # 0.004 seconds
    cProfile.run('f3()') # 0.000 seconds
# testListVsSet()  
