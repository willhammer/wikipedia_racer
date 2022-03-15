from itertools import chain
from nltk.corpus import wordnet
import wikipediaapi
import wikipedia
import sys

wiki_wiki = wikipediaapi.Wikipedia('en')

def get_synonyms(word):
    word_synonyms = wordnet.synsets(word)
    lemmas = set(chain.from_iterable([word.lemma_names() for word in word_synonyms]))
    lemmas.remove(word)
    return lemmas

def get_closest_word(word, word_set):
    word_synsets = wordnet.synsets(word)
    if len(word_synsets) < 1:
        return None, float("inf")

    word_synset = wordnet.synsets(word)[0]
    closest_dist = float("inf")
    closest_word = word

    for check_word in word_set:
        check_word_synsets = wordnet.synsets(check_word)
        if len(check_word_synsets) == 0:
            continue

        check_word_synset = check_word_synsets[0];
        temp_dist = word_synset.shortest_path_distance(check_word_synset)
        #print("dist between " + word + " and " + check_word + " is " + str(temp_dist))
        if temp_dist is not None and temp_dist < closest_dist:
            closest_dist = temp_dist
            closest_word = check_word

    if len(word_set) == 1 and word_set[0].__contains__(word):
        closest_dist -= 100

    return closest_word, closest_dist

def get_link_words(page_link):
    tokens = str.split(page_link)

    if tokens.__contains__("(disambiguation)"):
        tokens.remove("(disambiguation)")

    return tokens

def get_best_link(current_word, search_word):

    closest_link = current_word
    closest_dist = float("inf")

    for search_result in wikipedia.search(current_word):
        page_py = wiki_wiki.page(search_result)
        print(page_py.title)
        if current_word.lower().__contains__(search_word):
            print(page_py.links);

        for page_link in page_py.links:
            #print('--------------------')

            link_words = get_link_words(page_link)
            temp_closest_word, temp_closest_dist = get_closest_word(search_word, link_words)
            if temp_closest_dist < 0 and temp_closest_word.__contains__("(disambiguation)"):
                temp_closest_dist += 50

            #print(page_link + ': CLOSEST WORD: ' + temp_closest_word + ' at dist ' + str(temp_closest_dist))
            if temp_closest_dist < closest_dist:
                print("current best: " + page_link + " from " + page_py.title)
                closest_link = page_link
                closest_dist = temp_closest_dist

    print("========================BEST LINK ===========================")
    try:
        print(current_word + " " + wiki_wiki.page(current_word).fullurl)
    except:
        pass

    return closest_link

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("the incorrect num args provided. please provide a start word and a target word")
        sys.exit()

    start_word = sys.argv[1]
    start_word = start_word.capitalize()

    search_word = sys.argv[2]
    search_word = search_word.capitalize()

    print("starting with " + start_word + " and looking for " + search_word)
    current_word = start_word

    while not current_word == search_word:
        current_word = get_best_link(current_word, search_word)

    print(wiki_wiki.page(current_word).fullurl)