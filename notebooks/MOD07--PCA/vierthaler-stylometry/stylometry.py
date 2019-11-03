'''
This script will perform PCA-based stylometric analysis on any files loaded
into a corpus folder found in the same directory.
'''

############################
# Load necessary libraries #
############################

import re, os, sys, platform, json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from sklearn.decomposition import PCA

# Plotting libraries
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.font_manager
import matplotlib.colors

#########################
# Adjustable Parameters # 
#########################
# Size of n-grams:
ngrams = 1 # 1 will look at one character at a time, 2 will look at two, etc. # integer

# Limit the number of words to look at
commonWords = 500 # Integer. Set to None if you want to look at all words or use custom vocab

# Do you want to use a set vocabulary? If so, provide set limitVocab to True
# and provide a filename for limitVocabularyFile.
limitVocab = False # True or False

# This value is only read if limitVocab is set to True.
limitVocabularyFile = "vocab.txt"

# Types of labels for documents in the corpus
labelTypes = ('author', 'title', 'section', 'genre') # tuple with strings

# Index of label used to set Color:
colorValue = 3 # Index of label to use for color (integer). Here 2 points to "siku"

# Index of label to use for plot labels (if points are labeled)
labelValue = 0 # Index of label to use for labels (integer). Here 0 points to "title"

# Point size (integer)
pointSize = 8

# Show point labels (add labels for each text):
pointLabels = False # True or False

# Plot loadings (write the characters tot he plot)
plotLoadings = False # True or False

# Hide points (useful for seeing loadings better):
hidePoints = False # True or False

# Output file info (dimensions are in inches (width, height)):
outputDimensions = (10, 7.5) # Tuple of integers or floats

# Output file extension determines output type. Save as a pdf if you want to edit in illustator
# PDF Output on mac is very large, but just opening and saving a copy in illustrator will fix this
outputFile = "myfigure.png"


##################################
# Adjustable, but can be ignored #
##################################

# How many components?
pcaComponents = 2 # More than two is useful for digging even deeper in the data

# Input folder
corpusFolder = "corpus"

# File with items to remove from consideration (each item to remove is on a line):
removeItemsFile = "remove.txt"


###########
###########
###########
'''
Nothing beyond this point in the script needs any adjustment, but feel free to
explore it and make changes as you see fit! Changes will just require a bit
more work to integrate.
'''
###########
###########
###########


####################
# Type Enforcement #
####################

# This section enforces the input values for all the adjustable variables. This
# is to make sure the script isn't run incorrectly.

# function to check values
def valueChecker(varname, typeofobj, value):
    if type(typeofobj) == type:
        if typeofobj == bool and type(value) != typeofobj:
            print(f"{varname} must be a {typeofobj} (True or False). Please fix to run script.")
            sys.exit()
        if type(value) != typeofobj:
            print(f"{varname} must be {typeofobj}. Please fix to run script.")
            sys.exec_info()
            sys.exit() 
    elif type(typeofobj) == tuple:
        if type(value) != typeofobj[0] and type(value) != typeofobj[1]:
            print(f"{varname} must be {typeofobj[0]} or {typeofobj[1]}. Please fix to run script.")
            sys.exit() 

# check values
valueChecker('ngrams', int, ngrams)
valueChecker('commonWords', (int, None), commonWords)
valueChecker('limitVocab', bool, limitVocab)
valueChecker('colorValue', int, colorValue)
valueChecker('labelValue', int, labelValue)
valueChecker('pointSize', int, pointSize)
valueChecker('pointLabels', bool, pointLabels)
valueChecker('plotLoadings', bool, plotLoadings)
valueChecker('hidePoints', bool, hidePoints)
valueChecker('outputFile', str, outputFile)
valueChecker('pcaComponents', int, pcaComponents)
valueChecker('corpusFolder', str, corpusFolder)
valueChecker('removeItemsFile', str, removeItemsFile)

# check tuples and internal values
if type(labelTypes) != tuple:
    print('labelTypes must be a tuple. Please fix to run script.')
    sys.exit()
else:
    for lab in labelTypes:
        valueChecker('labelType item', str, lab)

if type(outputDimensions) != tuple:
    print(f"outputDimensions must be {tuple}. Please fix to run the script")
else:
    for d in outputDimensions:
        valueChecker("outerDimension value", (float, int), d)

# Load in external files
try:
    removeItems = []
    with open(removeItemsFile, "r", encoding='utf8') as rf:
        removeItems = [item.strip() for item in rf.read().split("\n") if item != ""]
except FileNotFoundError:
    print(f"No file named {removeItemsFile} found. Please check filename or create the file.")
    sys.exit()

if limitVocab == True:
    valueChecker('limitVocabularyFile', str, limitVocabularyFile)
    try:
        limitVocabulary = [] 
        with open(limitVocabularyFile, "r", encoding='utf8') as rf:
            limitVocabulary = [item.strip() for item in rf.read().split("\n") if item != ""]
        if commonWords:
            print(f"You are limiting analysis to the {commonWords} most common words but also using a set vocabulary.")
            print("If you want to avoid unexpected behavior, set commonWords to None when limiting vocab.")
    except FileNotFoundError:
        print(f"No file named {limitVocabularyFile} found. Please check filename or create the file")
        print("Defaulting to no limit on the vocabulary")       
        limitVocabulary = None
else:
    limitVocabulary = None

# Ensure corpus folder exists
if not os.path.isdir(corpusFolder):
    print(f"Could not find the corpus folder '{corpusFolder}'. Please double check.")
    sys.exit()


