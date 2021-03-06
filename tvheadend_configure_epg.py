#!/bin/python2
# -*- coding: utf-8 -*-

__version__ = "0.2.12"

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
import os
from subprocess import STDOUT, check_call
import commands

reload(sys)
sys.setdefaultencoding('utf-8')


CONFIG = {
    'devmode': False,
    'updateurl': "https://raw.githubusercontent.com/josemoraes99/tvheadend_scripts/master/tvheadend_configure_epg.py",
    'scriptsurl': "https://raw.githubusercontent.com/josemoraes99/tvheadend_scripts/master/",
    'urlPicons': "https://hk319yfwbl.execute-api.sa-east-1.amazonaws.com/prod",
    'tvheadendAddress': 'localhost',
    'tvheadendPort': '9981',
    'scriptspath': '/usr/bin/',
    'crontabpath': '/var/spool/cron/crontabs/root',
    'scripts_grabber': ['tv_grab_br', 'category-filter.pl'],
}

DEV_CONFIG = {
    'devmode': True,
    'updateurl': CONFIG['updateurl'],
    'scriptsurl': CONFIG['scriptsurl'],
    'urlPicons': CONFIG['urlPicons'],
    'tvheadendAddress': 'e2.lan',
    'tvheadendPort': '9981',
    'scriptspath': 'tmp/',
    'crontabpath': 'tmp/root',
    'scripts_grabber': CONFIG['scripts_grabber'],
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
        if vA == vB:
            return 0

        def num(s):
            if s.isdigit():
                return int(s)
            return s

        seqA = map(num, re.findall('\d+|\w+', vA.replace('-SNAPSHOT', '')))
        seqB = map(num, re.findall('\d+|\w+', vB.replace('-SNAPSHOT', '')))

        # this is to ensure that 1.0 == 1.0.0 in cmp(..)
        lenA, lenB = len(seqA), len(seqB)
        for i in range(lenA, lenB):
            seqA += (0,)
        for i in range(lenB, lenA):
            seqB += (0,)

        rc = cmp(seqA, seqB)

        if rc == 0:
            if vA.endswith('-SNAPSHOT'):
                return -1
            if vB.endswith('-SNAPSHOT'):
                return 1
        return rc

    # dl the first 256 bytes and parse it for version number
    try:
        http_stream = urllib.urlopen(dl_url)
        # update_file = http_stream.read(256)
        update_file = http_stream.read(300)
        http_stream.close()

    except IOError, (errno, strerror):
        logging.info("Unable to retrieve version data")
        logging.info("Error %s: %s" % (errno, strerror))
        return

    match_regex = re.search(r'__version__ *= *"(\S+)"', update_file)
    if not match_regex:
        logging.info("No version info could be found")
        return
    update_version = match_regex.group(1)

    if not update_version:
        logging.info("Unable to parse version data")
        return

    if force_update:
        logging.info("Forcing update, downloading version %s..." %
                     update_version)

    else:
        cmp_result = compare_versions(__version__, update_version)
        if cmp_result < 0:
            logging.info("Newer version %s available, downloading..." %
                         update_version)
        elif cmp_result > 0:
            logging.info("Local version %s newer then available %s, not updating." % (
                __version__, update_version))
            return
        else:
            logging.info("You already have the latest version.")
            return

    # dl, backup, and save the updated script
    app_path = os.path.realpath(sys.argv[0])
    # if __asModule__ == True:
    #     app_path = __file__

    if not os.access(app_path, os.W_OK):
        logging.info("Cannot update -- unable to write to %s" % app_path)

    dl_path = app_path + ".new"
    backup_path = app_path + ".old"
    try:
        dl_file = open(dl_path, 'w')
        http_stream = urllib.urlopen(dl_url)
        total_size = None
        bytes_so_far = 0
        chunk_size = 8192
        try:
            total_size = int(http_stream.info().getheader(
                'Content-Length').strip())
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
        logging.info("Download failed")
        logging.info("Error %s: %s" % (errno, strerror))
        return

    try:
        os.rename(app_path, backup_path)
    except OSError, (errno, strerror):
        logging.info("Unable to rename %s to %s: (%d) %s" %
                     (app_path, backup_path, errno, strerror))
        return

    try:
        os.rename(dl_path, app_path)
    except OSError, (errno, strerror):
        logging.info("Unable to rename %s to %s: (%d) %s" %
                     (dl_path, app_path, errno, strerror))
        return

    try:
        import shutil
        shutil.copymode(backup_path, app_path)
    except:
        os.chmod(app_path, 0755)

    logging.info("New version installed as %s" % app_path)
    logging.info("(previous version backed up to %s)" % (backup_path))
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
        req = urllib2.Request(
            "http://" + conf['tvheadendAddress'] + ":" + conf['tvheadendPort'] + '/api/serverinfo')
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
    req = urllib2.Request("http://" + conf['tvheadendAddress'] + ":" +
                          conf['tvheadendPort'] + '/api/channel/grid?limit=2000&all=1')
    tvhreq = urllib2.urlopen(req)
    data = json.load(tvhreq)
    for l in data['entries']:
        final_list.append({"number": l['number'], "uuid": l['uuid'],
                           "name": l['name'], "epggrab": l['epggrab'], "enabled": l['enabled']})
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

    req = urllib2.Request(conf['urlPicons'], data, {
                          'Content-Type': 'application/json'})
    fil = urllib2.urlopen(req)
    list_url = json.load(fil)
    fil.close()

    return list_url


def alterar_epg_item(conf, idCanal, idEpg):
    """
    envia alteracao de epg no canal para o tvh
    """
    req = urllib2.Request("http://" + conf['tvheadendAddress'] + ":" + conf['tvheadendPort'] +
                          '/api/idnode/save?node={"uuid":"' + idCanal + '","epggrab":["' + idEpg + '"]}')
    urllib2.urlopen(req)


def executar_grabber_manual(conf):
    """
    executa tv_grab_br
    """
    if verificar_scripts_grabber(conf) and verifica_xmltv_external(conf):
        logging.info("Executando tv_grab_br")
        if not conf['devmode']:
            cmd = conf['scriptspath'] + \
                'tv_grab_br | /usr/bin/socat - UNIX-CONNECT:/home/root/.hts/tvheadend/epggrab/xmltv.sock'
            # os.system(cmd)
            output = commands.getoutput(cmd)
        else:
            logging.info("Dev mode - skip executando tv_grab_br")


def verificar_socat_instalado(conf):
    resp = False
    socat_path = "/usr/bin/socat"
    if not os.path.isfile(socat_path):
        logging.info("Não encontrado %s, instalando" % socat_path)

        if not conf['devmode']:
            logging.info("Executando apt-get update")
            check_call(['apt-get', 'update'],
                       stdout=open(os.devnull, 'wb'), stderr=STDOUT)

            logging.info("Executando apt-get install socat")
            check_call(['apt-get', 'install', '-y', 'socat'],
                       stdout=open(os.devnull, 'wb'), stderr=STDOUT)
            if os.path.isfile(socat_path):
                resp = True

    return resp


def verificar_crontab():
    """
    verifica crontab
    """
    found_string_hour = False
    found_string_reboot = False

    str_search = "/usr/bin/tv_grab_br | /usr/bin/socat - UNIX-CONNECT:/home/root/.hts/tvheadend/epggrab/xmltv.sock"
    stream = os.popen('crontab -u root -l').read().strip()

    if stream == "":  # crontab vazio
        crontab_vazio = True
        adicionar_crontab_hour(False)
        adicionar_crontab_reboot()

    else:
        result_items = stream.split("\n")

        for item in result_items:
            if str_search in item and "@reboot" in item:
                found_string_reboot = True
            if str_search in item and "@reboot" not in item:
                found_string_hour = True

        if not found_string_hour:
            adicionar_crontab_hour(True)

        if not found_string_reboot:
            adicionar_crontab_reboot()


def adicionar_crontab_hour(first):
    """
    adciona tvgrab ao crontab a cada 12 horas
    input --> true se hover crontab e adiciona linefeed
    """
    logging.info("Adicionando crontab as 0 e 12 horas")
    line_spacer = ""
    cmd_str = "/usr/bin/tv_grab_br | /usr/bin/socat - UNIX-CONNECT:/home/root/.hts/tvheadend/epggrab/xmltv.sock"
    if first:
        line_spacer = "\n"
    cmd = "bash -c 'echo -e \"$(crontab -u root -l)" + line_spacer + \
        "0 0,12 * * * " + cmd_str + "\" | crontab -u root -'"
    output = commands.getoutput(cmd)


def adicionar_crontab_reboot():
    """
    adciona tvgrab ao crontab ao reboot
    """
    logging.info("Adicionando crontab ao reboot")
    cmd_str = "/usr/bin/tv_grab_br | /usr/bin/socat - UNIX-CONNECT:/home/root/.hts/tvheadend/epggrab/xmltv.sock"
    cmd = "bash -c 'echo -e \"$(crontab -u root -l)\n@reboot sleep 120; " + \
        cmd_str + "\" | crontab -u root -'"
    output = commands.getoutput(cmd)


def executa_internal_grabber(conf):
    """
    executa internal grabber
    """
    logging.info("Executando 'Re-run internal epg Grabbers'")
    req = urllib2.Request("http://" + conf['tvheadendAddress'] + ":" +
                          conf['tvheadendPort'] + '/api/epggrab/internal/rerun?rerun=1')
    urllib2.urlopen(req)
    # wait
    time.sleep(10)


def verificar_scripts_grabber(conf):
    files_dl = conf['scripts_grabber']
    found_files = True

    for file_donwload in files_dl:
        file_donwload_path = conf['scriptspath'] + file_donwload
        if not os.path.isfile(file_donwload_path):
            found_files = False
    return found_files


def obter_uuid_xmltv(conf):
    uuid_external_xml = False

    req = urllib2.Request("http://" + conf['tvheadendAddress'] +
                          ":" + conf['tvheadendPort'] + '/api/epggrab/module/list')
    tvhreq = urllib2.urlopen(req)
    data = json.load(tvhreq)

    for l in data['entries']:
        req1 = urllib2.Request("http://%s:%s/api/idnode/load?uuid=%s" %
                               (conf['tvheadendAddress'], conf['tvheadendPort'], l['uuid']))
        tvhreq1 = urllib2.urlopen(req1)
        data1 = json.load(tvhreq1)

        if "External: XMLTV" in data1['entries'][0]['text']:
            uuid_external_xml = data1['entries'][0]['uuid']
            break

    return uuid_external_xml


def obter_lista_de_grabbers(conf):
    logging.info("Obtendo lista de epg grabbers")
    req = urllib2.Request("http://" + conf['tvheadendAddress'] +
                          ":" + conf['tvheadendPort'] + '/api/epggrab/module/list')
    tvhreq = urllib2.urlopen(req)
    data = json.load(tvhreq)

    uuid_str = ''
    name_str = ''

    logging.info("Verificando grabbers ativados")

    grabbers_found = []

    for l in data['entries']:

        req1 = urllib2.Request("http://%s:%s/api/idnode/load?uuid=%s" %
                               (conf['tvheadendAddress'], conf['tvheadendPort'], l['uuid']))
        tvhreq1 = urllib2.urlopen(req1)
        data1 = json.load(tvhreq1)
        grabber_enabled = False
        scrape_extra = False
        scrape_onto_desc = False
        use_category_not_genre = False
        for t in data1['entries'][0]['params']:
            if t['id'] == "enabled" and t['value'] == True:
                grabber_enabled = True
            if t['id'] == "scrape_extra" and t['value'] == True:
                scrape_extra = True
            if t['id'] == "scrape_onto_desc" and t['value'] == True:
                scrape_onto_desc = True
            if t['id'] == "use_category_not_genre" and t['value'] == True:
                use_category_not_genre = True

        # if grabber_enabled and not ("PSIP: ATSC Grabber" in data1['entries'][0]['text'] or "EIT: EPG Grabber" in data1['entries'][0]['text']):
        if grabber_enabled:
            grabbers_found.append({'name': data1['entries'][0]['text'],
                                   'uuid': data1['entries'][0]['uuid'],
                                   'scrape_extra': scrape_extra,
                                   'scrape_onto_desc': scrape_onto_desc,
                                   'use_category_not_genre': use_category_not_genre,
                                   })
    return grabbers_found


def verifica_xmltv_external(conf):
    found_grabber = False
    grabbers_found = obter_lista_de_grabbers(conf)

    for grabber in grabbers_found:
        if "External: XMLTV" in grabber['name']:
            found_grabber = True

    # sys.exit()
    return found_grabber


def reconfigure_epg_grabber(conf):
    """
    Desativar Save EPG to disk after xmltv import
    """
    req = urllib2.Request("http://" + conf['tvheadendAddress'] +
                          ":" + conf['tvheadendPort'] + '/api/epggrab/config/load')
    tvhreq = urllib2.urlopen(req)
    data = json.load(tvhreq)

    for item in data['entries'][0]['params']:
        if item['id'] == 'epgdb_saveafterimport' and item['value'] == False:
            logging.info("Recconfigurando Save EPG to disk after xmltv import")
            req = urllib2.Request("http://" + conf['tvheadendAddress'] + ":" + conf['tvheadendPort'] +
                                  '/api/epggrab/config/save?node={"epgdb_saveafterimport":"true"}')
            urllib2.urlopen(req)


def download_scripts_grabber(conf):
    import hashlib
    files_dl = conf['scripts_grabber']
    scripts_updated = False

    for file_donwload in files_dl:
        file_donwload_path = conf['scriptspath'] + file_donwload
        overwrite_file = True

        md5_remoto = ""
        url = conf['scriptsurl'] + file_donwload
        f = urllib2.urlopen(url)
        data_download = f.read()
        md5_returned = hashlib.md5(data_download).hexdigest()
        md5_remoto = md5_returned

        if os.path.isfile(file_donwload_path):
            overwrite_file = False
            md5_local = ""
            with open(file_donwload_path, 'r') as file_to_check:
                # read contents of the file
                data = file_to_check.read()
                # pipe contents of the file through
                md5_returned = hashlib.md5(data).hexdigest()
                md5_local = md5_returned

            if md5_local and md5_remoto:
                if md5_local != md5_remoto:

                    overwrite = raw_input(
                        'Arquivo %s é diferente do repositório, sobrescrever? S = sim, N = não ' % (file_donwload_path))
                    if overwrite.lower() == 's':
                        overwrite_file = True

        if overwrite_file:

            logging.info("Download do arquivo %s e salvando em %s" %
                         (file_donwload, file_donwload_path))
            # url = conf['scriptsurl'] + file_donwload
            # url = conf['updateurl']
            # f = urllib2.urlopen(url)
            with open(file_donwload_path, 'wb') as local_file:
                # local_file.write(f.read())
                local_file.write(data_download)

            # verificar permissao necessaria
            os.chmod(file_donwload_path, 0o0777)
            scripts_updated = True

    if scripts_updated:
        cleanup = raw_input(
            'Deseja apagar a lista de epg atual? S = sim, N = não ')
        if cleanup.lower() == 's':
            apagar_base_epg(conf)


def configure_epg_grabber(conf):
    """
    Habilita EPG Brasil Net
    """
    grabbers_found = obter_lista_de_grabbers(conf)

    grabber_xml_external_found = False
    grabber_xml_internal_found = False

    for item in grabbers_found:
        logging.info("Encontrado %s" % item['name'])
        if "External: XMLTV" in item['name']:
            grabber_xml_external_found = True
        if "Internal: XMLTV" in item['name']:
            grabber_xml_internal_found = True

        if not "External: XMLTV" in item['name'] and not "Internal: XMLTV" in item['name']:
            logging.info("Desativando %s" % item['name'])
            req = urllib2.Request("http://" + conf['tvheadendAddress'] + ":" + conf['tvheadendPort'] +
                                  '/api/idnode/save?node={"uuid":"' + item['uuid'] + '","enabled":"false"}')
            urllib2.urlopen(req)

    if grabber_xml_external_found:
        for g in grabbers_found:
            # logging.info("Encontrado %s" % g['name'])
            if g['scrape_extra'] and g['scrape_onto_desc'] and not g['use_category_not_genre']:
                logging.info("%s configurado ok" % g['name'])
            else:
                logging.info("Reconfigurando %s", g['name'])
                req = urllib2.Request("http://" + conf['tvheadendAddress'] + ":" + conf['tvheadendPort'] +
                                      '/api/idnode/save?node={"uuid":"' + g['uuid'] + '","enabled":"true","scrape_extra":"true","scrape_onto_desc":"true","use_category_not_genre":"false"}')
                urllib2.urlopen(req)

    if not grabber_xml_external_found and not grabber_xml_internal_found:
        logging.info("Nenhum grabber encontrado, adicionando External: XMLTV")

        # files_dl = conf['scripts_grabber']

        # for file_donwload in files_dl:
        #     file_donwload_path = conf['scriptspath'] + file_donwload

        #     overwrite_file = True

        #     if os.path.isfile(file_donwload_path):
        #         overwrite = raw_input(
        #             'Arquivo %s já existe, sobrescrever? S = sim, N = não ' % (file_donwload_path))
        #         if not overwrite.lower() == 's':
        #             overwrite_file = False

        #     if overwrite_file:

        #         logging.info("Download do arquivo %s e salvando em %s" %
        #                      (file_donwload, file_donwload_path))
        #         url = conf['scriptsurl'] + file_donwload
        #         # url = conf['updateurl']
        #         f = urllib2.urlopen(url)
        #         with open(file_donwload_path, 'wb') as local_file:
        #             local_file.write(f.read())

        #         # verificar permissao necessaria
        #         os.chmod(file_donwload_path, 0o0777)

        uuid_external_xml = obter_uuid_xmltv(conf)

        logging.info("Habilitando e reconfigurando External: XMLTV")
        req = urllib2.Request("http://" + conf['tvheadendAddress'] + ":" + conf['tvheadendPort'] +
                              '/api/idnode/save?node={"uuid":"' + uuid_external_xml + '","enabled":"true","scrape_extra":"true","scrape_onto_desc":"true","use_category_not_genre":"false"}')
        urllib2.urlopen(req)

        grabber_xml_external_found = True

    if grabber_xml_external_found:
        # verificar scripts
        download_scripts_grabber(conf)

        # verificar socat
        verificar_socat_instalado(conf)

        # rodar tvgrab uma vez
        executar_grabber_manual(conf)

    # Verificar no crontab
    logging.info("Verificando se %stv_grab_br está no crontab" %
                 conf['scriptspath'])

    if not conf['devmode']:
        verificar_crontab()

    if not verifica_xmltv_external(conf):

        executa_internal_grabber(conf)

    else:

        if not conf['devmode']:
            logging.info("Aguardando lista de canais no epg ser carregada")
            list_loaded = False
            count_loop = 1
            while not list_loaded:
                req = urllib2.Request(
                    "http://" + conf['tvheadendAddress'] + ":" + conf['tvheadendPort'] + '/api/epggrab/channel/list')
                tvhreq = urllib2.urlopen(req)
                data = json.load(tvhreq)

                if len(data['entries']) > 0:
                    break

                count_loop += 1
                time.sleep(0.5)
                if count_loop > 30:
                    logging.info(
                        "Aguardando lista de canais no epg ser carregada - timeout!")
                    break


def processa_lista_canais(conf):
    """
    Obtem lista de canais
    """
    list_epg = []
    req = urllib2.Request("http://%s:%s/api/epggrab/channel/list" %
                          (conf['tvheadendAddress'], conf['tvheadendPort']))
    tvhreq = urllib2.urlopen(req)
    data_epg = json.load(tvhreq)
    for l in data_epg['entries']:
        cn_str = l['text'].split(':')[0].strip()
        cn_str = re.sub(re.compile('\W'), '', ''.join(c.lower() for c in unicodedata.normalize(
            'NFKD', cn_str.replace("+", "mais")).encode('ascii', 'ignore') if not c.isspace()))
        # print ( "%s %s - %s" % (l['uuid'], cnStr, l['text']) )
        list_epg.append({"uuid": l['uuid'], "name": cn_str, "text": l['text']})

    list_channels = get_tvh_channel_list(conf)

    # lista envio
    lista_envio = []
    for i in list_epg:
        if i['name'] not in lista_envio:
            lista_envio.append(i['name'])

    for l in list_channels:
        if not l['epggrab']:
            cn_str = re.sub(re.compile('\W'), '', ''.join(c.lower() for c in unicodedata.normalize(
                'NFKD', l['name'].replace("+", "mais")).encode('ascii', 'ignore') if not c.isspace()))
            if cn_str not in lista_envio:
                lista_envio.append(cn_str)

    # lista externa
    # executar apos
    list_ext = get_external_list(conf, lista_envio)

    # lista envio
    final = {'lista_canais': list_channels,
             'lista_epg': list_epg, 'lista_externa': list_ext}
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
                canalclean = re.sub(re.compile('\W'), '', ''.join(c.upper() for c in unicodedata.normalize(
                    'NFKD', l['name'].replace("+", "plus").replace(" HD", "")).encode('ascii', 'ignore') if not c.isspace()))
                found = False
                # cn = ''
                for e in lista['lista_epg']:
                    # AXN: AXN (XMLTV: EPG Brasil Net)
                    tmp_name_01 = e['text'].split(':')[0]
                    tmp_name_01 = re.sub(re.compile('\W'), '', ''.join(c.upper() for c in unicodedata.normalize(
                        'NFKD', tmp_name_01.replace("+", "plus")).encode('ascii', 'ignore') if not c.isspace()))
                    if canalclean == tmp_name_01:
                        msg = bcolors.OKGREEN + "found 1 - " + \
                            e['text'] + bcolors.ENDC
                        found = True
                        alterar_epg_item(conf, l['uuid'], e['uuid'])
                if not found:
                    # print(l['name'])
                    key = ""
                    cn_str = re.sub(re.compile('\W'), '', ''.join(c.lower() for c in unicodedata.normalize(
                        'NFKD', l['name'].replace("+", "mais")).encode('ascii', 'ignore') if not c.isspace()))
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

            print("%-*s %-*s %s" %
                  (3, l['number'], 25, l['name'], msg)).encode('utf-8')
    logging.info("Concluido")


def apagar_base_epg(conf):
    list_epg = []
    req = urllib2.Request("http://%s:%s/api/epggrab/channel/grid?limit=2000&all=1" %
                          (conf['tvheadendAddress'], conf['tvheadendPort']))
    tvhreq = urllib2.urlopen(req)
    data_epg = json.load(tvhreq)
    for l in data_epg['entries']:
        logging.info("removendo {}".format(l['name']))
        # print('http://{}:{}/api/idnode/delete?node={{"uuid":"{}"}}'.format(
        #     conf['tvheadendAddress'], conf['tvheadendPort'], l['uuid']))
        req1 = urllib2.Request('http://{}:{}/api/idnode/delete?uuid=["{}"]'.format(
            conf['tvheadendAddress'], conf['tvheadendPort'], l['uuid']))
        tvhreq1 = urllib2.urlopen(req1)


def main():
    """Main function."""

    global CONFIG, DEV_CONFIG

    parser = argparse.ArgumentParser(
        description='Configuração de epg no Tvheadend.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--no-update', action='store_true',
                       help='não verifica por atualização')
    group.add_argument('--force-update', action='store_true',
                       help='força atualização')

    group_debug = parser.add_mutually_exclusive_group()
    group_debug.add_argument(
        '--dev', action='store_true', help='modo de testes')

    parser.add_argument('-a', '--apagar-base', action="store_true", default=False,
                        help="apaga lista antiga de canais epg")

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
        update(CONFIG['updateurl'], True)
        logging.info("Pronto.")
        sys.exit()

    if ckUpdates:
        updateReturn = update(CONFIG['updateurl'])
        if updateReturn:
            logging.info("Reiniciando script")
            python = sys.executable
            os.execl(python, python, *sys.argv)

    if args.apagar_base:
        apagar_base_epg(CONFIG)
        sys.exit()

    has_tvh = check_for_tvh(CONFIG)

    if has_tvh:
        configure_epg_grabber(CONFIG)
        lista_canais = processa_lista_canais(CONFIG)
        processa_alteracoes(CONFIG, lista_canais)
        reconfigure_epg_grabber(CONFIG)
        executar_grabber_manual(CONFIG)


if __name__ == '__main__':
    main()
