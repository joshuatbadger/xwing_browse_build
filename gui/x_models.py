# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *
# from PyQt5.QtCore import *

import os
import json
import operator

from PyQt5 import QtGui, QtWidgets, QtCore
from xwing import INFO_DIR


def get_attack_or_energy(item):
    if operator.attrgetter('attack')(item):
        return {'type': 'attack', 'value': '%s' % operator.attrgetter('attack')(item)}
    return {'type': 'energy', 'value': '%s' % operator.attrgetter('energy')(item)}

def get_card_name(item):
    name = operator.attrgetter('name')(item)
    unique = operator.attrgetter('unique')(item)
    # return a circle (the unicode character) next to the name if it's unique
    return '%s%s' % (name, u' \u25CF' if unique else '')

def get_ship_stat(item, stat):
    return {'type': stat, 'value': operator.attrgetter(stat)(item)}


class PilotModel(QtCore.QAbstractTableModel):
    methlist = {
                # 0: operator.attrgetter('name'),
                0: get_card_name,
                1: operator.attrgetter('skill'),
                2: operator.attrgetter('ship'),
                3: operator.attrgetter('faction'),
                4: operator.attrgetter('cost'),
                5: get_attack_or_energy,
                6: operator.attrgetter('agility'),
                7: operator.attrgetter('hull'),
                8: operator.attrgetter('shields'),
                9: operator.attrgetter('size')
                #9: operator.attrgetter('full_data')
               }

    headers =  { 
                0: 'Name', 
                1: 'PS', 
                2: 'Ship',
                3: 'Faction',
                4: 'Cost',
                5: 'Attack/\nEnergy',
                6: 'Agility',
                7: 'Hull',
                8: 'Shields',
                9: 'Ship Size'
                # 5: 'test'
               }

    stat_ref = {
                6: 'agility',
                7: 'hull',
                8: 'shields'
               }

    color_ref = {
                 'attack':  QtCore.Qt.red,
                 'energy':  QtCore.Qt.magenta,
                 'agility': QtCore.Qt.green,
                 'hull':    QtCore.Qt.yellow,
                 'shields': QtCore.Qt.cyan
                }

    def __init__(self, pilotview, parent=None): 
        super(PilotModel, self).__init__()
        self.pilot_data = pilotview

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.pilot_data) 

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.methlist)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        item = self.pilot_data[index.row()]

        # Normal display
        if role == QtCore.Qt.DisplayRole:# and index.column() != 3: # and index.column() != len(self.methlist):
            retval = self.methlist[index.column()](item)
            # Occasionally we'll return a dictionary instead of just a value
            if type(retval) == dict:
                return retval['value']
            return retval

        # Anything with an icon
        elif role == QtCore.Qt.DecorationRole:
            if index.column() == 3:
                icon_name = self.methlist[index.column()](item).lower().replace(" ", "-")
                icon_path = os.path.join(INFO_DIR, 'images', 'factions', '%s-small.png' % icon_name)
                pixmap = QtGui.QPixmap(icon_path)#.scaled(QtCore.QSize(36,36))
                return pixmap
            else:
                return

        # When we want to return special information
        elif role == QtCore.Qt.UserRole:
            return operator.attrgetter('full_data')(item)

        # For tool-tip
        elif role == QtCore.Qt.ToolTipRole:
            return operator.attrgetter('text')(item)

        # Changing color
        elif role == QtCore.Qt.ForegroundRole:
            # Only change colors for certain columns/stats; call distinct functions 
            if index.column() in self.stat_ref:
                stat = get_ship_stat(item, self.stat_ref[index.column()])
            else:
                stat = self.methlist[index.column()](item)
            # color if we know what the stat is
            if type(stat) == dict:
                return QtGui.QBrush(QtGui.QColor(self.color_ref[stat['type']]))
            else:
                return

        # Make colored text bold somehow?
        elif role == QtCore.Qt.FontRole:
            # TODO: Figure out how to boldify these columns
            if index.column() in self.stat_ref:
                stat = get_ship_stat(item, self.stat_ref[index.column()])
            else:
                stat = self.methlist[index.column()](item)
            if type(stat) == dict:
                return QtGui.QFont('Sans-serif', 12, QtGui.QFont.Bold)
            else:
                return 

        # Align certain columns to center, and others left
        elif role == QtCore.Qt.TextAlignmentRole:
            if index.column() in self.stat_ref:
                retval = get_ship_stat(item, self.stat_ref[index.column()])
            else:
                retval = self.methlist[index.column()](item)
            if type(retval) == dict and retval['type'] in self.color_ref:
                return QtCore.Qt.AlignCenter
            return (QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        # else:
        #     return QtCore.QVariant()

    def headerData(self, section, orientation, role): 
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole and section != len(self.methlist): 
            return self.headers[section] 
        else: 
            return None 

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

class UpgradeAstromechModel(QtCore.QAbstractTableModel):
    methlist = {
                0: get_card_name,
                1: operator.attrgetter('type'),
                2: operator.attrgetter('cost'),
                # 3: operator.attrgetter('text'),
               }

    headers =  { 
                0: 'Name', 
                1: 'Type', 
                2: 'Cost',
                # 3: 'Text',
               }


    def __init__(self, astroview, parent=None): 
        super(UpgradeAstromechModel, self).__init__()
        self.astromech = astroview

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.astromech) 

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.methlist) 

    def data(self, index, role=QtCore.Qt.DisplayRole):
        item = self.astromech[index.row()]

        # Normal display
        if role == QtCore.Qt.DisplayRole: # and index.column() != len(self.methlist):
            retval = self.methlist[index.column()](item)
            # Occasionally we'll return a dictionary instead of just a value
            # if type(retval) == dict:
            #     return retval['value']
            # if index.column() == 4:
            #     return QtWidgets.QLabel().setText(retval)
            return retval

        # Anything with an icon
        # elif role == QtCore.Qt.DecorationRole:
        #     if index.column() == 3:
        #         faction = self.methlist[index.column()](item)
        #         if faction:
        #             icon_name = self.methlist[index.column()](item).lower().replace(" ", "-")
        #             icon_path = os.path.join(INFO_DIR, 'images', 'factions', '%s-small.png' % icon_name)
        #             pixmap = QtGui.QPixmap(icon_path)#.scaled(QtCore.QSize(36,36))
        #             return pixmap
        #         return
        #     else:
        #         return

        # When we want to return special information
        elif role == QtCore.Qt.UserRole:
            return operator.attrgetter('full_data')(item)

        # For tool-tip
        elif role == QtCore.Qt.ToolTipRole:
            return operator.attrgetter('text')(item)

        # Changing color
        # elif role == QtCore.Qt.ForegroundRole:
        #     # Only change colors for certain columns/stats; call distinct functions 
        #     if index.column() in self.stat_ref:
        #         stat = get_ship_stat(item, self.stat_ref[index.column()])
        #     else:
        #         stat = self.methlist[index.column()](item)
        #     # color if we know what the stat is
        #     if type(stat) == dict:
        #         return QtGui.QBrush(QtGui.QColor(self.color_ref[stat['type']]))
        #     else:
        #         return

        # Make colored text bold somehow?
        # elif role == QtCore.Qt.FontRole:
        #     # TODO: Figure out how to boldify these columns
        #     if index.column() in self.stat_ref:
        #         stat = get_ship_stat(item, self.stat_ref[index.column()])
        #     else:
        #         stat = self.methlist[index.column()](item)
        #     if type(stat) == dict:
        #         return QtGui.QFont('Sans-serif', 12, QtGui.QFont.Bold)
        #     else:
        #         return 

        # Align certain columns to center, and others left
        # elif role == QtCore.Qt.TextAlignmentRole:
        #     if index.column() in self.stat_ref:
        #         retval = get_ship_stat(item, self.stat_ref[index.column()])
        #     else:
        #         retval = self.methlist[index.column()](item)
        #     if type(retval) == dict and retval['type'] in self.color_ref:
        #         return QtCore.Qt.AlignCenter
        #     return (QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        # else:
        #     return QtCore.QVariant()

    def headerData(self, section, orientation, role): 
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole: 
            return self.headers[section] 
        else: 
            return None 

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

