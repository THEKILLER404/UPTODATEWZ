#!/usr/bin/env python3
from threading import Thread
from base64 import b64decode
from json import loads
from os import path
from uuid import uuid4
from hashlib import sha256
from time import sleep
from re import findall, match, search

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from lxml.etree import HTML
from requests import Session, session as req_session, post
from urllib.parse import parse_qs, quote, unquote, urlparse, urljoin
from cloudscraper import create_scraper
from lk21 import Bypass
from http.cookiejar import MozillaCookieJar

from bot import LOGGER, config_dict
from bot.helper.ext_utils.bot_utils import get_readable_time, is_share_link, is_index_link, is_magnet
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException
from bot.helper.ext_utils.help_messages import PASSWORD_ERROR_MESSAGE

_caches = {}

user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
)

fmed_list = ['fembed.net', 'fembed.com', 'femax20.com', 'fcdn.stream', 'feurl.com', 'layarkacaxxi.icu',
             'naniplay.nanime.in', 'naniplay.nanime.biz', 'naniplay.com', 'mm9842.com']

anonfilesBaseSites = ['anonfiles.com', 'hotfile.io', 'bayfiles.com', 'megaupload.nz', 'letsupload.cc',
                      'filechan.org', 'myfile.is', 'vshare.is', 'rapidshare.nu', 'lolabits.se',
                      'openload.cc', 'share-online.is', 'upvid.cc']

debrid_sites = ['1fichier.com', '2shared.com', '4shared.com', 'alfafile.net', 'anzfile.net', 'backin.net',
                'bayfiles.com', 'bdupload.in', 'brupload.net', 'btafile.com', 'catshare.net', 'clicknupload.me',
                'clipwatching.com', 'cosmobox.org', 'dailymotion.com', 'dailyuploads.net', 'daofile.com',
                'datafilehost.com', 'ddownload.com', 'depositfiles.com', 'dl.free.fr', 'douploads.net',
                'drop.download', 'earn4files.com', 'easybytez.com', 'ex-load.com', 'extmatrix.com',
                'down.fast-down.com', 'fastclick.to', 'faststore.org', 'file.al', 'file4safe.com', 'fboom.me',
                'filefactory.com', 'filefox.cc', 'filenext.com', 'filer.net', 'filerio.in', 'filesabc.com', 'filespace.com',
                'file-up.org', 'fileupload.pw', 'filezip.cc', 'fireget.com', 'flashbit.cc', 'flashx.tv', 'florenfile.com',
                'fshare.vn', 'gigapeta.com', 'goloady.com', 'docs.google.com', 'gounlimited.to', 'heroupload.com',
                'hexupload.net', 'hitfile.net', 'hotlink.cc', 'hulkshare.com', 'icerbox.com', 'inclouddrive.com',
                'isra.cloud', 'katfile.com', 'keep2share.cc', 'letsupload.cc', 'load.to', 'down.mdiaload.com', 'mediafire.com',
                'mega.co.nz', 'mixdrop.co', 'mixloads.com', 'mp4upload.com', 'nelion.me', 'ninjastream.to', 'nitroflare.com',
                'nowvideo.club', 'oboom.com', 'prefiles.com', 'sky.fm', 'rapidgator.net', 'rapidrar.com', 'rapidu.net',
                'rarefile.net', 'real-debrid.com', 'redbunker.net', 'redtube.com', 'rockfile.eu', 'rutube.ru', 'scribd.com',
                'sendit.cloud', 'sendspace.com', 'simfileshare.net', 'solidfiles.com', 'soundcloud.com', 'speed-down.org',
                'streamon.to', 'streamtape.com', 'takefile.link', 'tezfiles.com', 'thevideo.me', 'turbobit.net', 'tusfiles.com',
                'ubiqfile.com', 'uloz.to', 'unibytes.com', 'uploadbox.io', 'uploadboy.com', 'uploadc.com', 'uploaded.net',
                'uploadev.org', 'uploadgig.com', 'uploadrar.com', 'uppit.com', 'upstore.net', 'upstream.to', 'uptobox.com',
                'userscloud.com', 'usersdrive.com', 'vidcloud.ru', 'videobin.co', 'vidlox.tv', 'vidoza.net', 'vimeo.com',
                'vivo.sx', 'vk.com', 'voe.sx', 'wdupload.com', 'wipfiles.net', 'world-files.com', 'worldbytez.com', 'wupfile.com',
                'wushare.com', 'xubster.com', 'youporn.com', 'youtube.com']

