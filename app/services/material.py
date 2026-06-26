import os
import random
import threading
from typing import List
from urllib.parse import urlparse, urlencode

import requests
from loguru import logger
from moviepy import CompositeVideoClip, ImageClip
from moviepy.video.io.VideoFileClip import VideoFileClip

from app.config import config
from app.models import const
from app.models.schema import MaterialInfo, VideoAspect, VideoConcatMode
from app.utils import utils

# Thread-safe counter for API key rotation
_api_key_counter = 0
_api_key_lock = threading.Lock()


def _get_tls_verify() -> bool:
    # 榛樿寮€鍚?TLS 璇佷功鏍￠獙锛岄槻姝㈢礌鏉愭悳绱㈠拰涓嬭浇杩囩▼琚腑闂翠汉绡℃敼銆?    # 浠呭湪浼佷笟浠ｇ悊銆佽嚜绛捐瘉涔︾瓑鏄庣‘闇€瑕佺殑鍦烘櫙涓嬶紝鍏佽鐢ㄦ埛閫氳繃
    # `config.toml` 鏄惧紡璁剧疆 `tls_verify = false` 涓存椂鍏抽棴銆?    tls_verify = config.app.get("tls_verify", True)
    if isinstance(tls_verify, str):
        tls_verify = tls_verify.strip().lower() not in ("0", "false", "no", "off")

    if not tls_verify:
        logger.warning(
            "TLS certificate verification is disabled by config.app.tls_verify=false. "
            "Only use this in trusted proxy environments."
        )

    return bool(tls_verify)


def get_api_key(cfg_key: str):
    api_keys = config.app.get(cfg_key)
    if not api_keys:
        raise ValueError(
            f"\n\n##### {cfg_key} is not set #####\n\nPlease set it in the config.toml file: {config.config_file}\n\n"
            f"{utils.to_json(config.app)}"
        )

    # if only one key is provided, return it
    if isinstance(api_keys, str):
        return api_keys

    global _api_key_counter
    with _api_key_lock:
        _api_key_counter += 1
        return api_keys[_api_key_counter % len(api_keys)]


def search_videos_pexels(
    search_term: str,
    minimum_duration: int,
    video_aspect: VideoAspect = VideoAspect.portrait,
) -> List[MaterialInfo]:
    aspect = VideoAspect(video_aspect)
    video_orientation = aspect.name
    video_width, video_height = aspect.to_resolution()
    api_key = get_api_key("pexels_api_keys")
    headers = {
        "Authorization": api_key,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    }
    # Build URL
    params = {"query": search_term, "per_page": 20, "orientation": video_orientation}
    query_url = f"https://api.pexels.com/videos/search?{urlencode(params)}"
    logger.info(f"searching videos: {query_url}, with proxies: {config.proxy}")

    try:
        r = requests.get(
            query_url,
            headers=headers,
            proxies=config.proxy,
            verify=_get_tls_verify(),
            timeout=(30, 60),
        )
        response = r.json()
        video_items = []
        if "videos" not in response:
            logger.error(f"search videos failed: {response}")
            return video_items
        videos = response["videos"]
        # loop through each video in the result
        for v in videos:
            duration = v["duration"]
            # check if video has desired minimum duration
            if duration < minimum_duration:
                continue
            video_files = v["video_files"]
            # loop through each url to determine the best quality
            for video in video_files:
                w = int(video["width"])
                h = int(video["height"])
                if w == video_width and h == video_height:
                    item = MaterialInfo()
                    item.provider = "pexels"
                    item.url = video["link"]
                    item.duration = duration
                    video_items.append(item)
                    break
        return video_items
    except Exception as e:
        logger.error(f"search videos failed: {str(e)}")

    return []


