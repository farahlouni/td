"""
Lancement : python3 defi-du-6-style.py


"""

import os
import random
import sys


def _activer_ansi():
    """Autorise les couleurs ANSI dans le terminal Windows classique."""
    if os.name == "nt":
        os.system("")


class Style:
    RESET = "\033[0m"
    GRAS = "\033[1m"
    ROUGE = "\033[31m"
    VERT = "\033[32m"
    JAUNE = "\033[33m"
    CYAN = "\033[36m"
    GRIS = "\033[90m"


def colorer(texte, *styles):
    return "".join(styles) + str(texte) + Style.RESET


def effacer_ecran():
    os.system("cls" if os.name == "nt" else "clear")


def entete(titre, emoji="🎲"):
    ligne = "─" * (len(titre) + 4)
    print(colorer(ligne, Style.GRIS))
    print(colorer(f"  {emoji} {titre}", Style.GRAS, Style.CYAN))
    print(colorer(ligne, Style.GRIS))


def demander_entier(prompt, min_val=None, max_val=None):
    """Boucle jusqu'à obtenir un entier valide, avec un message d'erreur clair."""
    while True:
        brut = input(prompt).strip()
        try:
            valeur = int(brut)
        except ValueError:
            print(colorer("Merci d'entrer un nombre entier valide.", Style.ROUGE))
            continue
        if min_val is not None and valeur < min_val:
            print(colorer(f"La valeur doit être au moins {min_val}.", Style.ROUGE))
            continue
        if max_val is not None and valeur > max_val:
            print(colorer(f"La valeur doit être au plus {max_val}.", Style.ROUGE))
            continue
        return valeur


def demander_choix(prompt, options):
    """Boucle jusqu'à obtenir l'une des options (comparaison insensible à la casse)."""
    options_normalisees = [o.lower() for o in options]
    while True:
        brut = input(prompt).strip().lower()
        if brut in options_normalisees:
            return brut
        print(colorer(f"Choisis parmi : {', '.join(options)}.", Style.ROUGE))


def texte_gain(gain):
    if gain > 0:
        return colorer(f"+{gain:g}", Style.VERT, Style.GRAS)
    if gain < 0:
        return colorer(f"{gain:g}", Style.ROUGE, Style.GRAS)
    return colorer(f"{gain:+g}", Style.JAUNE)


class DefiDuSix:
    def lancer_de(self):
        return random.randint(1, 6)

    def jouer(self, mise=1):
        if type(mise) != int or mise <= 0:
            raise ValueError("La mise doit être un nombre entier positif.")

        entete(f"Défi du six — mise : {mise} jeton(s)")
        print(colorer("Jusqu'à trois lancers : un 6 et tu doubles ta mise !", Style.CYAN))
        print(colorer("Après deux échecs, tu peux arrêter et récupérer 25 % de ta mise.", Style.GRIS))

        for lancer in range(1, 4):
            input(colorer(f"\nAppuie sur Entrée pour le lancer {lancer}/3...", Style.GRIS))
            de = self.lancer_de()
            print(f"🎲 Lancer {lancer} : {colorer(de, Style.GRAS)}")

            if de == 6:
                print(colorer("\nGagné !", Style.VERT, Style.GRAS))
                print(f"Tu empoches : {2 * mise} jetons, mise comprise.")
                print(f"Ton bénéfice net est de {texte_gain(mise)} jeton(s).")
                return mise

            if lancer == 2:
                choix = demander_choix(
                    f"Cashout à 25 % : récupérer {mise * 0.25:g} jeton(s) et arrêter ? "
                    "(o = oui / n = tenter le troisième lancer) : ",
                    ["o", "n"],
                )
                if choix == "o":
                    remboursement = mise * 0.25
                    gain = remboursement - mise
                    print(colorer("\nCashout !", Style.JAUNE, Style.GRAS))
                    print(f"Retour : {remboursement:g} jeton(s) ; bénéfice net : {texte_gain(gain)}.")
                    print(f"Le casino conserve {-gain:g} jeton(s).")
                    return gain

        print(colorer("\nPerdu !", Style.ROUGE, Style.GRAS))
        print(f"Trois échecs. Ton bénéfice net est de {texte_gain(-mise)} jeton(s).")
        return -mise

    def bot(self, mise=1, cashout=False):

        if type(mise) != int or mise <= 0:
            raise ValueError("La mise doit être un entier positif.")

        if type(cashout) != bool:
            raise ValueError("cashout doit valoir True ou False.")

        for lancer in range(1, 4):
            de = self.lancer_de()
            if de == 6:
                return mise
            if lancer == 2 and cashout == True:
                remboursement = mise * 0.25
                return remboursement - mise
        return -mise

    """
1/ 4 mise - 1/6 * 2 mise
Comparaison au moment du choix, après deux échecs.
mise = 1

Cashout : remboursement de 25 % moins la mise initiale.
e_cashout = mise * 0.25 - mise = -0.75

Continuer : victoire avec probabilité 1/6, défaite avec probabilité 5/6.
e_continuer = (1 / 6) * mise + (5 / 6) * (-mise) = - 0.6667

Espérance avec cashout : -0.75
Espérance en continuant : - 0.667
e_continuer > e_cashout

Refuser le cashout maximise l'espérance de gain du joueur.
    """
    def esperance(self, n=100_000, mise=1, cashout=True):
        """Gain net moyen du joueur pour la stratégie de cashout choisie."""
        if type(n) != int or n <= 0:
            raise ValueError("Le nombre de parties doit être un entier positif.")
        if type(mise) != int or mise <= 0:
            raise ValueError("La mise doit être un nombre entier positif.")
        benef = 0
        for i in range(n):
            benef += self.bot(mise, cashout)
        return benef / n

    def esperance_roulette(self, n=100_000, mise=1):
        if type(n) != int or n <= 0:
            raise ValueError("Le nombre de tours doit être un entier positif.")
        if type(mise) != int or mise <= 0:
            raise ValueError("La mise doit être un nombre entier positif.")
        benef = 0
        for i in range(n):
            numero = random.randint(0, 36)
            if numero == 7:
                benef += 35 * mise
            else:
                benef -= mise
        return benef / n