class UpgradeBombModel(QtCore.QAbstractTableModel):
    methlist = {
                0: operator.attrgetter('name'),
                1: operator.attrgetter('type'),
                2: operator.attrgetter('cost'),
                3: operator.attrgetter('text'),
                4: operator.attrgetter('effect'),
               }

    headers =  { 
                0: 'Name', 
                1: 'Type', 
                2: 'Cost',
                3: 'Text',
                4: 'Effect',
               }


    def __init__(self, bombview, parent=None): 
        super(UpgradeBombModel, self).__init__()
        self.bomb = bombview

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.bomb) 

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.methlist) 

    def data(self, index, role=QtCore.Qt.DisplayRole):
        item = self.bomb[index.row()]

        # Normal display
        if role == QtCore.Qt.DisplayRole: # and index.column() != len(self.methlist):
            retval = self.methlist[index.column()](item)
            # Occasionally we'll return a dictionary instead of just a value
            # if type(retval) == dict:
            #     return retval['value']
            # if index.column() == 4:
            #     return QtWidgets.QLabel().setText(retval)
            return retval


        # When we want to return special information
        elif role == QtCore.Qt.UserRole:
            return operator.attrgetter('full_data')(item)

        # For tool-tip
        elif role == QtCore.Qt.ToolTipRole:
            return operator.attrgetter('text')(item)

        # Changing color
        # elif role == QtCore.Qt.ForegroundRole:
        #     # Only change colors for certain columns/stats; call distinct functions 
        #     if index.column() in self.stat_ref:
        #         stat = get_ship_stat(item, self.stat_ref[index.column()])
        #     else:
        #         stat = self.methlist[index.column()](item)
        #     # color if we know what the stat is
        #     if type(stat) == dict:
        #         return QtGui.QBrush(QtGui.QColor(self.color_ref[stat['type']]))
        #     else:
        #         return

        # Make colored text bold somehow?
        # elif role == QtCore.Qt.FontRole:
        #     # TODO: Figure out how to boldify these columns
        #     if index.column() in self.stat_ref:
        #         stat = get_ship_stat(item, self.stat_ref[index.column()])
        #     else:
        #         stat = self.methlist[index.column()](item)
        #     if type(stat) == dict:
        #         return QtGui.QFont('Sans-serif', 12, QtGui.QFont.Bold)
        #     else:
        #         return 

        # Align certain columns to center, and others left
        # elif role == QtCore.Qt.TextAlignmentRole:
        #     if index.column() in self.stat_ref:
        #         retval = get_ship_stat(item, self.stat_ref[index.column()])
        #     else:
        #         retval = self.methlist[index.column()](item)
        #     if type(retval) == dict and retval['type'] in self.color_ref:
        #         return QtCore.Qt.AlignCenter
        #     return (QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        # else:
        #     return QtCore.QVariant()

    def headerData(self, section, orientation, role): 
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole: 
            return self.headers[section] 
        else: 
            return None 

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

