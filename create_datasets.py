from database import Database, SolutionsAndCategoriesData, read_gpt_to_file


prep_solutions_for_gpt = False
create_dataset_from_GPT_output = False
update_solutions_data = False

if prep_solutions_for_gpt:
    database = Database()
    sols = SolutionsAndCategoriesData(database)
    sols.translate_data_to_file_for_gpt()

if create_dataset_from_GPT_output:
    read_gpt_to_file(infile="./data/gpt_dataset_many_questions.txt",
                     outfile="./data/dataset_clean_with_4_questions.json")

if update_solutions_data:
    database = Database()
    sols = SolutionsAndCategoriesData(database)
    sols.export_data_to_json()
