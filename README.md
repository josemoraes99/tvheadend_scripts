# tvheadend_scripts

Script para configuração do epg no tvheadend no pixel

* Se não houver nenhum grabber configurado, o script faz a configuração automática.
* Verifica se o source "EPG Brasil Net" está instalado e ativo.
* Busca por canais em que não o epg não está configurado. Os que já estão configurados, o script não altera.
* A primeira comparação é simplesmente uma busca por canais com mesmo nome sem "HD"
* A segunda comparação é utilizando a base de picons para procurar um nome de canal aproximado
* Os canais não encontrados precisam ser configurados manualmente na interface de admin do Tvheadend

## Instalação

Entrar no terminal do e2/tvh e fazer o download do script:
```
wget https://raw.githubusercontent.com/josemoraes99/tvheadend_scripts/master/tvheadend_configure_epg.py
```
## Para executar:
```
python tvheadend_configure_epg.py
```