def search_videos_pixabay(
    search_term: str,
    minimum_duration: int,
    video_aspect: VideoAspect = VideoAspect.portrait,
) -> List[MaterialInfo]:
    aspect = VideoAspect(video_aspect)

    video_width, video_height = aspect.to_resolution()

    api_key = get_api_key("pixabay_api_keys")
    # Build URL
    params = {
        "q": search_term,
        "video_type": "all",  # Accepted values: "all", "film", "animation"
        "per_page": 50,
        "key": api_key,
    }
    query_url = f"https://pixabay.com/api/videos/?{urlencode(params)}"
    logger.info(f"searching videos: {query_url}, with proxies: {config.proxy}")

    try:
        r = requests.get(
            query_url, proxies=config.proxy, verify=_get_tls_verify(), timeout=(30, 60)
        )
        response = r.json()
        video_items = []
        if "hits" not in response:
            logger.error(f"search videos failed: {response}")
            return video_items
        videos = response["hits"]
        # loop through each video in the result
        for v in videos:
            duration = v["duration"]
            # check if video has desired minimum duration
            if duration < minimum_duration:
                continue
            video_files = v["videos"]
            # loop through each url to determine the best quality
            for video_type in video_files:
                video = video_files[video_type]
                w = int(video["width"])
                # h = int(video["height"])
                if w >= video_width:
                    item = MaterialInfo()
                    item.provider = "pixabay"
                    item.url = video["url"]
                    item.duration = duration
                    video_items.append(item)
                    break
        return video_items
    except Exception as e:
        logger.error(f"search videos failed: {str(e)}")

    return []


def search_videos_coverr(
    search_term: str,
    minimum_duration: int,
    video_aspect: VideoAspect = VideoAspect.portrait,
) -> List[MaterialInfo]:
    """
    Coverr (https://coverr.co) - free HD/4K stock videos,
    subject to Coverr license terms (https://coverr.co/license).
    """
    api_key = get_api_key("coverr_api_keys")
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {
        "query": search_term,
        "page_size": 20,
        "urls": "true",
        "sort": "popular",
    }
    query_url = f"https://api.coverr.co/videos?{urlencode(params)}"
    logger.info(f"searching videos: {query_url}, with proxies: {config.proxy}")

    try:
        r = requests.get(
            query_url,
            headers=headers,
            proxies=config.proxy,
            verify=_get_tls_verify(),
            timeout=(30, 60),
        )
        response = r.json()
        video_items: List[MaterialInfo] = []

        if not isinstance(response, dict) or "hits" not in response:
            logger.error(f"search videos failed: {response}")
            return video_items

        for v in response["hits"]:
            try:
                duration = int(float(v.get("duration") or 0))
            except (TypeError, ValueError):
                continue
            if duration < minimum_duration:
                continue

            video_id = v.get("id")
            mp4_download_url = (v.get("urls") or {}).get("mp4_download")
            if not video_id or not mp4_download_url:
                continue

            item = MaterialInfo()
            item.provider = "coverr"
            item.url = mp4_download_url
            item.duration = duration
            video_items.append(item)
        return video_items
    except Exception as e:
        logger.error(f"search videos failed: {str(e)}")

    return []


