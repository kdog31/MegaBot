import spacy
import datetime

word_list=[]

nlp=spacy.load('en_core_web_sm')         #loading en_core_web_sm model from spaCy
   
async def get_reminder(query):
  for word in query.split(' '):
    wk = word
    word = word.replace("th","")
    word = word.replace("rd","")
    word = word.replace("st","")
    word = word.replace("nd","")
    try:
      temp = int(word)
      if len(word==1):
        word = "0"+word 			  #to convert 1,2,3,.... to 01,02,03.....
        query = query.replace(wk,word)
    except:
      pass

  doc=nlp(query)   			                    #tokenizing the query

  adjs=[]     				                      #'''initiating an adjective list
                        #(bcoz numbers in date like 5 in 5th December is recognized as an adjective instead of date)'''
  for token in doc:                         

    if token.pos_=="ADJ":                   
      adjs.append(token.text)               #creates a list of numbers from which the date starts

  for token in doc:
    word_list.append(token.text)            #creates a list of tokenized words


  '''
  Checking if Remind phrase is present or not
  '''

  if "Reminder" in word_list or "Remind" in word_list or "remind" in word_list or "reminder" in word_list:

    '''Verb list'''
    def verb(x):
      verb_list=[]
      for token in x:
        if token.pos_=='VERB':
          verb_list.append(token.text)   
      return verb_list

    '''Noun list'''
    def noun(x):
      noun_list=[]
      for token in x:
        if token.pos_=='NOUN':
          noun_list.append(token.text)
      return noun_list
    
    def propn(x):
      pnoun_list=[]
      for token in x:
        if token.pos_=='PROPN':
          pnoun_list.append(token.text)
      return pnoun_list

    def sconj(x):
      sconj_list=[]
      for token in x:
        if token.pos_=='SCONJ':
          sconj_list.append(token.text)
      return sconj_list

    Noun=noun(doc)
    Verb=verb(doc)
    Proper=propn(doc)
    Conj=sconj(doc)

    for i in Noun:
      if 'p.m.' in Noun:
        Noun.remove('p.m.')
      if 'a.m.' in Noun:
        Noun.remove('a.m.')

    
    '''
    Displaying task
    '''
    if not Noun:
      task=(Verb[1])
    if Proper:
      if Conj:
        task=("{} {} {}".format(Conj[0], Proper[0], Verb[1]))
      else:
        task=(Proper[0] + ' ' +Verb[1])
    else:
      task=('to ' + Verb[1]+' '+Noun[0])
    return(task)
      

  
  else:                                    #if the phrase 'remind' or 'Remind' is not present in the query the program won't do anything.
    return False