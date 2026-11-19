from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


QUALITY_OPTIONS = (240, 360, 480, 720, 1080, 1440)


def quality_keyboard(
    qualities: list[int],
    preferred_quality: int | None = None,
) -> InlineKeyboardMarkup:
    available = sorted(
        {
            quality
            for quality in qualities
            if quality in QUALITY_OPTIONS
        }
    )

    rows = []

    for index in range(0, len(available), 2):
        row = []

        for quality in available[index:index + 2]:
            label = f"{quality}p"

            if quality == preferred_quality:
                label += " (ذخیره‌شده)"

            row.append(
                InlineKeyboardButton(
                    text=label,
                    callback_data=f"quality_select:{quality}",
                )
            )

        rows.append(row)

    rows.append(
        [
            InlineKeyboardButton(
                text="لغو انتخاب",
                callback_data="quality_cancel",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=rows)