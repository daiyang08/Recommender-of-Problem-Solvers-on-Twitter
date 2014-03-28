import nltk
import twitter
from nltk.corpus import webtext
from nltk.corpus import gutenberg
from nltk.corpus import stopwords
import networkx as nx
import matplotlib.pyplot as plt

import sys

import re, os
from nltk.classify import NaiveBayesClassifier

sentiment_enable = 0
corpus_enable = 1

stopwords = stopwords.words('english')
lemmatizer = nltk.WordNetLemmatizer()

class keyword:
  def __init__(self):
    self.keyword = '' #keyword's name
    self.recommenders = {}  #recommenders' name: weight

class person:
  def __init__(self):
    self.name = ''  #the person's name
    self.interest = []  #the person's interest


POLARITY_DATA_DIR = os.path.join('rt-polaritydata')
RT_POLARITY_POS_FILE = os.path.join(POLARITY_DATA_DIR, 'rt-polarity-pos.txt')
RT_POLARITY_NEG_FILE = os.path.join(POLARITY_DATA_DIR, 'rt-polarity-neg.txt')

#this function takes a feature selection mechanism and returns its performance in a variety of metrics
def train_classifier(feature_select):
  posFeatures = []
  negFeatures = []
  #http://stackoverflow.com/questions/367155/splitting-a-string-into-words-and-punctuation
  #breaks up the sentences into lists of individual words (as selected by the input mechanism) and appends 'pos' or 'neg' after each list
  with open(RT_POLARITY_POS_FILE, 'r') as posSentences:
    for i in posSentences:
      posWords = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
      posWords = [feature_select(posWords), 'pos']
      posFeatures.append(posWords)
  with open(RT_POLARITY_NEG_FILE, 'r') as negSentences:
    for i in negSentences:
      negWords = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
      negWords = [feature_select(negWords), 'neg']
      negFeatures.append(negWords)

  #trains a Naive Bayes Classifier
  trainFeatures = posFeatures + negFeatures
  classifier = NaiveBayesClassifier.train(trainFeatures)
  return classifier

#creates a feature selection mechanism that uses all words
def make_full_dict(words):
  return dict([(word, True) for word in words])

def guess_sentiment(text, classifier):
  print text;
  text1 = re.findall(r"[\w']+|[.,!?;]", text.rstrip())
  text1 = make_full_dict(text1)
  #print text1;
  return classifier.classify(text1);


def leaves(tree):
    """Finds NP (nounphrase) leaf nodes of a chunk tree."""
    for subtree in tree.subtrees(filter = lambda t: t.node=='NP'):
        yield subtree.leaves()

def normalise(word):
    """Normalises words to lowercase and stems and lemmatizes it."""
    word = word.lower()
    #word = stemmer.stem_word(word)
    word = lemmatizer.lemmatize(word)
    return word

def acceptable_word(word):
    """Checks conditions for acceptable word: length, stopword."""
    accepted = bool(2 <= len(word) <= 40
        and word.lower() not in stopwords)
    return accepted


def get_terms(tree):
    for leaf in leaves(tree):
        term = [ normalise(w) for w,t in leaf if acceptable_word(w) ]
        yield term

