from matplotlib import pyplot as plt
import mysql.connector
from mysql.connector import MySQLConnection
from configparser import ConfigParser
import numpy as np
from sklearn.linear_model import LinearRegression

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

class DatabaseObject:
    db = Database()
    cursor = db.database_connection.cursor()


class QueryDb(DatabaseObject):

    def get_gain_and_cout_financier(self, codeSolution: int):

        # | numgainrex | codesolution | coderex | gainfinanciergainrex | codemonnaiegainrex | codeperiodeeconomie | energiegainrex | uniteenergiegainrex | codeperiodeenergie | gesgainrex | minigainrex | maxigainrex | moyengainrex | reelgainrex | trireelgainrex | trimingainrex | trimaxgainrex | codelicense | numcoutrex | codesolution | coderex | minicoutrex | maxicoutrex | reelcoutrex | codemonnaiecoutrex | codeunitecoutrex | codedifficulte | codelicense |
        DatabaseObject.cursor.execute(
            f"""select g.coderex, gainfinanciergainrex, codemonnaiegainrex,codeperiodeeconomie , reelcoutrex, codemonnaiecoutrex
            from tblgainrex as g 
            join tblcoutrex as c 
            on c.coderex = g.coderex and c.codesolution = g.codesolution 
            where   g.codesolution = {codeSolution}
                    and not gainfinanciergainrex is null
                    and not c.reelcoutrex is null
                    and c.reelcoutrex > 0.0
                    and codeperiodeeconomie > 2
                    and c.codeunitecoutrex = 1
            """
        )
        return DatabaseObject.cursor.fetchall()
    

    def get_gainenergie(self, codeSolution: int):
        # energiegainrex | reelcoutrex | uniteenergiegainrex | codeperiodeenergie | codemonnaiecoutrex
        DatabaseObject.cursor.execute(
            f"""
            SELECT g.energiegainrex,
                c.reelcoutrex,
                g.uniteenergiegainrex,
                g.codeperiodeenergie,
                c.codemonnaiecoutrex
            FROM tblgainrex as g
            INNER JOIN tblcoutrex as c
            ON g.coderex = c.coderex
            and c.codesolution = g.codesolution
            WHERE g.codesolution = {codeSolution}
                AND NOT g.energiegainrex IS NULL
                AND NOT g.uniteenergiegainrex IS NULL
                AND NOT g.codeperiodeenergie IS NULL
                AND NOT c.reelcoutrex IS NULL
                AND NOT c.codemonnaiecoutrex IS NULL
                AND g.codeperiodeenergie != 2
                and c.codeunitecoutrex = 1
            """
        )
        return DatabaseObject.cursor.fetchall()
    
    def get_gain_gaz_serre(self, codeSolution: int):
        # gesgainrex |  reelgainrex | codemonnaiecoutrex
        DatabaseObject.cursor.execute(
            f"""
            SELECT gesgainrex, reelcoutrex, codemonnaiecoutrex
            FROM tblgainrex as g
            join tblcoutrex as c 
                on  c.coderex = g.coderex
                and c.codesolution = g.codesolution 
            
            WHERE g.codesolution = {codeSolution}
                and not gesgainrex is null
                and not c.reelcoutrex is null
                and c.codemonnaiecoutrex != 1
                and not c.codemonnaiecoutrex is null
            """
        )
        return DatabaseObject.cursor.fetchall()
    



class Convert(DatabaseObject):


