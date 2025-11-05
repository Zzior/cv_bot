from datetime import datetime, tzinfo

DATE_FORMATS = (
    "%H %M",
    "%H %M %S",
    "%Y %m %d",
    "%Y %m %d %H %M",
    "%Y %m %d %H %M %S",
)

def parse_date(text: str, tz: tzinfo | None = None) -> datetime | None:
    if not text:
        return None
    normalized = (
        text.strip()
        .replace("/", " ")
        .replace("-", " ")
        .replace(".", " ")
        .replace(":", " ")
    )
    now = datetime.now()
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(normalized, fmt)
            if "%S" not in fmt:
                dt = dt.replace(second=0)

            if "%H %M" not in fmt:
                dt = dt.replace(hour=0, minute=0)

            if "%Y %m %d" not in fmt:
                dt = dt.replace(year=now.year, month=now.month, day=now.day)

            return dt.astimezone(tz=tz)
        except ValueError:
            continue
    return None