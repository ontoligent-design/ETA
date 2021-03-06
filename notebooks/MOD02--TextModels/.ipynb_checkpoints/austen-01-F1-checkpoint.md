---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.1'
      jupytext_version: 1.1.1
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

```python
import pandas as pd
import glob
```

```python
import sys
sys.path.append('/home/rca2t/Public/ETA/lib')
# import textman as tx
import seaborn as sns
```

```python
sns.set()
%matplotlib inline
```

```python
data_dir = '/home/rca2t/Public/ETA/data/austen'
OHCO = ['title_id', 'chap_num', 'para_num', 'token_num']
```

# Create corpus of documents from source docs

```python
# Import downloadd Gutenberg texts from source directory
texts = []
titles = []
for path in glob.glob(data_dir + "/*.txt"):
    
    # Get Gutenberg id -- CHANGE TO REFLECT NEW FORMAT
    guten_id = path.split('/')[-1].split('.')[0]
        
    # Import file into a dataframe
    epub = open(path, 'r', encoding='utf-8-sig').readlines()
    df = pd.DataFrame(epub, columns=['line_str'])
    df.index.name = 'line_num'
    df.line_str = df.line_str.str.strip()
    del(epub)
        
    # Extract title of work from first line
    title = df.loc[0].line_str.replace('The Project Gutenberg EBook of ', '')
    titles.append((guten_id, title))
    title_id = len(titles) - 1
    print(guten_id, title_id, title)
    
    # Remove Gutenberg's front and back matter
    a = df.line_str.str.match(r"\*\*\*\s*START OF (THE|THIS) PROJECT")
    b = df.line_str.str.match(r"\*\*\*\s*END OF (THE|THIS) PROJECT")
    an = df.loc[a].index[0]
    bn = df.loc[b].index[0]
    df = df.iloc[an + 1 : bn - 2]
    
    # Chunk by chapter
    chap_lines = df.line_str.str.match(r"\s*chapter", case=False)
    chap_nums = [i+1 for i in range(df.loc[chap_lines].shape[0])]
    df.loc[chap_lines, 'chap_num'] = chap_nums
    df.chap_num = df.chap_num.ffill()
    df = df.loc[~df.chap_num.isna()] # Remove chapter heading lines
    df = df.loc[~chap_lines] # Remove everything before Chapter 1
    df.chap_num = df.chap_num.astype('int') # Convert chap_num from float to int
    df = df.groupby(['chap_num']).line_str.apply(lambda x: '\n'.join(x)).to_frame() # Make big string
    
    # Gather paragraphs 
    df = df['line_str'].str.split(r'\n\n+', expand=True).stack()\
        .to_frame().rename(columns={0:'para_str'})
    df.index.names = OHCO[1:3] # ['chap_num', 'para_num']
    df['para_str'] = df['para_str'].str.replace(r'\n', ' ').str.strip()
    df = df[~df['para_str'].str.match(r'^\s*$')] # Remove empty paragraphs
    df['title_id'] = title_id
    
    # Add OHCO index
    df = df.reset_index().set_index(OHCO[:3])

    # Add to corpus
    texts.append(df)
```

```python
# Combine all texts into a corpus
corpus = pd.concat(texts)
del(texts)
```

```python
corpus.head()
```

# Create library table

```python
library = pd.DataFrame(titles, columns=['guten_id', 'gut_str'])
library.index.name  = 'work_id'
```

```python
library
```

```python
library.gut_str = library.gut_str.str.replace('The Project Gutenberg eBook, ', '')
```

```python
library[['title', 'author']] = library['gut_str'].str.split(', by', expand=True)
```

```python
library
```

```python
corpus.iloc[0].para_str
```

```python
corpus.head()
```

# Create tokens table

```python
tokens = corpus['para_str'].str.split(r'\W+', expand=True).stack().to_frame()\
        .rename(columns={0:'token_str'})
tokens.index.names = OHCO
```