debrid_link_sites = ["1dl.net", "1fichier.com", "alterupload.com", "cjoint.net", "desfichiers.com", "dfichiers.com", "megadl.org", 
                "megadl.fr", "mesfichiers.fr", "mesfichiers.org", "piecejointe.net", "pjointe.com", "tenvoi.com", "dl4free.com", 
                "apkadmin.com", "bayfiles.com", "clicknupload.link", "clicknupload.org", "clicknupload.co", "clicknupload.cc", 
                "clicknupload.link", "clicknupload.download", "clicknupload.club", "clickndownload.org", "ddl.to", "ddownload.com", 
                "depositfiles.com", "dfile.eu", "dropapk.to", "drop.download", "dropbox.com", "easybytez.com", "easybytez.eu", 
                "easybytez.me", "elitefile.net", "elfile.net", "wdupload.com", "emload.com", "fastfile.cc", "fembed.com", 
                "feurl.com", "anime789.com", "24hd.club", "vcdn.io", "sharinglink.club", "votrefiles.club", "there.to", "femoload.xyz", 
                "dailyplanet.pw", "jplayer.net", "xstreamcdn.com", "gcloud.live", "vcdnplay.com", "vidohd.com", "vidsource.me", 
                "votrefile.xyz", "zidiplay.com", "fcdn.stream", "femax20.com", "sexhd.co", "mediashore.org", "viplayer.cc", "dutrag.com", 
                "mrdhan.com", "embedsito.com", "diasfem.com", "superplayxyz.club", "albavido.xyz", "ncdnstm.com", "fembed-hd.com", 
                "moviemaniac.org", "suzihaza.com", "fembed9hd.com", "vanfem.com", "fikper.com", "file.al", "fileaxa.com", "filecat.net", 
                "filedot.xyz", "filedot.to", "filefactory.com", "filenext.com", "filer.net", "filerice.com", "filesfly.cc", "filespace.com", 
                "filestore.me", "flashbit.cc", "dl.free.fr", "transfert.free.fr", "free.fr", "gigapeta.com", "gofile.io", "highload.to", 
                "hitfile.net", "hitf.cc", "hulkshare.com", "icerbox.com", "isra.cloud", "goloady.com", "jumploads.com", "katfile.com", 
                "k2s.cc", "keep2share.com", "keep2share.cc", "kshared.com", "load.to", "mediafile.cc", "mediafire.com", "mega.nz", 
                "mega.co.nz", "mexa.sh", "mexashare.com", "mx-sh.net", "mixdrop.co", "mixdrop.to", "mixdrop.club", "mixdrop.sx", 
                "modsbase.com", "nelion.me", "nitroflare.com", "nitro.download", "e.pcloud.link", "pixeldrain.com", "prefiles.com", "rg.to", 
                "rapidgator.net", "rapidgator.asia", "scribd.com", "sendspace.com", "sharemods.com", "soundcloud.com", "noregx.debrid.link", 
                "streamlare.com", "slmaxed.com", "sltube.org", "slwatch.co", "streamtape.com", "subyshare.com", "supervideo.tv", "terabox.com", 
                "tezfiles.com", "turbobit.net", "turbobit.cc", "turbobit.pw", "turbobit.online", "turbobit.ru", "turbobit.live", "turbo.to", 
                "turb.to", "turb.cc", "turbabit.com", "trubobit.com", "turb.pw", "turboblt.co", "turboget.net", "ubiqfile.com", "ulozto.net", 
                "uloz.to", "zachowajto.pl", "ulozto.cz", "ulozto.sk", "upload-4ever.com", "up-4ever.com", "up-4ever.net", "uptobox.com", 
                "uptostream.com", "uptobox.fr", "uptostream.fr", "uptobox.eu", "uptostream.eu", "uptobox.link", "uptostream.link", "upvid.pro", 
                "upvid.live", "upvid.host", "upvid.co", "upvid.biz", "upvid.cloud", "opvid.org", "opvid.online", "uqload.com", "uqload.co", 
                "uqload.io", "userload.co", "usersdrive.com", "vidoza.net", "voe.sx", "voe-unblock.com", "voeunblock1.com", "voeunblock2.com", 
                "voeunblock3.com", "voeunbl0ck.com", "voeunblck.com", "voeunblk.com", "voe-un-block.com", "voeun-block.net", 
                "reputationsheriffkennethsand.com", "449unceremoniousnasoseptal.com", "world-files.com", "worldbytez.com", "salefiles.com", 
                "wupfile.com", "youdbox.com", "yodbox.com", "youtube.com", "youtu.be", "4tube.com", "academicearth.org", "acast.com", 
                "add-anime.net", "air.mozilla.org", "allocine.fr", "alphaporno.com", "anysex.com", "aparat.com", "www.arte.tv", "video.arte.tv", 
                "sites.arte.tv", "creative.arte.tv", "info.arte.tv", "future.arte.tv", "ddc.arte.tv", "concert.arte.tv", "cinema.arte.tv", 
                "audi-mediacenter.com", "audioboom.com", "audiomack.com", "beeg.com", "camdemy.com", "chilloutzone.net", "clubic.com", "clyp.it", 
                "daclips.in", "dailymail.co.uk", "www.dailymail.co.uk", "dailymotion.com", "touch.dailymotion.com", "democracynow.org", 
                "discovery.com", "investigationdiscovery.com", "discoverylife.com", "animalplanet.com", "ahctv.com", "destinationamerica.com", 
                "sciencechannel.com", "tlc.com", "velocity.com", "dotsub.com", "ebaumsworld.com", "eitb.tv", "ellentv.com", "ellentube.com", 
                "flipagram.com", "footyroom.com", "formula1.com", "video.foxnews.com", "video.foxbusiness.com", "video.insider.foxnews.com", 
                "franceculture.fr", "gameinformer.com", "gamersyde.com", "gorillavid.in", "hbo.com", "hellporno.com", "hentai.animestigma.com", 
                "hornbunny.com", "imdb.com", "instagram.com", "itar-tass.com", "tass.ru", "jamendo.com", "jove.com", "keek.com", "k.to", 
                "keezmovies.com", "khanacademy.org", "kickstarter.com", "krasview.ru", "la7.it", "lci.fr", "play.lcp.fr", "libsyn.com", 
                "html5-player.libsyn.com", "liveleak.com", "livestream.com", "new.livestream.com", "m6.fr", "www.m6.fr", "metacritic.com", 
                "mgoon.com", "m.mgoon.com", "mixcloud.com", "mojvideo.com", "movieclips.com", "movpod.in", "musicplayon.com", "myspass.de", 
                "myvidster.com", "odatv.com", "onionstudios.com", "ora.tv", "unsafespeech.com", "play.fm", "plays.tv", "playvid.com", 
                "pornhd.com", "pornhub.com", "www.pornhub.com", "pyvideo.org", "redtube.com", "embed.redtube.com", "www.redtube.com", 
                "reverbnation.com", "revision3.com", "animalist.com", "seeker.com", "rts.ch", "rtve.es", "videos.sapo.pt", "videos.sapo.cv", 
                "videos.sapo.ao", "videos.sapo.mz", "videos.sapo.tl", "sbs.com.au", "www.sbs.com.au", "screencast.com", "skysports.com", 
                "slutload.com", "soundgasm.net", "store.steampowered.com", "steampowered.com", "steamcommunity.com", "stream.cz", "streamable.com", 
                "streamcloud.eu", "sunporno.com", "teachertube.com", "teamcoco.com", "ted.com", "tfo.org", "thescene.com", "thesixtyone.com", 
                "tnaflix.com", "trutv.com", "tu.tv", "turbo.fr", "tweakers.net", "ustream.tv", "vbox7.com", "veehd.com", "veoh.com", "vid.me", 
                "videodetective.com", "vimeo.com", "vimeopro.com", "player.vimeo.com", "player.vimeopro.com", "wat.tv", "wimp.com", "xtube.com", 
                "yahoo.com", "screen.yahoo.com", "news.yahoo.com", "sports.yahoo.com", "video.yahoo.com", "youporn.com"]


