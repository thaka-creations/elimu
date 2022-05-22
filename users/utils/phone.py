import phonenumbers


def phone_number_format(country_code, phone_number):
    _phone = country_code + phone_number

    try:
        converted_phone = phonenumbers.parse(_phone, None)
    except Exception as e:
        print(e)
        return False

    try:
        national_format = phonenumbers.format_number(converted_phone, phonenumbers.PhoneNumberFormat.E164)
    except Exception as e:
        print(e)
        return False

    return national_format
