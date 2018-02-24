

import os
import sys
import copy
import json
import platform

from textwrap import wrap
# import urllib2



def main(args = None):

    args = args if args is not None else sys.argv

    # os.system('cls')
    print(platform.python_version())

    try:
        search_term = str(args[1]).lower()
    except IndexError:
        search_term = None

    proj_root_dir = "T:\\X-Wing Project\\info\\data"

    card_data = load_card_data(proj_root_dir)[0]

    found = search_for_value(card_data, search_term)
    # print(json.dumps(found, sort_keys=True, indent=4, separators=(',', ': ')))
    found_data = []
    for item in found:
        card = [entry for entry in card_data[item['dict']] if entry['id'] == item['id']][0]
        card['card_type'] = item['dict']
        found_data.append(card)
        # print("%s\n\t%s" % (item['dict'], card['name']))

    # input()

    sorted_data = sorted(found_data, key=lambda k: k['name'])

    for result in sorted_data:
        # print(result)
        # print(json.dumps(result, sort_keys=True))
        card_type = result['card_type']
        card_id = result['id']
        sources = get_sources(card_data, card_type, card_id)

        
        if card_type == 'Pilot':
            ship_chars = get_ship_chars(result, card_data['Ship'])
            print("{card_type}\n{name} - {ship}\n\tCost: {cost}\n\tPS: {PS}\n\tATK: {ATK}  AGL: {AGL}\n\tHUL: {HUL}  SHD: {SHD}\n\t{text}\n\tComes in:\n\t\t{sources}\n".format(card_type=result['card_type'],
                                                                                                                                                                 name=result['name'] if not result.get('unique', False) else "%s *" % result['name'],
                                                                                                                                                                 cost=result['points'],
                                                                                                                                                                 ship=result['ship'],
                                                                                                                                                                 PS=result['skill'],
                                                                                                                                                                 ATK=ship_chars.get('attack', 'N/A'),
                                                                                                                                                                 AGL=ship_chars.get('agility', 'N/A'),
                                                                                                                                                                 HUL=ship_chars.get('hull', 'N/A'),
                                                                                                                                                                 SHD=ship_chars.get('shields', 'N/A'),
                                                                                                                                                                 text="%s\n" % "\n\t".join(wrap(result.get('text', ''), 80)) if result.get('text', '') != '' else '',
                                                                                                                                                                 sources="\n\t\t".join([pack['name'] for pack in sources])))
            # pass
        elif card_type == 'Upgrade':
            # print(result['slot'])
            slot = result['slot']
            # if slot == 'Crew':
            print("{card_type}\n{name}\n\tCost: {cost}\n\t{text}\n\n\tComes in:\n\t\t{sources}\n".format(name=result['name'] if not result.get('unique', False) else "%s * " % result['name'],
                                                            card_type="Upgrade - %s" % result['slot'],
                                                            cost=result['points'],
                                                            text="\n\t".join(wrap(result.get('text', ''), 80)),
                                                            sources="\n\t\t".join([pack['name'] for pack in sources])))
            # print(sources)
            # else:
            #     print("\n\n\n------%s------\n\n\n" % slot)
        else:
            # print("\n\n\n------%s------\n\n\n" % result['card_type'])
            pass

         # % (result['name'] if not result.get('unique', False) else "%s * " % result['name'], result['ship'], result.get('text', "")))
    # print(len(card_data['pilot_data']))

    # print(pilot_data[0]['name'])

def load_card_data(root_dir):
    try:
        # Load all data from .js files
        card_data = {}

        card_data['Pilot'] = load_data(root_dir, "pilots")
        card_data['Ship'] = load_data(root_dir, "ships")
        card_data['Source'] = load_data(root_dir, "sources")
        card_data['Upgrade'] = load_data(root_dir, "upgrades")

        reference_data = load_data(root_dir, "reference-cards")
        conditions = load_data(root_dir, "conditions")

        damage_data = {}
        damage_data['regular'] = load_data(root_dir, "damage-deck-core")
        damage_data['tfa'] = load_data(root_dir, "damage-deck-core-tfa")
        damage_data['rebel_transport'] = load_data(root_dir, "damage-deck-rebel-transport")

    except Exception as e:
        raise Exception("Couldn't load card information:\n%s" % e)

    return [card_data, reference_data, conditions, damage_data]


    
def load_data(root_dir, data):
    data_file = os.path.join(root_dir, "%s.js" % data)
    
    try:
        assert os.path.exists(data_file)
    except:
        raise AssertionError("Source for %s doesn't exist!" % data)

    with open(data_file, encoding='utf-8') as data_json:
        data_dict = json.load(data_json)

    return data_dict



