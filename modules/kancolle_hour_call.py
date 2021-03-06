import pytz
from datetime import datetime
import kokkoro
from kokkoro.service import Service, BroadcastTag, BroadcastService
from kokkoro.common_interface import KokkoroBot, EventInterface
from kokkoro import priv, R

#sv = Service('hourcall', enable_on_default=True, help_='时报')
#sv = BroadcastService('kancolle_hour_call', broadcast_tag=BroadcastTag.default, enable_on_default=True, help_='舰C时报')
sv = BroadcastService('kc_call', broadcast_tag=BroadcastTag.default, use_priv=priv.SUPERUSER, manage_priv=priv.SUPERUSER, enable_on_default=True)
tz = pytz.timezone('America/New_York')

def get_hour_call():
    """挑出一组时报，每日更换，一日之内保持相同"""
    cfg = kokkoro.config.modules.kancolle_hour_call
    now = datetime.now(tz)
    hc_groups = cfg.HOUR_CALLS_ON
    g = hc_groups[ now.day % len(hc_groups) ]
    return cfg.HOUR_CALLS[g]


@sv.scheduled_job('cron', hour='*')
async def kc_hour_call():
    cfg = kokkoro.config.modules.kancolle_hour_call
    hc_groups = cfg.HOUR_CALLS_ON
    now = datetime.now(tz)
    if 4 <= now.hour <= 8:
        return  # 宵禁 免打扰
    msg = get_hour_call()[now.hour]
    await sv.broadcast(msg)
    #发送语音
    number = str(cfg.HOUR_CALLS_ON[ now.day % len(hc_groups) ])
    file_name = f"{number}-{now.hour:02}00.mp3"
    await sv.broadcast(R.record(f"kc/{file_name}"))

@sv.on_fullmatch('手动报时')
async def manual_hour_call(bot: KokkoroBot, ev: EventInterface):
    #dir = R.get('record/kc/').path
    cfg = kokkoro.config.modules.kancolle_hour_call
    hc_groups = cfg.HOUR_CALLS_ON
    now = datetime.now(tz)
    msg = get_hour_call()[now.hour]
    await sv.broadcast(msg)
    #发送语音
    number = str(cfg.HOUR_CALLS_ON[ now.day % len(hc_groups) ])
    file_name = f"{number}-{now.hour:02}00.mp3"
    await sv.broadcast(R.record(f"kc/{file_name}"))
