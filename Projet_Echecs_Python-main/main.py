import pyxel

SIDE = 16  
CASE_PER_LINE = 8  
SCREEN_SIZE = SIDE * CASE_PER_LINE


#PARTIE 1 : LES REGLS DU JEU 
class Mouvement:
    def __init__(self):
        self.selection = None  # Aucune pièce sélectionnée (on n'a pas encore cliqué)
        self.pieces = {}  # Le dictionnaire dans lequel on note les positions des pièces sur le plateau
        self.tour = "B"  # C'est aux blancs de jouer 
        self.pieces_ont_bouge = set() # Pour savoir quelles pièces ont déjà bougé (pour le roque)
        self.echec_au_roi = False 
        self.configurer_depart()  # On place les pièces au départ

    def configurer_depart(self):
        ordre_pieces = ["T", "C", "F", "D", "R", "F", "C", "T"] # Liste qui contient les pièces à placer, chaque pièce est appelée par son initiale
        for i in range(8): 
            self.pieces[(i, 0)] = ordre_pieces[i] + "N" #On place les noirs
            self.pieces[(i, 1)] = "PN"     
            self.pieces[(i, 7)] = ordre_pieces[i] + "B" # On place les blancs          
            self.pieces[(i, 6)] = "PB"                  
            
    #GESTION DES ECHECS AU ROI
    def trouver_roi(self, couleur): #Trouve la position du roi d'une certaine couleur
        target = "R" + couleur  #On cherche ce roi là
        for pos, nom in self.pieces.items():  # On parcourt le dictionnaire avec les positions des pièces
            if nom == target: 
                return pos  # on renvoie sa position s'il est encore sur la plateau
        return None 

    def case_attaquee(self, x, y, couleur_attaquant):
        for pos_p, nom_p in self.pieces.items():  # On regarde toutes les pièces
            if nom_p.endswith(couleur_attaquant):  # Si c'est un ennemi  
                if self.regles_de_base(nom_p, pos_p[0], pos_p[1], x, y): # On regarde s'il peut atteindre cette case
                    return True 
        return False 

    def est_en_echec(self, couleur): #regarde ou est le roi et s'il est attaqué
        pos_roi = self.trouver_roi(couleur)
        if not pos_roi: return False
        couleur_ennemie = "N" if couleur == "B" else "B" 
        return self.case_attaquee(pos_roi[0], pos_roi[1], couleur_ennemie)

    # REGLES DE BASE : DEPLACEMENT DE CHAQUE TYPE DE PIECE
    def regles_de_base(self, type_piece, old_x, old_y, x_g, y_g):
        dx = abs(x_g - old_x)  # Distance horizontale parcourue
        dy = abs(y_g - old_y)  # Distance verticale parcourue
        nom = type_piece[0]    # Première lettre donne le type de pièce 
        couleur = type_piece[1] # Deuxième lettre donne la couleur
        couleur_ennemie = "N" if couleur == "B" else "B"

        piece_cible = self.pieces.get((x_g, y_g)) #On regarde dans le dictionnaire si on mange une pièce
        if piece_cible and piece_cible.endswith(couleur): #on peut pas manger ses propres pièces
            return False 

        # DEPLACEMENT AUTORISE POUR CHAQUE PIECE
        # PION
        if nom == "P":
            direction = -1 if couleur == "B" else 1
            depart_y = 6 if couleur == "B" else 1
            if x_g == old_x:
                if piece_cible is None: # On vérifie que aucune pièce bloque le pion devant lui
                    if y_g == old_y + direction: 
                        return True
                    if old_y == depart_y and y_g == old_y + (2 * direction): #Si le pion a pas encore bougé et qu'il y a deux cases vides devant
                        if self.pieces.get((x_g, old_y + direction)) is None: 
                            return True
            
            # Cas où on mange en diago
            elif abs(x_g - old_x) == 1 and y_g == old_y + direction:
                if piece_cible and piece_cible.endswith(couleur_ennemie): #On vérifie qu'il y a une pièce à manger
                    return True
            return False

        # TOUR
        if nom == "T":
            if dx != 0 and dy != 0: # On peut pas manger en diago
                return False 
            #Vertical
            if dx == 0: 
                pas = 1 if y_g > old_y else -1
                for i in range(1, dy):
                    if self.pieces.get((old_x, old_y + i * pas)): #On vérifie pour chaque case sur le chemin s'il y a un ennemi (on en veut pas ici)
                        return False
            
            #Horizontal
            else: 
                pas = 1 if x_g > old_x else -1
                for i in range(1, dx):
                    if self.pieces.get((old_x + i * pas, old_y)): #On vérifie pour chaque case sur le chemin s'il y a un ennemi (on en veut pas ici)
                        return False
            return True

        # FOU
        if nom == "F":
            if dx != dy: 
                return False # Seules les diagonales sont autorisées
            pas_x = 1 if x_g > old_x else -1
            pas_y = 1 if y_g > old_y else -1
            for i in range(1, dx):
                if self.pieces.get((old_x + i * pas_x, old_y + i * pas_y)): # On vérifie s'il y a des pièces qui bloquent
                    return False
            return True

        # CAVALIER
        if nom == "C":
            return (dx == 1 and dy == 2) or (dx == 2 and dy == 1) #Les règles pour que le mouvement soit bien en L

        # DAME = TOUR et FOU
        if nom == "D":
            if dx == dy: # Fou
                pas_x = 1 if x_g > old_x else -1
                pas_y = 1 if y_g > old_y else -1
                for i in range(1, dx):
                    if self.pieces.get((old_x + i * pas_x, old_y + i * pas_y)):
                        return False
                return True
            elif dx == 0 or dy == 0: # Tour
                if dx == 0:
                    pas = 1 if y_g > old_y else -1
                    for i in range(1, dy):
                        if self.pieces.get((old_x, old_y + i * pas)): 
                            return False
                else:
                    pas = 1 if x_g > old_x else -1
                    for i in range(1, dx):
                        if self.pieces.get((old_x + i * pas, old_y)): 
                            return False
                return True
            return False

        # ROI
        if nom == "R":
            if dx <= 1 and dy <= 1: 
                return True #Règles pour bouger d'une case n'importe où
            return False

    # REGLES + APPRONFONDIES : ON VERIFIE LES ECHECS ET LE ROQUE
    def coup_valide_complet(self, old_x, old_y, x_g, y_g):
        if old_x == x_g and old_y == y_g: return False #Se passe rien si on reste sur la même case
        type_piece = self.pieces[(old_x, old_y)]
        couleur = type_piece[1]
        
        # GESTION DU ROQUE
        if type_piece[0] == "R" and abs(x_g - old_x) == 2 and (y_g == old_y):
            if self.est_en_echec(couleur): return False # On peut pas roquer s'il y a échec
            if (old_x, old_y) in self.pieces_ont_bouge: return False # On vérifie que le roi a pas encore bougé

            x_tour = 7 if x_g > old_x else 0 
            pos_tour = (x_tour, old_y)
            piece_tour = self.pieces.get(pos_tour)
            if not piece_tour or piece_tour[0] != "T" or pos_tour in self.pieces_ont_bouge:
                return False #On vérifie si la tour est à sa place et a pas bougé

            # On vérifie qu'il y a personne entre le roi et la tour
            pas = 1 if x_tour > old_x else -1
            start, end = (old_x + 1, x_tour) if pas == 1 else (x_tour + 1, old_x)
            for k in range(start, end):
                if self.pieces.get((k, old_y)) is not None: return False
            
            # On vérifie que le roi passe pas sur une case qui est attaquée
            case_intermediaire_x = old_x + pas
            couleur_ennemie = "N" if couleur == "B" else "B"
            if self.case_attaquee(case_intermediaire_x, old_y, couleur_ennemie): return False
            if self.case_attaquee(x_g, y_g, couleur_ennemie): return False 
                
            return "ROQUE" # C'est le code qu'on renvoie pour dire que le roque est valide 

        # ECHEC AU ROI : On joue le coup pour de faux et on vérifie si le roi meurt. Si le roi meurt, alors le roi était en échec et le coup était pas légal
        if not self.regles_de_base(type_piece, old_x, old_y, x_g, y_g): #on vérifie déja que le mouvement respecte la géométrie
            return False

        # On simule le coup pour voir s'il y avait échec
        cible_temp = self.pieces.get((x_g, y_g)) # Si on mange une pièce, on la garde en mémoire
        del self.pieces[(old_x, old_y)]          # On supprime l'ancienne position de la pièce du dico et on la met à sa nouvelle position
        self.pieces[(x_g, y_g)] = type_piece     # On la met à l'arrivée
        
        roi_en_danger = self.est_en_echec(couleur) #On regarde si le roi meurt à cause de ce coup
        
        #S'il y avait échec, on annule le coup simulé
        self.pieces[(old_x, old_y)] = type_piece # On remet la pièce à sa position initiale
        if cible_temp:
            self.pieces[(x_g, y_g)] = cible_temp # On remet la pièce mangée dans le dictionnaire
        else:
            del self.pieces[(x_g, y_g)]          # on supprime la pièce de sa case d'arrivée

        
        if roi_en_danger: 
            return False #Si le roi est en danger, le coup est pas valide

        return True #Si le roi est pas en danger, le coup est valide

    # INTELLIGENCE ARTIFICIELLE (MINIMAX AVEC ALPHA BETA)
    def obtenir_tous_coups(self, pieces, tour): #fonction qui renvoie TOUS les coups possibles pour l'ordi
        coups = []
        for (x, y), code in list(pieces.items()):
            if code.endswith(tour): #On regarde que les pièces de la bonne couleur
                for gx in range(8): # On teste toutes les cases du plateau
                    for gy in range(8):
                        if self.coup_valide_complet(x, y, gx, gy):
                            coups.append(((x, y), (gx, gy))) # On ajoute les coups valides à la liste
        return coups

    def evaluer_plateau(self, pieces): # Evaluateur de coups. Les pièces noires = points positifs, les blanches = points négatifs
        valeurs = {"P": 10, "C": 30, "F": 30, "T": 50, "D": 90, "R": 900}
        score = 0
        for code in pieces.values():
            nom = code[0]
            val = valeurs.get(nom, 0)
            if code[1] == "B": 
                score -= val # A l'avantage du joueur, on fait baisser le score
            else: score += val # A l'avantage de l'IA, on augmente le score
        return score

    def simuler_coup(self, pieces, coup): #Fonction qui permet à l'IA de simuler des coups pour analyser plusieurs coups
        nouvelles_pieces = pieces.copy()
        (old_x, old_y), (new_x, new_y) = coup
        type_piece = nouvelles_pieces.pop((old_x, old_y))
        nouvelles_pieces[(new_x, new_y)] = type_piece
        return nouvelles_pieces

    def minimax(self, pieces, profondeur, alpha, beta, maximisant):#Algorithme mini max recursif avec alpha/beta. Maximisant est le booléen qui indique si c'est celui qui veut maximiser le score qui joue le coup
        

        if profondeur == 0:#le cas de base
            return self.evaluer_plateau(pieces), None

        coups = self.obtenir_tous_coups(pieces, "N" if maximisant else "B")
       

        if not coups:#si on peut rien faire
            return self.evaluer_plateau(pieces), None

        meilleur_coup = None

        if maximisant:#si on simule un tour d'IA
            max_eval = -float('inf')
            for coup in coups:
                sim_pieces = self.simuler_coup(pieces, coup)
                eval, truc = self.minimax(sim_pieces, profondeur - 1, alpha, beta, False)
                if eval > max_eval:#si on trouve un meilleur coup on le retient
                    max_eval = eval
                    meilleur_coup = coup
                alpha = max(alpha, eval)
                if beta <= alpha:#si on est sur de trouver un meilleur coup ailleurs on ne continue pas dans cette branche
                    break
            return max_eval, meilleur_coup
        

        else:#si on simule le meilleur coup de l'humain
            min_eval = float('inf')
            for coup in coups:
                sim_pieces = self.simuler_coup(pieces, coup)
                eval, _ = self.minimax(sim_pieces, profondeur - 1, alpha, beta, True)
                if eval < min_eval:#si l'humain trouve un meilleur coup, il le retient et cherche ensuite parmi les coups meiulleurs que celui ci
                    min_eval = eval
                    meilleur_coup = coup
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, meilleur_coup
   

    def gerer_clic(self, x_g, y_g):

        if self.selection is None:#si on avait pas encore chosi de piece
            if (x_g, y_g) in self.pieces:#si on clique pas sur une case vide
                piece = self.pieces[(x_g, y_g)]
                if piece.endswith(self.tour):#si on clique sur une de nos pieces
                    self.selection = (x_g, y_g)

        else:#si on avait deja clique sur une de nos pieces, c est a dire qu on va cliquer sur la case de destination
            old_x, old_y = self.selection
            if old_x == x_g and old_y == y_g:#si on reclique sur la case selectionee on annule la selection
                self.selection = None
                return

            resultat_coup = self.coup_valide_complet(old_x, old_y, x_g, y_g)#le nouveau coup
           

            if resultat_coup:#si on a fait un coup valide on met a jour le plateau
                type_piece = self.pieces[(old_x, old_y)]
               

                del self.pieces[(old_x, old_y)]
                self.pieces[(x_g, y_g)] = type_piece
               

                self.pieces_ont_bouge.add((old_x, old_y))
                self.pieces_ont_bouge.add((x_g, y_g))

                if resultat_coup == "ROQUE":
                    y_roque = old_y
                    if x_g > old_x: # Petit Roque
                        tour = self.pieces.pop((7, y_roque))
                        self.pieces[(x_g - 1, y_roque)] = tour
                        self.pieces_ont_bouge.add((7, y_roque))
                    else: # Grand Roque
                        tour = self.pieces.pop((0, y_roque))
                        self.pieces[(x_g + 1, y_roque)] = tour
                        self.pieces_ont_bouge.add((0, y_roque))

                #on prepare les variables poir le coup d'apres (changement joueur, effacement clic,...)
                self.selection = None
                self.tour = "N" if self.tour == "B" else "B"
                self.echec_au_roi = self.est_en_echec(self.tour)
               

            else:#si on a pas clique sur une case de destination où on peut emmener notre piece
                cible = self.pieces.get((x_g, y_g))
                if cible and cible.endswith(self.tour):#si on a cliqué sur une de nos piece, on met a jour la piece selectionnée
                    self.selection = (x_g, y_g)
                else:#si on clique sur une case où on a pas le droit de jouer on ne fait rien
                    self.selection = None

