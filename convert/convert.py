# Python3
#
# Instalar a lib xmltodict:
# pip3 install xmltodict
#
# python3 convert.py --input-file <arquivo de origem> --output-file <arquivo de saida> --dias <qtd de dias>
# 
# ex:
# python3 convert.py --input-file guide.xml --output-file novo.xml --dias 5
#

import xmltodict
import logging
import argparse
import os
import json
import re
from datetime import datetime
from datetime import timedelta
from datetime import timezone

def get_category(pg):
    if "category" in pg:
        cat = []
        if isinstance(pg['category'], list):
            for category in pg['category']:
                if isinstance(category, dict):
                    cat.append(category['#text'])
                else:
                    cat.append(category)

        else:
            cat.append(pg['category']['#text'])
        return f"\n - Categoria: {', '.join(cat)}"
    return ''


def get_actors(pg):
    if "credits" in pg and pg['credits'] and 'actor' in pg['credits']:
        if isinstance(pg['credits']['actor'], list):
            actors = []
            for act in pg['credits']['actor']:
                if isinstance(act, dict) and '#text' in act:
                    actors.append(act['#text'])
                else:
                    actors.append(act)
            return f"\n - Elenco: {', '.join(actors)}"

        else:
            return f"\n - Elenco: {pg['credits']['actor']}"
    return ''

def get_director(pg):
    if "credits" in pg and pg['credits'] and 'director' in pg['credits']:
        if isinstance(pg['credits']['director'], list):
            return f"\n - Direção: {', '.join(pg['credits']['director'])}"
        else:
            return f"\n - Direção: {pg['credits']['director']}"
    return ''


def get_year(pg):
    if "date" in pg:
        return f"\n - Produzido em: {pg['date']}"
    return ''


def get_rating(pg):
    if "rating" in pg:
        if isinstance(pg['rating'], list):
            ratings = []
            for r in pg['rating']:
                ratings.append(r['value'])
            return f"\n - Classificação: {', '.join(ratings)}"
        else:
            return f"\n - Classificação: {pg['rating']['value']}"
    return ''

def get_sub_title(pg):
    if "sub-title" in pg:
        if isinstance(pg['sub-title'], dict) and '#text' in pg['sub-title']:
            return f"\n - Subtítulo: {pg['sub-title']['#text']}"
    
        return f"\n - Subtítulo: {pg['sub-title']}"

    return ''


def get_episode(pg):
    if "episode-num" in pg:
        episode = ''
        if isinstance(pg['episode-num'], dict) and '#text' in pg['episode-num']:
            episode = pg['episode-num']['#text']
        else:
            for ep in pg['episode-num']:
                if ep['@system'] == "onscreen":
                    episode = ep['#text']

        return episode if match_episode(episode) else False
    return False


def match_episode(ep):
    regex = r"(.*?)(S\d{1,3}.*?E\d{1,3})"
    for match in re.finditer(regex, ep):
        return True

    return False


def process_programme(pg, channel_ids):

    episode_number = get_episode(pg)
    if episode_number:
        pg["title"] += f" {episode_number}"

    if not 'desc' in pg:
        pg["desc"] = {
            '#text' : '',
        }

    pg["desc"]['#text'] += get_sub_title(pg)

    pg["desc"]['#text'] += get_category(pg)

    pg["desc"]['#text'] += get_actors(pg)
    
    pg["desc"]['#text'] += get_director(pg)
    
    pg["desc"]['#text'] += get_year(pg)

    pg["desc"]['#text'] += get_rating(pg)

    programme = {
        "@start"  : pg["@start"],
        "@stop"   : pg["@stop"],
        "@channel": replace_channel_id(pg["@channel"], channel_ids),
        "title"   : pg["title"],
        "desc"    : pg["desc"],
    }
    return programme

def replace_channel_id(channel, ids):
    for c in ids:
        if c['old_id'] == channel:
            return c['new_id']
    return ''

def get_channels_ids(ch):
    new_ids = []
    for channel in ch:
        new_ids.append({
            'old_id' : channel['@id'],
            'new_id' : channel['display-name'][1],
            'name'   : channel['display-name'][0],
            })
    return new_ids


def process_channel(ch):
    channel = {
        '@id' : ch['new_id'],
        'display-name' : {
            '@lang' : 'en',
            '#text' : ch['name'],
        }
    }
    return channel



def open_xml_file(xml_file):
    logging.info(f"Lendo arquivo {xml_file}")
    with open(xml_file,'rb') as f:
        xmldata = xmltodict.parse(f)
    
    return xmldata



def save_xml_file(data, xml_file):
    logging.info(f"Salvando arquivo {xml_file}")
    with open(xml_file, 'w') as result_file:
        result_file.write(data)



def print_stats(xmldata, label):
    logging.info(f"Arquivo {label} contém {len(xmldata['tv']['channel'])} canais")
    logging.info(f"Arquivo {label} contém {len(xmldata['tv']['programme'])} programas")


def export_to_json(xmldata):
    logging.info(f"Salvando arquivo dump.json")
    with open('dump.json', 'w') as fp:
        json.dump(xmldata, fp,  indent=4)


def today_date():
    return datetime.now(timezone.utc).astimezone()

def check_date_range(prog, today, dias):
    program_start = datetime.strptime(prog["@start"], '%Y%m%d%H%M%S %z')
    datelimit = today + timedelta(days = dias )

    if program_start < today:
        return False

    if program_start < datelimit:
        return True

    return False


def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

    parser = argparse.ArgumentParser(description = 'Script para personalizacao de xml-tv')
    parser.add_argument('--input-file', action = 'store', dest = 'input_file',
                           default = 'Hello, world!', required = True,
                           help = 'Arquivo xml de origem')
    parser.add_argument('--output-file', action = 'store', dest = 'output_file', required = True,
                           help = 'Arquivo xml de saída')

    parser.add_argument('--dias', type=int, choices=range(1, 20), required = False, nargs="?", const=0, help = 'Limite de dias')

    arguments = parser.parse_args()

    dias = arguments.dias #1

    today = today_date()

    if not os.path.exists(arguments.input_file):
        logging.info(f"Arquivo de origem não encontrado")
        exit(1)


    xmldata = open_xml_file(arguments.input_file)

    print_stats(xmldata, arguments.input_file)

    # export_to_json(xmldata)

    original_channel   = xmldata['tv']['channel']
    original_programme = xmldata['tv']['programme']

    xmldata['tv'].pop('programme', None)

    logging.info(f"Modificando channel tags")

    new_channel_id = get_channels_ids(original_channel)

    new_channel = []
    for chan in new_channel_id:
        new_ch = process_channel(chan)
        new_channel.append(new_ch)

    logging.info(f"Modificando programme tags")

    new_programme = []
    for prog in original_programme:

        if dias and not check_date_range(prog, today, dias):
            continue

        try:
            new_pg = process_programme(prog, new_channel_id)
            new_programme.append(new_pg)
        except:
            print("erro ao processar:")
            print( json.dumps(prog, sort_keys=True, indent=4) )

    new_xmldata = {
        'tv' : {
            'channel'   : new_channel,
            'programme' : new_programme,
        }
    }

    print_stats(new_xmldata, arguments.output_file)

    logging.info(f"Formatando XML")
    xml_data_final = xmltodict.unparse(new_xmldata, pretty=True,newl="\n",indent="  ")

    save_xml_file(xml_data_final, arguments.output_file)


if __name__ == "__main__":
    main()