def direct_link_generator(link):
    auth = None
    if isinstance(link, tuple):
        link, auth = link
    if is_magnet(link):
        return real_debrid(link, True)

    domain = urlparse(link).hostname
    if not domain:
        raise DirectDownloadLinkException("ERROR: Invalid URL")
    if 'youtube.com' in domain or 'youtu.be' in domain:
        raise DirectDownloadLinkException("ERROR: Use ytdl cmds for Youtube links")
    elif config_dict['DEBRID_LINK_API'] and any(x in domain for x in debrid_link_sites):
        return debrid_link(link)
    elif config_dict['REAL_DEBRID_API'] and any(x in domain for x in debrid_sites):
        return real_debrid(link)
    elif any(x in domain for x in ['filelions.com', 'filelions.live', 'filelions.to', 'filelions.online']):
        return filelions(link)
    elif 'mediafire.com' in domain:
        return mediafire(link)
    elif 'osdn.net' in domain:
        return osdn(link)
    elif 'github.com' in domain:
        return github(link)
    elif 'hxfile.co' in domain:
        return hxfile(link)
    elif '1drv.ms' in domain:
        return onedrive(link)
    elif 'pixeldrain.com' in domain:
        return pixeldrain(link)
    elif 'antfiles.com' in domain:
        return antfiles(link)
    elif 'racaty' in domain:
        return racaty(link)
    elif '1fichier.com' in domain:
        return fichier(link)
    elif 'solidfiles.com' in domain:
        return solidfiles(link)
    elif 'krakenfiles.com' in domain:
        return krakenfiles(link)
    elif 'upload.ee' in domain:
        return uploadee(link)
    elif 'akmfiles' in domain:
        return akmfiles(link)
    elif 'linkbox' in domain:
        return linkbox(link)
    elif 'shrdsk' in domain:
        return shrdsk(link)
    elif 'letsupload.io' in domain:
        return letsupload(link)
    elif 'gofile.io' in domain:
        return gofile(link, auth)
    elif 'easyupload.io' in domain:
        return easyupload(link)
    elif 'streamvid.net' in domain:
        return streamvid(link)
    elif any(x in domain for x in ['dood.watch', 'doodstream.com', 'dood.to', 'dood.so', 'dood.cx', 'dood.la', 'dood.ws', 'dood.sh', 'doodstream.co', 'dood.pm', 'dood.wf', 'dood.re', 'dood.video', 'dooood.com', 'dood.yt', 'doods.yt', 'dood.stream', 'doods.pro']):
        return doods(link)
    elif any(x in domain for x in ['streamtape.com', 'streamtape.co', 'streamtape.cc', 'streamtape.to', 'streamtape.net', 'streamta.pe', 'streamtape.xyz']):
        return streamtape(link)
    elif any(x in domain for x in ['wetransfer.com', 'we.tl']):
        return wetransfer(link)
    elif any(x in domain for x in anonfilesBaseSites):
        raise DirectDownloadLinkException('ERROR: R.I.P Anon Sites!')
    elif any(x in domain for x in ['terabox.com', 'nephobox.com', '4funbox.com', 'mirrobox.com', 'momerybox.com', 'teraboxapp.com', '1024tera.com']):
        return terabox(link)
    elif any(x in domain for x in fmed_list):
        return fembed(link)
    elif any(x in domain for x in ['sbembed.com', 'watchsb.com', 'streamsb.net', 'sbplay.org']):
        return sbembed(link)
    elif is_index_link(link) and link.endswith('/'):
        return gd_index(link, auth)
    elif is_share_link(link):
        if 'gdtot' in domain:
            return gdtot(link)
        elif 'filepress' in domain:
            return filepress(link)
        elif 'www.jiodrive' in domain:
            return jiodrive(link)
        else:
            return sharer_scraper(link)
    elif 'zippyshare.com' in domain:
        raise DirectDownloadLinkException('ERROR: R.I.P Zippyshare')
    else:
        raise DirectDownloadLinkException(f'No Direct link function found for {link}')


