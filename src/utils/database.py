import mysql.connector
from mysql.connector import MySQLConnection
from configparser import ConfigParser
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import nltk
from bs4 import BeautifulSoup
import torch


class Database:

    def __init__(self) -> None:
        config = ConfigParser()
        config.read("config.ini")
        self.database_connection = Database._init_database_connection(config)

    def _init_database_connection(config_file: ConfigParser) -> MySQLConnection:
        print("COnnection")
        mydb = mysql.connector.connect(
            host=config_file['mysqlDB']['host'],
            user=config_file['mysqlDB']['user'],
            password=config_file['mysqlDB']["password"],
            database=config_file['mysqlDB']['db'],
            ssl_disabled=True,
        )
        return mydb


db = Database()


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


# class SolutionsAndCategoriesData:

#     def __init__(self, database: Database) -> None:
#         self.database = database
#         self.cursor = database.database_connection.cursor()
#         self.solutions = self._init_solutions()
#         self.data = self._init_classes()

#     def _init_solutions(self):
#         """Returns all list of all the solutions in the database and the id of the first category/techno above it"""
#         self.cursor.execute("""SELECT traductiondictionnaire, numtechno, numsolution FROM tblsolution
#                     JOIN tbltechno ON codetechno = numtechno
#                     JOIN tbldictionnaire ON numsolution = codeappelobjet
#                     WHERE typedictionnaire='sol'
#                     AND codelangue=2
#                     AND indexdictionnaire=1""")
#         all_solutions = self.cursor.fetchall()
#         return all_solutions

#     def _init_classes(self):
#         """Organize all solutions within their category

#         Returns:
#             solutions_dict : Dictionnary of the following format {"class_index" : [{"text-label" : name of the class, "solution" : name of the solution}]}
#         """
#         class_ids = [category_id for _, category_id, _ in self.solutions]
#         init_values = [{"class_name": "Aucune", "solutions": []}
#                        for x in range(len(class_ids))]
#         solutions_dict = dict((key, value)
#                               for key, value in zip(class_ids, init_values))
#         for solution_name, class_id, solution_id in self.solutions:
#             parent_technologies = self._retrieve_parent_technos(class_id)
#             class_name = " + ".join(parent_technologies[::-1])
#             if class_name:
#                 solutions_dict[class_id]["class_name"] = class_name
#             solutions_dict[class_id]["solutions"].append(
#                 (solution_id, solution_name))
#         return solutions_dict

#     def _retrieve_parent_technos(self, first_category_of_the_solution):
#         techno_associe = []
#         # 1 Getting the name of the first category associated with the solution and the id of the parent
#         self.cursor.execute(
#             f"""SELECT numtechno, traductiondictionnaire, codeparenttechno FROM tbltechno t
#             JOIN tbldictionnaire d ON numtechno = codeappelobjet
#             WHERE codelangue = 2 AND typedictionnaire = 'tec' AND codeappelobjet ={first_category_of_the_solution}""")
#         techno = self.cursor.fetchall()
#         if techno:  # If the first category isn't empty, add it to the list of categories the techno belongs to
#             techno_associe.append(techno[0][1])
#         while techno:  # While the last category has a parent, keep adding it to the list of categories the techno belongs to
#             code_techno_parent = techno[0][2]
#             self.cursor.execute(f"""
#                           SELECT numtechno, traductiondictionnaire, codeparenttechno FROM tbltechno t
#                           JOIN tbldictionnaire d ON numtechno = codeappelobjet
#                           WHERE codelangue = 2 AND typedictionnaire = 'tec'
#                           AND indexdictionnaire = 1
#                           AND codeappelobjet ={code_techno_parent}""")
#             techno = self.cursor.fetchall()
#             if techno:  # Don't add parent if it is null
#                 techno_associe.append(techno[0][1])
#         return techno_associe


class DatabaseObject:
    cursor = db.database_connection.cursor(buffered=True)

    def clean_up_text(text_extraction_func) -> str:
        """A decorator I can just add to clean up the text that comes out of the database

        Args:
            text_extraction_func : a function that query the database for some text

        Returns:
            str: Cleaned up text
        """
        def wrapper(*args):
            text = text_extraction_func(*args)
            soup = BeautifulSoup(text, 'html.parser')

            # Extracting and joining all non-empty text
            extracted_text = ' '.join(soup.stripped_strings)
            return extracted_text
        return wrapper