#main function
def main_process(api,text, token_key, token_key_secret):
  #print 'text',text;
  # Used when tokenizing words
  sentence_re = r'''(?x)      # set flag to allow verbose regexps
        ([A-Z])(\.[A-Z])+\.?  # abbreviations, e.g. U.S.A.
      | \w+(-\w+)*            # words with optional internal hyphens
      | \$?\d+(\.\d+)?%?      # currency and percentages, e.g. $12.40, 82%
      | \.\.\.                # ellipsis
      | [][.,;"'?():-_`]      # these are separate tokens
  '''

  
  #stemmer = nltk.stem.porter.PorterStemmer()

  #Taken from Su Nam Kim Paper...
  grammar = r"""
      NBAR:
          {<NN.*|JJ>*<NN.*>}  # Nouns and Adjectives, terminated with Nouns
          
      NP:
          {<NBAR>}
          {<NBAR><IN><NBAR>}  # Above, connected with in/of/etc...
  """
  chunker = nltk.RegexpParser(grammar)

  toks = nltk.regexp_tokenize(text, sentence_re)

  postoks = nltk.tag.pos_tag(toks)

  #print postoks

  #print 'sbl0';
  #print text;
  #print toks;
  #print postoks;
  tree = chunker.parse(postoks)
  #print 'sbl0';
  #from nltk.corpus import stopwords
  #stopwords = stopwords.words('english')

  terms = get_terms(tree)

  key_words = []
  key_words_list = []

  for term in terms:
    key_words = []
    for word in term:
      key_words.append(word)
      print word,
    key_words_list.append(key_words)
    print

  #get user instance on Twitter
  #api = twitter.Api(consumer_key='TuLPEoqwSkiVreWEODQ6tA',consumer_secret='LnPHHrMOiPVX5PlObJKryROYtdC3475Xq0WJ2tHlJHM',access_token_key=access_token['oauth_token'],access_token_secret=access_token['oauth_token_secret'])
  #api = twitter.Api(consumer_key='TuLPEoqwSkiVreWEODQ6tA',consumer_secret='LnPHHrMOiPVX5PlObJKryROYtdC3475Xq0WJ2tHlJHM',access_token_key=token_key,access_token_secret=token_key_secret)

  keyword_recommenders = {}

  people_interests = {}

  followers = api.GetFollowers()

  keywords_count_all = []
  keywords_count = []

  person_count = {}

  if len(followers)  == 0:
    print "No followers!";
    sys.exit(1)
  #print 'sbl1';
  classifier = train_classifier(make_full_dict)
  for person in followers:
    timeline = api.GetUserTimeline(person.id)
    keywords_count_all = []
    for status in timeline:
      keywords_count = []
      coin_count = 0
      for term in key_words_list:
        tmp_count = 0
        for word in term:
          tmp_count = tmp_count + status.text.lower().count(word)
        if tmp_count > 0:
          coin_count = coin_count + 1
        keywords_count.append(tmp_count)
      for k_count in keywords_count:
        if k_count > 0:
          k_count = k_count + coin_count
      if sum(keywords_count) > 0:
        sentiment = guess_sentiment(status.text, classifier)
        print sentiment;
        if sentiment == 'neg' and sentiment_enable == 1:
          continue
      if keywords_count_all == []:
        keywords_count_all = keywords_count
      else:
        for i in range(0, len(keywords_count_all)):
          keywords_count_all[i] = keywords_count_all[i] + keywords_count[i]
    person_count[person.name] = keywords_count_all
  #print 'sbl2';
  for i in range(0,len(key_words_list)):
    term = key_words_list[i]
    key_word = ''
    for word in term:
      if key_word == []:
        key_word = key_word + word
      else:
        key_word = key_word + ' ' + word
    recommenders_weight = {}
    for person in followers:
      #print i,len(person_count[person.name]);
      #print person.name;
      if person_count[person.name]:
        recommenders_weight[person.name] = person_count[person.name][i]

    recommenders_weight = sorted(recommenders_weight.iteritems(), key=lambda d:d[1], reverse = True)
    j = 0
    recommenders_weight_sort = {}
    for pair in recommenders_weight:
      j = j + 1
      if j > 3 or pair[1] == 0:
        break
      recommenders_weight_sort[pair[0]] = [pair[1]]
    if len(recommenders_weight_sort) > 0:
      keyword_recommenders[key_word] = recommenders_weight_sort

  followers = sorted(followers, key = lambda follower: follower.followers_count, reverse = True)
  connectors = []
  connectors.append(followers[0])
  if len(followers) > 1:
    connectors.append(followers[1])
  print "connector:"
  for connector in connectors:
    print connector.name;

  replyNum = {}
  replys = api.GetReplies()
  for reply in replys:
    if reply.in_reply_to_screen_name != None:
      reply.in_reply_to_screen_name = api.GetUsersSearch(reply.in_reply_to_screen_name)[0].name
      if reply.in_reply_to_screen_name in replyNum:
        replyNum[reply.in_reply_to_screen_name] = replyNum[reply.in_reply_to_screen_name] + 1
      else:
        replyNum[reply.in_reply_to_screen_name] = 1

  connectors_info = {}

  if len(keyword_recommenders) > 0:
    for key in keyword_recommenders:
      closeness = {}
      for person in keyword_recommenders[key]:
        if person in replyNum:
          closeness[person] = replyNum[person]
        else:
          closeness[person] = 0
      closeness = sorted(closeness.iteritems(), key=lambda d:d[1], reverse = True)
      j = 0
      for pair in closeness:
        j = j + 1
        keyword_recommenders[key][pair[0]].append(j)

  closeness = {}
  for connector in connectors:
    if connector.name in replyNum:
      closeness[connector.name] = replyNum[connector.name]
    else:
      closeness[connector.name] = 0
  closeness = sorted(closeness.iteritems(), key=lambda d:d[1], reverse = True)
  j = 0
  #print 'closeness:',closeness;
  for pair in closeness:
    j = j + 1
    for connector in connectors:
      if connector.name == pair[0]:
        connectors_info[pair[0]] = [connector.followers_count, j]
        break


