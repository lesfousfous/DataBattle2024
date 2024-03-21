import json
from googletrans import Translator
import mysql.connector
from mysql.connector import MySQLConnection
from configparser import ConfigParser
import pandas as pd
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import nltk


class Database:

    def __init__(self) -> None:
        config = ConfigParser()
        config.read("config.ini")
        self.database_connection = Database._init_database_connection(config)

    def _init_database_connection(config_file: ConfigParser) -> MySQLConnection:
        mydb = mysql.connector.connect(
            host=config_file['mysqlDB']['host'],
            user=config_file['mysqlDB']['user'],
            password=config_file['mysqlDB']["password"],
            database=config_file['mysqlDB']['db'],
        )
        return mydb


class Table():

    def __init__(self, name: str, database: Database) -> None:
        self.database_connection = database.database_connection
        self.name = name
        self.dataframe = self._load_solution_data_from_db()

    def _load_solution_data_from_db(self):
        data = {}
        keys = self._load_all_keys_of_table()
        for x in keys:
            data[x] = self._get_attribute(x)

        dataframe = Table._dict_to_dataframe(data)
        return dataframe

    def _dict_to_dataframe(dictionnary):
        dataframe = pd.DataFrame(dictionnary)
        return dataframe

    def _get_attribute(self, attribute_name):
        cursor = self.database_connection.cursor()
        cursor.execute(f"SELECT {attribute_name} FROM {self.name};")
        attribute_data = [column_name[0] for column_name in cursor.fetchall()]
        cursor.close()
        return attribute_data

    def _load_all_keys_of_table(self):
        cursor = self.database_connection.cursor()
        cursor.execute(f"SELECT column_name FROM information_schema.columns \
                          WHERE table_schema = 'kerdos'\
                          AND table_name = '{self.name}';")
        keys = [column_name[0] for column_name in cursor.fetchall()]
        cursor.close()
        return keys

    def __str__(self) -> str:
        return self.dataframe.__str__()


class Preprocessor:
    """Removes useless information from text (punctuation, stopwords, lemmatization)"""

    def _pipeline(self, text: str):
        text = text.lower()
        text = self._remove_punctuation(text)
        text = self._remove_stopwords(text)
        text = self._lemmatize_words(text)
        text = self._remove_specific_words(text)
        return text

    def __call__(self, text):
        return self._pipeline(text)

    def _remove_punctuation(self, text):
        """custom function to remove the punctuation"""
        return text.translate(str.maketrans('', '', string.punctuation))

    def _remove_stopwords(self, text):
        """custom function to remove the stopwords"""
        STOPWORDS = set(stopwords.words('english'))
        return " ".join([word for word in str(text).split() if word not in STOPWORDS])

    def _lemmatize_words(self, text):
        wordnet_map = {"N": wordnet.NOUN, "V": wordnet.VERB,
                       "J": wordnet.ADJ, "R": wordnet.ADV}
        lemmatizer = WordNetLemmatizer()
        pos_tagged_text = nltk.pos_tag(text.split())
        return " ".join([lemmatizer.lemmatize(word, wordnet_map.get(pos[0], wordnet.NOUN)) for word, pos in pos_tagged_text])

    def _remove_specific_words(self, text):
        BANNED_VOCAB = ["reduce", "optimize",
                        "improve", "increase", "optimized", "would", "like"]
        return " ".join([word for word in str(text).split() if word not in BANNED_VOCAB])