class Category(DatabaseObject):

    def __init__(self, technologies: 'list[Technology]') -> None:
        self.technologies = technologies

    def get_solutions(self):
        techno_id = self.technologies[-1].id
        DatabaseObject.cursor.execute(
            f"""SELECT numsolution FROM tblsolution WHERE codetechno = {techno_id}""")
        solutions = [SolutionDB(x[0])
                     for x in DatabaseObject.cursor.fetchall()]
        DatabaseObject.cursor.execute(
            f"""SELECT numtechno FROM tbltechno WHERE codeparenttechno = {techno_id}""")
        techno_children = [Technology(child[0])
                           for child in DatabaseObject.cursor.fetchall()]
        while techno_children:
            for child in techno_children:
                solutions.extend(child.get_solutions())
            DatabaseObject.cursor.execute(
                f"""SELECT numtechno FROM tbltechno WHERE codeparenttechno = {child.get_id()}""")
            techno_children = [Technology(child[0])
                               for child in DatabaseObject.cursor.fetchall()]
        return solutions

    def get_technologies(self):
        return self.technologies

    def get_name(self):
        try:
            return self.name
        except AttributeError:
            self.name = " + ".join([techno.get_name()
                                   for techno in self.technologies[1:]])
            return self.name

    def __str__(self) -> str:
        # We don't keep the base category Aucune
        return self.get_name()


class Technology(DatabaseObject):

    def __init__(self, id) -> None:
        self.id = id

    @DatabaseObject.clean_up_text
    def _retrieve_data(self, indexdictionnaire):
        DatabaseObject.cursor.execute(
            f"""SELECT traductiondictionnaire FROM tbldictionnaire WHERE codeappelobjet = {self.id} AND codelangue = 2 and typedictionnaire = 'tec' and indexdictionnaire = {indexdictionnaire}""")
        data = DatabaseObject.cursor.fetchone()
        if data:
            return data[0]
        else:
            return "Aucune"

    def get_solutions(self):
        DatabaseObject.cursor.execute(
            f"""SELECT numsolution FROM tblsolution WHERE codetechno = {self.id}""")
        solution_ids = [x[0] for x in DatabaseObject.cursor.fetchall()]
        return [SolutionDB(id) for id in solution_ids]

    def get_id(self):
        return self.id

    def get_name(self):
        try:
            return self.name
        except AttributeError:
            self.name = self._retrieve_data(1)
            return self.name

    def get_description(self):
        try:
            return self.description
        except AttributeError:
            self.description = self._retrieve_data(2)
            return self.description

    def get_application(self):
        try:
            return self.application
        except AttributeError:
            self.application = self._retrieve_data(3)
            return self.application

    def get_impact_opex(self):
        try:
            return self.impact_opex
        except AttributeError:
            self.impact_opex = self._retrieve_data(11)
            return self.impact_opex

    def get_approche_systeme(self):
        try:
            return self.approche_systeme
        except AttributeError:
            self.approche_systeme = self._retrieve_data(13)
            return self.approche_systeme

    def get_capex_cout_global(self):
        try:
            return self.capex_cout_global
        except AttributeError:
            self.capex_cout_global = self._retrieve_data(8)
            return self.capex_cout_global

    def get_carac_technique(self):
        try:
            return self.caract_technique
        except AttributeError:
            self.caract_technique = self._retrieve_data(18)
            return self.caract_technique

    def __str__(self) -> str:
        return f"{self.get_name()} : {self.get_description()}"