#def extract_keyword():
  corpus = webtext.words()
  corpus_length = len(corpus)

  people_interest_words = {}

  for person in followers:
    timeline = api.GetUserTimeline(person.id)
    status_all = ''
    for status in timeline:
      if status_all == '':
        status_all = status.text
      else:
        status_all = status_all + '. ' + status.text
    status_all = status_all.lower()

    timeline_length = len(status_all)

    toks = nltk.regexp_tokenize(status_all, sentence_re)
    postoks = nltk.tag.pos_tag(toks)
    tree = chunker.parse(postoks)
    terms = get_terms(tree)

    interest_words_prob = {}
    interest_words = []
    for term in terms:
      interest_word = ''
      for word in term:
        if interest_word == '':
          interest_word = word
        else:
          interest_word = interest_word + ' ' + word
      if len(interest_word) > 1:
        interest_words.append(interest_word)
    for phrase in interest_words:
      status_count = status_all.count(phrase)
      if corpus_enable == 1:
        corpus_count = corpus.count(phrase)
      else:
        corpus_count = 1
      if corpus_count == 0:
        corpus_count = 1;
      interest_words_prob[phrase] = status_count * corpus_length / corpus_count / timeline_length

    interest_words_prob = sorted(interest_words_prob.iteritems(), key=lambda d:d[1], reverse = True)
    j = 0
    tmp = []
    for pair in interest_words_prob:
      j = j + 1
      if j > 4:
        break
      tmp.append(pair[0])
    people_interest_words[person.name] = tmp

  #print people_interest_words

  keys = keyword_recommenders
  people = people_interest_words


  #visualisation
  #print 'mavens';
  fig_num = 0
  for k in keys.keys():
    fig_num = fig_num + 1
  if connectors_info.keys():
    fig_num = fig_num + 1
  max_volumn = 2
  max_row = fig_num / max_volumn + fig_num % max_volumn
  #mavens
  i = 0
  for k in keys.keys():
    #if keys[k]:
    #print 'exist mavens';
    i = i + 1
    G = nx.Graph()
    #print G
    node_size_list = []
    node_color_list = []
    nodes_list = []
    G.add_node(k)
    nodes_list.append(k)
    #print G.node
    node_size_list.append(5000)
    node_color_list.append('r')
    for name in keys[k].keys():
      G.add_node(name)
      nodes_list.append(name)
      G.add_edge(k,name,weight = (1.0 / keys[k][name][1])*0.5)
      node_size_list.append(keys[k][name][0]*1500)
      node_color_list.append('y')
      
      if name in people.keys():
        for itrst in people[name]:
          if itrst != k and itrst != name:
            if itrst in nodes_list:
              continue
            else:
              G.add_node(itrst)
              nodes_list.append(itrst)
              G.add_edge(name,itrst,weight=3)
              node_size_list.append(1500)
              node_color_list.append('c')
      
    plt.subplot(max_row,max_volumn,i)
    plt.title('maven')
    #for i in range(len(node_size_list)):
    #  node_size_list[i] = node_size_list[i] / sum(node_size_list) * 100

    #nx.draw_networkx(G,pos=nx.spring_layout(G),with_labels=True,nodelist=nodes_list,node_size=node_size_list,node_color=node_color_list,tick_labels=False)
    nx.draw(G,pos=nx.spring_layout(G),title='mavens', with_labels=True,nodelist=nodes_list,node_size=node_size_list,node_color=node_color_list,tick_labels=False)
    #plt.show()
  #print 'connectors';
  #connectors
  user = api.VerifyCredentials()
  username = user.name

  if connectors_info.keys():
    #print 'connectors_info_keys()';
    G = nx.Graph()
    i = i + 1
    node_size_list = []
    node_color_list = []
    nodes_list = []
    G.add_node(username)
    nodes_list.append(username)
    node_size_list.append(5000)
    node_color_list.append('r')
    for c in connectors_info.keys():
      #print c;
      G.add_node(c)
      nodes_list.append(c)
      G.add_edge(c,username,weight = (1.0 / connectors_info[c][1])*500)
      node_size_list.append(connectors_info[c][0] * 700)
      node_color_list.append('y')
    #plt.subplot(1,fig_num,i)
    plt.subplot(max_row,max_volumn,i)
    plt.title('Connectors')

    #for i in range(len(node_size_list)):
    #  node_size_list[i] = node_size_list[i] / sum(node_size_list) * 100

    nx.draw(G,pos=nx.spring_layout(G),with_labels=True,nodelist=nodes_list,node_size=node_size_list,node_color=node_color_list)
  
  plt.show()

  #print 'end';
