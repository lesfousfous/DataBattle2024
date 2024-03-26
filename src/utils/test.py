from database import Category, SolutionDB

for x in SolutionDB(422).get_category().get_technologies():
    print(x)
liste = Category(SolutionDB(422).get_category(
).get_technologies()).get_solutions()
for x in liste:
    print(x)
