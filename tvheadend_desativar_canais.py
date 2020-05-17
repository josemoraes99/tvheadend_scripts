#!/bin/python3

# -*- coding: utf-8 -*-

__version__ = "0.1.3"

import argparse
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError, HTTPError
import json
import sys
import re
import unicodedata
import uuid
import os
import stat
import logging
import socket


CONFIG = {
    'devmode': False,
    'updateurl': "https://raw.githubusercontent.com/josemoraes99/tvheadend_scripts/master/tvheadend_desativar_canais.py",
    'urlPicons': "https://hk319yfwbl.execute-api.sa-east-1.amazonaws.com/prod",
    'tvheadendAddress': 'localhost',
    'tvheadendPort': '9981',
}

DEV_CONFIG = {
    'devmode': True,
    'updateurl': CONFIG['updateurl'],
    'urlPicons': CONFIG['urlPicons'],
    'tvheadendAddress': 'e2.lan',
    'tvheadendPort': '9981',
}


def update(dl_url, force_update=False):
    """
https://gist.github.com/gesquive/8363131
Attempts to download the update url in order to find if an update is needed.
If an update is needed, the current script is backed up and the update is
saved in its place.
"""
    def compare_versions(vA, vB):
        """
Compares two version number strings
@param vA: first version string to compare
@param vB: second version string to compare
@author <a href="http_stream://sebthom.de/136-comparing-version-numbers-in-jython-pytho/">Sebastian Thomschke</a>
@return negative if vA < vB, zero if vA == vB, positive if vA > vB.
"""
        if vA == vB: return 0

        def num(s):
            if s.isdigit(): return int(s)
            return s

        seqA = list(map(num, re.findall('\d+|\w+', vA.replace('-SNAPSHOT', ''))))
        seqB = list(map(num, re.findall('\d+|\w+', vB.replace('-SNAPSHOT', ''))))

        # this is to ensure that 1.0 == 1.0.0 in cmp(..)
        lenA, lenB = len(seqA), len(seqB)
        for i in range(lenA, lenB): seqA += (0,)
        for i in range(lenB, lenA): seqB += (0,)

        rc = cmp(seqA, seqB)

        if rc == 0:
            if vA.endswith('-SNAPSHOT'): return -1
            if vB.endswith('-SNAPSHOT'): return 1
        return rc

    def cmp(a, b):
        return (a > b) - (a < b)

    # dl the first 256 bytes and parse it for version number
    try:
        http_stream = urlopen(dl_url)
        # update_file = http_stream.read(256)
        update_file = http_stream.read(300)
        http_stream.close()

    # except IOError, (errno, strerror):
    except IOError as errno:
        logging.info( "Unable to retrieve version data" )
        # logging.info( "Error %s: %s" % (errno, strerror) )
        logging.info( "Error %s" % (errno) )
        return

    match_regex = re.search(r'__version__ *= *"(\S+)"', update_file.decode('utf-8'))
    if not match_regex:
        logging.info( "No version info could be found" )
        return
    update_version = match_regex.group(1)

    if not update_version:
        logging.info( "Unable to parse version data" )
        return

    if force_update:
        logging.info( "Forcing update, downloading version %s..." % update_version )

    else:
        cmp_result = compare_versions(__version__, update_version)
        if cmp_result < 0:
            logging.info( "Newer version %s available, downloading..." % update_version )
        elif cmp_result > 0:
            logging.info( "Local version %s newer then available %s, not updating." % (__version__, update_version) )
            return
        else:
            logging.info( "You already have the latest version." )
            return

    # dl, backup, and save the updated script
    app_path = os.path.realpath(sys.argv[0])
    # if __asModule__ == True:
    #     app_path = __file__

    if not os.access(app_path, os.W_OK):
        logging.info( "Cannot update -- unable to write to %s" % app_path )

    dl_path = app_path + ".new"
    backup_path = app_path + ".old"
    try:
        dl_file = open(dl_path, 'wb')
        http_stream = urlopen(dl_url)
        total_size = None
        bytes_so_far = 0
        chunk_size = 8192
        try:
            # total_size = int(http_stream.info().getheader('Content-Length').strip())
            total_size = int(http_stream.headers['content-length'].strip())
        except:
            # The header is improper or missing Content-Length, just download
            dl_file.write(http_stream.read())

        while total_size:
            chunk = http_stream.read(chunk_size)
            dl_file.write(chunk)
            bytes_so_far += len(chunk)

            if not chunk:
                break

            percent = float(bytes_so_far) / total_size
            percent = round(percent*100, 2)
            sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" %
                             (bytes_so_far, total_size, percent))

            if bytes_so_far >= total_size:
                sys.stdout.write('\n')

        http_stream.close()
        dl_file.close()
    # except IOError, (errno, strerror):
    except IOError as errno:
        logging.info( "Download failed" )
        # logging.info( "Error %s: %s" % (errno, strerror) )
        logging.info( "Error %s" % (errno) )
        return

    try:
        os.rename(app_path, backup_path)
    # except OSError, (errno, strerror):
    except OSError as errno:
        # logging.info( "Unable to rename %s to %s: (%d) %s" % (app_path, backup_path, errno, strerror) )
        logging.info( "Unable to rename %s to %s: (%d) " % (app_path, backup_path, errno) )
        return

    try:
        os.rename(dl_path, app_path)
    # except OSError, (errno, strerror):
    except OSError as errno:
        # logging.info( "Unable to rename %s to %s: (%d) %s" % (dl_path, app_path, errno, strerror) )
        logging.info( "Unable to rename %s to %s: (%d)" % (dl_path, app_path, errno) )
        return

    try:
        import shutil
        shutil.copymode(backup_path, app_path)
    except:
        # os.chmod(app_path, 0755)
        os.chmod(app_path, stat.S_IRWXU)


    logging.info( "New version installed as %s" % app_path )
    logging.info( "(previous version backed up to %s)" % (backup_path) )
    return True


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


