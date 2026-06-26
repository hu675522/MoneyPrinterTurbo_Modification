import os
import shutil
import socket

import toml
from loguru import logger

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
config_file = f"{root_dir}/config.toml"
_CONTAINER_CGROUP_MARKERS = ("docker", "containerd", "kubepods", "libpod", "podman")
_DOCKER_HOST_GATEWAY_NAME = "host.docker.internal"


def is_running_in_container(
    dockerenv_path: str = "/.dockerenv",
    containerenv_path: str = "/run/.containerenv",
    cgroup_path: str = "/proc/1/cgroup",
) -> bool:
    """
    鍒ゆ柇褰撳墠杩涚▼鏄惁杩愯鍦ㄥ鍣ㄥ唴銆?

    杩欎釜鍒ゆ柇涓昏鐢ㄤ簬 Ollama 榛樿鍦板潃閫夋嫨锛?
    - 鏅€氭湰鏈鸿繍琛屾椂锛宍localhost` 鎸囧悜鐢ㄦ埛鏈哄櫒鏈韩锛?
    - Docker 瀹瑰櫒鍐咃紝`localhost` 鎸囧悜瀹瑰櫒鑷繁锛岃闂涓绘満 Ollama
      閫氬父闇€瑕佷娇鐢?`host.docker.internal`銆?

    涓嶈兘鍙垽鏂?`/proc/1/cgroup` 鏄惁瀛樺湪锛屽洜涓烘櫘閫?Linux 涔熶細鏈夎繖涓枃浠躲€?
    杩欓噷鍙湪妫€娴嬪埌鏄庣‘鐨勫鍣ㄦ爣璁版椂杩斿洖 True锛岄伩鍏嶈浼ら潪 Docker Linux 鐢ㄦ埛銆?
    鍙傛暟淇濈暀涓哄彲娉ㄥ叆璺緞锛屼究浜庡崟鍏冩祴璇曡鐩栦笉鍚岃繍琛岀幆澧冦€?
    """
    if os.path.isfile(dockerenv_path) or os.path.isfile(containerenv_path):
        return True

    try:
        with open(cgroup_path, mode="r", encoding="utf-8") as fp:
            cgroup_content = fp.read().lower()
    except OSError:
        return False

    return any(marker in cgroup_content for marker in _CONTAINER_CGROUP_MARKERS)


def _can_resolve_hostname(hostname: str) -> bool:
    try:
        socket.gethostbyname(hostname)
    except OSError:
        return False
    return True


def _decode_linux_route_gateway(hex_gateway: str) -> str:
    # /proc/net/route 閲岀殑 Gateway 鏄?16 杩涘埗灏忕搴忥紝渚嬪 010011AC 琛ㄧず
    # 172.17.0.1銆傝繖閲屽崟鐙В鏋愶紝鏄负浜嗗湪鍘熺敓 Linux Docker 娌℃湁
    # host.docker.internal DNS 璁板綍鏃讹紝杩樿兘灏濊瘯璁块棶瀹瑰櫒榛樿缃戝叧涓婄殑瀹夸富鏈恒€?
    if len(hex_gateway) != 8:
        raise ValueError("invalid gateway length")

    octets = [
        str(int(hex_gateway[index : index + 2], 16))
        for index in range(6, -1, -2)
    ]
    return ".".join(octets)


def get_container_default_gateway_ip(route_path: str = "/proc/net/route") -> str:
    """
    璇诲彇 Linux 瀹瑰櫒閲岀殑榛樿缃戝叧 IP銆?

    Docker Desktop 閫氬父鎻愪緵 `host.docker.internal`锛屼絾鍘熺敓 Linux Docker
    榛樿涓嶄竴瀹氭彁渚涜繖涓?DNS 鍚嶇О銆傞粯璁ょ綉鍏抽€氬父鍙互浣滀负璁块棶瀹夸富鏈烘湇鍔＄殑
    鍏滃簳鍦板潃锛涘鏋滅敤鎴风殑 Ollama 鍙洃鍚?127.0.0.1锛屽垯浠嶉渶瑕佺敤鎴疯
    Ollama 鐩戝惉瀹夸富鏈虹綉鍗℃垨鎵嬪姩閰嶇疆 `ollama_base_url`銆?
    """
    try:
        with open(route_path, mode="r", encoding="utf-8") as fp:
            route_lines = fp.readlines()
    except OSError:
        return ""

    for line in route_lines[1:]:
        fields = line.strip().split()
        if len(fields) < 3:
            continue

        destination = fields[1]
        gateway = fields[2]
        if destination != "00000000" or gateway == "00000000":
            continue

        try:
            return _decode_linux_route_gateway(gateway)
        except ValueError:
            logger.warning(f"invalid container gateway route entry: {line.strip()}")
            return ""

    return ""


