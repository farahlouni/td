"""Blackjack à plusieurs joueurs : tirer, rester, séparer et gérer les capitaux.

Règles de cette version  :
- Le sabot contient six paquets de 52 cartes, soit 312 cartes.
- Un sabot complet est mélangé au début de chaque manche.
- Pendant une partie, chaque carte tirée est retirée du sabot commun
  au joueur et au croupier : les tirages se font sans remise.
- Un as vaut 11, ou 1 si cela permet d'éviter de dépasser 21.
- Le joueur choisit de tirer ou de rester ; le croupier s'arrête à 17,
  y compris avec un as compté comme 11.
- Un blackjack initial (21 en deux cartes) rapporte +1,5 mise nette.
- Une victoire ordinaire rapporte +1 mise ; une défaite coûte -1 mise.
- Une égalité rend la mise : le gain net est 0.
- Les blackjacks initiaux sont réglés avant toute décision du joueur.
- Deux cartes initiales de même valeur peuvent être séparées une seule fois :
  on obtient deux mains et on ajoute une mise identique à la première.
- Les deux mains sont jouées avant le tour du croupier, qui joue une seule
  main commune. Chaque main du joueur est ensuite réglée séparément.
- Deux as séparés reçoivent une seule carte supplémentaire chacun.
- Un 21 obtenu après séparation rapporte +1 mise nette, pas +1,5 mise.
- Le bot sépare les as et les 8, puis tire jusqu'à 17 hors as séparés.
- Cette version ne propose ni doublement ni assurance.
- De 1 à 7 joueurs peuvent participer, avec chacun un nom et un capital.
- Tous les joueurs misent avant la distribution ; une mise de 0 fait passer le tour.
- Chaque joueur joue ses mains avant le tour du croupier, commun à tous.
- Chaque joueur choisit son capital de départ, puis mise des jetons entiers.
- Une mise, y compris celle d'une séparation, doit être couverte par le capital.
- Après chaque partie, le gain net est ajouté au capital (une perte est négative).
- Les capitaux restants et les bilans individuels sont affichés en fin de session.
- La simulation reste une référence avec un seul bot face au croupier.


Lancement : python3 blackjack-3-3-2.py
"""

import os
import random
import sys
import time


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
    BLEU = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    GRIS = "\033[90m"


def colorer(texte, *styles):
    return "".join(styles) + str(texte) + Style.RESET


def effacer_ecran():
    os.system("cls" if os.name == "nt" else "clear")


def entete(titre, emoji="🃏"):
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
    options_normalisees = [o.lower() for o in options]
    while True:
        brut = input(prompt).strip().lower()
        if brut in options_normalisees:
            return brut
        print(colorer(f"Choisis parmi : {', '.join(options)}.", Style.ROUGE))