# Sauvegarder toute la table en mémoire car petite table et evite plusieur requetes
    @staticmethod
    def to_euro(value : float, codeMonnaie:int = 2):
        DatabaseObject.cursor.execute(
        f"""SELECT valeurtauxmonnaie FROM tbltauxmonnaie WHERE codemonnaie = {codeMonnaie}"""
        )

        res = DatabaseObject.cursor.fetchall()

        taux = 1
        if res and len(res) == 1:
            taux = float(res[0][0])
        else:
            raise Exception("Code monnaie inconnue")
        
        return value * taux


    @staticmethod
    def to_year(value: float, codePeriode: int = 1):

        # if codePeriode == 1:
        #     raise Exception("Unité manquante")
        
        if codePeriode == 2:
            raise Exception("/Projet ne peut etre transformé en /an")

        if codePeriode > 5:
            raise Exception("Pas traité")

        if codePeriode == 5: # passage de /heure => /jour
            value *= 24
            codePeriode = codePeriode - 1

        if codePeriode == 4: # passage de /jour => /an
            value *= 365.25
            codePeriode = codePeriode - 1
        
        return value


    @staticmethod
    def unit_convertion(value: float, codeUnit:int):


        DatabaseObject.cursor.execute(
        f"""
        SELECT traductiondictionnairecategories
        FROM tbldictionnairecategories
        WHERE codelangue = 2
        AND typedictionnairecategories = "uni"
        AND codeappelobjet = {codeUnit}
        """
        )

        res = DatabaseObject.cursor.fetchall()
        unit = ""
        if res and len(res) == 1:
            unit = res[0][0] #.split(" ")[0] # si osef de cunac
        else:
            raise Exception("Code monnaie inconnue")
        
        conversions = {
            'GJ': {
                'kWh': 277.778
                # Pour le gaz naturel, la conversion en mètre cube (m3) dépend du pouvoir calorifique du gaz.
            },
            'tep': {
                'GJ': 41.868,
            },
            'GWh': {
                'kWh': 1000000,
            },
            'MMBtu': {
                'GJ': 1.05506,
            },
            'm3': {
                'litre': 1000,
                # Pour le gaz naturel, la conversion en GJ dépend du pouvoir calorifique du gaz.
            },
            'therm': {
                'MMBtu': 0.1055,
            },
            'tonne': {
                'kg': 1000,
            },
            'W': {
                'kW': 0.001,
            },
            'MWh': {
                'kWh': 1000,
            }
        }

        keys = list(conversions.keys())
        while(unit in keys):
            newUnit = next(iter(conversions[unit]))
            value = value * float(conversions[unit][newUnit])
            unit = newUnit

        return value, unit


class Parse(QueryDb):

    def parse_gain_financer(self, codeSolution: int):
        # (coderex, gainfinanciergainrex, codemonnaiegainrex, codeperiodeeconomie, reelcoutrex, codemonnaiecoutre)
        outputRexFin = self.get_gain_and_cout_financier(codeSolution)

        res = []
        for rex in outputRexFin:

            codeMonnaieGain = rex[2] if rex[2] != 1 else rex[5]
            if codeMonnaieGain == 1:
                continue

            gainEuro = Convert.to_euro(float(rex[1]), codeMonnaieGain)
            gainEuro = Convert.to_year(gainEuro, rex[3])

            codeMonnaieCout = rex[5] if rex[5] != 1 else rex[2]
            coutEuro = Convert.to_euro(float(rex[4]), codeMonnaieCout)


            res.append((rex[0], coutEuro, gainEuro))
        
        return res
    
    def parse_gain_eco(self, codeSolution:int):
        # (energiegainrex | reelcoutrex | uniteenergiegainrex | codeperiodeenergie | codemonnaiecoutrex)
        outputRexEco = self.get_gainenergie(codeSolution)

        res = []
        for rex in outputRexEco:
            codeMonnaieGain = rex[4] 
            if codeMonnaieGain == 1:
                continue

            gainEuro = Convert.to_euro(float(rex[1]), codeMonnaieGain)

            gainEnergie, unit = Convert.unit_convertion(float(rex[0]), rex[2])
            gainEnergie = Convert.to_year(gainEnergie, rex[3])  

            res.append((gainEuro, gainEnergie, unit))

        return res

    def parse_gain_gaz_serre(self, codeSolution:int):
        # (gesgainrex | reelgainrex | codemonnaiecoutrex)
        outputRexGaz = self.get_gain_gaz_serre(codeSolution)

        res = []
        unit = "tCO2e"
        for rex in outputRexGaz:
            codeMonnaieGain = rex[2] 
            gainEuro = Convert.to_euro(float(rex[1]), codeMonnaieGain)

            res.append((float(rex[0]), gainEuro, unit))

        return res

    
