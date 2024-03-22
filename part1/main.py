from findrelevantinfo import Preprocessor, BestSolutionsFinder, retrieve_all_solutions_and_classes
from database import SolutionDB, Technology
import json

with open("./data/data.json", "r") as f:
    input_dict = json.load(f)

preprocessor = Preprocessor()
solutions = retrieve_all_solutions_and_classes(input_dict)
user_query = "How does heat pump work ?"
preprocessed_query = preprocessor(user_query)
finder = BestSolutionsFinder(solutions, preprocessed_query)
relevant_solutions_ids, class_info = finder.relevant_solutions()

relevant_solutions = [SolutionDB(id) for id in relevant_solutions_ids]
for x in relevant_solutions:
    print(x)


def find_techno_id(class_info):
    """Using the data from the model, find the best techno id so you can give all the solutions in that category to the user"""
    solution = SolutionDB(class_info[1].id)
    category = solution.category.technologies[:class_info[0]+1]
    return category[-1].id


print(Technology(find_techno_id(class_info[0])))