def get_default_ollama_base_url() -> str:
    """
    杩斿洖 Ollama 鐨勯粯璁?OpenAI-compatible base_url銆?

    鐢ㄦ埛鏄惧紡閰嶇疆 `ollama_base_url` 鏃朵笉浼氳蛋杩欓噷锛涜繖閲屽彧澶勭悊鈥滄湭閰嶇疆鏃剁殑
    鏈€浣抽粯璁ゅ€尖€濄€傚鍣ㄥ唴榛樿鎸囧悜瀹夸富鏈猴紝鏅€氭湰鏈鸿繍琛岄粯璁ゆ寚鍚?localhost銆?
    """
    if not is_running_in_container():
        return "http://localhost:11434/v1"

    if _can_resolve_hostname(_DOCKER_HOST_GATEWAY_NAME):
        return f"http://{_DOCKER_HOST_GATEWAY_NAME}:11434/v1"

    gateway_ip = get_container_default_gateway_ip()
    if gateway_ip:
        logger.info(
            "host.docker.internal is not resolvable, fallback to container "
            f"default gateway for Ollama: {gateway_ip}"
        )
        return f"http://{gateway_ip}:11434/v1"

    logger.warning(
        "failed to resolve host.docker.internal and container default gateway; "
        "fallback to host.docker.internal for Ollama"
    )
    return f"http://{_DOCKER_HOST_GATEWAY_NAME}:11434/v1"


def load_config():
    # fix: IsADirectoryError: [Errno 21] Is a directory: '/MoneyPrinterTurbo/config.toml'
    if os.path.isdir(config_file):
        shutil.rmtree(config_file)

    if not os.path.isfile(config_file):
        example_file = f"{root_dir}/config.example.toml"
        if os.path.isfile(example_file):
            shutil.copyfile(example_file, config_file)
            logger.info("copy config.example.toml to config.toml")

    logger.info(f"load config from file: {config_file}")

    try:
        _config_ = toml.load(config_file)
    except Exception as e:
        logger.warning(f"load config failed: {str(e)}, try to load as utf-8-sig")
        with open(config_file, mode="r", encoding="utf-8-sig") as fp:
            _cfg_content = fp.read()
            _config_ = toml.loads(_cfg_content)
    return _config_


def save_config():
    with open(config_file, "w", encoding="utf-8") as f:
        _cfg["app"] = app
        _cfg["azure"] = azure
        _cfg["siliconflow"] = siliconflow
        _cfg["elevenlabs"] = elevenlabs
        _cfg["ui"] = ui
        f.write(toml.dumps(_cfg))


_cfg = load_config()
app = _cfg.get("app", {})
whisper = _cfg.get("whisper", {})
proxy = _cfg.get("proxy", {})
azure = _cfg.get("azure", {})
siliconflow = _cfg.get("siliconflow", {})
elevenlabs = _cfg.get("elevenlabs", {})
ui = _cfg.get(
    "ui",
    {
        "hide_log": False,
    },
)

hostname = socket.gethostname()

log_level = _cfg.get("log_level", "DEBUG")
listen_host = _cfg.get("listen_host", "0.0.0.0")
listen_port = _cfg.get("listen_port", 8080)
project_name = _cfg.get("project_name", "MoneyPrinterTurbo")
project_description = _cfg.get(
    "project_description",
    "<a href='https://github.com/harry0703/MoneyPrinterTurbo'>https://github.com/harry0703/MoneyPrinterTurbo</a>"
    "<br><small>Supported by <a href='https://aihubmix.com/?aff=CEve'>AIHubMix</a></small>",
)
project_version = _cfg.get("project_version", "2.0.1")
reload_debug = False

app["redis_host"] = os.getenv(
    "MPT_APP_REDIS_HOST",
    os.getenv("REDIS_HOST", app.get("redis_host", "localhost")),
)

imagemagick_path = app.get("imagemagick_path", "")
if imagemagick_path and os.path.isfile(imagemagick_path):
    os.environ["IMAGEMAGICK_BINARY"] = imagemagick_path

ffmpeg_path = app.get("ffmpeg_path", "")
if ffmpeg_path and os.path.isfile(ffmpeg_path):
    os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_path

logger.info(f"{project_name} v{project_version}")