class UpgradeCannonModel(QtCore.QAbstractTableModel):
    methlist = {
                0: operator.attrgetter('name'),
                1: operator.attrgetter('type'),
                2: operator.attrgetter('cost'),
                3: operator.attrgetter('attack'),
                4: operator.attrgetter('range'),
                # 5: operator.attrgetter('text')
               }

    headers =  { 
                0: 'Name', 
                1: 'Type', 
                2: 'Cost',
                3: 'Attack',
                4: 'Range',
                # 5: 'Text'
               }


    def __init__(self, cannonview, parent=None): 
        super(UpgradeCannonModel, self).__init__()
        self.cannon = cannonview

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.cannon) 

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.methlist) 

    def data(self, index, role=QtCore.Qt.DisplayRole):
        item = self.cannon[index.row()]

        # Normal display
        if role == QtCore.Qt.DisplayRole: # and index.column() != len(self.methlist):
            retval = self.methlist[index.column()](item)
            # Occasionally we'll return a dictionary instead of just a value
            # if type(retval) == dict:
            #     return retval['value']
            # if index.column() == 4:
            #     return QtWidgets.QLabel().setText(retval)
            return retval


        # When we want to return special information
        elif role == QtCore.Qt.UserRole:
            return operator.attrgetter('full_data')(item)

        # For tool-tip
        elif role == QtCore.Qt.ToolTipRole:
            return operator.attrgetter('text')(item)

        # Changing color
        elif role == QtCore.Qt.ForegroundRole:
            # Only change colors for certain columns/stats; call distinct functions 
            if index.column() == 3:
                # Attack value
                return QtGui.QBrush(QtGui.QColor(QtCore.Qt.red))
            else:
                return

        # Make colored text bold somehow?
        elif role == QtCore.Qt.FontRole:
            if index.column() in [3,4]:
                # Attack, range values
                return QtGui.QFont('Sans-serif', 12, QtGui.QFont.Bold)
            else:
                return 

        # Align certain columns to center, and others left
        elif role == QtCore.Qt.TextAlignmentRole:
            if index.column() in [3,4]:
                return QtCore.Qt.AlignCenter
            return (QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)

        # else:
        #     return QtCore.QVariant()

    def headerData(self, section, orientation, role): 
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole: 
            return self.headers[section] 
        else: 
            return None 

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