class Blackjack:
    def __init__(self):
        self.nouveau_sabot()
        self.mise_totale = 0
        self.vitesse = 1.0 

    def pause(self, secondes):
        if self.vitesse:
            time.sleep(secondes * self.vitesse)

    def nouveau_sabot(self):
        valeurs = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "V", "D", "R"]
        self.sabot = valeurs * 4 * 6
        random.shuffle(self.sabot)

    def tirer_carte(self):
        return self.sabot.pop()

    def valeur_hand(self, hand):
        total = 0
        nombre_as = 0

        for carte in hand:
            if carte == "A":
                total += 11
                nombre_as += 1
            elif carte in ("V", "D", "R"):
                total += 10
            else:
                total += int(carte)

        while total > 21 and nombre_as > 0:
            total -= 10
            nombre_as -= 1

        return total

    def peut_separer(self, hand):
        return (
            len(hand) == 2
            and self.valeur_hand([hand[0]]) == self.valeur_hand([hand[1]])
        )

    def gain_initial(self, hand_joueur, hand_croupier, mise):
        blackjack_joueur = len(hand_joueur) == 2 and self.valeur_hand(hand_joueur) == 21
        blackjack_croupier = len(hand_croupier) == 2 and self.valeur_hand(hand_croupier) == 21

        if blackjack_joueur and blackjack_croupier:
            return 0
        if blackjack_joueur:
            return 1.5 * mise
        if blackjack_croupier:
            return -mise
        return None

    def gain_final(self, hand_joueur, hand_croupier, mise):
        total_joueur = self.valeur_hand(hand_joueur)

        if total_joueur > 21:
            return -mise

        while self.valeur_hand(hand_croupier) < 17:
            hand_croupier.append(self.tirer_carte())

        total_croupier = self.valeur_hand(hand_croupier)

        if total_croupier > 21 or total_joueur > total_croupier:
            return mise
        if total_joueur == total_croupier:
            return 0
        return -mise


    def afficher_main(self, titre, hand, style_titre=Style.BLEU):
        total = self.valeur_hand(hand)
        print(f"\n{colorer(titre, Style.GRAS, style_titre)} : {' '.join(hand)}")
        if total == 21:
            print(colorer(f"Total : {total} — 21 !", Style.VERT, Style.GRAS))
        elif total > 21:
            print(colorer(f"Total : {total} — dépassé !", Style.ROUGE, Style.GRAS))
        else:
            print(f"Total : {total}")

    def texte_gain(self, gain):
        if gain > 0:
            return colorer(f"+{gain:g}", Style.VERT, Style.GRAS)
        if gain < 0:
            return colorer(f"{gain:g}", Style.ROUGE, Style.GRAS)
        return colorer(f"{gain:+g}", Style.JAUNE)


    def jouer_hands(self, hand_joueur, mise, capital=None):
        mise_totale = mise
        hands = [hand_joueur]
        as_separes = False

        if self.peut_separer(hand_joueur):
            if capital is not None and 2 * mise > capital:
                print(colorer(
                    f"Capital insuffisant pour séparer : il faut {2 * mise} jeton(s) au total.",
                    Style.JAUNE,
                ))
                print("Tu continues avec une seule main.")
            else:
                choix = demander_choix(
                    f"Séparer la paire en ajoutant {mise} jeton(s) "
                    f"(mise totale : {2 * mise}) ? o = oui / n = non : ",
                    ["o", "n"],
                )
                print("")
                if choix == "o":
                    hands = [[hand_joueur[0]], [hand_joueur[1]]]
                    as_separes = hand_joueur[0] == "A"
                    mise_totale = 2 * mise
                    print(colorer(
                        f"Deux mains de {mise} jeton(s), soit {mise_totale} au total.",
                        Style.CYAN,
                    ))
                    self.pause(1)
                    if as_separes:
                        print(colorer(
                            "As séparés : une seule carte supplémentaire par main.",
                            Style.GRIS,
                        ))

        for i in range(len(hands)):
            hand = hands[i]
            if len(hand) == 1:
                hand.append(self.tirer_carte())

            self.afficher_main(f"🃏 Main {i + 1}", hand)

            if not as_separes:
                while self.valeur_hand(hand) < 21:
                    choix = demander_choix("t = tirer une carte / r = rester : ", ["t", "r"])
                    if choix == "t":
                        hand.append(self.tirer_carte())
                        input(colorer("Appuie sur Entrée pour voir la carte tirée...", Style.GRIS))
                        self.afficher_main("Tes cartes", hand)
                        self.pause(1.5)
                    else:
                        break

            if self.valeur_hand(hand) > 21:
                print(colorer(f"Main {i + 1} : plus de 21, cette main est perdue.", Style.ROUGE))
                self.pause(1)

        return hands, mise_totale

    def jouer(self, mise=1, capital=None):
        if type(mise) != int or mise <= 0:
            raise ValueError("La mise doit être un nombre entier positif.")
        if capital is not None and mise > capital:
            raise ValueError(f"Ta mise dépasse ton capital de {capital:g} jeton(s).")

        self.nouveau_sabot()
        self.mise_totale = mise
        hand_joueur = [self.tirer_carte(), self.tirer_carte()]
        hand_croupier = [self.tirer_carte(), self.tirer_carte()]

        print(colorer(f"\nTu mises {mise} jeton(s).", Style.CYAN))
        input(colorer("Appuie sur Entrée pour voir ta main...", Style.GRIS))
        self.afficher_main("🃏 Tes cartes", hand_joueur)
        self.pause(1)
        input(colorer("Appuie sur Entrée pour voir la main du croupier...", Style.GRIS))
        print(f"\n🎩 Croupier : {hand_croupier[0]} 🂠")
        self.pause(1)

        gain = self.gain_initial(hand_joueur, hand_croupier, mise)
        if gain is not None:
            print("\nCartes du croupier :", " ".join(hand_croupier))
            print("")
            print(colorer("Blackjack !!", Style.GRAS, Style.MAGENTA))
            print("")
            if gain > 0:
                print(colorer("Bravo ! Tu gagnes 1,5 fois ta mise !", Style.VERT))
            elif gain < 0:
                print(colorer("Le croupier a un blackjack : tu perds ta mise.", Style.ROUGE))
            else:
                print(colorer("Deux blackjacks : égalité, ta mise est rendue.", Style.JAUNE))
            self.pause(2)
            print(f"Tu récupères : {mise + gain:g} jeton(s), mise comprise.")
            return gain

        hands, self.mise_totale = self.jouer_hands(hand_joueur, mise, capital)

        gains = []
        gain_total = 0
        for hand in hands:
            gain = self.gain_final(hand, hand_croupier, mise)
            gains.append(gain)
            gain_total += gain

        self.pause(1)
        self.afficher_main("🎩 Cartes finales du croupier", hand_croupier, style_titre=Style.MAGENTA)
        self.pause(1)
        for i in range(len(hands)):
            print(f"\nMain {i + 1} :", " ".join(hands[i]))
            print(f"Total : {self.valeur_hand(hands[i])} ; gain net : {self.texte_gain(gains[i])}.")
            self.pause(1)

        print(f"\nT'as misé : {self.mise_totale:g} jeton(s).")
        self.pause(1)
        print(f"Tu repars avec : {self.mise_totale + gain_total:g} jeton(s), mises comprises.")
        self.pause(1)
        print(f"Ton gain net total : {self.texte_gain(gain_total)} jeton(s).")
        self.pause(1)
        return gain_total

    def jouer_manche(self, joueurs):
        participants = []

        for joueur in joueurs:
            print(f"\n👤 {colorer(joueur['nom'], Style.GRAS)} — capital : {joueur['capital']:g} jeton(s).")
            if joueur["capital"] < 1:
                print(colorer("Le capital est inférieur à 1 jeton : ce joueur passe son tour.", Style.GRIS))
                continue

            mise = demander_entier(
                f"{joueur['nom']}, ta mise (0 pour passer, "
                f"maximum {int(joueur['capital'])}) : ",
                min_val=0,
                max_val=int(joueur["capital"]),
            )

            if mise == 0:
                print(colorer(f"{joueur['nom']} passe cette manche.", Style.GRIS))
                continue

            participants.append({
                "joueur": joueur,
                "mise": mise,
                "mise_totale": mise,
                "hands": [[]],
                "gains": None,
            })

        if len(participants) == 0:
            print(colorer("Personne n'a misé : aucune manche n'est jouée.", Style.JAUNE))
            return False

        self.nouveau_sabot()
        hand_croupier = []

        for tour in range(2):
            for participant in participants:
                participant["hands"][0].append(self.tirer_carte())
            hand_croupier.append(self.tirer_carte())

        for participant in participants:
            joueur = participant["joueur"]
            mise = participant["mise"]
            hand_joueur = participant["hands"][0]

            entete(f"Au tour de {joueur['nom']} — mise : {mise} jeton(s)", emoji="👤")
            input(colorer("Appuie sur Entrée pour voir ta main...", Style.GRIS))
            self.afficher_main("🃏 Tes cartes", hand_joueur)
            self.pause(1)
            input(colorer("Appuie sur Entrée pour voir la main du croupier...", Style.GRIS))
            print(f"\n🎩 Croupier : {hand_croupier[0]} 🂠")
            self.pause(1)

            gain = self.gain_initial(hand_joueur, hand_croupier, mise)
            if gain is not None:
                participant["gains"] = [gain]
                print("")
                if gain > 0:
                    print(colorer("Blackjack !! Bravo, tu gagnes 1,5 fois ta mise !", Style.VERT, Style.GRAS))
                elif gain < 0:
                    print(colorer("Le croupier a un blackjack : tu perds ta mise.", Style.ROUGE, Style.GRAS))
                else:
                    print(colorer("Deux blackjacks : égalité, ta mise est rendue.", Style.JAUNE, Style.GRAS))
                self.pause(2)
            else:
                hands, mise_totale = self.jouer_hands(
                    hand_joueur, mise, capital=joueur["capital"]
                )
                participant["hands"] = hands
                participant["mise_totale"] = mise_totale

        for participant in participants:
            if participant["gains"] is None:
                gains = []
                for hand in participant["hands"]:
                    gains.append(self.gain_final(hand, hand_croupier, participant["mise"]))
                participant["gains"] = gains

        self.pause(1)
        self.afficher_main("🎩 Cartes finales du croupier", hand_croupier, style_titre=Style.MAGENTA)
        self.pause(1)

        entete("Résultats de la manche", emoji="💰")
        for participant in participants:
            joueur = participant["joueur"]
            gain_total = 0
            print(f"\n👤 {colorer(joueur['nom'], Style.GRAS)}")
            for i in range(len(participant["hands"])):
                hand = participant["hands"][i]
                gain = participant["gains"][i]
                gain_total += gain
                print(f"Main {i + 1} :", " ".join(hand))
                print(f"Total : {self.valeur_hand(hand)} ; gain net : {self.texte_gain(gain)}.")
                self.pause(1)

            mise_totale = participant["mise_totale"]
            print(f"T'as misé : {mise_totale:g} jeton(s).")
            self.pause(1)
            print(f"Tu repars avec : {mise_totale + gain_total:g} jeton(s), mises comprises.")
            self.pause(1)
            print(f"Ton gain net total : {self.texte_gain(gain_total)} jeton(s).")

            joueur["capital"] += gain_total
            joueur["nombre_parties"] += 1
            print(f"💰 Capital de {joueur['nom']} : {joueur['capital']:g} jeton(s).")
            self.pause(1)

        return True

    def bot(self, mise=1):
        if type(mise) != int or mise <= 0:
            raise ValueError("La mise doit être un nombre entier positif.")

        self.nouveau_sabot()
        self.mise_totale = mise
        hand_joueur = [self.tirer_carte(), self.tirer_carte()]
        hand_croupier = [self.tirer_carte(), self.tirer_carte()]

        gain = self.gain_initial(hand_joueur, hand_croupier, mise)
        if gain is not None:
            return gain

        hands = [hand_joueur]
        as_separes = False

        if self.peut_separer(hand_joueur) and hand_joueur[0] in ("A", "8"):
            hands = [[hand_joueur[0]], [hand_joueur[1]]]
            as_separes = hand_joueur[0] == "A"
            self.mise_totale = 2 * mise

        for hand in hands:
            if len(hand) == 1:
                hand.append(self.tirer_carte())
            if not as_separes:
                while self.valeur_hand(hand) < 17:
                    hand.append(self.tirer_carte())

        gain_total = 0
        for hand in hands:
            gain_total += self.gain_final(hand, hand_croupier, mise)
        return gain_total

    def esperance(self, n=100_000, mise=1):
        if type(n) != int or n <= 0:
            raise ValueError("Le nombre de parties doit être un entier positif.")
        if type(mise) != int or mise <= 0:
            raise ValueError("La mise doit être un nombre entier positif.")

        benef = 0
        total_mises = 0
        for i in range(n):
            gain = self.bot(mise=mise)
            benef += gain
            total_mises += self.mise_totale

        self.mise_moyenne = total_mises / n
        self.gain_par_jeton = benef / total_mises
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