# PARTIE 2 : On s'occupe maintenant de l'affichage du plateau, des pièces et de la partie qui évolue
class App:
    def __init__(self):
        pyxel.init(SCREEN_SIZE, SCREEN_SIZE, title="Echecs")
        pyxel.load("assets.pyxres") # On charge les images de nos pièces
     

        self.mouvement = Mouvement()# On lance le jeu actif
        pyxel.mouse(True)#On active la souris
        pyxel.run(self.update, self.draw)# On lance les mises a jour successives apres chaque coup

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):#Pour quitte le jeu on fait Q
            pyxel.quit()
       

        # On définit le tour de l'IA qui joue les noirs
        if self.mouvement.tour == "N":
            # On demande a IA de réfléchir (profondeur 2 definit tout en haut)
            _, meilleur_coup = self.mouvement.minimax(
                self.mouvement.pieces, 2 , -float('inf'), float('inf'), True
            )
           

            if meilleur_coup:#Si un coup est trouvé par l'IA on le joue en mettant à jour le dictionnaire de l'état du plateau nommé pieces
                (ox, oy), (nx, ny) = meilleur_coup
                piece_jouee = self.mouvement.pieces.pop((ox, oy))
                self.mouvement.pieces[(nx, ny)] = piece_jouee
                self.mouvement.tour = "B"# C'est a l'homme de jouer désormais
                self.mouvement.echec_au_roi = self.mouvement.est_en_echec("B")
            else:
                print("L'IA ne peut plus bouger !")# Si l IA ne peut rien faire c'est qu elle a perdu ou fait égalité
                self.mouvement.tour = "B"
            return

        # On definit maintenat le tour de l'homme qui doit cliquer pour biuger ses pieces
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT): # Si on fait clic gauche
            # On convertit les pixels de la souris en cases de la grille (0 à 7)
            x_g = pyxel.mouse_x // SIDE
            y_g = pyxel.mouse_y // SIDE
            if 0 <= x_g < 8 and 0 <= y_g < 8: # Si on clique dans l'écran
                self.mouvement.gerer_clic(x_g, y_g)

    def draw(self):
        pyxel.cls(0) # On efface l'écran (tout noir)
        self.draw_plateau() # On dessine le damier
        self.draw_pieces() # On dessine les pièces

    def draw_plateau(self):

        #dessine le damier 
        for i in range(CASE_PER_LINE):
            for j in range(CASE_PER_LINE):
                couleur = 7 if (i + j) % 2 == 0 else 5
                pyxel.rect(i * SIDE, j * SIDE, SIDE, SIDE, couleur)
       

        # Dessine le cadre jaune si une pièce est sélectionnée
        if self.mouvement.selection:
            sx, sy = self.mouvement.selection
            pyxel.rectb(sx * SIDE, sy * SIDE, SIDE, SIDE, 10) #rectb sert a faire que le contour

        # Met en rouge la case si le roi est en echec
        if self.mouvement.echec_au_roi:
            roi_pos = self.mouvement.trouver_roi(self.mouvement.tour)
            if roi_pos:
                pyxel.rect(roi_pos[0] * SIDE, roi_pos[1] * SIDE, SIDE, SIDE, 8)

    def draw_pieces(self):
        for (x, y), code in self.mouvement.pieces.items():
            self.draw_piece_seule(code, x, y)

    def draw_piece_seule(self, code, x, y):#attention besoin du fichier du dessin de chaque piece
        px = x * SIDE
        py = y * SIDE
        if code == "PB": pyxel.circ(px + 8, py + 8, 5, 15)
        elif code == "RB": pyxel.blt(px, py, 0, 0, 0, 16, 16, 0)
        elif code == "DB": pyxel.blt(px, py, 0, 16, 0, 16, 16, 0)
        elif code == "CB": pyxel.blt(px, py, 0, 32, 0, 16, 16, 0)
        elif code == "FB": pyxel.blt(px, py, 0, 48, 0, 16, 16, 0)
        elif code == "TB": pyxel.blt(px, py, 0, 64, 0, 16, 16, 0)
        elif code == "PN": pyxel.circ(px + 8, py + 8, 5, 9)
        elif code == "RN": pyxel.blt(px, py, 0, 0, 16, 16, 16, 0)
        elif code == "DN": pyxel.blt(px, py, 0, 16, 16, 16, 16, 0)
        elif code == "CN": pyxel.blt(px, py, 0, 32, 16, 16, 16, 0)
        elif code == "FN": pyxel.blt(px, py, 0, 48, 16, 16, 16, 0)
        elif code == "TN": pyxel.blt(px, py, 0, 64, 16, 16, 16, 0)


#C'est parti, en voiture Simone
App()