def real_debrid(url: str, tor=False):
    """ Real-Debrid Link Extractor (VPN Maybe Needed)
    Based on Real-Debrid v1 API (Heroku/VPS) [Without VPN]"""
    def __unrestrict(url, tor=False):
        cget = create_scraper().request
        resp = cget('POST', f"https://api.real-debrid.com/rest/1.0/unrestrict/link?auth_token={config_dict['REAL_DEBRID_API']}", data={'link': url})
        if resp.status_code == 200:
            if tor:
                _res = resp.json()
                return (_res['filename'], _res['download'])
            else:
                return resp.json()['download']
        else:
            raise DirectDownloadLinkException(f"ERROR: {resp.json()['error']}")
            
    def __addMagnet(magnet):
        cget = create_scraper().request
        hash_ = search(r'(?<=xt=urn:btih:)[a-zA-Z0-9]+', magnet).group(0)
        resp = cget('GET', f"https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/{hash_}?auth_token={config_dict['REAL_DEBRID_API']}")
        if resp.status_code != 200 or len(resp.json()[hash_.lower()]['rd']) == 0:
            return magnet
        resp = cget('POST', f"https://api.real-debrid.com/rest/1.0/torrents/addMagnet?auth_token={config_dict['REAL_DEBRID_API']}", data={'magnet': magnet})
        if resp.status_code == 201:
            _id = resp.json()['id']
        else:
            raise DirectDownloadLinkException(f"ERROR: {resp.json()['error']}")
        if _id:
            _file = cget('POST', f"https://api.real-debrid.com/rest/1.0/torrents/selectFiles/{_id}?auth_token={config_dict['REAL_DEBRID_API']}", data={'files': 'all'})
            if _file.status_code != 204:
                raise DirectDownloadLinkException(f"ERROR: {resp.json()['error']}")
            
        contents = {'links': []}
        while len(contents['links']) == 0:
            _res = cget('GET', f"https://api.real-debrid.com/rest/1.0/torrents/info/{_id}?auth_token={config_dict['REAL_DEBRID_API']}")
            if _res.status_code == 200:
                contents = _res.json()
            else:
                raise DirectDownloadLinkException(f"ERROR: {_res.json()['error']}")
            sleep(0.5)
        
        details = {'contents': [], 'title': contents['original_filename'], 'total_size': contents['bytes']}

        for file_info, link in zip(contents['files'], contents['links']):
            link_info = __unrestrict(link, tor=True)
            item = {
                "path": path.join(details['title'], path.dirname(file_info['path']).lstrip("/")), 
                "filename": unquote(link_info[0]),
                "url": link_info[1],
            }
            details['contents'].append(item)
        return details
    
    try:
        if tor:
            details = __addMagnet(url)
        else:
            return __unrestrict(url)
    except Exception as e:
        raise DirectDownloadLinkException(e)
    if isinstance(details, dict) and len(details['contents']) == 1:
        return details['contents'][0]['url']
    return details
    
    