def search_for_value(d_dict, card_type, search_terms, slot=None):

    search_sets = []
    return_list = []

    if search_terms == '':
        print("\tNo search terms")
        for d in d_dict:
            c = check_for_value(d, None, slot) 
            if c['retval']:
                # print(c['id'])
                return_list.append({'dict': card_type, 'id': c['id']})
        return return_list

    print("\tSearch terms: %s" % search_terms)

    search_term_list = search_terms.split()

    for search_term in search_term_list:

        search_term = search_term.strip()
        search_set = set()

        for d in d_dict:
            c = check_for_value(d, search_term, slot) 
            if c['retval']:
                # return_list.append({'dict': card_type, 'id': c['id']})
                search_set.add('%s%s' % ('p' if card_type == 'Pilot' else 'u', c['id']))

        print('Results for %s:\n\t%s' % (search_term, '\n\t'.join(sorted(list(search_set)))))
        search_sets.append(search_set)

    print(search_sets)
    if len(search_sets) == 1:
        for i in search_sets[0]:
            return_list.append({'dict': card_type, 'id': int(i[1:])})
    else:
        for i in search_sets[0].intersection(*search_sets[1:]):
            return_list.append({'dict': card_type, 'id': int(i[1:])})

    # for q in return_list:
        # print(q)
    print("Return list: %s" % str(return_list))
    return return_list



def check_for_value(ref_dict, search_term, slot=None):
    '''
    Check a dictionary for a value. Return true if that value
    (generally a string) occurs in the name or text of the card.
        
    '''
    d = copy.deepcopy(ref_dict)
    retval = False
    # print("Checking for %s" % search_term)

    # Check to see if this is a pilot card. If so, add ship characteristics to it before searching.
    if d.get('skill', None):
        ship_chars = get_ship_chars(d, CARD_DATA['Ship'])
        # Get rid of factions for each ship, so we don't search those. Let that be only pilots.
        if ship_chars.get('faction', None):
            ship_chars.pop('faction')
        d['ship_chars'] = ship_chars

    if not search_term:
        if slot and d['slot'] == slot:
            # print(d)
            return {'retval': True, 'id': d['id']}
        elif slot:
            return {'retval': False}
        else:
            # print(d)
            return {'retval': True, 'id': d['id']}

    try:
        assert type(d) == dict
    except:
        raise TypeError("Somehow I don't have a dictionary.")

    # print(json.dumps(d, sort_keys=True, indent=4, separators=(',', ': ')))

    for val in d.values():
        if slot:
            if search_term in str(val).lower() and d['slot'] == slot:
                retval = True
                break
        else:
            if search_term in str(val).lower():
                retval = True
                break
    for key in d:
        if slot:
            if search_term in key.lower() and d['slot'] == slot and d[key] == True:
                retval = True
                break
        else:
            if search_term in key.lower() and d[key] == True:
                retval = True
                break

    if retval:
        return {'retval': retval, 'id': d['id']}

    return {'retval': retval}



def get_sources(card_data, card_dict_name, card_id):
    conv_dict = {'Pilot': 'pilots', 'Upgrade': 'upgrades'}
    try:
        card_type = conv_dict[card_dict_name]
    except KeyError:
        return []

    ret_list = []
    for sku_dict in card_data['Source']:
        # print(json.dumps(sku_dict, sort_keys=True, indent=4, separators=(',', ': ')))
        if sku_dict['contents'][card_type].get(str(card_id), 0) != 0:
            ret_list.append(sku_dict)

    # print(ret_list)

    return ret_list

def get_ship_chars(pilot_dict, ship_list):
    ship_chars = pilot_dict.get('ship_override', None)

    ship_name = pilot_dict['ship']
    ship_dict = [ship for ship in ship_list if ship['name'] == ship_name][0]
    if ship_chars:
        ship_dict.update(ship_chars)
    return ship_dict

def list_upgrade_types():
    print('*********************************')
    upgrade_types = set()
    for up in CARD_DATA['Upgrade']:
        upgrade_types.add(up['slot'])
    for up_type in sorted(upgrade_types):
        print(up_type)
    print('*********************************')

INFO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "info"))
CARD_DATA, REFERENCE_DATA, CONDITIONS, DAMAGE_DATA = load_card_data(os.path.abspath(os.path.join(os.path.dirname(__file__), "info", "data")))

if __name__ == "__main__":
    # Build package path and append to system path
    xwing_main_path = os.path.normpath(os.path.join(os.path.realpath(__file__), "..", ".."))
    if xwing_main_path not in sys.path:
        sys.path.append(xwing_main_path)

    list_upgrade_types()
    
    # Import GUI and run
    from xwing.gui import main as g_main
    g_main()