class SolutionsAndCategoriesData:

    def __init__(self, database: Database) -> None:
        self.database = database
        self.cursor = database.database_connection.cursor()
        self.solutions = self._init_solutions()
        self.data = self._init_classes()

    def _init_solutions(self):
        """Returns all list of all the solutions in the database and the id of the first category/techno above it"""
        self.cursor.execute("""SELECT traductiondictionnaire, numtechno, numsolution FROM tblsolution 
                    JOIN tbltechno ON codetechno = numtechno 
                    JOIN tbldictionnaire ON numsolution = codeappelobjet
                    WHERE typedictionnaire='sol'
                    AND codelangue=2
                    AND indexdictionnaire=1""")
        all_solutions = self.cursor.fetchall()
        return all_solutions

    def _init_classes(self):
        """Organize all solutions within their category

        Returns:
            solutions_dict : Dictionnary of the following format {"class_index" : [{"text-label" : name of the class, "solution" : name of the solution}]}
        """
        class_ids = [category_id for _, category_id, _ in self.solutions]
        init_values = [{"class_name": "Aucune", "solutions": []}
                       for x in range(len(class_ids))]
        solutions_dict = dict((key, value)
                              for key, value in zip(class_ids, init_values))
        for solution_name, class_id, solution_id in self.solutions:
            parent_technologies = self._retrieve_parent_technos(class_id)
            class_name = " + ".join(parent_technologies[::-1])
            if class_name:
                solutions_dict[class_id]["class_name"] = class_name
            solutions_dict[class_id]["solutions"].append(
                (solution_id, solution_name))
            # print(f"Added {solution_name} to {class_name} / {class_id}")
        return solutions_dict

    def _retrieve_parent_technos(self, first_category_of_the_solution):
        techno_associe = []
        # 1 Getting the name of the first category associated with the solution and the id of the parent
        self.cursor.execute(
            f"""SELECT numtechno, traductiondictionnaire, codeparenttechno FROM tbltechno t
            JOIN tbldictionnaire d ON numtechno = codeappelobjet
            WHERE codelangue = 2 AND typedictionnaire = 'tec' AND codeappelobjet ={first_category_of_the_solution}""")
        techno = self.cursor.fetchall()
        if techno:  # If the first category isn't empty, add it to the list of categories the techno belongs to
            techno_associe.append(techno[0][1])
        while techno:  # While the last category has a parent, keep adding it to the list of categories the techno belongs to
            code_techno_parent = techno[0][2]
            self.cursor.execute(f"""
                          SELECT numtechno, traductiondictionnaire, codeparenttechno FROM tbltechno t
                          JOIN tbldictionnaire d ON numtechno = codeappelobjet
                          WHERE codelangue = 2 AND typedictionnaire = 'tec' 
                          AND indexdictionnaire = 1
                          AND codeappelobjet ={code_techno_parent}""")
            techno = self.cursor.fetchall()
            if techno:  # Don't add parent if it is null
                techno_associe.append(techno[0][1])
        return techno_associe

    def translate_data_to_file_for_gpt(self):
        translator = Translator()
        print("Translating...")
        with open("translated_data.txt", "w+") as f:
            for class_id in self.data.keys():
                class_name = self.data[class_id]["class_name"]
                class_name_translated = translator.translate(
                    class_name).text
                f.write(f"{class_id} : {class_name_translated}\n")
                solutions_translated = translator.translate(
                    self.data[class_id]["solutions"])
                for solution in solutions_translated:
                    f.write(f"{solution.text}\n")
                f.write("\n")

    def export_data_to_json(self):
        solutions_text = []
        solution_ids = []
        label = []
        label_text = []
        for class_id in self.data.keys():
            class_name = self.data[class_id]["class_name"]
            for solution in self.data[class_id]["solutions"]:
                solutions_text.append(solution[1])
                solution_ids.append(solution[0])
                label.append(class_id)
                label_text.append(class_name)
        translator = Translator()
        preprocessor = Preprocessor()
        print('Translating...')
        solutions_text = translator.translate(solutions_text, dest="en")
        solutions_text = [preprocessor(x.text) for x in solutions_text]
        label_text = translator.translate(label_text, dest="en")
        processed_label_text = [preprocessor(x.text) for x in label_text]
        unmodified_label_text = [x.text for x in label_text]
        dataset = {"solution_text": solutions_text,
                   "solution_ids": solution_ids,
                   "label": label,
                   "label_text": processed_label_text,
                   "base_label_text": unmodified_label_text}
        with open("./data/data.json", "w") as outfile:
            json.dump(dataset, outfile)