def choisir_vitesse():
    entete("Réglage du rythme", emoji="⏱️")
    print("1 : Normal (recommandé pour découvrir le jeu)")
    print("2 : Rapide (pauses raccourcies)")
    print("3 : Instantané (aucune pause, tout s'enchaîne)")
    choix = demander_choix("Ton choix (1/2/3) : ", ["1", "2", "3"])
    return {"1": 1.0, "2": 0.35, "3": 0.0}[choix]


def afficher_regles():
    entete("Règles du jeu")
    regles = [
        "But : battre le croupier sans dépasser 21.",
        "Tous les joueurs misent avant la distribution. Miser 0 permet de passer son tour.",
        "Chaque joueur joue à son tour, face à une même main de croupier.",
        "As : 1 ou 11 ; V, D et R : 10. Le croupier s'arrête à 17.",
        "Blackjack initial : bénéfice net de +1,5 mise ; victoire ordinaire : +1 mise.",
        "Égalité : mise rendue ; défaite : mise perdue.",
        "Les blackjacks sont réglés avant tout tirage supplémentaire.",
        "Paire : séparation possible en deux mains avec une deuxième mise identique.",
        "Une seule séparation ; as séparés : une carte supplémentaire par main.",
        "La mise totale doit être couverte par ton capital, y compris après séparation.",
        "Le capital de chacun est mis à jour après la manche. Les demi-jetons sont conservés.",
        "Un 21 après séparation est payé comme une victoire ordinaire.",
        "Six paquets, soit 312 cartes, remélangés au début de chaque manche.",
        "Cartes tirées sans remise ; choix de jeu : tirer, rester ou séparer une paire.",
    ]
    for regle in regles:
        print(f"• {regle}")
    print("")