```python
# puncs = corpus['para_str'].str.split(r'\w+', expand=True).stack().to_frame()\
#         .rename(columns={0:'punc'})
# puncs.index.names = OHCO
# pd.concat([tokens, puncs], 1)
# puncs.head(10)
```

```python
tokens['term_str'] = tokens.token_str.str.lower().str.replace(r'_+', ' ').str.replace(r'\s+', ' ').str.strip()
```

```python
tokens = tokens[tokens.term_str != '']
```

# Create vocabulary table

```python
vocab = tokens.term_str.value_counts().to_frame().reset_index()\
    .rename(columns={'term_str':'term_count', 'index':'term_str'})
vocab = vocab.sort_values('term_str').reset_index(drop=True)
vocab.index.name = 'term_id'
```

```python
vocab.sort_values('term_count').tail()
```

```python
vocab.sort_values('term_count', ascending=False).head()
```

```python
vocab[['term_str','term_count']].sort_values('term_count').tail(50)\
    .plot(kind='barh', figsize=(5,15), x='term_str')
```

# Replace `term_str` with `term_id` in tokens table

```python
tokens['term_id'] = tokens.term_str.map(vocab.reset_index().set_index('term_str').term_id)
# tokens = tokens.drop('term_str', 1)
```

# Creat Doc-Term Matrix

```python
CHUNK = OHCO[:3] # By Paragraph (could be Chap, etc.)
```

```python
dtm = tokens.groupby(CHUNK + ['term_id']).term_id.count()\
    .to_frame().rename(columns={'term_id':'n'}).unstack()
dtm.columns = dtm.columns.droplevel(0)
dtm = dtm.fillna(0)
```

```python
dtm.head()
```

```python
dtm.sum().sort_values(ascending=False).head()
```

# Add some stats to vocab table

Here we take note of various statistics we learn from the tokens table and apply them to the vocab table

```python
import numpy as np
```

```python
vocab['tf'] = vocab['term_count'] / vocab['term_count'].sum()
vocab['std'] = dtm.std()
vocab['mean'] = dtm.mean()
vocab['max'] = dtm.max()
vocab['df'] = dtm[dtm > 0].count()
vocab['idf'] = np.log10(corpus.shape[0] / vocab.df)
```

```python
from scipy.stats import entropy
vocab['entropy'] = (dtm / dtm.sum()).apply(entropy)
```

```python
vocab[vocab.term_count >= 10].sort_values('idf', ascending=False).head()
```

```python
vocab.sort_values('entropy', ascending=False).head(20)
```

```python
vocab.plot(kind='scatter', x='idf', y='entropy', figsize=(10,10))
```

```python
from scipy.stats import linregress
```

```python
slope, intercept, r, p, stderr = linregress(vocab.idf, vocab.entropy)
```

```python
vocab['test'] = (-1 * vocab.entropy) + intercept
```

```python
vocab.plot(kind='scatter', x='idf', y='test', figsize=(10,10))
```

```python
vocab.plot(kind='scatter', x='idf', y='entropy', figsize=(10,10))
```

```python
# Plot
```

# Word lengths

```python
vocab['len'] = vocab.term_str.str.len()
```

```python
vocab.sort_values('len', ascending=False).head(50)
```

```python
vocab['len'].value_counts().sort_index().plot(kind='bar')
```

```python
vocab['len'].describe()
```

# Save the data

```python
library.to_csv(data_dir + '/austen-library.csv', )
corpus.to_csv(data_dir + '/austen-corpus.csv')
tokens.to_csv(data_dir + '/austen-tokens.csv')
vocab.to_csv(data_dir + '/austen-vocab.csv')
```

```python
import sqlite3
with sqlite3.connect(data_dir + '/austen.db') as db:
    library.to_sql('library', db, index=True, if_exists='replace')
    corpus.to_sql('corpus', db, index=True, if_exists='replace')
    tokens.to_sql('tokens', db, index=True, if_exists='replace')
    vocab.to_sql('vocab', db, index=True, if_exists='replace')
```

```python
vocab.head()
```

```python
dtm.head()
```

```python
dtm.sum(1).plot.kde()
```

```python

```