########################
# Function definitions #
########################

# Function to clean the text. Remove desired characters and white space.
def clean(text, removeitems):
    for item in removeitems:
        text = text.replace(item, "")
    text = re.sub("\s+", " ", text)
    return text

##############
# Load Texts #
##############

print("Loading, cleaning, and tokenizing")
# Go through each document in the corpus folder and save info to lists
texts = []
labels = []

for root, dirs, files in os.walk(corpusFolder):
    for i, f in enumerate(files):
        if f not in {'.DS_Store'}:
            # add the labels to the label list
            labels.append(f[:-4].split("_"))

            # Open the text, clean it, and tokenize it
            with open(os.path.join(root,f),"r", encoding='utf8', errors='ignore') as rf:
                texts.append(clean(rf.read(), removeItems))
            
            if i == len(files) - 1:
                print(f"\r{i+1} of {len(files)} processed", end='\n', flush=True)
            else:
                print(f"\r{i+1} of {len(files)} processed", end='', flush=True)

####################
# Perform Analysis #
####################

print("Vectorizing")
countVectorizer = TfidfVectorizer(max_features=commonWords, use_idf=False, vocabulary=limitVocabulary,  ngram_range=(ngrams, ngrams))
countMatrix = countVectorizer.fit_transform(texts)
print("Normalizing values")
countMatrix = normalize(countMatrix)
countMatrix = countMatrix.toarray()

print("Performing PCA")
# Lets perform PCA on the countMatrix:
pca = PCA(n_components=pcaComponents)
myPCA = pca.fit_transform(countMatrix)


##############
# Plot Setup #
##############

print("Setting plot info")
# set the plot size
plt.figure(figsize=outputDimensions)

# find all the unique values for each of the label types
uniqueLabelValues = [set() for i in range(len(labelTypes))]
for labelList in labels:
    for i, label in enumerate(labelList):
        uniqueLabelValues[i].add(label)

# create color dictionaries for all labels
colorDictionaries = []
for uniqueLabels in uniqueLabelValues:
    colorpalette = sns.color_palette("husl",len(uniqueLabels)).as_hex()
    colorDictionaries.append(dict(zip(uniqueLabels,colorpalette)))

# Now we need the Unique Labels
uniqueColorLabels = list(uniqueLabelValues[colorValue])
# Let's get a number for each class
numberForClass = [i for i in range(len(uniqueColorLabels))]

# Make a dictionary! This is new sytax for us! It just makes a dictionary where
# the keys are the unique years and the values are found in numberForClass
labelForClassNumber = dict(zip(uniqueColorLabels,numberForClass))

# Let's make a new representation for each document that is just these integers
# and it needs to be a numpy array
textClass = np.array([labelForClassNumber[lab[colorValue]] for lab in labels])


# Make a list of the colors
colors = [colorDictionaries[colorValue][lab] for lab in uniqueColorLabels]

if hidePoints:
    pointSize = 0

###################
# Create the plot #
###################

print("Plotting texts")
for col, classNumber, lab in zip(colors, numberForClass, uniqueColorLabels):
    plt.scatter(myPCA[textClass==classNumber,0],myPCA[textClass==classNumber,1],label=lab,c=col, s=pointSize)

# Let's label individual points so we know WHICH document they are
if pointLabels:
    print("Adding Labels")
    for lab, datapoint in zip(labels, myPCA):
        plt.annotate(str(lab[labelValue]),xy=datapoint)

# Let's graph component loadings
vocabulary = countVectorizer.get_feature_names()
loadings = pca.components_
if plotLoadings:
    print("Rendering Loadings")    
    for i, word in enumerate(vocabulary):
        plt.annotate(word, xy=(loadings[0, i], loadings[1,i]))
    

# Let's add a legend! matplotlib will make this for us based on the data we 
# gave the scatter function.
plt.legend()
plt.savefig(outputFile)


############################################
# Output data for JavaScript Visualization #
############################################

data = []
for datapoint in myPCA:
    pcDict = {}
    for i, dp in enumerate(datapoint):
        pcDict[f"PC{str(i + 1)}"] = dp
    data.append(pcDict)

jsLoadings = []
for i, word in enumerate(vocabulary):
    temploading = {}
    for j,dp in enumerate(loadings):
        temploading[f"PC{str(j+1)}"] = dp[i]
    jsLoadings.append([word, temploading])

colorDictionaryList = []
for cd in colorDictionaries:
    cdlist = [v for v in cd.values()]
    colorDictionaryList.append(cdlist)

colorstrings = json.dumps(colorDictionaryList)
labelstrings = json.dumps(labels)
valuetypes = json.dumps([k for k in data[0].keys()])
datastrings = json.dumps(data)

limitedlabeltypes = []
for i, t in enumerate(labelTypes):
    if len(uniqueLabelValues[i]) <= 20:
        limitedlabeltypes.append(t)

cattypestrings = json.dumps(limitedlabeltypes)
loadingstrings = json.dumps(jsLoadings)
stringlist = [f"var colorDictionaries = {colorstrings};", f"var labels = {labelstrings};",
            f"var data = {datastrings};", f"var categoryTypes = {list(labelTypes)};", 
            f"var loadings = {jsLoadings};", f"var valueTypes = {valuetypes};",
            f"var limitedCategories = {limitedlabeltypes};",
            f"var activecatnum = {colorValue};", f"var activelabelnum = {labelValue};"]


with open("data.js", "w", encoding="utf8") as wf:
    wf.write("\n".join(stringlist))



# Show the plot
plt.show()