def afficher_capitaux(joueurs):
    entete("Capitaux actuels", emoji="💰")
    disponibles = 0
    for joueur in joueurs:
        variation = joueur["capital"] - joueur["capital_initial"]
        if variation > 0:
            style = Style.VERT
        elif variation < 0:
            style = Style.ROUGE
        else:
            style = Style.GRIS
        print(f"{joueur['nom']} : " + colorer(f"{joueur['capital']:g} jeton(s)", style)
              + f" ({variation:+g})")
        if joueur["capital"] >= 1:
            disponibles += 1
    print("")
    return disponibles


def menu_principal():
    print("1 : Jouer une manche")
    print("2 : Voir les règles du jeu")
    print("3 : Comparer blackjack et roulette sur 100 000 parties (espérance)")
    print("4 : Quitter")
    return input(colorer("Ton choix : ", Style.GRIS)).strip()


def comparer_esperances(jeu):
    entete("Comparaison blackjack / roulette", emoji="📊")
    n = 100_000
    mise_simulation = 1
    print("Simulation de 100 000 parties par jeu, avec une mise initiale de 1.")
    print("Référence : un seul bot face au croupier. Les capitaux des joueurs restent disponibles.")
    print("Une séparation au blackjack engage un jeton supplémentaire.\n")

    e_blackjack = jeu.esperance(n=n, mise=mise_simulation)
    e_blackjack_par_jeton = jeu.gain_par_jeton
    mise_moyenne = jeu.mise_moyenne
    e_roulette = jeu.esperance_roulette(n=n, mise=mise_simulation)

    print(colorer("Gains nets moyens par partie :", Style.GRAS))
    print(f"Blackjack : joueur {e_blackjack:+.5f} ; casino {-e_blackjack:+.5f}.")
    print(f"Roulette : joueur {e_roulette:+.5f} ; casino {-e_roulette:+.5f}.")
    print(f"Montant moyen engagé au blackjack : {mise_moyenne:.5f} jeton(s).")

    print(colorer("\nComparaison par jeton effectivement misé :", Style.GRAS))
    print(f"Blackjack : joueur {e_blackjack_par_jeton:+.5f} ; casino {-e_blackjack_par_jeton:+.5f}.")
    print(f"Roulette : joueur {e_roulette / mise_simulation:+.5f} ; casino {-e_roulette / mise_simulation:+.5f}.")
    print(f"Espérance théorique du joueur à la roulette : {-1 / 37:+.5f}.")
    print("")
    input(colorer("Appuie sur Entrée pour revenir au menu...", Style.GRIS))


