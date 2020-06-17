#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import copy
import xml.etree.ElementTree as ET
import gzip
import sys
try:
    from urllib.error import URLError, HTTPError
    from urllib.request import Request
    from urllib.request import urlopen
except:
    if sys.version_info[0] < 3:
        print("usar python3")
        sys.exit()

URL_EPG = "http://github.com/hbaldner/RepoEpgE2/raw/master/guide.xml.gz"

CANAIS = {
    "AE": ['A&E'],
    "AMC": ['AMC HD'],
    "ANIMALPLANET": ['Animal Planet', 'Animal Planet HD'],
    "APARECIDA": ['TV Aparecida'],
    "ARTE1": ['Arte 1 HD'],
    "AXN": ['AXN HD'],
    "BANDEIRANTES": ['Band HD'],
    "BANDNEWS": ['Band News'],
    "BANDSPORTS": ['Band Sports HD'],
    "BBCWORLD": ['BBC'],
    "BIS": ['BIS HD'],
    "BOOMERANG": ['Boomerang'],
    "CANALBRASIL": ['Canal Brasil HD'],
    "CANALDOBOI": ['Canal do Boi HD'],
    "CANALRURAL": ['Canal Rural'],
    "CANONOVA": ['TV Canção Nova'],
    "CARTOONNETWORK": ['Cartoon Network'],
    "CGTN": ['CGTN'],
    "CINEMAX": ['Cinemax'],
    "CNNBRASIL": ['CNN Brasil HD'],
    "COMBATE": ['Combate HD'],
    "COMEDYCENTRAL": ['Comedy Central'],
    "CURTA": ['Curta!', 'Curta! HD'],
    "DISCOVERYCHANNEL": ['Discovery Channel', 'Discovery Channel HD'],
    "DISCOVERYKIDS": ['Discovery Kids'],
    "DISNEY": ['Disney Channel', 'Disney Channel HD'],
    "E": ['E! HD'],
    "ESPN": ['ESPN HD'],
    "ESPN+": ['ESPN2 HD'],
    "ESPNBRASIL": ['ESPN Brasil HD'],
    "ESPNEXTRAHD": ['ESPN Extra HD'],
    "EUROCHANNEL": ['Eurochannel HD'],
    "FASHIONTV": ['Fashion TV HD'],
    "FILMARTS": ['Film&Arts', 'Film&Arts HD'],
    "FISHTV": ['Fish TV HD'],
    "FOODNETWORKHD": ['Food Network HD'],
    "FOXLIFE": ['FOX Life'],
    "FOXSPORTS": ['FOX Sports HD'],
    "FOXSPORTS2": ['FOX Sports 2 HD'],
    "FUTURA": ['Futura HD'],
    "FX": ['FX HD'],
    "GLOBONEWS": ['GloboNews', 'GloboNews HD'],
    "GLOBOSATHD": ['Mais Globosat HD'],
    "GLOBOSP": ['Globo HD'],
    "GLOOB": ['Gloob'],
    "GNT": ['GNT HD'],
    "H2": ['History 2 HD'],
    "HBO": ['HBO HD'],
    "HBO2": ['HBO2 HD'],
    "HBOFAMILY": ['HBO Family HD'],
    "HBOPLUS": ['HBO+', 'HBO+ HD'],
    "HBOSIGNATURE": ['HBO Signature HD'],
    "HGTV": ['HGTV HD'],
    "LIFETIME": ['Lifetime'],
    "LIKEHD": ['Like HD'],
    "LOVENATUREHD": ['Love Nature HD'],
    "MAX": ['HBO MUNDI HD'],
    "MAXPRIMEHD": ['HBO XTREME HD'],
    "MAXUP": ['HBO POP HD'],
    "MEGAPIX": ['Megapix'],
    "MTV": ['MTV HD'],
    "MULTISHOW": ['Multishow HD'],
    "MUSICBOXBRAZIL": ['Music Box Brazil HD'],
    "NATGEOWILDHD": ['NatGeo Wild', 'NatGeo Wild HD'],
    "NETTV": ['Canal do Cliente HD'],
    "NICKELODEON": ['Nickelodeon'],
    "NICKJR": ['Nick Jr.'],
    "OFFHD": ['OFF HD'],
    "PAIETERNO": ['Pai Eterno HD'],
    "PLAYBOYTV": ['Playboy TV HD'],
    "PREMIERE2": ['Premiere 2 HD'],
    "PREMIERE3": ['Premiere 3 HD'],
    "PREMIERE4": ['Premiere 4 HD'],
    "PREMIERE5": ['Premiere 5 HD'],
    "PREMIERE6": ['Premiere 6 HD'],
    "PREMIERE7": ['Premiere 7 HD'],
    "PREMIERECLUBES": ['Premiere Clubes HD'],
    "PRIMEBOXBRAZIL": ['Prime Box Brazil'],
    "REDERECORD": ['Record', 'Record HD'],
    "REDETV": ['RedeTV!', 'RedeTV! HD'],
    "REDEVIDA": ['Rede Vida HD'],
    "SBT": ['SBT HD'],
    "SMITHSONIANHD": ['Smithsonian HD'],
    "SPACE": ['Space'],
    "SPORTV": ['SporTV HD'],
    "SPORTV2": ['SporTV2', 'SporTV2 HD'],
    "SPORTV3": ['SporTV3', 'SporTV3 HD'],
    "STUDIOUNIVERSAL": ['Studio Universal'],
    "SYFY": ['SYFY HD'],
    "TBS": ['TBS HD'],
    "TELECINEACTION": ['Telecine Action HD'],
    "TELECINECULT": ['Telecine Cult HD'],
    "TELECINEFUN": ['Telecine Fun HD'],
    "TELECINEPIPOCA": ['Telecine Pipoca HD'],
    "TELECINEPREMIUM": ['Telecine Premium HD'],
    "TELECINETOUCH": ['Telecine Touch HD'],
    "TERRAVIVA": ['Terra Viva'],
    "THEHISTORYCHANNEL": ['History HD'],
    "TNT": ['TNT HD'],
    "TRAVELANDLIVINGCHANNEL": ['TLC HD'],
    "TRAVELBOXBRAZIL": ['Travel Box Brazil HD'],
    "TVBRASIL": ['TV Brasil HD'],
    "TVCULTURA": ['Cultura', 'Cultura HD'],
    "TVRTIMBUM": ['TV Rá Tim Bum'],
    "UNIVERSAL": ['Universal TV'],
    "VIVA": ['Viva', 'Viva HD'],
    "WARNER": ['Warner Channel'],
    "WOOHOO": ['Woohoo HD'],
    "ZOOMOO": ['Zoomoo'],
}


