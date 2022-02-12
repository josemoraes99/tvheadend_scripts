# Python3
#
# Instalar a lib xmltodict:
# pip3 install xmltodict
#
# python3 convert.py --input-file <arquivo de origem> --output-file <arquivo de saida>
# 
# ex:
# python3 convert.py --input-file guide.xml --output-file novo.xml
#

import xmltodict
import logging
import argparse
import os
import json

def process_programme(pg):
    if "category" in pg:
        cat = []
        if isinstance(pg['category'], list):
            # print( pg['category'] )
            for category in pg['category']:
                cat.append(category['#text'])
        else:
            cat.append(pg['category']['#text'])
        pg["desc"]['#text'] += f"\n - Categoria: {', '.join(cat)}"

    if "credits" in pg and 'actor' in pg['credits']:
        if isinstance(pg['credits']['actor'], list):
            pg["desc"]['#text'] += f"\n - Elenco: {', '.join(pg['credits']['actor'])}"
        else:
            pg["desc"]['#text'] += f"\n - Elenco: {pg['credits']['actor']}"

    if "credits" in pg and 'director' in pg['credits']:
        if isinstance(pg['credits']['director'], list):
            pg["desc"]['#text'] += f"\n - Direção: {', '.join(pg['credits']['director'])}"
        else:
            pg["desc"]['#text'] += f"\n - Direção: {pg['credits']['director']}"

    if "date" in pg:
        pg["desc"]['#text'] += f"\n - Produzido em: {pg['date']}"

    if "rating" in pg:
        pg["desc"]['#text'] += f"\n - Classificação: {pg['rating']['value']}"


    programme = {
        "@start"  : pg["@start"],
        "@stop"   : pg["@stop"],
        "@channel": pg["@channel"],
        "title"   : pg["title"],
        "desc"    : pg["desc"],
    }
    return programme



def open_xml_file(xml_file):
    logging.info(f"Lendo arquivo {xml_file}")
    with open(xml_file,'rb') as f:
        xmldata = xmltodict.parse(f)
    
    return xmldata



def save_xml_file(data, xml_file):
    logging.info(f"Salvando arquivo {xml_file}")
    with open(xml_file, 'w') as result_file:
        result_file.write(data)



def print_stats(xmldata):
    logging.info(f"Arquivo de input contém {len(xmldata['tv']['channel'])} canais")
    logging.info(f"Arquivo de input contém {len(xmldata['tv']['programme'])} programas")


def export_to_json(xmldata):
    logging.info(f"Salvando arquivo dump.json")
    with open('dump.json', 'w') as fp:
        json.dump(xmldata, fp,  indent=4)



def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

    parser = argparse.ArgumentParser(description = 'Script para personalizacao de xml-tv')
    parser.add_argument('--input-file', action = 'store', dest = 'input_file',
                           default = 'Hello, world!', required = True,
                           help = 'Arquivo xml de origem')
    parser.add_argument('--output-file', action = 'store', dest = 'output_file', required = True,
                           help = 'Arquivo xml de saída')

    arguments = parser.parse_args()

    if not os.path.exists(arguments.input_file):
        logging.info(f"Arquivo de origem não encontrado")
        exit(1)


    xmldata = open_xml_file(arguments.input_file)

    print_stats(xmldata)

    # export_to_json(xmldata)

    original_programme = xmldata['tv']['programme']

    xmldata['tv'].pop('programme', None)

    logging.info(f"Modificando programme tags")

    new_programme = []
    for prog in original_programme:
        new_pg = process_programme(prog)
        new_programme.append(new_pg)

    xmldata['tv']['programme'] = new_programme

    logging.info(f"Formatando XML")
    xml_data_final = xmltodict.unparse(xmldata, pretty=True,newl="\n",indent="  ")

    save_xml_file(xml_data_final, arguments.output_file)



if __name__ == "__main__":
    main()
