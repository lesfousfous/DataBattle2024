from database import SolutionDB, Preprocessor, Database, SolutionDBList
from findrelevantinfo import EmbeddingsModel
from googletrans import Translator


def fill_embeddings_table_from_scratch():
    """Calculates embeddings for all solutions in the database"""
    db = Database()
    cursor = db.database_connection.cursor()

    cursor.execute("TRUNCATE TABLE tblsolutionembeddings;")
    cursor.execute("SELECT numsolution from tblsolution")
    solutions_ids = [x[0] for x in cursor.fetchall()]
    solutions = [SolutionDB(id) for id in solutions_ids]

    translator = Translator()
    preprocessor = Preprocessor()
    print('Translating...')

    solutions_text = [" + ".join([x.get_name() for x in solution.get_category().get_technologies()][1:]) + " " +
                      solution.get_title() for solution in solutions]
    translated = []
    for x in solutions_text:
        translated.append(translator.translate(x, dest="en"))

    translated_solutions_text = [preprocessor(x.text) for x in translated]

    embeddings_model = EmbeddingsModel()
    solutions_embeddings = embeddings_model(translated_solutions_text)

    data = []
    for i in range(len(solutions)):
        data.append(
            (solutions[i].id, str(solutions_embeddings[i].tolist()), translated_solutions_text[i]))
    insert_statement = (
        "INSERT INTO `tblsolutionembeddings` (codesolution, embeddingvector, englishtrad) "
        "VALUES (%s, %s, %s)"
    )
    cursor.executemany(insert_statement, data)
    db.database_connection.commit()


def add_solution_embedding(solution_id: int):
    """Adds a specific solution embedding and trad to the tblsolutionembeddings"""
    solution = SolutionDB(solution_id)

    translator = Translator()
    preprocessor = Preprocessor()
    print('Translating...')

    solutions_text = " + ".join(
        [x.name for x in solution.category.technologies][1:]) + " " + solution.title
    translated = translator.translate(solutions_text, dest="en")
    translated_solutions_text = translated.text

    embeddings_model = EmbeddingsModel()
    solution_embedding = embeddings_model([translated_solutions_text])[0]

    db = Database()
    cursor = db.database_connection.cursor()
    cursor.execute(
        f"INSERT INTO `tblsolutionembeddings` (codesolution, embeddingvector, englishtrad) VALUES ({solution.id}, '{list(solution_embedding)}', '{translated_solutions_text}')")
    db.database_connection.commit()


# fill_embeddings_table_from_scratch()
