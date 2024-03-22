from database import SolutionDB, CaseStudy, Reference, Secteur

secteur = Secteur(53)
case_studies = secteur.find_all_case_studies()
solutions = []
for case_study in case_studies:
    cout_sols = case_study.retrieve_cout_solutions()
    if cout_sols:  # Cout sols can be Non
        solutions.extend(cout_sols)
    gain_sols = case_study.retrieve_gain_solutions()
    if gain_sols:
        solutions.extend(gain_sols)

# Dictionary to count duplicates
duplicate_counts = {}

for solution in solutions:
    # If the solution's id is already in the dictionary, increment its count
    if solution.id in duplicate_counts:
        duplicate_counts[solution.id] += 1
    else:
        # Otherwise, add it to the dictionary with a count of 1
        duplicate_counts[solution.id] = 1

top_3_ids = sorted(
    duplicate_counts, key=duplicate_counts.get, reverse=True)[:3]

for id in top_3_ids:
    print(SolutionDB(id))