# class UpgradeCargoModel(QtCore.QAbstractTableModel):

class UpgradeCrewModel(QtCore.QAbstractTableModel):
    methlist = {
                0: get_card_name,
                1: operator.attrgetter('type'),
                2: operator.attrgetter('cost'),
                3: operator.attrgetter('faction'),
                # 4: operator.attrgetter('range'),
                # 5: operator.attrgetter('text')
               }

    headers =  { 
                0: 'Name', 
                1: 'Type', 
                2: 'Cost',
                3: 'Faction',
                # 4: 'Range',
                # 5: 'Text'
               }


    def __init__(self, cannonview, parent=None): 
        super(UpgradeCrewModel, self).__init__()
        self.cannon = cannonview

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.cannon) 

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.methlist) 

    def data(self, index, role=QtCore.Qt.DisplayRole):
        item = self.cannon[index.row()]

        # Normal display
        if role == QtCore.Qt.DisplayRole: # and index.column() != len(self.methlist):
            retval = self.methlist[index.column()](item)
            # Occasionally we'll return a dictionary instead of just a value
            # if type(retval) == dict:
            #     return retval['value']
            # if index.column() == 4:
            #     return QtWidgets.QLabel().setText(retval)
            return retval

        # Anything with an icon
        elif role == QtCore.Qt.DecorationRole:
            if index.column() == 3:
                # Faction
                faction = self.methlist[index.column()](item)
                if not faction:
                    return
                icon_name = faction.lower().replace(" ", "-")
                icon_path = os.path.join(INFO_DIR, 'images', 'factions', '%s-small.png' % icon_name)
                pixmap = QtGui.QPixmap(icon_path)#.scaled(QtCore.QSize(36,36))
                return pixmap
            else:
                return


        # When we want to return special information
        elif role == QtCore.Qt.UserRole:
            return operator.attrgetter('full_data')(item)

        # For tool-tip
        elif role == QtCore.Qt.ToolTipRole:
            return operator.attrgetter('text')(item)

        # Changing color
        # elif role == QtCore.Qt.ForegroundRole:
        #     # Only change colors for certain columns/stats; call distinct functions 
        #     if index.column() == 3:
        #         # Attack value
        #         return QtGui.QBrush(QtGui.QColor(QtCore.Qt.red))
        #     else:
        #         return

        # Make colored text bold somehow?
        # elif role == QtCore.Qt.FontRole:
        #     if index.column() in [3,4]:
        #         # Attack, range values
        #         return QtGui.QFont('Sans-serif', 12, QtGui.QFont.Bold)
        #     else:
        #         return 

        # Align certain columns to center, and others left
        elif role == QtCore.Qt.TextAlignmentRole:
            # if index.column() in [3,4]:
            #     return QtCore.Qt.AlignCenter
            return (QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)

        # else:
        #     return QtCore.QVariant()

    def headerData(self, section, orientation, role): 
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole: 
            return self.headers[section] 
        else: 
            return None 

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


# class UpgradeEliteModel(QtCore.QAbstractTableModel):
# class UpgradeHardpointModel(QtCore.QAbstractTableModel):
# class UpgradeIllicitModel(QtCore.QAbstractTableModel):
# class UpgradeMissileModel(QtCore.QAbstractTableModel):
# class UpgradeModificationModel(QtCore.QAbstractTableModel):
# class UpgradeSalvaged AstromechModel(QtCore.QAbstractTableModel):
# class UpgradeSystemModel(QtCore.QAbstractTableModel):
# class UpgradeTeamModel(QtCore.QAbstractTableModel):
# class UpgradeTechModel(QtCore.QAbstractTableModel):
# class UpgradeTitleModel(QtCore.QAbstractTableModel):
# class UpgradeTorpedoModel(QtCore.QAbstractTableModel):
# class UpgradeTurretModel(QtCore.QAbstractTableModel):