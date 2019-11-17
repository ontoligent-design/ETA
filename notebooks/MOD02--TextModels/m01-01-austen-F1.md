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

# Module 1: Text Into Data: Importing a Corpus

* DS 5001: Exploratory Text Analytics
* Raf Alvarado


# Set Up

```python
import pandas as pd
import glob
import seaborn as sns
```

```python
sns.set()
%matplotlib inline
```

```python
epub_dir = '/home/rca2t/Public/ETA/data/epubs/AUSTEN'
data_dir = '/home/rca2t/Public/ETA/data/'
OHCO = ['title_id', 'chap_num', 'para_num', 'sent_num', 'token_num']
```

# Create corpus of documents from source docs

```python
# Import downloaded Gutenberg texts from source directory

texts = []
titles = []
for path in glob.glob(epub_dir + "/*.txt"):
    
    guten_id = path.split('/')[-1]\
        .split('-pg')[-1]\
        .split('.')[0]
        
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
    df['title_id'] = title_id

    print(guten_id, title_id, title)

    # Remove Gutenberg's front and back matter
    a = df.line_str.str.match(r"\*\*\*\s*START OF (THE|THIS) PROJECT")
    b = df.line_str.str.match(r"\*\*\*\s*END OF (THE|THIS) PROJECT")
    an = df.loc[a].index[0]
    bn = df.loc[b].index[0]
    df = df.iloc[an + 1 : bn - 2]
    
    # Chunk by chapter
    chap_lines = df.line_str.str.match(r"\s*(chapter|letter)", case=False)
    chap_nums = [i+1 for i in range(df.loc[chap_lines].shape[0])]
    df.loc[chap_lines, 'chap_num'] = chap_nums
    df.chap_num = df.chap_num.ffill()
    df = df.loc[~df.chap_num.isna()] # Remove chapter heading lines
    df = df.loc[~chap_lines] # Remove everything before Chapter 1
    df.chap_num = df.chap_num.astype('int') # Convert chap_num from float to int
    df = df.groupby(OHCO[:2]).line_str.apply(lambda x: '\n'.join(x)).to_frame() # Make big string
    
    # Split into paragraphs 
    df = df['line_str'].str.split(r'\n\n+', expand=True).stack()\
        .to_frame().rename(columns={0:'para_str'})
    df.index.names = OHCO[:3]
    df['para_str'] = df['para_str'].str.replace(r'\n', ' ').str.strip()
    df = df[~df['para_str'].str.match(r'^\s*$')] # Remove empty paragraphs
    
    # Split into sentences
    df = df['para_str'].str.split(r'[.?!;]', expand=True).stack()\
        .to_frame().rename(columns={0:'sent_str'})
    df.index.names = OHCO[:4]
    df = df[~df['sent_str'].str.match(r'^\s*$')] # Remove empty paragraphs
        
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

```python
corpus.values
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
corpus.iloc[0].sent_str
```

# Regrouping


## By Paragraph

```python
PARAS = corpus.groupby(OHCO[:3]).sent_str.apply(lambda x: ' '.join(x))\
    .to_frame().rename(columns={'sent_str':'para_str'})
```

```python
PARAS.head()
```

## By Chapter

```python
CHAPS = corpus.groupby(OHCO[:2]).sent_str.apply(lambda x: '\n'.join(x))\
    .to_frame().rename(columns={'sent_str':'chap_str'})
```

```python
CHAPS.head()
```

## By Book

```python
BOOKS = corpus.groupby(OHCO[:1]).sent_str.apply(lambda x: ' '.join(x))\
    .to_frame().rename(columns={'sent_str':'book_str'})
```

```python
BOOKS.head()
```

# Create tokens table

```python
tokens = corpus['sent_str'].str.split(r'\W+', expand=True).stack().to_frame()\
        .rename(columns={0:'token_str'})
tokens.index.names = OHCO
```

```python
tokens['term_str'] = tokens.token_str.str.lower().str.replace(r'_+', ' ').str.replace(r'\s+', ' ').str.strip()
```

```python
tokens = tokens[tokens.term_str != '']
```

```python
tokens.head()
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
vocab[['term_str', 'term_count']]\
    .sort_values('term_count').tail(50)\
    .plot(kind='barh', figsize=(5,15), x='term_str')
```

# Replace `term_str` with `term_id` in tokens table

```python
tokens['term_id'] = tokens.term_str.map(vocab.reset_index().set_index('term_str').term_id)
# tokens = tokens.drop('term_str', 1)
```

# Add some stats to vocab table


## Term Frequency

Actually, this is relative frequency

```python
vocab['tf'] = vocab['term_count'] / vocab['term_count'].sum()
```

## Term lengths

```python
vocab['len'] = vocab.term_str.str.len()
```

```python
vocab.sort_values('len', ascending=False).head(20)
```

```python
vocab['len'].value_counts().sort_index().plot(kind='bar')
```

```python
vocab['len'].describe()
```

# Save the data

```python
library.to_csv(data_dir + '/austen-library.csv')
corpus.to_csv(data_dir + '/austen-corpus.csv')
tokens.to_csv(data_dir + '/austen-tokens.csv')
tokens['term_id'].to_csv(data_dir + '/austen-tokens-light.csv')
vocab.to_csv(data_dir + '/austen-vocab.csv')
```

```python

```