def read_gpt_to_file(infile, outfile, do_translate=False):
    with open(infile, "r") as f:
        file = f.readlines()
        labels = []
        label_texts = []
        questions_english = []
        for i in range(len(file)):
            if "Category" in file[i]:
                label, label_text = file[i].split(":")
                label = int(label.split(" ")[1])
            elif "Question" in file[i] or "Demand" in file[i]:
                questions_english.append(file[i+2])
                labels.append(label)
                label_texts.append(label_text)
                questions_english.append(file[i+3])
                labels.append(label)
                label_texts.append(label_text)
        if do_translate:
            translator = Translator()
            print('Translating...')
            question_fr = translator.translate(questions_english, dest="fr")
            question_fr = [x.text for x in question_fr]
            dataset = {"text": question_fr,
                       "label": labels, "label_text": label_texts}
        else:
            dataset = {"text": questions_english,
                       "label": labels, "label_text": label_texts}
        with open(outfile, "w+") as f:
            json.dump(dataset, f)


class DatabaseObject:
    db = Database()
    cursor = db.database_connection.cursor()


class Category(DatabaseObject):

    def __init__(self, technologies: 'list[Technology]') -> None:
        self.technologies = technologies

    def __str__(self) -> str:
        return str([str(techno) for techno in self.technologies])


class Technology(DatabaseObject):

    def __init__(self, id) -> None:
        self.id = id
        self.name = self._retrieve_name()
        self.description = self._retrieve_data(1)
        self.application = self._retrieve_data(2)
        self.impact_opex = self._retrieve_data(11)
        self.approche_systeme = self._retrieve_data(13)
        self.capex_cout_global = self._retrieve_data(8)
        self.caract_technique = self._retrieve_data(18)

    def _retrieve_data(self, indexdictionnaire):
        DatabaseObject.cursor.execute(
            f"""SELECT traductiondictionnaire FROM tbldictionnaire WHERE codeappelobjet = {self.id} AND codelangue = 2 and typedictionnaire = 'tec' and indexdictionnaire = {indexdictionnaire}""")
        data = DatabaseObject.cursor.fetchone()
        if data:
            return data[0]
        else:
            return "Aucune"

    def __str__(self) -> str:
        return f"{self.name} : {self.description}"


class Solution(DatabaseObject):

    def __init__(self, numsolution) -> None:
        self.id = numsolution
        self.category = self._category()
        self.cursor = DatabaseObject.cursor
        self.title = self._retrieve_data(1)
        self.description = self._retrieve_data(2)
        self.application = self._retrieve_data(5)
        self.bilan_energie = self._retrieve_data(6)
        self.regle_pouce_text = self._retrieve_data(10)
        self.difficultes = self._retrieve_data(9)
        self.gain_text = self._retrieve_data(11)
        self.effets_positifs = self._retrieve_data(12)

    def _category(self):
        # 1 Getting the name of the first category associated with the solution and the id of the parent
        self.cursor.execute(
            f"""SELECT codetechno FROM tblsolution WHERE numsolution = {self.id}""")
        technos = []
        techno = self.cursor.fetchone()
        print(f"First techno : {techno[0]}")
        if techno:  # If the first category isn't empty, add it to the list of categories the techno belongs to
            technos.append(techno[0])
        while techno:  # While the last category has a parent, keep adding it to the list of categories the techno belongs to
            self.cursor.execute(f"""
                          SELECT codeparenttechno FROM tbltechno t
                          JOIN tbldictionnaire d ON numtechno = codeappelobjet
                          WHERE codelangue = 2 
                          AND typedictionnaire = 'tec' 
                          AND indexdictionnaire = 1
                          AND codeappelobjet ={techno[0]}""")
            techno = self.cursor.fetchone()
            if techno:  # Don't add parent if it is null
                print(f"New techno : {techno[0]}")
                technos.append(techno[0])
        list_of_technos = [Technology(x) for x in technos][::-1]
        return Category(list_of_technos)

    def _retrieve_data(self, indexdictionnaire):
        DatabaseObject.cursor.execute(
            f"""SELECT traductiondictionnaire FROM tbldictionnaire WHERE codeappelobjet = {self.id} AND codelangue = 2 and typedictionnaire = 'sol' and indexdictionnaire = {indexdictionnaire}""")
        data = DatabaseObject.cursor.fetchone()
        if data:
            return data[0]
        else:
            return "Aucune"

    def __str__(self) -> str:
        return str(self.category)