class SolutionDB(DatabaseObject):

    def __init__(self, numsolution) -> None:
        self.id = numsolution
        self.cursor = DatabaseObject.cursor

    def _category(self):
        # 1 Getting the name of the first category associated with the solution and the id of the parent
        self.cursor.execute(
            f"""SELECT codetechno FROM tblsolution WHERE numsolution = {self.id}""")
        technos = []
        techno = self.cursor.fetchone()
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

    def _retrieve_numeric_data(self, property: str):
        DatabaseObject.cursor.execute(
            f"""SELECT {property} FROM tblsolution WHERE numsolution = {self.id}""")
        data = DatabaseObject.cursor.fetchone()
        if data[0]:
            return data[0]
        else:
            return "Aucune"

    def get_id(self):
        return self.id

    def get_title(self):
        try:
            return self.title
        except AttributeError:
            self.title = self._retrieve_data(1)
            return self.title

    def get_category(self):
        try:
            return self.category
        except AttributeError:
            self.category = self._category()
            return self.category

    @DatabaseObject.clean_up_text
    def get_description(self):
        try:
            return self.description
        except AttributeError:
            self.description = self._retrieve_data(2)
            return self.description

    def get_application(self):
        try:
            return self.application
        except AttributeError:
            self.application = self._retrieve_data(5)
            return self.application

    def get_bilan_energie(self):
        try:
            return self.bilan_energie
        except AttributeError:
            self.bilan_energie = self._retrieve_data(6)
            return self.bilan_energie

    def get_regle_pouce_cout(self):
        try:
            return self.regle_pouce_cout
        except AttributeError:
            self.regle_pouce_cout = self._retrieve_numeric_data(
                "jaugecoutsolution")
            return self.regle_pouce_cout

    def get_regle_pouce_gain(self):
        try:
            return self.regle_pouce_gain
        except AttributeError:
            self.regle_pouce_gain = self._retrieve_numeric_data(
                "jaugecoutsolution")
            return self.regle_pouce_gain

    def get_cout_text(self):
        try:
            return self.regle_pouce_text
        except AttributeError:
            self.regle_pouce_text = self._retrieve_data(9)
            return self.regle_pouce_text

    def get_difficultes(self):
        try:
            return self.difficultes
        except AttributeError:
            self.difficultes = self._retrieve_data(10)
            return self.difficultes

    def get_gain_text(self):
        try:
            return self.gain_text
        except AttributeError:
            self.gain_text = self._retrieve_data(11)
            return self.gain_text

    def get_effets_positifs(self):
        try:
            return self.effets_positifs
        except AttributeError:
            self.effets_positifs = self._retrieve_data(12)
            return self.effets_positifs

    def __str__(self) -> str:
        return f"{str(self.get_category())}\n{self.get_title()} :\n{self.get_description()}\n"


class CaseStudy(DatabaseObject):

    def __init__(self, id) -> None:
        self.id = id
        self.eco_energie = self._retrieve_numeric_data(property="energierex")
        self.gain_financier = self._retrieve_numeric_data(
            property="gainfinancierrex")
        self.gaz_effet_serre = self._retrieve_numeric_data(property="gesrex")
        self.tri = self._retrieve_numeric_data(property="trirex")
        self.ratio_eco_energie = self._retrieve_numeric_data(
            property="ratiogainrex")
        self.capex = self._retrieve_numeric_data(property="capexrex")
        self.techno1 = self._retrieve_numeric_data(property="codeTechno1")
        self.techno2 = self._retrieve_numeric_data(property="codeTechno2")
        self.techno3 = self._retrieve_numeric_data(property="codeTechno3")

    def retrieve_gain_solutions(self):
        ids = self._retrieve_gain_solutions_ids()
        if ids != "Aucune":
            return [SolutionDB(id) for id in ids]

    def _retrieve_gain_solutions_ids(self):
        DatabaseObject.cursor.execute(
            f"""SELECT codesolution FROM tblgainrex WHERE coderex = {self.id}""")
        data = DatabaseObject.cursor.fetchall()
        if data:
            return [x[0] for x in data]
        else:
            return "Aucune"

    def retrieve_cout_solutions(self):
        ids = self._retrieve_cout_solutions_ids()
        if ids != "Aucune":
            return [SolutionDB(id) for id in ids]

    def _retrieve_cout_solutions_ids(self):
        DatabaseObject.cursor.execute(
            f"""SELECT codesolution FROM tblcoutrex WHERE coderex = {self.id}""")
        data = DatabaseObject.cursor.fetchall()
        if data:
            return [x[0] for x in data]
        else:
            return "Aucune"

    def _retrieve_numeric_data(self, property: str):
        DatabaseObject.cursor.execute(
            f"""SELECT {property} FROM tblrex WHERE numrex = {self.id}""")
        data = DatabaseObject.cursor.fetchone()
        if data:
            return data[0]
        else:
            return "Aucune"

    @DatabaseObject.clean_up_text
    def _retrieve_text_data(self, indexdictionnaire):
        DatabaseObject.cursor.execute(
            f"""SELECT traductiondictionnaire FROM tbldictionnaire WHERE codeappelobjet = {self.id} AND codelangue = 2 and typedictionnaire = 'rex' and indexdictionnaire = {indexdictionnaire}""")
        data = DatabaseObject.cursor.fetchone()
        if data:
            return data[0]
        else:
            return "Aucune"

    def retrieve_reference(self):
        ref_id = self._retrieve_numeric_data("codereference")
        return Reference(ref_id)


