import mysql.connector as mysql
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
########################################
# Connect to the database
db = mysql.connect(
    host = "localhost",
    port = 3307, 
    user = "root",
    passwd = "example",
    database = "ikeo_bdd"
)

cursor = db.cursor()
########################################

# Fonction pour afficher tous les produits ainsi que leurs sites de production

def afficher_produits():
    query = "SELECT nom, usine FROM produits"
    cursor.execute(query)
    # cration dataframe
    df = pd.DataFrame(cursor.fetchall(), columns = ['Produit', 'Sites de production'])
    return df

########################################
st.title("IKEO")
########################################

produits = afficher_produits()
st.header("Liste des produits par site de production")
st.write(produits)

########################################

# Requête SQL pour récupérer tous les sites de production distincts
def get_sites_production():
    query = "SELECT DISTINCT usine FROM produits"
    cursor.execute(query)
    sites = cursor.fetchall()
    return [site[0] for site in sites]


# Requête SQL pour récupérer les produits selon le site de production sélectionné
def get_products(site):
    query = "SELECT nom FROM produits WHERE usine = %s"
    cursor.execute(query, (site,))
    products = cursor.fetchall()
    return [product[0] for product in products]


# Interface utilisateur avec Streamlit
st.title("Filtrer les produits par site de production")


# Sélection de l'entreprise
selected_site = st.selectbox("Sélectionnez une entreprise", get_sites_production())


# Affichage du nom de l'entreprise sélectionnée
st.header(f"Entreprise : {selected_site}")

# Récupération des produits selon l'entreprise sélectionnée
products = get_products(selected_site)


# Affichage des produits
st.header("Liste des produits")
for product in products:

    st.write(product)

########################################

# Fonction pour afficher le nombre de commandes par produits

def commande_par_produit():
    query = """
            SELECT p.nom, CAST(SUM(f.quantite) AS DECIMAL(10,2)) AS quantite_totale 
            FROM produits p
            JOIN facturer f ON p.id_produit = f.id_produit
            GROUP BY p.id_produit
            """
    cursor.execute(query)
    results = cursor.fetchall()
    df = pd.DataFrame(results, columns=['Produit', 'Quantité'])
    df['Quantité'] = df['Quantité'].astype(float)
    return df


# Affichage du graphique
df = commande_par_produit()
st.header('Ikeo - Commandes par produits')
st.bar_chart(df.set_index('Produit'))


########################################

# Afficher le nombre de commandes par clients dans un graphique

query = """
SELECT raison_sociale, SUM(quantite) FROM facturer 
JOIN factures ON facturer.id_facture = factures.id_facture 
JOIN clients ON factures.id_client = clients.id_client GROUP BY raison_sociale
"""

cursor.execute(query)
#creation dataframe
df2 = pd.DataFrame(cursor.fetchall())
df2.columns = cursor.column_names

st.bar_chart(df2.set_index('raison_sociale'))


########################################

query = """
SELECT raison_sociale, SUM(quantite) AS total_commandes
FROM facturer
JOIN factures ON facturer.id_facture = factures.id_facture
JOIN clients ON factures.id_client = clients.id_client
GROUP BY raison_sociale
"""

cursor.execute(query)

# Récupération des résultats de la requête
results = cursor.fetchall()

# Conversion des résultats en DataFrame
df = pd.DataFrame(results, columns=["Client", "Total Commandes"])

# Affichage dans Streamlit
st.title("Graphique des commandes par clients")
# st.dataframe(df)

# Création du graphique à barres

plt.bar(df["Client"], df["Total Commandes"])
plt.xlabel("Client")
plt.ylabel("Nombre de commandes")
plt.title("Commandes par clients")

# Affichage du graphique dans Streamlit
st.pyplot(plt)

########################################

# Fermeture de la connexion à la base de données
db.close()
