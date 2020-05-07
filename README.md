# tvheadend_scripts

Script para configuração do epg no tvheadend no pixel

* Verifica se source "EPG Brasil Net" está instalado e ativo.
* Busca por canais em que não o epg não está configurado. Os que já estão configurados, o script não altera.

## Instalação

Entrar no terminal do e2/tvh e fazer o download do script:
```
wget https://raw.githubusercontent.com/josemoraes99/tvheadend_scripts/master/tvheadend_configure_epg.py
```
## Para executar:
```
python tvheadend_configure_epg.py
```