import os
import sys
import json
import traceback
import collections

from PyQt5 import QtCore, QtGui, QtWidgets, uic

# Make sure the xwing module is in the path
xwing_path = os.path.normpath(os.path.join(os.path.realpath(__file__), "..", "..", ".."))
if xwing_path not in sys.path:
    sys.path.append(xwing_path)

from xwing import CARD_DATA, REFERENCE_DATA, CONDITIONS, DAMAGE_DATA, INFO_DIR
from xwing import search_for_value, get_ship_chars
from xwing.gui.x_models import PilotModel, UpgradeAstromechModel, UpgradeBombModel, UpgradeCannonModel, UpgradeCrewModel

# Create object template for sending up to the tableview via the model
_FlattenedPilot = collections.namedtuple('FlattenedPilot', ['name',
                                                            'skill',
                                                            'text',
                                                            'faction',
                                                            'ship',
                                                            'cost',
                                                            'attack',
                                                            'energy',
                                                            'agility',
                                                            'hull',
                                                            'shields',
                                                            'size',
                                                            'unique',
                                                            'full_data'
                                                           ])

_FlattenedAstromech = collections.namedtuple('FlattenedAstro', ['name',
                                                                'type',
                                                                'cost',
                                                                'text',
                                                                'unique',
                                                                'full_data'
                                                               ])

_FlattenedBomb = collections.namedtuple('FlattenedBomb', ['name',
                                                          'type',
                                                          'cost',
                                                          'text',
                                                          'effect',
                                                          'full_data'
                                                         ])

_FlattenedCannon = collections.namedtuple('FlattenedCannon', ['name',
                                                              'type',
                                                              'cost',
                                                              'attack',
                                                              'range',
                                                              'text',
                                                              'full_data'
                                                             ])

_FlattenedCrew = collections.namedtuple('FlattenedCrew', ['name',
                                                          'type',
                                                          'cost',
                                                          'limited',
                                                          'unique',
                                                          'faction',
                                                          'text',
                                                          'full_data'
                                                         ])


form_class, base_class = uic.loadUiType(os.path.join(xwing_path, 'xwing', 'gui', 'xgui.ui'))

def main():
    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QMainWindow()

    prog = XWingCardViewer()

    prog.show()
    sys.exit(app.exec_())