def configurer_joueurs():
    nombre_joueurs = demander_entier("Combien de joueurs ? (de 1 à 7) : ", min_val=1, max_val=7)

    joueurs = []
    for numero in range(1, nombre_joueurs + 1):
        while True:
            nom = input(f"Nom du joueur {numero} (Entrée = Joueur {numero}) : ").strip()
            if nom == "":
                nom = f"Joueur {numero}"
            if not any(j["nom"].lower() == nom.lower() for j in joueurs):
                break
            print(colorer("Ce nom est déjà utilisé. Choisis un autre nom ou pseudonyme.", Style.ROUGE))

        capital_initial = demander_entier(f"Capital de départ de {nom} (entier positif) : ", min_val=1)

        joueurs.append({
            "nom": nom,
            "capital_initial": capital_initial,
            "capital": capital_initial,
            "nombre_parties": 0,
        })
    return joueurs


def afficher_bilan_final(jeu, joueurs, nombre_manches):
    entete("Bilan final de la session", emoji="💰")
    print(f"Nombre de manches jouées : {nombre_manches}")
    for joueur in joueurs:
        bilan = joueur["capital"] - joueur["capital_initial"]
        print(f"\n👤 {colorer(joueur['nom'], Style.GRAS)}")
        print(f"Nombre de parties jouées : {joueur['nombre_parties']}")
        print(f"Capital de départ : {joueur['capital_initial']:g} jeton(s).")
        print(f"Capital restant : {joueur['capital']:g} jeton(s).")
        print(f"Bénéfice ou perte totale : {jeu.texte_gain(bilan)} jeton(s).")