class Reference(DatabaseObject):

    def __init__(self, id) -> None:
        self.id = id
        self.secteur = self._retrieve_numeric_data("codesecteur")
        self.date = self._retrieve_numeric_data("datereference")
        self.region = self._retrieve_numeric_data("coderegion")

    def _retrieve_numeric_data(self, property: str):
        DatabaseObject.cursor.execute(
            f"""SELECT {property} FROM tblreference WHERE numreference = {self.id}""")
        data = DatabaseObject.cursor.fetchone()
        if data:
            return data[0]
        else:
            return "Aucune"

    def retrieve_case_study(self):
        return self._retrieve_numeric_data("coderex")

    def __str__(self) -> str:
        return f"Date : {self.date}\nRegion : {self.region}"


class SolutionForInference(DatabaseObject):

    def __init__(self, title, class_name, id) -> None:
        self.title = title
        self.class_name = class_name
        self.id = id
        self.text = self._get_text()
        self.cosine_similarity_score = None
        self.cross_encoded_score = None

    def set_cosine_similarity_score(self, value: float):
        self.cosine_similarity_score = value

    def get_cosine_similarity_score(self):
        return self.cosine_similarity_score

    def set_cross_encoded_score(self, value: float):
        self.cross_encoded_score = value

    def get_cross_encoded_score(self):
        return self.cross_encoded_score

    def _retrieve_data(self, property: str):
        DatabaseObject.cursor.execute(
            f"""SELECT {property} FROM tblsolutionembeddings WHERE codesolution = {self.id}""")
        data = DatabaseObject.cursor.fetchone()
        if data:
            return data[0]
        else:
            return "Aucune"

    def get_embedding(self):
        try:
            return self.embedding
        except AttributeError:
            self.embedding = torch.Tensor([float(x) for x in list(
                self._retrieve_data("embeddingvector")[1:-1].split(","))])
            return self.embedding

    def _get_text(self):
        try:
            return self.text
        except AttributeError:
            self.text = self._retrieve_data("englishtrad")
            return self.text

    def __str__(self) -> str:
        return str([self.title, self.class_name])


class Secteur(DatabaseObject):

    def __init__(self, id) -> None:
        self.id = id

    def find_all_case_studies(self):
        try:
            return self.case_studies
        except AttributeError:
            references = self.find_all_references()
            case_study_ids = []
            for reference in references:
                new_case_studies = self._find_case_studies_for_one_reference(
                    reference.id)
                if new_case_studies != "Aucune":
                    case_study_ids.extend(new_case_studies)
            self.case_studies = [CaseStudy(id) for id in case_study_ids]
            return self.case_studies

    def _find_case_studies_for_one_reference(self, reference_id):
        DatabaseObject.cursor.execute(
            f"""SELECT numrex FROM tblrex WHERE codereference = {reference_id}""")
        data = DatabaseObject.cursor.fetchall()
        if data:
            return [x[0] for x in data]
        else:
            return "Aucune"

    def find_all_references(self):
        try:
            return self.references
        except AttributeError:  # If self.references doesn't exist already
            self.references = [Reference(id)
                               for id in self._find_all_references_ids()]
            return self.references

    def _find_all_references_ids(self):
        DatabaseObject.cursor.execute(
            f"""SELECT numreference FROM tblreference WHERE codesecteur = {self.id}""")
        data = DatabaseObject.cursor.fetchall()
        if data:
            return [x[0] for x in data]
        else:
            return "Aucune"

    def find_all_solutions(self):
        try:
            return self.solutions
        except AttributeError:
            case_studies = self.find_all_case_studies()
            solutions = []
            for case_study in case_studies:
                cout_sols = case_study.retrieve_cout_solutions()
                if cout_sols:  # Cout sols can be Non
                    solutions.extend(cout_sols)
                gain_sols = case_study.retrieve_gain_solutions()
                if gain_sols:
                    solutions.extend(gain_sols)
            self.solutions = solutions
            return solutions

    def find_3_most_frequent_solutions(self):
        # Dictionary to count duplicates
        duplicate_counts = {}

        for solution in self.find_all_solutions():
            # If the solution's id is already in the dictionary, increment its count
            if solution.id in duplicate_counts:
                duplicate_counts[solution.id] += 1
            else:
                # Otherwise, add it to the dictionary with a count of 1
                duplicate_counts[solution.id] = 1

        top_3_ids = sorted(
            duplicate_counts, key=duplicate_counts.get, reverse=True)[:3]

        return [SolutionDB(id) for id in top_3_ids]


