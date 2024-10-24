## Overlap of IGES and ASHG abstracts/talks

### Process

#### IGES

* Copied text from the provided IGES PDF into sublime text and did a regex findall to isolate abstract titles

  * `^(\d+\n.*\n.*\n.*\n)`
  * Affiliations were similar enough to titles that a simple pattern couldn't be isolated them from abstract titles, but ChatGPT can help here!
  * Unfortunately, ChatGPT cannot process the entire document (too long...)

* In batches of ~10 abstracts & affiliations, ChatGPT was prompted with: 

  > The following unstructured text contains both abstract titles and affiliations, please create a list of only abstract titles, please:
  >
  > <batch text>

  * Results in `IGES abstracts.txt`
  * Spot checked for accuracy



#### ASHG

* Abstracts provided [here](https://eppro01.ativ.me/src/EventPilot/php/express/web/planner.php?id=ASHG23)
  * Appear to include talk titles as well (from spot checking a few)

* Copied and Pasted titles to `ASHG abstracts.txt`



#### Overlap

* Results are too large to provide to ChatGPT for direct pairwise comparison. Python can be used to look at fuzzy matches between the two lists, however. This is simple enough to write, but I thought I'd let ChatGPT take a crack:

  *Me:*

  > I have two lists with similar abstract titles. Can you write some python code that determines the fuzzy match between the two lists and then creates a venn diagram of results? 

  *Response:*

  >To determine the fuzzy match between two lists of abstract titles and create a Venn diagram of the results, you can use Python with the help of the `fuzzywuzzy` library for fuzzy string matching and the `matplotlib-venn` library for plotting Venn diagrams. Here's a step-by-step guide:
  >
  >1. Install the required libraries if you haven't already. You can install them using pip:
  >
  >```
  >pip install fuzzywuzzy python-Levenshtein matplotlib-venn
  >```

  * Super helpful, even gives instructions on how to install the required packages! I would have picked `fuzzywuzzy` myself. It continues:

  >1. Import the necessary libraries.
  >2. Prepare two lists of abstract titles.
  >3. Use fuzzy string matching to identify similar titles between the two lists.
  >4. Create a Venn diagram to visualize the results.
  >
  >Here's the Python code to accomplish this:
  >
  >```
  >from fuzzywuzzy import fuzz
  >from matplotlib_venn import venn2
  >import matplotlib.pyplot as plt
  >
  ># Sample lists of abstract titles
  >list1 = [
  >    "Introduction to Machine Learning",
  >    "Deep Learning for Beginners",
  >    "Natural Language Processing in Python",
  >    "Data Science in Action",
  >]
  >
  >list2 = [
  >    "Machine Learning Basics",
  >    "Introduction to NLP",
  >    "Data Science Essentials",
  >    "Understanding Deep Learning",
  >]
  >
  ># Define a similarity threshold (adjust as needed)
  >threshold = 80
  >
  ># Find similar titles using fuzzy string matching
  >similar_titles = set()
  >for title1 in list1:
  >    for title2 in list2:
  >        if fuzz.token_sort_ratio(title1, title2) >= threshold:
  >            similar_titles.add(title1)
  >            similar_titles.add(title2)
  >
  ># Create a Venn diagram to visualize the results
  >venn2([set(list1), set(list2)], set_labels=("List 1", "List 2"))
  >plt.title("Fuzzy Matching of Abstract Titles")
  >plt.show()
  >
  ># Display the similar titles
  >print("Similar Abstract Titles:")
  >for title in similar_titles:
  >    print(title)
  >```
  >
  >In this code, we use the `fuzz.token_sort_ratio` function from `fuzzywuzzy` to calculate the similarity between abstract titles. Titles with a similarity score above the specified threshold (in this case, 80) are considered similar. The Venn diagram shows the overlap between the two lists, and the similar abstract titles are printed as well.
  >
  >Make sure to replace the sample abstract titles with your actual data. You can adjust the similarity threshold to control the fuzziness of the matching.

* Reviewing the code, ChatGPT created an algorithm of O(N*M), which for all-by-all comparison is about as good as you get. The output also looks sane. It even used example AI abstract titles! Let's give it a try. The only modification is to read in actual title files. 

  * See `Overlap.ipynb`

  * Fuzzing string matching here uses *Levenshtein Distance*, where **0** is completely fuzzy, and **100** is a perfect match. ChatGPT chose **80** here, which is a good threshold.

  * The code also uses *token set ratio* `fuzz.token_sort_ratio` to compare the two titles:

    * > In token sort ratio, the strings are tokenized and pre-processed by converting to lower case and getting rid of punctuation. The strings are then sorted alphabetically and joined together. Post this, the Levenshtein distance similarity ratio is calculated between the strings.
      >
      > ```python
      > Str1 = "My name is Ali"
      > Str2 = "Ali is my name!"
      > print(fuzz.token_sort_ratio(Str1,Str2))
      > > 100 match
      > ```

* The code works perfectly, even generating the following Venn diagram:

  <img src="https://snipboard.io/PjGr68.jpg" width=250px style="float:left">

  

* **However, there's a problem**:

  * ⇨ `venn2([set(list1), set(list2)], set_labels=("List 1", "List 2"))`
  * Using `set()` in the venn2 command defeats the purpose of fuzzy matching, since venn2 now does set matching, which resorts back to exact matches only!

* Lets fix this and then sweep the threshold value between 50 and 100, generating Venn Diagrams for each threshold and finally save the results. See the notebook for detals, but here's a diagram at threshold>70:

  <img src="https://snipboard.io/14o3O7.jpg" width=250px style="float:left">

  

  
  
  ## History of topics
  
  > I have another little ask: could you parse the titles of IGES meeting abstracts over the years and create a word cloud figure for each year? I'd like to show how the presentation topics have changed from year to year (in my Presidential address). You have this year's abstracts already. The previous 9 years abstracts are here: https://iges.memberclicks.net/meeting-abstracts. All of the abstracts were published in Genetic Epidemiology, and pdfs are available here (to get the pdfs for free you can log in via Stanford): https://onlinelibrary.wiley.com/action/doSearch?AllField=International+Genetic+Epidemiology+Society+abstracts
  
  ### Process
  
  1. Get all the pdfs, which had to be done manually. Additionally, PDFs were manually subsetted to just abstracts and text (no cover pages, etc.). Files in `data/IGES Abstract PDFs/subsetted`
  
  2. Authorize ChatGPT on the machine:  
      ```bash
      curl https://api.openai.com/v1/models \
        -H "Authorization: Bearer $OPENAI_API_KEY" \
        -H "OpenAI-Organization: org-Rb2ucXnHjEpJxHHko7aGiSPf"
      ```
  
      **Note: `$OPENAI_API_KEY`** is the secret API key generated from the ChatGPT website and was exported into the environment just before this command and before jupyter notebook was launched
  
  3. A pdf parsing python utility as installed
  
  4. Ran the notebook: `notebooks/History`, which creates a dataframe of year and abstract title
  
      * It takes about 20-30s to parse each page with **gpt-3.5-turbo-16K-0613** which takes about 1 hour to parse everything
  
  5. Had to do some post cleanup with regex:
  
      ```bash
       - ⇨ 
      (\d+\t\d+\t)\d+\.* ⇨ \1
      .*Titles.*\n ⇨ 
      (\d+\t\d+\t)ABSTRACTS ⇨ \1
      ```
  
      2018 to 2020
  
      ```
      \d+ \| (.*)\n 
      ```
  
      2021+
  
      ```^\d+\n.*
      
      ^\d+\n.*
      ```
  
  
  
  Had to remove ABSTRACT, Methods --- etc other section headers
  
  Also empty lines and other split titles
  
  
  
  
  
  
  
  