def print_line(simb, text):
    """
    print line na tela
    """
    char = "*"
    if simb == "alert":
        char = "!"
    print("[%s] %s" % (char, text))


def disable_channel(conf, uuid, name):
    """
    desativar canal no tvh
    """
    print_line("info", "desativando " + name)
    urlopen('http://%s:%s/api/idnode/save?node={"uuid":"%s","enabled":"false"}' % (conf['tvheadendAddress'], conf['tvheadendPort'], uuid))


def enable_channel(conf, uuid, name):
    """
    desativar canal no tvh
    """
    print_line("info", "ativando " + name)
    urlopen('http://%s:%s/api/idnode/save?node={"uuid":"%s","enabled":"true"}' % (conf['tvheadendAddress'], conf['tvheadendPort'], uuid))


def get_tvh_channel_list(conf):
    """
    obtendo lista de canais
    """
    print_line("info", "Obtendo lista de canais do TVHeadend")

    final_list = []

    tvhreq = urlopen("http://%s:%s/api/channel/grid?limit=2000&all=1" % (conf['tvheadendAddress'], conf['tvheadendPort']))
    data = json.load(tvhreq)
    for l in data['entries']:
        final_list.append({"number":l['number'], "uuid":l['uuid'], "name":l['name'], "epggrab":l['epggrab'], "enabled":l['enabled']})

    final_list = sorted(final_list, key=lambda i: i['number'])

    return final_list


def desativar_canais_duplicados(conf):
    """
    desativar canais sd quando houver em hd
    """
    list_channel = get_tvh_channel_list(conf)

    new_channel = []
    for i in list_channel:
        iName = i["name"].lower().replace(' hd', '')
        iName = " ".join(iName.split())

        add_c = True

        for j in new_channel:

            jName = j["name"].lower().replace(' hd', '')
            jName = " ".join(jName.split())

            if jName == iName and " hd" in i["name"].lower() and " hd" not in j["name"].lower():
                if j["enabled"]:
                    disable_channel(conf, j["uuid"], j["name"])
                break

            if jName == iName and " hd" not in i["name"].lower() and " hd" in j["name"].lower():
                add_c = False
                break

            if i["name"].lower() == j["name"].lower() and i["number"] > j["number"]:
                if j["enabled"]:
                    disable_channel(conf, j["uuid"], j["name"])
                break

        if add_c:
            new_channel.append(i)


def obter_lista_externa(conf, list_send):
    uuid_one = uuid.getnode()
    picons_list = list(dict.fromkeys(list_send))
    params = {'src': 'kodi', 'node': uuid_one, 'listChannel': picons_list}
    params = json.dumps(params).encode('utf8')

    req = Request(conf['urlPicons'], data=params, headers={'content-type': 'application/json'})
    fil = urlopen(req)
    list_url = json.load(fil)
    fil.close()

    return list_url


def desativar_canais_adultos(conf):
    """
    desativar canais adultos
    """
    list_channel = get_tvh_channel_list(conf)
    lista_envio = []
    for l in list_channel:
        cn_str = re.sub(re.compile('\W'), '', ''.join(c.lower() for c in unicodedata.normalize('NFKD', l['name'].replace("+", "mais")).encode('ascii', 'ignore').decode('utf8') if not c.isspace()))
        if cn_str not in lista_envio and l['enabled']:
            lista_envio.append(cn_str)

    list_ext = obter_lista_externa(conf, lista_envio)

    lista_canais_adultos = list_ext['listaCanaisAdultos']

    for l in list_channel:
        cn_str = re.sub(re.compile('\W'), '', ''.join(c.lower() for c in unicodedata.normalize('NFKD', l['name'].replace("+", "mais")).encode('ascii', 'ignore').decode('utf8') if not c.isspace()))
        if cn_str in lista_canais_adultos and l['enabled']:
            disable_channel(conf, l["uuid"], l["name"])


