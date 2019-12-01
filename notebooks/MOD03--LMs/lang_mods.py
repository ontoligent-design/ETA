
# coding: utf-8

# # Module 3: Infer Language Models
# 
# * DS 6001
# * Raf Alvarado
# 
# We now create a series of langage models and evaluate them.

# # Set Up

# ## Configure

# In[1]:


OHCO = ['book_id', 'chap_num', 'para_num', 'sent_num', 'token_num']
text_file1 = '../MOD02--TextModels/austen-persuasion.csv'
text_file2 = '../MOD02--TextModels/austen-sense.csv'


# ## Import libraries

# In[2]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
get_ipython().run_line_magic('matplotlib', 'inline')


# # Import and combine texts

# In[3]:


text1 = pd.read_csv(text_file1)
text2 = pd.read_csv(text_file2)


# In[4]:


text1.head()


# In[5]:


text1['book_id'] = 1
text2['book_id'] = 2


# In[6]:


text1.head()


# In[7]:


tokens = pd.concat([text1, text2]).dropna()


# In[8]:


tokens = tokens.set_index(OHCO)


# In[9]:


tokens.head()


# # Create a vocabulary

# In[10]:


tokens['term_str'] = tokens['token_str'].str.lower().str.replace(r'[\W_]', '')


# In[11]:


tokens.head()


# In[12]:


vocab = tokens['term_str'].value_counts()    .to_frame()    .reset_index()    .rename(columns={'term_str':'n', 'index':'term_str'})    .sort_values('term_str')
vocab.index.name = 'term_id'


# In[14]:


vocab.head()


# In[16]:


vocab.sample(5)


# # Create Unigram Model

# In[17]:


n_tokens = vocab.n.sum()
vocab['p'] = vocab['n'] / n_tokens
vocab['log_p'] = np.log2(vocab['p'])


# In[18]:


n_tokens


# In[19]:


vocab.sort_values('p', ascending=False).head(10)


# In[20]:


smooth = vocab['p'].min()
def predict_sentence(sent_str):
    tokens = pd.DataFrame(sent_str.lower().split(), columns=['term_str'])
    tokens = tokens.merge(vocab, on='term_str', how='left')
    tokens.loc[tokens['p'].isna(), ['p', 'log_p']] = [smooth, np.log2(smooth)]
    p = tokens['p'].product()
    log_p = tokens['log_p'].sum()
    print('-' * 80)
    print("p('{}') = {}; log2: {}".format(sent_str, p, log_p))
    print('-' * 80)
    print(tokens)
    print('-' * 80)


# In[21]:


predict_sentence('I love you')
predict_sentence('I love cars')
predict_sentence("I want to")
predict_sentence("anne said to")
predict_sentence("said to her")
predict_sentence('she said')


# # Buld N-Gram models
# 
# This function generates models up to the length specified.

# In[23]:


def get_ngrams(tokens, n=2):
    
    # Create list to store copies of tokens table
    X = []
    
    # We convert the index to cols in order to change the value of token_num
    X.append(tokens['term_str'].reset_index())
        
    # Create copies of token table for each level of ngram, offset by 1, and 
    # merge with previous 
    for i in range(1, n):
        X.append(X[0].copy())
        X[i]['token_num'] = X[i]['token_num'] + i
        X[i] = X[i].merge(X[i-1], on=OHCO, how='left', sort=True).fillna('<s>')
        
    # Compress tables to unique ngrams with counts
    for i in range(0, n):
        X[i] = X[i].drop(OHCO, 1)
        cols = X[i].columns.tolist()
        X[i]['n'] = 0
        X[i] = X[i].groupby(cols).n.apply(lambda x: x.count()).to_frame()
        X[i].index.names = ['w{}'.format(j) for j in range(i+1)]
            
    # Return just the ngram tables
    return X


# ## Generate three models
# 
# Unigram, bigram, and trigram

# In[24]:


m1, m2, m3 = get_ngrams(tokens, n=3)


# In[29]:


m3.sample(10)


# ## Compute joint probabilities

# In[30]:


m1['p'] = m1['n'] / m1['n'].sum()
m2['p'] = m2['n'] / m2['n'].sum()
m3['p'] = m3['n'] / m3['n'].sum()


# In[31]:


m1.sort_values('p', ascending=False).head()


# In[32]:


m2.sort_values('p', ascending=False).head()


# In[37]:


m3.sort_values('p', ascending=False).head(15)


# ## Compute conditional probabilities
# 
# $p(w_1|w_0) = p(w_0, w_1) / p(w_0)$
# 
# $p(w_2|w_0,w_1) = p(w_0, w_1, w_2) / p(w_0, w_1)$

# In[38]:


m2m = m2.n.unstack().fillna(0).apply(lambda x: x / x.sum(), 1)


# In[45]:


m3m = m3.n.unstack().fillna(0).apply(lambda x: x / x.sum(), 1)


# # Explore

# In[47]:


m2m.loc[['he','she','it','anne','wentworth'], ['is','had','was','felt','thought','looked','said','saw']].style.background_gradient(cmap='Greens')


# In[48]:


m2m.loc[['he','she'],['felt','said']].style.background_gradient(cmap='Greens')


# # Generate Text
# 
# We use "stupid back-off" to account for missing ngrams.

# In[50]:


def generate_text(start_word='she', n=250):
    words = [start_word]
    for i in range(n):
        if len(words) == 1:
            w = m2m.loc[start_word]
            next_word = m2m.loc[start_word].sample(weights=w).index.values[0]
        elif len(words) > 1:
            bg = tuple(words[-2:])
            try:
                w = m3m.loc[bg]
                next_word = m3m.loc[bg].sample(weights=w).index.values[0]
            except KeyError:
                ug = bg[1]
                if ug == '<s>':
                    next_word = m1.sample(weights=m1.p).index[0]
                else:
                    w = m2m.loc[ug]
                    next_word = m2m.loc[ug].sample(weights=w).index.values[0]
        words.append(next_word)
    text = ' '.join(words)
    text = text.replace(' <s> <s>', '.') + '.'
    text = text.upper() # To give that telegraph message look :-)
    print(text)


# In[52]:


generate_text('the')


# In[53]:


generate_text('she')

