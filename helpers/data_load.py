import pdfplumber
import os
import string
import pandas as pd
import numpy as np
import string
from nltk.corpus import stopwords
import nltk

nltk.download("stopwords")


def read_script(
    pdf_path,
    pdf_folder="data/pdf_scripts",
    txt_folder="data/txt_scripts",
    return_script=True,
):
    """
    Takes in a pdf path
    of the script and transforms
    it into a .txt file to
    be process.
    """

    # define the list
    all_txt = []

    # define full path
    pdf_full_path = os.path.join(pdf_folder, pdf_path)

    # load the pdf
    with pdfplumber.open(pdf_full_path) as pdf:

        all_pages = pdf.pages
        print(f"Loaded {pdf_path}")
        print(f"Total pages: {len(all_pages)}")

        for pg in all_pages:

            # extract the text
            all_txt.append(pg.extract_text())

    # join all pages content
    all_txt = "\n".join(all_txt)

    # output the file
    output_fn = pdf_path.split(".pdf")[0] + ".txt"
    output_path = os.path.join(txt_folder, output_fn)

    with open(output_path, "w") as f:

        f.write(all_txt)

    print(f"Succesfully output script in: {output_path}")

    if return_script:
        return all_txt
    else:
        return


def pre_process_script(txt_path, txt_folder="data/txt_scripts"):
    """
    Takes in a path txt path of the
    script that was read from the 
    PDF file and then cleans it by
    removing any unnecesary data.
    
    """

    # get text file
    txt_path = os.path.join(txt_folder, txt_path)

    # read the file
    with open(txt_path, "r") as f:

        data = f.readlines()

    cleanned_data = []

    for line in data:

        if "\n" in line[-1:]:
            # remove spaces
            cleaned_line = line[:-1]
        else:
            cleaned_line = line

        # if it's a page line skip
        if "page" in cleaned_line.lower():

            continue

        # remove all the names of actors and scenes
        if cleaned_line.isupper():

            continue

        # remove asterisks
        if "*" in cleaned_line:

            # remove the star
            cleaned_line = cleaned_line.replace("*", "")

            if cleaned_line == "":

                continue

        if "www" in cleaned_line:
            continue

        # remove just numeric lines
        if cleaned_line.isdigit():

            continue

        if cleaned_line == "":

            continue

        # append to the cleanned data
        cleanned_data.append(cleaned_line.lower())

    # join all lines into one script
    joinned_text = " ".join(cleanned_data)

    return joinned_text


def get_words_df(txt_script, movie_name):
    """
    Takes in a txt script 
    and extracts all the words.
    It then removes any stopwords
    and punctuation.
    """

    all_words = txt_script.split(" ")

    # remove punctuation
    table = str.maketrans("", "", string.punctuation)
    clean_words = [word.translate(table) for word in all_words]

    # remove white space
    clean_words = [word for word in clean_words if word.strip() != ""]

    # remove stopwords
    stop_words = set(stopwords.words("english"))
    clean_words = [w for w in clean_words if not w in stop_words]

    # # add to a dataframe
    df_words = pd.DataFrame(clean_words, columns=["words"])

    is_swear = []
    swear_col = []
    swear_words = [
        "fuc",
        "shit",
        "crap",
        "asshole",
        "cunt",
        "dick",
        "pussy",
        "bitch",
        "cock",
        "dammit",
        "damn",
    ]

    for word in clean_words:
        is_sw = False

        for sw in swear_words:

            if not (is_sw) and (sw in word) and ("cocktail" not in word):

                is_sw = True
                is_swear.append(1)
                swear_col.append(sw)
                continue

        if not (is_sw):
            is_swear.append(0)
            swear_col.append("NA")
    # # add the swear columns
    df_words["is_swear"] = is_swear
    df_words["swear_col"] = swear_col
    df_words["cum_swear"] = df_words["is_swear"].cumsum()
    df_words["movie_progress"] = np.linspace(0, 1, num=df_words.shape[0])
    df_words["movie_name"] = movie_name

    # print total
    print(f"Total Swear Words : {df_words['is_swear'].sum()}")

    return df_words
