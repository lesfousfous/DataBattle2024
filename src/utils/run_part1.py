from utils.findrelevantinfo import BestSolutionsFinder, change_solutions_format
from utils.database import SolutionDB, Database, SolutionDBList, Category
from googletrans import Translator
import time


def process_description(string: str):
    db = Database()
    cursor = db.database_connection.cursor()
    cursor.execute(
        "SELECT numsolution FROM tblsolution WHERE NOT (codesysteme = NULL AND codetechno=1)")
    solutions_ids = [x[0] for x in cursor.fetchall()]
    solutions = SolutionDBList([SolutionDB(id) for id in solutions_ids])

    start_time = time.time()
    solutions_for_inference = change_solutions_format(solutions)
    db_time = time.time() - start_time
    print(f"Time to query the db : {db_time}")

    start_time2 = time.time()
    translator = Translator()
    user_query = string
    # preprocessor = Preprocessor()
    # preprocessed_query = preprocessor(user_query)
    preprocessed_query = translator.translate(user_query, dest="en").text
    print(f"Time to preprocess : {time.time() - start_time2} sec")
    finder = BestSolutionsFinder(solutions_for_inference, preprocessed_query)
    relevant_solutions_ids, class_info = finder.relevant_solutions()

    relevant_solutions = [SolutionDB(id) for id in relevant_solutions_ids]
    sol_time = time.time() - start_time - db_time
    print(f"Time to find the solutions : {sol_time}")
    if not class_info:
        return None, relevant_solutions
    else:
        return (find_category(class_info[0], solutions), relevant_solutions)
    # print(f"Total time : {time.time() - start_time} sec")


def find_category(class_info, solutions):
    if class_info[0] == 1:  # If we get one of the top classes it's weird most of the time
        return None
    """Using the data from the model, find the best techno id so you can give all the solutions in that category to the user"""
    solution = [x for x in solutions.solutions if x.id == class_info[1].id][0]
    category = solution.get_category().get_technologies()[:class_info[0]+1]
    return Category(category)