def comparer_esperances(jeu):
    entete("Comparaison des stratégies", emoji="📊")
    print(colorer("Simulation en cours, avec une mise de 1 jeton...\n", Style.GRIS))

    e_cashout = jeu.esperance(cashout=True)
    e_continuer = jeu.esperance(cashout=False)
    e_roulette = jeu.esperance_roulette()

    print(colorer("Gains nets moyens par partie :", Style.GRAS))
    print(f"Cashout systématique — joueur : {e_cashout:+.5f} ; casino : {-e_cashout:+.5f}.")
    print(f"Toujours continuer   — joueur : {e_continuer:+.5f} ; casino : {-e_continuer:+.5f}.")
    print(f"Roulette             — joueur : {e_roulette:+.5f} ; casino : {-e_roulette:+.5f}.")

    print(colorer("\nThéorie joueur, par jeton misé :", Style.GRAS))
    print(f"Cashout à 25 % : {-31 / 144:+.5f} ; continuer : {-17 / 108:+.5f} ; roulette : {-1 / 37:+.5f}.")
    print(colorer("Les quarts de jeton sont conservés : aucun remboursement n'est arrondi.", Style.GRIS))
    print("")
    input(colorer("Appuie sur Entrée pour revenir au menu...", Style.GRIS))


def menu_principal():
    print("1 : Jouer une partie")
    print("2 : Comparer les espérances sur 100 000 parties")
    print("3 : Quitter")
    return input(colorer("Ton choix : ", Style.GRIS)).strip()


def main():
    _activer_ansi()
    jeu = DefiDuSix()

    while True:
        effacer_ecran()
        entete("DÉFI DU SIX CASHOUT — OPTION À 25 % APRÈS DEUX ÉCHECS")
        print("")
        choix = menu_principal()

        if choix == "1":
            effacer_ecran()
            mise = demander_entier("Ta mise en jetons (entier positif) : ", min_val=1)
            gain = jeu.jouer(mise)
            print(f"\nBilan : joueur {texte_gain(gain)} ; casino {texte_gain(-gain)} jeton(s).")
            input(colorer("\nAppuie sur Entrée pour continuer...", Style.GRIS))
        elif choix == "2":
            effacer_ecran()
            comparer_esperances(jeu)
        elif choix == "3":
            break
        else:
            print(colorer("Choisis 1, 2 ou 3.", Style.ROUGE))
            input(colorer("Appuie sur Entrée pour continuer...", Style.GRIS))


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(colorer("\n\nÀ bientôt !", Style.CYAN))
        sys.exit(0)