def desativar_canais_internos(conf):
    """
    desativar canais internos
    """
    list_channel = get_tvh_channel_list(conf)
    lista_envio = []
    for l in list_channel:
        cn_str = re.sub(re.compile('\W'), '', ''.join(c.lower() for c in unicodedata.normalize('NFKD', l['name'].replace("+", "mais")).encode('ascii', 'ignore').decode('utf8') if not c.isspace()))
        if cn_str not in lista_envio and l['enabled']:
            lista_envio.append(cn_str)

    list_ext = obter_lista_externa(conf, lista_envio)

    lista_canais_internos = list_ext['listaCanaisInternos']

    for l in list_channel:
        cn_str = re.sub(re.compile('\W'), '', ''.join(c.lower() for c in unicodedata.normalize('NFKD', l['name'].replace("+", "mais")).encode('ascii', 'ignore').decode('utf8') if not c.isspace()))
        if cn_str in lista_canais_internos and l['enabled']:
            disable_channel(conf, l["uuid"], l["name"])

# {'listaCanaisInternos': ['canalcomunitario', 'canaldecliente', 'canaldoclientehd', 'cartoongames', 'clarorecomenda', 'clarousointerno', 'now', 'teletema'], 'listaCanaisAdultos': ['playboytvhd', 'sextreme', 'sexyhot', 'venus'], 'listaPicons': [['aehd', 'https://raw.githubusercontent.com/josemoraes99/kodi_picons/master/img/ae.png'], ['amchd', 'https://raw.githubusercontent.com/josemoraes99/kodi_picons/master/img/amc.png']

def ativar_todos_canais(conf):
    """
    reativa todos os canais
    """
    list_channel = get_tvh_channel_list(conf)

    for item in list_channel:
        if not item['enabled']:
            enable_channel(conf, item["uuid"], item["name"])


def check_for_tvh(conf):
    """
    Verifica se tvh ok
    """
    print_line("info", "Verificando TVHeadend")

    resp = False

    try:
        urlopen("http://%s:%s/api/serverinfo" % (conf['tvheadendAddress'], conf['tvheadendPort']))
    except HTTPError as e_error:
        print_line("alert", "TVHeadend com autenticação, funciona somente sem autenticação")
        print_line("alert", 'Error code: %s' % e_error.code)
    except URLError as e_error:
        print_line("alert", "TVHeadend nao encontrado")
        print_line("alert", 'Reason: %s' % e_error.reason)
    else:
        print_line("info", "TVHeadend running")
        resp = True

    return resp


def main():
    """Main function."""

    global CONFIG, DEV_CONFIG

    parser = argparse.ArgumentParser(description='Desativar canais no Tvheadend.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--no-update', action='store_true', help='não verifica por atualização')
    group.add_argument('--force-update', action='store_true', help='força atualização')


    group_debug = parser.add_mutually_exclusive_group()
    group_debug.add_argument('--dev', action='store_true', help='modo de testes')

    group_desativar = parser.add_mutually_exclusive_group(required=True)
    group_desativar.add_argument('--desativar-canais-sd', action='store_true', help='desativar canais sd quando hover em hd')
    group_desativar.add_argument('--desativar-canais-adultos', action='store_true', help='desativar canais adultos')
    group_desativar.add_argument('--desativar-canais-internos', action='store_true', help='desativar canais internos da operadora')
    group_desativar.add_argument('--ativar-todos-canais', action='store_true', help='Ativa todos os canais')

    args = parser.parse_args()

    # workaround tvheadend localhost
    CONFIG['tvheadendAddress'] = get_ip()

    if args.dev:
        print(args)
        CONFIG = DEV_CONFIG

    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    logging.info("version %s", __version__)

    ck_updates = True
    if args.no_update or args.dev:
        ck_updates = False

    if args.force_update:
        update(CONFIG['updateurl'], True)
        print_line("alert", "Pronto.")
        sys.exit()

    if ck_updates:
        update_return = update(CONFIG['updateurl'])
        if update_return:
            print_line("alert", "Reiniciando script")
            python = sys.executable
            os.execl(python, python, *sys.argv)

    has_tvh = check_for_tvh(CONFIG)

    if args.desativar_canais_sd and has_tvh:
        desativar_canais_duplicados(CONFIG)

    if args.desativar_canais_adultos and has_tvh:
        desativar_canais_adultos(CONFIG)

    if args.desativar_canais_internos and has_tvh:
        desativar_canais_internos(CONFIG)

    if args.ativar_todos_canais and has_tvh:
        ativar_todos_canais(CONFIG)

if __name__ == '__main__':
    main()