def _get_bearer_api_headers(api_key: str = "") -> dict:
    headers = {
        "Accept": "application/json",
        "User-Agent": "MoneyPrinterTurbo/2.0.1",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _get_douyin_material_api_headers() -> dict:
    api_key = (config.app.get("douyin_material_api_key") or "").strip()
    return _get_bearer_api_headers(api_key)


def _get_douyin_metadata_api_headers() -> dict:
    api_key = (config.app.get("douyin_metadata_api_key") or "").strip()
    return _get_bearer_api_headers(api_key)


def _get_douyin_resolver_api_headers() -> dict:
    api_key = (config.app.get("douyin_resolver_api_key") or "").strip()
    return _get_bearer_api_headers(api_key)


# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
# MODIFIED: _get_douyin_response_items
# 鏀寔 TikHub Douyin Search V2 鐨?data.business_data[].data.aweme_info锛?# 鍚屾椂鍏煎 TikHub App 鍘熺敓 data.aweme_list 鍜岃嚜瀹氫箟涓棿浠舵牸寮?# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def _get_douyin_response_items(response):
    """
    Normalize different Douyin/TikHub/custom API response shapes to a list of
    video material dictionaries.

    Supported shapes include:
    - TikHub Douyin Search V2: data.business_data[].data.aweme_info
    - TikHub Douyin App native: data.aweme_list
    - Custom middleware: data.items / data.materials / data.videos / items / videos
    """
    if isinstance(response, list):
        return response

    if not isinstance(response, dict):
        return []

    data = response.get("data")

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        # TikHub Douyin Search V2:
        # data.business_data[].data.aweme_info
        business_data = data.get("business_data")
        if isinstance(business_data, list):
            items = []
            for wrapper in business_data:
                if not isinstance(wrapper, dict):
                    continue

                wrapper_data = wrapper.get("data")
                if isinstance(wrapper_data, dict):
                    aweme_info = wrapper_data.get("aweme_info")
                    if isinstance(aweme_info, dict):
                        items.append(aweme_info)
                        continue

                aweme_info = wrapper.get("aweme_info")
                if isinstance(aweme_info, dict):
                    items.append(aweme_info)
                    continue

                # Keep a fallback item so custom gateways that wrap the media
                # differently still have a chance to be parsed later.
                items.append(wrapper)

            return items

        # TikHub / Douyin App native format: data.aweme_list
        aweme_list = data.get("aweme_list")
        if isinstance(aweme_list, list) and aweme_list:
            return aweme_list

        # Custom middleware formats
        return (
            data.get("items")
            or data.get("materials")
            or data.get("videos")
            or data.get("list")
            or []
        )

    return (
        response.get("items")
        or response.get("materials")
        or response.get("videos")
        or response.get("list")
        or []
    )

def _get_douyin_response_single_or_items(response):
    items = _get_douyin_response_items(response)
    if items:
        return items
    if isinstance(response, dict):
        data = response.get("data")
        if isinstance(data, dict):
            return [data]
        return [response]
    return []


# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
# MODIFIED: _material_url_from_item
# 鏂板瀵?TikHub 鎶栭煶 App 宓屽鏍煎紡 video.play_addr.url_list 鐨勬敮鎸?# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def _material_url_from_item(item: dict) -> str:
    # TikHub Douyin App 鏍煎紡锛氳棰?URL 鍦ㄥ祵濂楃殑 video 瀵硅薄閲?    video = item.get("video")
    if isinstance(video, dict):
        # 浼樺厛鍙栨棤姘村嵃鍦板潃锛屽叾娆℃櫘閫氭挱鏀惧湴鍧€
        for addr_key in ("download_addr", "play_addr_h264", "play_addr"):
            addr = video.get(addr_key)
            if isinstance(addr, dict):
                url_list = addr.get("url_list")
                if isinstance(url_list, list):
                    for url in url_list:
                        if isinstance(url, str) and url.strip():
                            return url.strip()

    # 鑷畾涔変腑闂翠欢 / 鏍囧噯骞抽摵鏍煎紡锛堝師鏈夐€昏緫淇濇寔涓嶅彉锛?    for key in (
        "download_url",
        "video_url",
        "image_url",
        "media_url",
        "url",
        "link",
        "play_url",
    ):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _media_type_from_item(item: dict, media_url: str) -> str:
    explicit_type = str(
        item.get("media_type") or item.get("type") or item.get("kind") or ""
    ).lower()
    if explicit_type in {"image", "photo", "picture"}:
        return "image"
    if explicit_type in {"video", "mp4"}:
        return "video"

    extension = utils.parse_extension(urlparse(media_url).path)
    if extension in const.FILE_TYPE_IMAGES:
        return "image"
    return "video"


# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
# MODIFIED: _build_material_info_from_item
# 鏂板瀵?TikHub 鎶栭煶 App 姣绾ф椂闀跨殑鑷姩杞崲
# TikHub 杩斿洖鐨?video.duration 鍗曚綅鏄绉掞紙濡?15000 = 15绉掞級
# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def _build_material_info_from_item(item: dict, minimum_duration: int) -> MaterialInfo | None:
    media_url = _material_url_from_item(item)
    if not media_url:
        return None

    media_type = _media_type_from_item(item, media_url)

    # TikHub Douyin App 鏍煎紡锛氭椂闀垮湪宓屽鐨?video 瀵硅薄閲岋紝鍗曚綅姣
    duration_raw = None
    video = item.get("video")
    if isinstance(video, dict):
        duration_raw = video.get("duration")
    # 濡傛灉宓屽閲屾病鏈夛紝鍐嶅彇椤跺眰 duration锛堣嚜瀹氫箟涓棿浠舵牸寮忥紝鍗曚綅绉掞級
    if duration_raw is None:
        duration_raw = item.get("duration")

    try:
        duration_val = int(float(duration_raw or minimum_duration))
        # 鑷姩妫€娴嬫绉掞細鎶栭煶 App 鍘熺敓鏃堕暱閫氬父鍦?1000~600000 姣鑼冨洿鍐?        # 濡傛灉鍊?> 600锛?0鍒嗛挓绉掓暟锛変笖鐪嬭捣鏉ユ槸姣閲忕骇锛屽垯闄や互1000杞崲
        if duration_val > 600 and duration_val >= minimum_duration * 1000:
            duration_val = duration_val // 1000
        duration = duration_val
    except (TypeError, ValueError):
        duration = minimum_duration

    if media_type == "video" and duration < minimum_duration:
        return None

    material_item = MaterialInfo()
    material_item.provider = "douyin"
    material_item.url = media_url
    material_item.duration = max(
        duration, minimum_duration if media_type == "image" else 0
    )
    material_item.media_type = media_type
    return material_item


# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
# MODIFIED: _search_videos_douyin_direct
# TikHub Douyin Search V2 浣跨敤 POST JSON锛屼笉鍐嶅厛 GET 鍐?fallback
# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def _get_douyin_filter_duration(minimum_duration: int) -> str:
    """
    TikHub Douyin Search V2 filter_duration:
    - "0": 涓嶉檺
    - "0-1": 1鍒嗛挓浠ュ唴
    - "1-5": 1-5鍒嗛挓
    - "5-10000": 5鍒嗛挓浠ヤ笂
    """
    if minimum_duration >= 300:
        return "5-10000"
    if minimum_duration >= 60:
        return "1-5"
    return "0"


def _search_videos_douyin_direct(
    search_term: str,
    minimum_duration: int,
    video_aspect: VideoAspect,
) -> List[MaterialInfo]:
    api_url = (config.app.get("douyin_material_api_url") or "").strip()
    if not api_url:
        logger.error(
            "douyin_material_api_url is not configured. "
            "Please set TikHub Douyin video search endpoint first."
        )
        return []

    sort_value = str(config.app.get("douyin_material_sort", "hot") or "hot").lower()

    # TikHub sort_type:
    # 0=缁煎悎鎺掑簭, 1=鏈€澶氱偣璧? 2=鏈€鏂板彂甯?    sort_type_map = {
        "hot": "0",
        "popular": "1",
        "latest": "2",
        "newest": "2",
    }

    payload = {
        "keyword": search_term,
        "cursor": 0,
        "sort_type": sort_type_map.get(sort_value, "0"),
        "publish_time": "0",
        "filter_duration": _get_douyin_filter_duration(minimum_duration),
        "content_type": "1",
        "search_id": "",
        "backtrace": "",
    }

    logger.info(f"searching douyin materials: {api_url}, payload: {payload}")

    headers = _get_douyin_material_api_headers()
    headers["Content-Type"] = "application/json"

    r = requests.post(
        api_url,
        json=payload,
        headers=headers,
        proxies=config.proxy,
        verify=_get_tls_verify(),
        timeout=(30, 60),
    )

    logger.info(f"TikHub raw response code={r.status_code}, body={r.text[:2000]}")

    if not r.ok:
        logger.error(
            f"TikHub douyin search failed: code={r.status_code}, body={r.text[:2000]}"
        )
        return []

    response = r.json()
    video_items: List[MaterialInfo] = []

    for raw_item in _get_douyin_response_items(response):
        if not isinstance(raw_item, dict):
            continue

        material_item = _build_material_info_from_item(raw_item, minimum_duration)
        if material_item:
            material_item.provider = "douyin"
            video_items.append(material_item)

    return video_items

