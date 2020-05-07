# -*- coding: utf-8 -*-

import argparse
import socket
import sys
import logging
import urllib2
import json
import time
import re
import unicodedata
import uuid

reload(sys)
sys.setdefaultencoding('utf-8')

__version__             = "0.1.0"

CONFIG = {
    'urlPicons': "https://hk319yfwbl.execute-api.sa-east-1.amazonaws.com/prod",
    'tvheadendAddress': 'localhost',
    'tvheadendPort': '9981',
}

DEV_CONFIG = {
    'urlPicons': CONFIG['urlPicons'],
    'tvheadendAddress': 'e2.lan',
    'tvheadendPort': '9981',
}

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_ip():
    """
    Verifica ip da interface de rede
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip_addr = s.getsockname()[0]
    except socket.error:
        ip_addr = '127.0.0.1'
    finally:
        s.close()
    return ip_addr


def check_for_tvh(conf):
    """
    Verifica se tvh ok
    """

    logging.info("Verificando TVHeadend")

    resp = False

    logging.info("TVHeadend running")
    try:
        req = urllib2.Request("http://" + conf['tvheadendAddress'] + ":" + conf['tvheadendPort'] + '/api/serverinfo')
        urllib2.urlopen(req)
    except urllib2.HTTPError as e_error:
        logging.info("TVHeadend com autenticação, utilize --help")
        logging.info('Error code: %s', e_error.code)
    except urllib2.URLError as e_error:
        logging.info("TVHeadend nao encontrado")
        logging.info('Reason: %s', e_error.reason)
    else:
        resp = True

    return resp


def get_tvh_channel_list(conf):
    """
    obtendo lista de canais
    """
    logging.info("Obtendo lista de canais do TVHeadend")
    final_list = []
    req = urllib2.Request("http://" + conf['tvheadendAddress'] + ":" + conf['tvheadendPort'] + '/api/channel/grid?limit=2000&all=1')
    tvhreq = urllib2.urlopen(req)
    data = json.load(tvhreq)
    for l in data['entries']:
        final_list.append({"number":l['number'], "uuid":l['uuid'], "name":l['name'], "epggrab":l['epggrab'], "enabled":l['enabled']})
        # print ( "%s %s %s %s" % (l['number'], l['uuid'], l['name'], l['epggrab']) )

    final_list = sorted(final_list, key=lambda i: i['number'])

    return final_list


def get_external_list(conf, lista):
    """
    obtendo lista de picons
    """
    logging.info("Obtendo lista externa")

    uuid_one = uuid.getnode()
    picons_list = list(dict.fromkeys(lista))
    data = {'src': 'e2', 'node': uuid_one, 'listChannel': picons_list}
    data = json.dumps(data)
    # print (data)

    req = urllib2.Request(conf['urlPicons'], data, {'Content-Type': 'application/json'})
    fil = urllib2.urlopen(req)
    list_url = json.load(fil)
    fil.close()

    return list_url


def alterar_epg_item(conf, idCanal, idEpg):
    """
    envia alteracao de epg no canal para o tvh
    """
    req = urllib2.Request("http://" + conf['tvheadendAddress'] + ":" + conf['tvheadendPort'] + '/api/idnode/save?node={"uuid":"' + idCanal + '","epggrab":["' + idEpg + '"]}')
    urllib2.urlopen(req)
    # tvhreq = urllib.urlopen( "http://" + conf['tvheadendAddress'] + ":" + conf['tvheadendPort'] + '/api/idnode/save?node={"uuid":"' + idCanal + '","epggrab":["' + idEpg + '"]}' )


def configure_epg_grabber(conf):
    """
    Habilita EPG Brasil Net
    """
    logging.info("Obtendo lista de epg grabbers")
    req = urllib2.Request("http://" + conf['tvheadendAddress'] + ":" + conf['tvheadendPort'] + '/api/epggrab/module/list')
    tvhreq = urllib2.urlopen(req)
    # tvhreq = urllib.urlopen( "http://" + conf['tvheadendAddress'] + ":" + conf['tvheadendPort'] + '/api/epggrab/module/list' )
    data = json.load(tvhreq)

    uuid_str = ''
    name_str = ''

    for l in data['entries']:
        if "EPG Brasil Net" in l['title']:
            # print l
            uuid_str = l['uuid']
            name_str = l['title']
            break

    if uuid_str != "":
        logging.info("Habilitando %s", name_str)
        req = urllib2.Request("http://" + conf['tvheadendAddress'] + ":" + conf['tvheadendPort'] + '/api/idnode/save?node={"uuid":"' + uuid_str + '","enabled":"true","scrape_extra":"true","scrape_onto_desc":"true","use_category_not_genre":"true"}')
        urllib2.urlopen(req)
        # tvhreq = urllib.urlopen( "http://" + conf['tvheadendAddress'] + ":" + conf['tvheadendPort'] + '/api/idnode/save?node={"uuid":"' + uuid_str + '","enabled":"true","scrape_extra":"true","scrape_onto_desc":"true","use_category_not_genre":"true"}' )

    logging.info("Executando 'Re-run internal epg Grabbers")
    req = urllib2.Request("http://" + conf['tvheadendAddress'] + ":" + conf['tvheadendPort'] + '/api/epggrab/internal/rerun?rerun=1')
    urllib2.urlopen(req)
    # tvhreq = urllib.urlopen( "http://" + conf['tvheadendAddress'] + ":" + conf['tvheadendPort'] + '/api/epggrab/internal/rerun?rerun=1' )
    # wait
    time.sleep(5)


def processa_lista_canais(conf):
    """
    Obtem lista de canais
    """
    list_epg = []
    req = urllib2.Request("http://%s:%s/api/epggrab/channel/list" % (conf['tvheadendAddress'],conf['tvheadendPort']))
    tvhreq = urllib2.urlopen(req)
    data_epg = json.load(tvhreq)
    for l in data_epg['entries']:
        cn_str = l['text'].split(':')[0].strip()
        cn_str = re.sub(re.compile('\W'), '', ''.join(c.lower() for c in unicodedata.normalize('NFKD', cn_str.replace("+", "mais")).encode('ascii', 'ignore') if not c.isspace()))
        # print ( "%s %s - %s" % (l['uuid'], cnStr, l['text']) )
        list_epg.append({"uuid":l['uuid'], "name":cn_str, "text":l['text']})

    list_channels = get_tvh_channel_list(conf)

    #lista envio
    lista_envio = []
    for i in list_epg:
        if i['name'] not in lista_envio:
            lista_envio.append(i['name'])

    for l in list_channels:
        if not l['epggrab']:
            cn_str = re.sub(re.compile('\W'), '', ''.join(c.lower() for c in unicodedata.normalize('NFKD', l['name'].replace("+", "mais")).encode('ascii', 'ignore') if not c.isspace()))
            if cn_str not in lista_envio:
                lista_envio.append(cn_str)

    list_ext = get_external_list(conf, lista_envio)
    #lista envio

    final = {'lista_canais': list_channels, 'lista_epg': list_epg, 'lista_externa': list_ext}
    return final


def processa_alteracoes(conf, lista):
    """
    Processa lista de canais sem epg
    """
    for l in lista['lista_canais']:
        if l['enabled']:
            msg = bcolors.FAIL + "não encontrado" + bcolors.ENDC

            if l['epggrab'] and l['epggrab'][0] != "":
                # print (l['epggrab'][0])
                epg_text = ''
                for e in lista['lista_epg']:
                    if e['uuid'] == l['epggrab'][0]:
                        epg_text = e['text']
                msg = bcolors.OKBLUE + "configurado anteriormente - " + epg_text + bcolors.ENDC
            else:
                canalclean = re.sub(re.compile('\W'), '', ''.join(c.upper() for c in unicodedata.normalize('NFKD', l['name'].replace("+", "plus").replace(" HD", "")).encode('ascii', 'ignore') if not c.isspace()))
                found = False
                # cn = ''
                for e in lista['lista_epg']:
                    # AXN: AXN (XMLTV: EPG Brasil Net)
                    tmp_name_01 = e['text'].split(':')[0]
                    tmp_name_01 = re.sub(re.compile('\W'), '', ''.join(c.upper() for c in unicodedata.normalize('NFKD', tmp_name_01.replace("+", "plus")).encode('ascii', 'ignore') if not c.isspace()))
                    if canalclean == tmp_name_01:
                        msg = bcolors.OKGREEN + "found 1 - " + e['text'] + bcolors.ENDC
                        found = True
                        alterar_epg_item(conf, l['uuid'], e['uuid'])
                if not found:
                    # print(l['name'])
                    key = ""
                    cn_str = re.sub(re.compile('\W'), '', ''.join(c.lower() for c in unicodedata.normalize('NFKD', l['name'].replace("+", "mais")).encode('ascii', 'ignore') if not c.isspace()))
                    for i in lista['lista_externa']:
                        if cn_str == i[0]:
                            if "nettv" not in i[1] and "anos2000" not in i[1]:
                                key = i[1]

                    tmp_l = []
                    for i in lista['lista_externa']:
                        if key == i[1]:
                            tmp_l.append(i[0])
                    epg_item = ''
                    uuid_item = ''
                    if tmp_l:
                        for i in lista['lista_epg']:
                            if i['name'] in tmp_l:
                                epg_item = i['text']
                                uuid_item = i['uuid']
                        if epg_item != "":
                            msg = bcolors.OKGREEN + "found 2 - " + epg_item + bcolors.ENDC
                            alterar_epg_item(conf, l['uuid'], uuid_item)

            print("%-*s %-*s %s" % (3, l['number'], 25, l['name'], msg))
    logging.info("Concluido")


def main():
    """Main function."""

    global CONFIG, DEV_CONFIG

    parser = argparse.ArgumentParser(description='Download de picons para o e2.')

    group_debug = parser.add_mutually_exclusive_group()
    group_debug.add_argument('--dev', action='store_true', help='modo de testes')

    args = parser.parse_args()

    # workaround tvheadend localhost
    CONFIG['tvheadendAddress'] = get_ip()

    if args.dev:
        print(args)
        CONFIG = DEV_CONFIG

    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    logging.info("version %s", __version__)

    has_tvh = check_for_tvh(CONFIG)

    if has_tvh:
        configure_epg_grabber(CONFIG)
        lista_canais = processa_lista_canais(CONFIG)
        processa_alteracoes(CONFIG, lista_canais)

if __name__ == '__main__':
    main()