def download_epg():
    # global URL_EPG
    # print(URL_EPG)
    req = Request(URL_EPG)
    epgreq = urlopen(req)
    epg_xml = gzip.open(epgreq)
    return epg_xml


def process_xml(epg_xml):
    document = ET.parse(epg_xml)
    root = document.getroot()
    # print(root.tag)
    # print(root.attrib)
    root = organizar_canais(root)
    # mostrar todos
    # filtro = "*"
    # for child in root.iter(filtro):
    #     print(child.tag, child.text)

    # for child in root.findall("channel"):
    #     # print(child.tag, child.attrib['id'])
    #     for title in child.findall("display-name"):
    #         print(child.tag, child.attrib['id'], title.text)
    #         if child.attrib['id'] == 'ANIMALPLANET':
    #             # title.text = "Animal Planet"

    #             # new_node = copy.deepcopy(child)
    #             # new_node.find("display-name").text = "Animal Planet"
    #             # root.append(new_node)

    #             new_node = copy.deepcopy(title)
    #             new_node.text = "Animal Planet HD"
    #             child.append(new_node)

    # sub_tree.append(copy.deepcopy(original_tree))
    # ET.dump(root)
    # indent(root)
    # import lxml
    return document


# def indent(elem, level=0):
#     i = "\n" + level*"  "
#     j = "\n" + (level-1)*"  "
#     if len(elem):
#         if not elem.text or not elem.text.strip():
#             elem.text = i + "  "
#         if not elem.tail or not elem.tail.strip():
#             elem.tail = i
#         for subelem in elem:
#             indent(subelem, level+1)
#         if not elem.tail or not elem.tail.strip():
#             elem.tail = j
#     else:
#         if level and (not elem.tail or not elem.tail.strip()):
#             elem.tail = j
#     return elem


def organizar_canais(xml_root):
    for child in xml_root.findall("channel"):
        # print(child.tag, child.attrib['id'])
        if child.attrib['id'] in CANAIS:
            add_channel_list = []
            new_node = ""
            for ch in CANAIS[child.attrib['id']]:
                # print("-->", ch)
                add_ch = True
                for title in child.findall("display-name"):
                    new_node = copy.deepcopy(title)  # procurar melhor solucao
                    if title == ch:
                        add_ch = False
                if add_ch:
                    add_channel_list.append(ch)
            for item_ch in add_channel_list:
                new_tmp = copy.deepcopy(new_node)
                new_tmp.text = item_ch
                child.append(new_tmp)

            # print(child.attrib['id'])
        # for title in child.findall("display-name"):
        #     print(child.tag, child.attrib['id'], title.text)

        #     if child.attrib['id'] == 'ANIMALPLANET':
        #         # title.text = "Animal Planet"

        #         # new_node = copy.deepcopy(child)
        #         # new_node.find("display-name").text = "Animal Planet"
        #         # root.append(new_node)

        #         new_node = copy.deepcopy(title)
        #         new_node.text = "Animal Planet HD"
        #         child.append(new_node)
    return xml_root


def salvar_arquivo(document):
    # salvar
    document.write('file-after-edits.xml', encoding='utf8')


def enviar_para_socket(document):
    default_xml_socket = "/home/root/.hts/tvheadend/epggrab/xmltv.sock"
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(default_xml_socket)
    sockfile = sock.makefile('w')
    sys.stdout = sockfile

    ET.dump(document)


def main():
    # print("start")
    epg_xml = download_epg()
    doc_xml = process_xml(epg_xml)
    salvar_arquivo(doc_xml)
    # enviar_para_socket(doc_xml)


if __name__ == '__main__':
    main()