def main():
    _activer_ansi()
    jeu = Blackjack()

    effacer_ecran()
    entete("BLACKJACK SIMPLIFIÉ — SIX PAQUETS")
    print("\nBut : battre le croupier sans dépasser 21.\n")
    jeu.vitesse = choisir_vitesse()

    effacer_ecran()
    joueurs = configurer_joueurs()

    nombre_manches = 0

    while True:
        effacer_ecran()
        disponibles = afficher_capitaux(joueurs)

        if disponibles == 0:
            print(colorer("Aucun joueur ne peut miser au moins 1 jeton. La session est terminée.", Style.JAUNE))
            break

        choix = menu_principal()

        if choix == "1":
            if jeu.jouer_manche(joueurs):
                nombre_manches += 1
                input(colorer("\nAppuie sur Entrée pour continuer...", Style.GRIS))
        elif choix == "2":
            effacer_ecran()
            afficher_regles()
            input(colorer("Appuie sur Entrée pour revenir au menu...", Style.GRIS))
        elif choix == "3":
            effacer_ecran()
            comparer_esperances(jeu)
        elif choix == "4":
            break
        else:
            print(colorer("Choisis 1, 2, 3 ou 4.", Style.ROUGE))
            input(colorer("Appuie sur Entrée pour continuer...", Style.GRIS))

    effacer_ecran()
    afficher_bilan_final(jeu, joueurs, nombre_manches)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(colorer("\n\nÀ bientôt !", Style.CYAN))
        sys.exit(0)