class XWingCardViewer(QtWidgets.QMainWindow):
    def __init__(self):
        super(XWingCardViewer, self).__init__()
        
        # Build UI
        self.ui = form_class()
        self.ui.setupUi(self)
        # self.setStyleSheet(open(os.path.join(xwing_path, 'xwing', 'gui', 'x_style.qss'), "r").read())

        # Initialize and populate views
        self.card_types = ['Pilots', 'Astros', 'Bombs', 'Cannons', 'Crew']
        # self.card_types = ['Pilots']
        self.initViews()
        self.populateViews()

        # self.ui.pilotView.resizeRowsToContents()
        # Set sorts going
        self.ui.card_search_button.clicked.connect(self.populateViews)
        self.ui.card_search_field.returnPressed.connect(self.populateViews)
        

    def updateImage(self, sel_card_info):
        img = self.ui.card_image
        # print(sel_card_info)
        try:
            path_to_image = "%s%s%s" % (os.path.join(xwing_path, "xwing", "info", "images"), os.sep, os.path.join(*sel_card_info['image'].split("/")))
            image_text = ''
        except:
            path_to_image = None
            image_text = 'No image available'
        # print(path_to_image)
        img.setPixmap(QtGui.QPixmap(path_to_image))
        img.setText(image_text)
        kind = 'upgrades' if sel_card_info.get('slot', None) else 'pilots'
        obtain_from = self.get_sources(kind, str(sel_card_info['id']))
        obtain_from_string = "\n\t\t".join(obtain_from)

        self.ui.obtain_source_label.setText("Can be purchased from: \n\t\t%s" % obtain_from_string)

    def updatePilotImage(self):
        sel_card_info = json.loads(self.selectedObject(self.ui.pilotView, self.ui.pilotView.currentIndex()))
        self.updateImage(sel_card_info)

    def updateAstroImage(self):
        sel_card_info = json.loads(self.selectedObject(self.ui.astroView, self.ui.astroView.currentIndex()))
        self.updateImage(sel_card_info)

    def updateBombImage(self):
        sel_card_info = json.loads(self.selectedObject(self.ui.bombView, self.ui.bombView.currentIndex()))
        self.updateImage(sel_card_info)

    def updateCannonImage(self):
        sel_card_info = json.loads(self.selectedObject(self.ui.cannonView, self.ui.cannonView.currentIndex()))
        self.updateImage(sel_card_info)

    def updateCrewImage(self):
        sel_card_info = json.loads(self.selectedObject(self.ui.crewView, self.ui.crewView.currentIndex()))
        self.updateImage(sel_card_info)

    def initViews(self):
        for card_type in self.card_types:
            getattr(self, 'init%s' % card_type)()

    def initPilots(self):
        pilot_view = self.ui.pilotView
        pilot_sort = QtCore.QSortFilterProxyModel(pilot_view)
        pilot_view.setModel(pilot_sort)

    def initAstros(self):
        astro_view = self.ui.astroView
        astro_sort = QtCore.QSortFilterProxyModel(astro_view)
        astro_view.setModel(astro_sort)

    def initBombs(self):
        bomb_view = self.ui.bombView
        bomb_sort = QtCore.QSortFilterProxyModel(bomb_view)
        bomb_view.setModel(bomb_sort)

    def initCannons(self):
        cannon_view = self.ui.cannonView
        cannon_sort = QtCore.QSortFilterProxyModel(cannon_view)
        cannon_view.setModel(cannon_sort)

    def initCrew(self):
        crew_view = self.ui.crewView
        crew_sort = QtCore.QSortFilterProxyModel(crew_view)
        crew_view.setModel(crew_sort)

    def populateViews(self):
        for card_type in self.card_types:
            getattr(self, 'populate%s' % card_type)()
        print('')

    def populatePilots(self):
        self.ui.pilotView.clearSpans()
        search_term = self.ui.card_search_field.text().lower()
        print("Searching Pilots for %s" % search_term)
        try:
            pilot_data = CARD_DATA['Pilot']
            found = search_for_value(pilot_data, 'Pilot', search_term)
            # print(json.dumps(found, sort_keys=True, indent=4, separators=(',', ': ')))
            found_pilots_set = set()
            for item in found:
                try:
                    
                    # print('item: %s' % json.dumps(item, sort_keys=True, indent=4, separators=(',', ': ')))
                    # grab_bag = 
                    # # grab_bag = next((entry for (index, entry) in enumerate(pilot_data) if entry['id'] == item['id']), None)
                    # print('Grab Bag: %s' % json.dumps(grab_bag, sort_keys=True, indent=4, separators=(',', ': ')))
                    card = [entry for entry in pilot_data if (entry['id'] == item['id'])][0]
                except:
                    continue
                # card['card_type'] = 'Pilot'
                # print("I'm adding a card to the list...")
                # print(json.dumps(card, sort_keys=True, indent=4))

                ship_chars = get_ship_chars(card, CARD_DATA['Ship'])
                # print(ship_chars)

                if ship_chars['size'] == 'huge':
                    ship_attack_type = 'attack' if 'attack' in ship_chars else 'energy'
                else:
                    ship_attack_type = 'attack'

                found_pilots_set.add(_FlattenedPilot(name=card['name'],
                                                     skill=str(card['skill']),
                                                     text=card.get('text',None),
                                                     faction=card['faction'],
                                                     ship=card['ship'],
                                                     cost=card['points'],
                                                     attack=ship_chars.get('attack', None),
                                                     energy=ship_chars.get('energy', None),
                                                     agility=ship_chars['agility'],
                                                     hull=ship_chars['hull'],
                                                     shields=ship_chars['shields'],
                                                     size=ship_chars['size'],
                                                     unique=card.get('unique', False),
                                                     full_data=json.dumps(card)
                                                    ))

            found_pilots = list(found_pilots_set)

            pilot_view  = self.ui.pilotView
            pilot_sort  = pilot_view.model()
            pilot_model = PilotModel(found_pilots)
            prev_model  = pilot_sort.sourceModel()
            # if prev_model: prev_model.deleteLater()
            pilot_sort.setSourceModel(pilot_model)
            # pilot_model.selectionChanged.connect(self.updateImage)
            
            # pilot_view.setWordWrap(True)
            pilot_view.horizontalHeader().setStretchLastSection(True)
            pilot_view.resizeColumnsToContents()
            pilot_view.resizeRowsToContents()
            pilot_view.setSortingEnabled(True)
            pilot_view.resizeRowsToContents()
            pilot_view.clicked.connect(self.updatePilotImage)
            pilot_view.sortByColumn(0, QtCore.Qt.AscendingOrder)

        except Exception as e:
            raise Exception("Something went wrong with the pilot initialization... BORK!\n%s" % traceback.format_exc())
            sys.exit(3)

    def populateAstros(self):
        self.ui.astroView.clearSpans()
        search_term = self.ui.card_search_field.text().lower()
        print("Searching Astromechs for %s" % search_term)
        try:
            upgrade_data = CARD_DATA['Upgrade']
            found = search_for_value(upgrade_data, 'Upgrade', search_term, slot='Astromech')
            # print(json.dumps(found, sort_keys=True, indent=4, separators=(',', ': ')))
            found_astros_set = set()
            for item in found:
                try:
                    card = [entry for entry in upgrade_data if (entry['id'] == item['id'])][0]
                except:
                    continue
                found_astros_set.add(_FlattenedAstromech(name=card['name'],
                                                         type=card['slot'],
                                                         cost=str(card['points']),
                                                         text=card['text'],
                                                         unique=card.get('unique', False),
                                                         full_data=json.dumps(card)
                                                        ))

            found_astros = list(found_astros_set)

            astro_view  = self.ui.astroView
            astro_sort  = astro_view.model()
            astro_model = UpgradeAstromechModel(found_astros)
            prev_model  = astro_sort.sourceModel()
            # if prev_model: prev_model.deleteLater()
            astro_sort.setSourceModel(astro_model)
            # astro_model.selectionChanged.connect(self.updateImage)
            
            
            astro_view.horizontalHeader().setStretchLastSection(True)
            astro_view.resizeColumnsToContents()
            astro_view.resizeRowsToContents()
            astro_view.setSortingEnabled(True)
            astro_view.resizeRowsToContents()
            astro_view.clicked.connect(self.updateAstroImage)
            astro_view.sortByColumn(0, QtCore.Qt.AscendingOrder)
            astro_view.setWordWrap(True)

        except Exception as e:
            raise Exception("Something went wrong with the astromech initialization... BORK!\n%s" % traceback.format_exc())
            sys.exit(3)

    def populateBombs(self):
        self.ui.bombView.clearSpans()
        search_term = self.ui.card_search_field.text().lower()
        print("Searching Bombs for %s" % search_term)
        try:
            upgrade_data = CARD_DATA['Upgrade']
            found = search_for_value(upgrade_data, 'Upgrade', search_term, slot='Bomb')
            # print(json.dumps(found, sort_keys=True, indent=4, separators=(',', ': ')))
            found_bomb_set = set()
            for item in found:
                try:
                    card = [entry for entry in upgrade_data if (entry['id'] == item['id'])][0]
                except:
                    continue

                found_bomb_set.add(_FlattenedBomb(name=card['name'],
                                                    type=card['slot'],
                                                    cost=str(card['points']),
                                                    text=card['text'],
                                                    effect=card.get('effect', None),
                                                    full_data=json.dumps(card)
                                                    ))

            found_bombs = list(found_bomb_set)

            bomb_view  = self.ui.bombView
            bomb_sort  = bomb_view.model()
            bomb_model = UpgradeBombModel(found_bombs)
            prev_model  = bomb_sort.sourceModel()
            # if prev_model: prev_model.deleteLater()
            bomb_sort.setSourceModel(bomb_model)
            # bomb_model.selectionChanged.connect(self.updateImage)
            
            bomb_view.horizontalHeader().setStretchLastSection(True)
            bomb_view.resizeColumnsToContents()
            bomb_view.resizeRowsToContents()
            bomb_view.setSortingEnabled(True)
            bomb_view.resizeRowsToContents()
            bomb_view.clicked.connect(self.updateBombImage)
            bomb_view.sortByColumn(0, QtCore.Qt.AscendingOrder)
            bomb_view.setWordWrap(True)

        except Exception as e:
            raise Exception("Something went wrong with the bomb initialization... BORK!\n%s" % traceback.format_exc())
            sys.exit(3)

    def populateCannons(self):
        self.ui.cannonView.clearSpans()
        search_term = self.ui.card_search_field.text().lower()
        print("Searching Cannons for %s" % search_term)
        try:
            upgrade_data = CARD_DATA['Upgrade']
            found = search_for_value(upgrade_data, 'Upgrade', search_term, slot='Cannon')
            # print(json.dumps(found, sort_keys=True, indent=4, separators=(',', ': ')))
            found_cannon_set = set()
            for item in found:
                try:
                    card = [entry for entry in upgrade_data if (entry['id'] == item['id'])][0]
                except:
                    continue

                found_cannon_set.add(_FlattenedCannon(name=card['name'],
                                                  type=card['slot'],
                                                  cost=str(card['points']),
                                                  attack=card.get('attack', None),
                                                  range=card.get('range', None),
                                                  text=card['text'],
                                                  full_data=json.dumps(card)
                                                 ))

            found_cannons = list(found_cannon_set)

            cannon_view  = self.ui.cannonView
            cannon_sort  = cannon_view.model()
            cannon_model = UpgradeCannonModel(found_cannons)
            prev_model  = cannon_sort.sourceModel()
            # if prev_model: prev_model.deleteLater()
            cannon_sort.setSourceModel(cannon_model)
            # cannon_model.selectionChanged.connect(self.updateImage)
            
            cannon_view.setWordWrap(True)
            cannon_view.horizontalHeader().setStretchLastSection(True)
            cannon_view.resizeColumnsToContents()
            cannon_view.resizeRowsToContents()
            cannon_view.setSortingEnabled(True)
            cannon_view.resizeRowsToContents()
            cannon_view.clicked.connect(self.updateCannonImage)
            cannon_view.sortByColumn(0, QtCore.Qt.AscendingOrder)
            cannon_view.setWordWrap(True)

        except Exception as e:
            raise Exception("Something went wrong with the cannon initialization... BORK!\n%s" % traceback.format_exc())
            sys.exit(3)

    def populateCrew(self):
        self.ui.crewView.clearSpans()
        search_term = self.ui.card_search_field.text().lower()
        print("Searching Crews for %s" % search_term)
        try:
            upgrade_data = CARD_DATA['Upgrade']
            found = search_for_value(upgrade_data, 'Upgrade', search_term, slot='Crew')
            # print(json.dumps(found, sort_keys=True, indent=4, separators=(',', ': ')))
            found_crew_set = set()
            for item in found:
                try:
                    card = [entry for entry in upgrade_data if (entry['id'] == item['id'])][0]
                except:
                    continue

                found_crew_set.add(_FlattenedCrew(name=card['name'],
                                                  type=card['slot'],
                                                  cost=str(card['points']),
                                                  limited=card.get('limited', False),
                                                  unique=card.get('unique', False),
                                                  faction=card.get('faction', None),
                                                  text=card['text'],
                                                  full_data=json.dumps(card)
                                                 ))


            found_crews = list(found_crew_set)

            crew_view  = self.ui.crewView
            crew_sort  = crew_view.model()
            crew_model = UpgradeCrewModel(found_crews)
            prev_model  = crew_sort.sourceModel()
            # if prev_model: prev_model.deleteLater()
            crew_sort.setSourceModel(crew_model)
            # crew_model.selectionChanged.connect(self.updateImage)
            
            crew_view.setWordWrap(True)
            crew_view.horizontalHeader().setStretchLastSection(True)
            crew_view.resizeColumnsToContents()
            crew_view.resizeRowsToContents()
            crew_view.setSortingEnabled(True)
            crew_view.resizeRowsToContents()
            crew_view.clicked.connect(self.updateCrewImage)
            crew_view.sortByColumn(0, QtCore.Qt.AscendingOrder)
            crew_view.setWordWrap(True)

        except Exception as e:
            raise Exception("Something went wrong with the crew initialization... BORK!\n%s" % traceback.format_exc())
            sys.exit(3)

    def selectedObject(self, view, index):
        data = view.model().data
        obj = data(index, role=QtCore.Qt.UserRole)
        return obj

    def get_sources(self, kind, id):
        retval = []
        # print("Looking for ID %s" % id)
        for entry in CARD_DATA['Source']:
            # print(entry['contents'][kind])
            try:
                entry['contents'][kind][id]
                # print("I found one!")
                retval.append(entry['name'])
            except KeyError:
                continue

        return retval


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QMainWindow()

    prog = XWingCardViewer()

    prog.show()
    sys.exit(app.exec_())