def _metadata_video_url_from_item(item: dict) -> str:
    for key in ("video_url", "share_url", "aweme_url", "url", "link"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _resolve_douyin_metadata_item(item: dict, minimum_duration: int) -> List[MaterialInfo]:
    resolver_url = (config.app.get("douyin_resolver_api_url") or "").strip()
    if not resolver_url:
        logger.error(
            "douyin_resolver_api_url is not configured. "
            "Configure an authorized resolver service before using metadata mode."
        )
        return []

    payload = {
        "aweme_id": item.get("aweme_id") or item.get("id") or "",
        "video_url": _metadata_video_url_from_item(item),
        "source": "douyin",
    }
    if not payload["aweme_id"] and not payload["video_url"]:
        return []

    r = requests.post(
        resolver_url,
        json=payload,
        headers=_get_douyin_resolver_api_headers(),
        proxies=config.proxy,
        verify=_get_tls_verify(),
        timeout=(30, 90),
    )
    response = r.json()

    resolved_items: List[MaterialInfo] = []
    for raw_item in _get_douyin_response_single_or_items(response):
        if not isinstance(raw_item, dict):
            continue
        material_item = _build_material_info_from_item(raw_item, minimum_duration)
        if material_item:
            resolved_items.append(material_item)
    return resolved_items


def _search_videos_douyin_metadata(
    search_term: str,
    minimum_duration: int,
    video_aspect: VideoAspect,
) -> List[MaterialInfo]:
    metadata_url = (config.app.get("douyin_metadata_api_url") or "").strip()
    if not metadata_url:
        logger.error(
            "douyin_metadata_api_url is not configured. "
            "Configure a third-party data API before using metadata mode."
        )
        return []

    resolver_url = (config.app.get("douyin_resolver_api_url") or "").strip()
    if not resolver_url:
        logger.error(
            "douyin_resolver_api_url is not configured. "
            "Configure an authorized resolver service before using metadata mode."
        )
        return []

    aspect = VideoAspect(video_aspect)
    params = {
        "query": search_term,
        "minimum_duration": minimum_duration,
        "aspect": aspect.value,
        "sort": config.app.get("douyin_material_sort", "hot"),
        "limit": int(config.app.get("douyin_material_limit", 20) or 20),
    }
    logger.info(f"searching douyin metadata: {metadata_url}, params: {params}")

    r = requests.get(
        metadata_url,
        params=params,
        headers=_get_douyin_metadata_api_headers(),
        proxies=config.proxy,
        verify=_get_tls_verify(),
        timeout=(30, 60),
    )
    response = r.json()
    video_items: List[MaterialInfo] = []

    for raw_item in _get_douyin_response_items(response):
        if not isinstance(raw_item, dict):
            continue
        video_items.extend(_resolve_douyin_metadata_item(raw_item, minimum_duration))

    return video_items


def search_videos_douyin(
    search_term: str,
    minimum_duration: int,
    video_aspect: VideoAspect = VideoAspect.portrait,
) -> List[MaterialInfo]:
    """
    Search an authorized Douyin material service.

    This project intentionally does not bypass Douyin anti-scraping controls. Set
    config.app.douyin_material_source_mode to "direct" for an official/authorized
    material service, or "metadata" to use a third-party data API plus an
    authorized resolver service.
    """
    try:
        source_mode = str(
            config.app.get("douyin_material_source_mode", "direct") or "direct"
        ).lower()
        if source_mode == "metadata":
            return _search_videos_douyin_metadata(
                search_term=search_term,
                minimum_duration=minimum_duration,
                video_aspect=video_aspect,
            )
        return _search_videos_douyin_direct(
            search_term=search_term,
            minimum_duration=minimum_duration,
            video_aspect=video_aspect,
        )
    except Exception as e:
        logger.error(f"search douyin materials failed: {str(e)}")

    return []


def save_video(video_url: str, save_dir: str = "") -> str:
    if not save_dir:
        save_dir = utils.storage_dir("cache_videos")

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    url_without_query = video_url.split("?")[0]
    url_hash = utils.md5(url_without_query)
    video_id = f"vid-{url_hash}"
    video_path = f"{save_dir}/{video_id}.mp4"

    # if video already exists, return the path
    if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
        logger.info(f"video already exists: {video_path}")
        return video_path

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    # if video does not exist, download it
    with open(video_path, "wb") as f:
        f.write(
            requests.get(
                video_url,
                headers=headers,
                proxies=config.proxy,
                verify=_get_tls_verify(),
                timeout=(60, 240),
            ).content
        )

    if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
        clip = None
        try:
            clip = VideoFileClip(video_path)
            duration = clip.duration
            fps = clip.fps
            if duration > 0 and fps > 0:
                return video_path
        except Exception as e:
            logger.warning(f"invalid video file: {video_path} => {str(e)}")
            try:
                os.remove(video_path)
            except Exception as remove_error:
                logger.warning(
                    f"failed to remove invalid video file: {video_path}, error: {str(remove_error)}"
                )
        finally:
            if clip is not None:
                try:
                    clip.close()
                except Exception as close_error:
                    logger.warning(
                        f"failed to close video clip: {video_path}, error: {str(close_error)}"
                    )
    return ""


def _get_url_file_extension(media_url: str, fallback: str) -> str:
    extension = utils.parse_extension(urlparse(media_url).path)
    if extension:
        return extension.lower()
    return fallback


def save_image_as_video(image_url: str, save_dir: str = "", clip_duration: int = 5) -> str:
    if not save_dir:
        save_dir = utils.storage_dir("cache_videos")

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    extension = _get_url_file_extension(image_url, "jpg")
    if extension not in const.FILE_TYPE_IMAGES:
        extension = "jpg"

    url_without_query = image_url.split("?")[0]
    url_hash = utils.md5(url_without_query)
    image_path = f"{save_dir}/img-{url_hash}.{extension}"
    video_path = f"{image_path}.mp4"

    if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
        logger.info(f"image video already exists: {video_path}")
        return video_path

    if not os.path.exists(image_path) or os.path.getsize(image_path) == 0:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        with open(image_path, "wb") as f:
            f.write(
                requests.get(
                    image_url,
                    headers=headers,
                    proxies=config.proxy,
                    verify=_get_tls_verify(),
                    timeout=(60, 240),
                ).content
            )

    clip = None
    final_clip = None
    try:
        clip = (
            ImageClip(image_path)
            .with_duration(max(1, clip_duration))
            .with_position("center")
        )
        zoom_clip = clip.resized(lambda t: 1 + (clip_duration * 0.03) * (t / clip.duration))
        final_clip = CompositeVideoClip([zoom_clip])
        final_clip.write_videofile(video_path, fps=30, logger=None)
        return video_path if os.path.exists(video_path) and os.path.getsize(video_path) > 0 else ""
    except Exception as e:
        logger.warning(f"failed to convert image material to video: {image_url}, error: {str(e)}")
        return ""
    finally:
        for opened_clip in (clip, final_clip):
            if opened_clip is not None:
                try:
                    opened_clip.close()
                except Exception:
                    pass


def _save_enhanced_material_response(response, source_path: str) -> str:
    content_type = response.headers.get("Content-Type", "")
    enhanced_path = f"{os.path.splitext(source_path)[0]}.enhanced.mp4"

    if content_type.startswith("application/json"):
        data = response.json()
        enhanced_url = ""
        if isinstance(data, dict):
            enhanced_url = (
                data.get("download_url")
                or data.get("video_url")
                or data.get("media_url")
                or data.get("url")
                or ""
            )
        if enhanced_url:
            return save_video(enhanced_url, save_dir=os.path.dirname(source_path))
        return ""

    with open(enhanced_path, "wb") as f:
        f.write(response.content)

    if os.path.exists(enhanced_path) and os.path.getsize(enhanced_path) > 0:
        return enhanced_path
    return ""


def _enhance_douyin_material_if_configured(item: MaterialInfo, local_path: str) -> str:
    enhance_url = (config.app.get("douyin_material_enhance_api_url") or "").strip()
    if not enhance_url or item.provider != "douyin" or not local_path:
        return local_path

    api_key = (config.app.get("douyin_material_enhance_api_key") or "").strip()
    headers = _get_bearer_api_headers(api_key)
    headers.pop("Accept", None)
    try:
        logger.info(f"enhancing douyin material with configured service: {local_path}")
        with open(local_path, "rb") as material_file:
            response = requests.post(
                enhance_url,
                files={"file": (os.path.basename(local_path), material_file)},
                data={
                    "provider": item.provider,
                    "media_type": item.media_type,
                },
                headers=headers,
                proxies=config.proxy,
                verify=_get_tls_verify(),
                timeout=(60, 600),
            )
        enhanced_path = _save_enhanced_material_response(response, local_path)
        if enhanced_path:
            logger.info(f"douyin material enhanced: {enhanced_path}")
            return enhanced_path
    except Exception as e:
        logger.warning(
            f"douyin material enhancement failed, using original material: {str(e)}"
        )
    return local_path


def save_material(item: MaterialInfo, save_dir: str = "", max_clip_duration: int = 5) -> str:
    media_type = (getattr(item, "media_type", "") or "").lower()
    if media_type == "image":
        saved_path = save_image_as_video(
            image_url=item.url,
            save_dir=save_dir,
            clip_duration=max_clip_duration,
        )
    else:
        saved_path = save_video(video_url=item.url, save_dir=save_dir)
    return _enhance_douyin_material_if_configured(item, saved_path)


def download_videos(
    task_id: str,
    search_terms: List[str],
    source: str = "pexels",
    video_aspect: VideoAspect = VideoAspect.portrait,
    video_concat_mode: VideoConcatMode = VideoConcatMode.random,
    audio_duration: float = 0.0,
    max_clip_duration: int = 5,
    match_script_order: bool = False,
) -> List[str]:
    search_videos = search_videos_pexels
    if source == "pixabay":
        search_videos = search_videos_pixabay
    elif source == "coverr":
        search_videos = search_videos_coverr
    elif source == "douyin":
        search_videos = search_videos_douyin

    material_directory = config.app.get("material_directory", "").strip()
    if material_directory == "task":
        material_directory = utils.task_dir(task_id)
    elif material_directory and not os.path.isdir(material_directory):
        material_directory = ""

    if match_script_order:
        return _download_videos_by_script_order(
            task_id=task_id,
            search_terms=search_terms,
            search_videos=search_videos,
            video_aspect=video_aspect,
            audio_duration=audio_duration,
            max_clip_duration=max_clip_duration,
            material_directory=material_directory,
        )

    valid_video_items = []
    valid_video_urls = []
    found_duration = 0.0
    for search_term in search_terms:
        video_items = search_videos(
            search_term=search_term,
            minimum_duration=max_clip_duration,
            video_aspect=video_aspect,
        )
        logger.info(f"found {len(video_items)} videos for '{search_term}'")

        for item in video_items:
            if item.url not in valid_video_urls:
                valid_video_items.append(item)
                valid_video_urls.append(item.url)
                found_duration += item.duration

    logger.info(
        f"found total videos: {len(valid_video_items)}, required duration: {audio_duration} seconds, found duration: {found_duration} seconds"
    )
    video_paths = []

    concat_mode_value = getattr(video_concat_mode, "value", video_concat_mode)
    if concat_mode_value == VideoConcatMode.random.value:
        random.shuffle(valid_video_items)

    total_duration = 0.0
    for item in valid_video_items:
        try:
            logger.info(f"downloading video: {item.url}")
            saved_video_path = save_material(
                item=item,
                save_dir=material_directory,
                max_clip_duration=max_clip_duration,
            )
            if saved_video_path:
                logger.info(f"video saved: {saved_video_path}")
                video_paths.append(saved_video_path)
                seconds = min(max_clip_duration, item.duration)
                total_duration += seconds
                if total_duration > audio_duration:
                    logger.info(
                        f"total duration of downloaded videos: {total_duration} seconds, skip downloading more"
                    )
                    break
        except Exception as e:
            logger.error(f"failed to download video: {utils.to_json(item)} => {str(e)}")
    logger.success(f"downloaded {len(video_paths)} videos")
    return video_paths


def _download_videos_by_script_order(
    task_id: str,
    search_terms: List[str],
    search_videos,
    video_aspect: VideoAspect,
    audio_duration: float,
    max_clip_duration: int,
    material_directory: str,
) -> List[str]:
    """
    鎸夎剼鏈枃妗堥『搴忎笅杞界礌鏉愩€?    """
    logger.info("downloading videos with script-order material matching")
    candidate_groups = []
    valid_video_urls = set()
    found_duration = 0.0

    for search_term in search_terms:
        video_items = search_videos(
            search_term=search_term,
            minimum_duration=max_clip_duration,
            video_aspect=video_aspect,
        )
        logger.info(f"found {len(video_items)} videos for '{search_term}'")

        term_items = []
        for item in video_items:
            if item.url in valid_video_urls:
                continue
            term_items.append(item)
            valid_video_urls.add(item.url)
            found_duration += item.duration

        if term_items:
            candidate_groups.append((search_term, term_items))

    logger.info(
        f"found total ordered video candidates: {sum(len(items) for _, items in candidate_groups)}, "
        f"required duration: {audio_duration} seconds, found duration: {found_duration} seconds"
    )

    video_paths = []
    total_duration = 0.0
    candidate_index = 0
    while candidate_groups and total_duration <= audio_duration:
        has_candidate = False
        for search_term, term_items in candidate_groups:
            if candidate_index >= len(term_items):
                continue

            has_candidate = True
            item = term_items[candidate_index]
            try:
                logger.info(
                    f"downloading ordered video for '{search_term}': {item.url}"
                )
                saved_video_path = save_material(
                    item=item,
                    save_dir=material_directory,
                    max_clip_duration=max_clip_duration,
                )
                if saved_video_path:
                    logger.info(f"video saved: {saved_video_path}")
                    video_paths.append(saved_video_path)
                    total_duration += min(max_clip_duration, item.duration)
                    if total_duration > audio_duration:
                        logger.info(
                            f"total duration of downloaded videos: {total_duration} seconds, skip downloading more"
                        )
                        break
            except Exception as e:
                logger.error(
                    f"failed to download ordered video: {utils.to_json(item)} => {str(e)}"
                )

        if not has_candidate:
            break
        candidate_index += 1

    logger.success(f"downloaded {len(video_paths)} ordered videos")
    return video_paths


if __name__ == "__main__":
    download_videos(
        "test123", ["Money Exchange Medium"], audio_duration=100, source="pixabay"
    )