def regression_lineaire(X: np.array, Y:np.array):
    
    model = LinearRegression()
    model.fit(X, Y)
    
    return model

@staticmethod
def show_regression(model, X, Y, xlabel: str, ylabel: str):
    # Prédire les valeurs y pour les données d'entraînement
    y_pred = model.predict(X)

    # Tracer les données et la courbe de régression linéaire
    plt.scatter(X, Y, color='blue', label='Données')
    plt.plot(X, y_pred, color='red', linewidth=1, label='Régression linéaire')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title('Régression linéaire')
    # plt.xscale('log')  # Échelle logarithmique pour l'axe des x
    # plt.yscale('log')  # Échelle logarithmique pour l'axe des y
    plt.legend()
    plt.show()


def gainFinancier(codeSolution: int):
    parse = Parse()

    res = parse.parse_gain_financer(codeSolution)
    if len(res) == 0:
        print("aucune valeur")
        return None

    X = [0]
    Y = [0]
    output = {}
    for _rex, cout, gain in res:
        X.append(cout)
        Y.append(gain)

    output['cost'] = X
    output['gain'] = Y
    X = np.array(X).reshape(-1,1)
    Y = np.array(Y)    

    model = regression_lineaire(X, Y)
    
    output['a'] = model.coef_[0]
    output['b'] = model.intercept_
    output['unit_cost'] = '€'
    output['unit_gain'] = '€/an'
    # show_regression(model, X, Y, "cout €", , "gain €/an")

    return output

def gainEnergie(codeSolution: int):
    parse = Parse()

    res = parse.parse_gain_eco(codeSolution)
    if len(res) == 0:
        print("aucune valeur")
        return None

    output = []
    data_split = {}
    for cout, gain, unit in res:
        if unit not in data_split:
            data_split[unit] = {'X': [0], 'Y': [0], 'model': None}
        
        data_split[unit]['X'].append(cout)
        data_split[unit]['Y'].append(gain)

    for unit in data_split:
        
        X = np.array(data_split[unit]['X']).reshape(-1,1)
        Y = np.array(data_split[unit]['Y'])

        model = regression_lineaire(X, Y)
        
        tmp = {}
        tmp['a'] = model.coef_[0]
        tmp['b'] = model.intercept_
        tmp['cost'] = data_split[unit]['X']
        tmp['gain'] = data_split[unit]['Y']
        tmp['unit_cost'] = '€'
        tmp['unit_gain'] = unit + '/an'
        output.append(tmp)
        # show_regression(data_split[unit]['model'], X, Y, f"{unit}/an", "cout €")
    
    return output


def gainGazSerre(codeSolution: int):
    parse = Parse()

    res = parse.parse_gain_gaz_serre(codeSolution)
    if len(res) == 0:
        print("aucune valeur")
        return None


    X = [0]
    Y = [0]
    unit = ""
    output = {}
    for gain, cout, unit in res:
        X.append(cout)
        Y.append(gain)
        unit = unit

    output['cost'] = X
    output['gain'] = Y
    X = np.array(X).reshape(-1,1)
    Y = np.array(Y)  

    model = regression_lineaire(X, Y)
    output['a'] = model.coef_[0]
    output['b'] = model.intercept_
    output['unit_cost'] = '€'
    output['unit_gain'] = 'tCO2e/an'
    # show_regression(model, X, Y, "cout €", f"{unit}/an")

    return output


def predict(codeSolution: int):
    res = {}
    res['financial'] = gainFinancier(codeSolution)
    res['energy'] = gainEnergie(codeSolution)
    res['greenhouse'] = gainGazSerre(codeSolution)

    return res

if __name__ == '__main__':
    # gainFinancier(312)
    # gainEnergie(240)
    # gainEnergie(79)
    # gainGazSerre(80)
    print((predict(160)))