def debrid_link(url):
    cget = create_scraper().request
    resp = cget('POST', f"https://debrid-link.com/api/v2/downloader/add?access_token={config_dict['DEBRID_LINK_API']}", data={'url': url}).json()
    if resp['success'] != True:
        raise DirectDownloadLinkException(f"ERROR: {resp['error']} & ERROR ID: {resp['error_id']}")
    if isinstance(resp['value'], dict):
        return resp['value']['downloadUrl']
    elif isinstance(resp['value'], list):
        details = {'contents': [], 'title': unquote(url.rstrip('/').split('/')[-1]), 'total_size': 0}
        for dl in resp['value']:
            if dl.get('expired', False):
                continue
            item = {
                "path": path.join(details['title']),
                "filename": dl['name'],
                "url": dl['downloadUrl']
            }
            if 'size' in dl:
                details['total_size'] += dl['size']
            details['contents'].append(item)
        return details


def get_captcha_token(session, params):
    recaptcha_api = 'https://www.google.com/recaptcha/api2'
    res = session.get(f'{recaptcha_api}/anchor', params=params)
    anchor_html = HTML(res.text)
    if not (anchor_token:= anchor_html.xpath('//input[@id="recaptcha-token"]/@value')):
        return
    params['c'] = anchor_token[0]
    params['reason'] = 'q'
    res = session.post(f'{recaptcha_api}/reload', params=params)
    if token := findall(r'"rresp","(.*?)"', res.text):
        return token[0]


def mediafire(url, session=None):
    if '/folder/' in url:
        return mediafireFolder(url)
    if final_link := findall(r'https?:\/\/download\d+\.mediafire\.com\/\S+\/\S+\/\S+', url):
        return final_link[0]
    if session is None:
        session = Session()
        parsed_url = urlparse(url)
        url = f'{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}'
    try:
        html = HTML(session.get(url).text)
    except Exception as e:
        session.close()
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if error:= html.xpath('//p[@class="notranslate"]/text()'):
        session.close()
        raise DirectDownloadLinkException(f"ERROR: {error[0]}")
    if not (final_link := html.xpath("//a[@id='downloadButton']/@href")):
        session.close()
        raise DirectDownloadLinkException("ERROR: No links found in this page Try Again")
    if final_link[0].startswith('//'):
        return mediafire(f'https://{final_link[0][2:]}', session)
    session.close()
    return final_link[0]


def osdn(url):
    with create_scraper() as session:
        try:
            html = H
