from datetime import timezone
import dateutil.parser


def formatTime(isoTime):
    """
    Formats a time string in ISO format to a time object.
    """
    # 将字符串时间 转化为 datetime 对象
    isoTime = (isoTime[:-1] + "000Z")
    dateObject = dateutil.parser.isoparse(isoTime)
    localdt = dateObject.replace(tzinfo=timezone.utc).astimezone(tz=None)
    # 本地格式 字符串
    return localdt.strftime('%Y-%m-%d %H:%M:%S')
