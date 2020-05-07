# -*- coding: utf-8 -*-

import argparse
import socket
import sys
import logging
import urllib
import urllib2
import json
import time
import re
import unicodedata
import uuid

reload(sys)
sys.setdefaultencoding('utf-8')

__version__             = "0.1.1"

CONFIG = {
    'updateurl': "https://raw.githubusercontent.com/josemoraes99/tvheadend_scripts/master/tvheadend_configure_epg.py",
    'urlPicons': "https://hk319yfwbl.execute-api.sa-east-1.amazonaws.com/prod",
    'tvheadendAddress': 'localhost',
    'tvheadendPort': '9981',
}

DEV_CONFIG = {
    'updateurl': CONFIG['updateurl'],
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


def update(dl_url, force_update=False):
    """
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

        seqA = map(num, re.findall('\d+|\w+', vA.replace('-SNAPSHOT', '')))
        seqB = map(num, re.findall('\d+|\w+', vB.replace('-SNAPSHOT', '')))

        # this is to ensure that 1.0 == 1.0.0 in cmp(..)
        lenA, lenB = len(seqA), len(seqB)
        for i in range(lenA, lenB): seqA += (0,)
        for i in range(lenB, lenA): seqB += (0,)

        rc = cmp(seqA, seqB)

        if rc == 0:
            if vA.endswith('-SNAPSHOT'): return -1
            if vB.endswith('-SNAPSHOT'): return 1
        return rc

    # dl the first 256 bytes and parse it for version number
    try:
        http_stream = urllib.urlopen(dl_url)
        # update_file = http_stream.read(256)
        update_file = http_stream.read(300)
        http_stream.close()

    except IOError, (errno, strerror):
        logging.info( "Unable to retrieve version data" )
        logging.info( "Error %s: %s" % (errno, strerror) )
        return

    match_regex = re.search(r'__version__ *= *"(\S+)"', update_file)
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
        dl_file = open(dl_path, 'w')
        http_stream = urllib.urlopen(dl_url)
        total_size = None
        bytes_so_far = 0
        chunk_size = 8192
        try:
            total_size = int(http_stream.info().getheader('Content-Length').strip())
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
    except IOError, (errno, strerror):
        logging.info( "Download failed" )
        logging.info( "Error %s: %s" % (errno, strerror) )
        return

    try:
        os.rename(app_path, backup_path)
    except OSError, (errno, strerror):
        logging.info( "Unable to rename %s to %s: (%d) %s" % (app_path, backup_path, errno, strerror) )
        return

    try:
        os.rename(dl_path, app_path)
    except OSError, (errno, strerror):
        logging.info( "Unable to rename %s to %s: (%d) %s" % (dl_path, app_path, errno, strerror) )
        return

    try:
        import shutil
        shutil.copymode(backup_path, app_path)
    except:
        os.chmod(app_path, 0755)

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

            print("%-*s %-*s %s" % (3, l['number'], 25, l['name'], msg)).encode('utf-8')
    logging.info("Concluido")


def main():
    """Main function."""

    global CONFIG, DEV_CONFIG

    parser = argparse.ArgumentParser(description='Configuração de epg no Tvheadend.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--no-update', action='store_true', help = 'não verifica por atualização')
    group.add_argument('--force-update', action='store_true', help = 'força atualização')


    group_debug = parser.add_mutually_exclusive_group()
    group_debug.add_argument('--dev', action='store_true', help='modo de testes')

    args = parser.parse_args()

    # workaround tvheadend localhost
    CONFIG['tvheadendAddress'] = get_ip()

    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    logging.info("version %s", __version__)

    ckUpdates = True
    if args.no_update or args.dev:
        ckUpdates = False

    if args.dev:
        print(args)
        CONFIG = DEV_CONFIG

    if args.force_update:
        update( CONFIG['updateurl'], True)
        logging.info( "Pronto." )
        sys.exit()

    if ckUpdates:
        updateReturn = update( CONFIG['updateurl'])
        if updateReturn:
            logging.info( "Reiniciando script" )
            python = sys.executable
            os.execl(python, python, *sys.argv)

    has_tvh = check_for_tvh(CONFIG)

    if has_tvh:
        configure_epg_grabber(CONFIG)
        lista_canais = processa_lista_canais(CONFIG)
        processa_alteracoes(CONFIG, lista_canais)

if __name__ == '__main__':
    main()