class SolutionDBList(DatabaseObject):
    """Enables efficient querying of the databases for big solutions lists"""

    def __init__(self, solutions: 'list[SolutionDB]') -> None:
        self.solutions = solutions

    def get_ids(self):
        return [solution.id for solution in self.solutions]

    def get_titles(self):
        try:
            return self.titles
        except AttributeError:
            self.titles = self._retrieve_data(1)
            for solution in self.solutions:
                for title in self.titles:
                    if title[1] == str(solution.id):
                        solution.title = title
                        break

            return self.titles

    def get_categories(self):
        try:
            return self.categories
        except AttributeError:
            self.categories = self._categories()
            return self.categories

    def _categories(self) -> 'list[Category]':
        categories = []
        for solution in self.solutions:
            categories.append(self._category(solution.get_id(), categories))
        return categories

    def _category(self, solution_id, categories: 'list[Category]'):
        all_tech_ids = []
        for category in categories:
            all_tech_ids.append(category.get_technologies()[-1].get_id())

        self.cursor.execute(
            f"""SELECT codetechno FROM tblsolution WHERE numsolution = {solution_id}""")
        techno = self.cursor.fetchone()
        # If the solution belongs to a category that's already been queried just associate the two
        for i in range(len(all_tech_ids)):
            if techno[0] == all_tech_ids[i]:
                return categories[i]
        # Else find which category this solution belongs to
        technos = []
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
                technos.append(techno[0])
        list_of_technos = [Technology(x) for x in technos][::-1]
        return Category(list_of_technos)

    def _retrieve_data(self, indexdictionnaire):
        query = f"""SELECT traductiondictionnaire, codeappelobjet FROM tbldictionnaire WHERE codeappelobjet IN ({', '.join(['%s'] * len(self.solutions))}) AND codelangue = 2 and typedictionnaire = 'sol' and indexdictionnaire = {indexdictionnaire}"""
        DatabaseObject.cursor.execute(query, self.get_ids())
        data = DatabaseObject.cursor.fetchall()
        if data:
            return [x[0] for x in data]
        else:
            return "Aucune"


class TechnoList(DatabaseObject):

    def __init__(self, technologies: 'list[Technology]') -> None:
        self.technologies = technologies

    def get_ids(self):
        return [techno.id for techno in self.technologies]

    def get_names(self):
        try:
            return self.names
        except AttributeError:
            self.names = self._retrieve_data(1)
            return self.names

    def _retrieve_data(self, indexdictionnaire):
        query = f"""SELECT traductiondictionnaire FROM tbldictionnaire WHERE codeappelobjet IN ({', '.join(['%s'] * len(self.technologies))}) AND codelangue = 2 and typedictionnaire = 'tec' and indexdictionnaire = {indexdictionnaire}"""
        DatabaseObject.cursor.execute(query, self.get_ids())
        data = DatabaseObject.cursor.fetchall()
        if data:
            return [x[0] for x in data]
        else:
            return "Aucune"
